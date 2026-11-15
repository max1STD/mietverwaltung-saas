"""Billing-Service — WE-basierte Preisberechnung und Stripe-Integration."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.plan_usage import PlanUsage
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.billing import (
    CheckoutSessionResponse,
    PortalResponse,
    PricePreviewResponse,
    SubscriptionResponse,
)
from app.services.audit_log import audit_log

# Stripe ist optional: falls Keys fehlen, laufen alle Funktionen im Stub-Modus.
try:
    import stripe as stripe_lib

    stripe_lib.api_key = settings.STRIPE_SECRET_KEY or "sk_test_stub"
    STRIPE_AVAILABLE = bool(settings.STRIPE_SECRET_KEY and not settings.STRIPE_SECRET_KEY.startswith("change-me"))
except Exception:  # pragma: no cover
    stripe_lib = None  # type: ignore[assignment]
    STRIPE_AVAILABLE = False


# Preisstaffel gemäß Abo-Modell v3 (Preise in Cent, da Stripe Cent erwartet).
PRICE_TIERS: list[tuple[int, int, Decimal]] = [
    (1, 5, Decimal("9.75")),
    (6, 25, Decimal("7.50")),
    (26, 50, Decimal("5.90")),
]
MAX_WE_SELF_SERVICE = 50
INDIVIDUAL_PRICE_MESSAGE = "Ab 51 Wohneinheiten erstellen wir dir ein individuelles Angebot."


class IndividualPriceResult:
    """Ergebnis für Preisberechnungen über 50 WE."""

    def __init__(self, we_count: int) -> None:
        self.price_per_we = Decimal("0")
        self.total_monthly = Decimal("0")
        self.total_yearly = Decimal("0")
        self.is_individual = True
        self.message = INDIVIDUAL_PRICE_MESSAGE
        self.we_count = we_count


def _tier_for_we(we_count: int) -> Decimal:
    """Ermittelt den Preis pro WE für eine gegebene Anzahl (1-50)."""
    if we_count < 1:
        raise ValueError("Wohnungsanzahl muss mindestens 1 sein")
    if we_count > MAX_WE_SELF_SERVICE:
        raise ValueError(INDIVIDUAL_PRICE_MESSAGE)
    for low, high, price in PRICE_TIERS:
        if low <= we_count <= high:
            return price
    raise ValueError(f"Ungültige Wohnungsanzahl: {we_count}")


def calculate_we_price(
    we_count: int,
    interval: str,
) -> tuple[Decimal, Decimal, Decimal]:
    """Berechnet Preis pro WE, monatlichen und jährlichen Gesamtbetrag.

    Args:
        we_count: Anzahl Wohneinheiten (1-50, Self-Service).
        interval: 'monthly' oder 'yearly'.

    Returns:
        (price_per_we, total_monthly, total_yearly)

    Raises:
        ValueError: bei ungültiger WE-Anzahl oder Interval.
    """
    if interval not in ("monthly", "yearly"):
        raise ValueError("interval muss 'monthly' oder 'yearly' sein")

    price_per_we = _tier_for_we(we_count)
    total_monthly = price_per_we * Decimal(we_count)
    # Jährlich = 10 Monate zahlen (2 Monate geschenkt ≈ 16,67% Rabatt).
    total_yearly = total_monthly * Decimal("10")
    return price_per_we, total_monthly, total_yearly


def is_individual_price(we_count: int) -> bool:
    """Gibt zurück, ob für diese WE-Anzahl ein individuelles Angebot nötig ist."""
    return we_count > MAX_WE_SELF_SERVICE


def _to_decimal(value: Decimal | float | int | str | None) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _subscription_to_response(
    subscription: Subscription,
    plan_usage: PlanUsage | None,
) -> SubscriptionResponse:
    """Mappt DB-Modelle auf das öffentliche Subscription-Response-Schema."""
    we_count = plan_usage.wohnungen_count if plan_usage else 1
    price_per_we = _to_decimal(subscription.price_per_we)
    total_monthly = price_per_we * Decimal(we_count)
    total_yearly = total_monthly * Decimal("10")
    return SubscriptionResponse(
        id=subscription.id,
        user_id=subscription.user_id,
        status=subscription.status,
        price_per_we=price_per_we,
        billing_cycle=subscription.billing_cycle,
        wohnungen_count=we_count,
        total_monthly=total_monthly,
        total_yearly=total_yearly,
        trial_ends_at=subscription.trial_ends_at,
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
        stripe_subscription_id=subscription.stripe_subscription_id,
        cancel_at_period_end=False,
    )


async def get_or_create_subscription(
    db: AsyncSession,
    user: User,
    we_count: int = 1,
    interval: str = "yearly",
) -> Subscription:
    """Liefert das bestehende Abo oder legt ein Trial-Abo an."""
    if user.subscription is not None:
        return user.subscription

    result = await db.execute(select(Subscription).where(Subscription.user_id == user.id))
    existing = result.scalar_one_or_none()
    if existing:
        user.subscription = existing
        return existing

    price_per_we, _, _ = calculate_we_price(max(we_count, 1), interval)
    subscription = Subscription(
        user_id=user.id,
        price_per_we=price_per_we,
        billing_cycle=interval,
        status="trial",
        trial_ends_at=datetime.now(UTC) + timedelta(days=14),
    )
    db.add(subscription)
    await db.flush()
    await db.refresh(subscription)
    user.subscription = subscription

    # PlanUsage anlegen falls nicht vorhanden.
    await _ensure_plan_usage(db, user, max(we_count, 1))

    return subscription


async def _count_einheiten(db: AsyncSession, vermieter_id: int) -> int:
    """Zählt die aktiven Wohneinheiten eines Vermieters."""
    from app.models.einheit import Einheit

    result = await db.execute(
        select(Einheit).where(
            Einheit.vermieter_id == vermieter_id,
            Einheit.deleted_at.is_(None),
        )
    )
    return len(result.scalars().all())


async def _ensure_plan_usage(
    db: AsyncSession,
    user: User,
    we_count: int = 1,
) -> PlanUsage:
    """Liefert oder erstellt PlanUsage ohne Duplikate."""
    from sqlalchemy import select

    if user.plan_usage is not None:
        return user.plan_usage

    result = await db.execute(select(PlanUsage).where(PlanUsage.user_id == user.id))
    existing = result.scalar_one_or_none()
    if existing:
        user.plan_usage = existing
        return existing

    plan_usage = PlanUsage(
        user_id=user.id,
        wohnungen_count=max(we_count, 1),
    )
    db.add(plan_usage)
    await db.flush()
    await db.refresh(plan_usage)
    user.plan_usage = plan_usage
    return plan_usage


async def sync_plan_usage(
    db: AsyncSession,
    user: User,
) -> PlanUsage:
    """Synchronisiert PlanUsage mit der aktuellen WE-Anzahl."""
    we_count = await _count_einheiten(db, user.id)
    we_count = max(we_count, 1)
    plan_usage = await _ensure_plan_usage(db, user, we_count)
    plan_usage.wohnungen_count = we_count
    plan_usage.last_checked_at = datetime.now(UTC)
    await db.flush()
    return plan_usage


async def get_current_subscription_response(
    db: AsyncSession,
    user: User,
) -> SubscriptionResponse:
    """Gibt den aktuellen Abo-Status zurück (inkl. Live-WE-Anzahl)."""
    plan_usage = await sync_plan_usage(db, user)
    subscription = await get_or_create_subscription(
        db,
        user,
        we_count=plan_usage.wohnungen_count,
        interval="yearly",
    )
    return _subscription_to_response(subscription, plan_usage)


def get_price_preview(
    we_count: int,
    interval: str,
) -> PricePreviewResponse:
    """Berechnet eine Preisvorschau ohne DB-Zugriff."""
    if is_individual_price(we_count):
        return PricePreviewResponse(
            wohnungen_count=we_count,
            price_per_we=Decimal("0"),
            interval=interval,
            total_monthly=Decimal("0"),
            total_yearly=Decimal("0"),
            yearly_discount_percent=17 if interval == "yearly" else 0,
            currency="eur",
            is_individual=True,
            message=INDIVIDUAL_PRICE_MESSAGE,
        )
    price_per_we, total_monthly, total_yearly = calculate_we_price(we_count, interval)
    return PricePreviewResponse(
        wohnungen_count=we_count,
        price_per_we=price_per_we,
        interval=interval,
        total_monthly=total_monthly,
        total_yearly=total_yearly,
        yearly_discount_percent=17 if interval == "yearly" else 0,
        currency="eur",
        is_individual=False,
        message=None,
    )

async def _ensure_stripe_customer(
    db: AsyncSession,
    user: User,
) -> str:
    """Erzeugt oder liefert die Stripe-Customer-ID eines Users."""
    subscription = await get_or_create_subscription(db, user)
    if subscription.stripe_customer_id:
        return subscription.stripe_customer_id

    if not STRIPE_AVAILABLE:
        subscription.stripe_customer_id = f"cus_stub_{user.id}"
        await db.flush()
        return subscription.stripe_customer_id

    customer = stripe_lib.Customer.create(
        email=user.email,
        name=user.full_name,
        metadata={"user_id": str(user.id)},
    )
    subscription.stripe_customer_id = customer.id
    await db.flush()
    return customer.id  # type: ignore[no-any-return]


def _stripe_price_cents(price_per_we: Decimal, we_count: int, interval: str) -> int:
    """Berechnet den Stripe-Preis in Cent für eine Subscription."""
    if interval == "yearly":
        total = price_per_we * Decimal(we_count) * Decimal("10")
    else:
        total = price_per_we * Decimal(we_count)
    return int(total * Decimal("100"))


async def create_stripe_checkout_session(
    db: AsyncSession,
    user: User,
    we_count: int,
    interval: str,
    success_url: str | None = None,
    cancel_url: str | None = None,
    ip: str | None = None,
) -> CheckoutSessionResponse:
    """Erstellt eine Stripe Checkout-Session mit 14-Tage-Trial.

    Ohne Stripe-Keys wird ein Stub zurückgegeben (Dev-Modus, keine echte Abrechnung).
    """
    if we_count > MAX_WE_SELF_SERVICE:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Ab {MAX_WE_SELF_SERVICE + 1} Wohneinheiten bitte individuelles Angebot anfragen",
        )

    price_per_we, total_monthly, _ = calculate_we_price(we_count, interval)
    plan_usage = await sync_plan_usage(db, user)
    plan_usage.wohnungen_count = we_count
    plan_usage.last_checked_at = datetime.now(UTC)

    subscription = await get_or_create_subscription(db, user, we_count, interval)
    subscription.price_per_we = price_per_we
    subscription.billing_cycle = interval

    customer_id = await _ensure_stripe_customer(db, user)

    default_url = "http://localhost:5173/dashboard"
    success_url = success_url or default_url
    cancel_url = cancel_url or default_url

    if not STRIPE_AVAILABLE:
        # Dev-Stub: keine echte Stripe-Abrechnung.
        await audit_log(
            db,
            user_id=user.id,
            vermieter_id=user.id,
            action="checkout_session_created_stub",
            entity="subscriptions",
            entity_id=subscription.id,
            details={
                "we_count": we_count,
                "interval": interval,
                "price_per_we": str(price_per_we),
                "customer_id": customer_id,
            },
            ip=ip,
            risk_level="niedrig",
        )
        return CheckoutSessionResponse(
            session_url=None,
            session_id=f"cs_stub_{user.id}_{datetime.now(UTC).timestamp()}",
            mode="stripe",
            message="Stripe-Keys nicht konfiguriert — Checkout läuft im Demo-Modus.",
        )

    # Stripe Checkout mit Inline-Preis (Custom dynamic price).
    unit_amount = _stripe_price_cents(price_per_we, we_count, interval)
    session = stripe_lib.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": f"MietVerwaltung Pro-WE — {we_count} Wohneinheit{'en' if we_count > 1 else ''}",
                        "description": f"{price_per_we} €/WE/Monat, abgerechnet {interval}",
                    },
                    "unit_amount": unit_amount,
                    # Für jährliche Zahlung: einmalig alle 12 Monate (Trial beginnt danach).
                    "recurring": {"interval": "year" if interval == "yearly" else "month"},
                },
                "quantity": 1,
            }
        ],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        subscription_data={
            "trial_period_days": 14,
            "metadata": {
                "user_id": str(user.id),
                "we_count": str(we_count),
                "price_per_we": str(price_per_we),
            },
        },
        metadata={
            "user_id": str(user.id),
            "we_count": str(we_count),
            "interval": interval,
        },
    )

    subscription.stripe_subscription_id = session.subscription
    await audit_log(
        db,
        user_id=user.id,
        vermieter_id=user.id,
        action="checkout_session_created",
        entity="subscriptions",
        entity_id=subscription.id,
        details={
            "session_id": session.id,
            "we_count": we_count,
            "interval": interval,
            "price_per_we": str(price_per_we),
        },
        ip=ip,
        risk_level="niedrig",
    )

    return CheckoutSessionResponse(
        session_url=session.url,
        session_id=session.id,
        mode="stripe",
        message=None,
    )


async def update_subscription_we_count(
    db: AsyncSession,
    user: User,
    we_count: int,
    interval: str,
    ip: str | None = None,
) -> SubscriptionResponse:
    """Aktualisiert WE-Anzahl und Intervall (Upgrade/Downgrade).

    Bei aktivem Stripe-Abonnement wird die bestehende Subscription über
    Stripe geupdatet (Items mit neuer Menge/Preis).
    """
    if we_count > MAX_WE_SELF_SERVICE:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Ab {MAX_WE_SELF_SERVICE + 1} Wohneinheiten bitte individuelles Angebot anfragen",
        )

    price_per_we, _, _ = calculate_we_price(we_count, interval)
    plan_usage = await sync_plan_usage(db, user)
    plan_usage.wohnungen_count = we_count
    plan_usage.last_checked_at = datetime.now(UTC)

    subscription = await get_or_create_subscription(db, user, we_count, interval)
    subscription.price_per_we = price_per_we
    subscription.billing_cycle = interval

    if STRIPE_AVAILABLE and subscription.stripe_subscription_id:
        try:
            stripe_sub = stripe_lib.Subscription.retrieve(subscription.stripe_subscription_id)
            if stripe_sub.items.data:
                item_id = stripe_sub.items.data[0].id
                new_amount = _stripe_price_cents(price_per_we, we_count, interval)
                stripe_lib.Subscription.modify(
                    subscription.stripe_subscription_id,
                    items=[
                        {
                            "id": item_id,
                            "price_data": {
                                "currency": "eur",
                                "product_data": {
                                    "name": f"MietVerwaltung Pro-WE — {we_count} WE",
                                },
                                "unit_amount": new_amount,
                                "recurring": {
                                    "interval": "year" if interval == "yearly" else "month",
                                },
                            },
                        }
                    ],
                    proration_behavior="create_prorations",
                    metadata={
                        "user_id": str(user.id),
                        "we_count": str(we_count),
                        "price_per_we": str(price_per_we),
                    },
                )
        except Exception as exc:
            # Stripe-Fehler sollten das eigene DB-Update nicht verhindern.
            await audit_log(
                db,
                user_id=user.id,
                vermieter_id=user.id,
                action="subscription_stripe_update_failed",
                entity="subscriptions",
                entity_id=subscription.id,
                details={"error": str(exc)},
                ip=ip,
                risk_level="mittel",
            )

    await audit_log(
        db,
        user_id=user.id,
        vermieter_id=user.id,
        action="subscription_updated",
        entity="subscriptions",
        entity_id=subscription.id,
        details={
            "we_count": we_count,
            "interval": interval,
            "price_per_we": str(price_per_we),
        },
        ip=ip,
        risk_level="niedrig",
    )
    await db.flush()
    return _subscription_to_response(subscription, plan_usage)


async def cancel_subscription(
    db: AsyncSession,
    user: User,
    reason: str | None = None,
    ip: str | None = None,
) -> SubscriptionResponse:
    """Kündigt das Abo zum Periodenende.

    Ohne Stripe-Keys wird nur der lokale Status auf 'cancelled' gesetzt (Dev-Stub).
    """
    subscription = await get_or_create_subscription(db, user)

    if STRIPE_AVAILABLE and subscription.stripe_subscription_id:
        try:
            stripe_lib.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True,
            )
        except Exception as exc:
            await audit_log(
                db,
                user_id=user.id,
                vermieter_id=user.id,
                action="subscription_cancel_stripe_failed",
                entity="subscriptions",
                entity_id=subscription.id,
                details={"error": str(exc)},
                ip=ip,
                risk_level="mittel",
            )

    subscription.status = "cancelled"
    await audit_log(
        db,
        user_id=user.id,
        vermieter_id=user.id,
        action="subscription_cancelled",
        entity="subscriptions",
        entity_id=subscription.id,
        details={"reason": reason},
        ip=ip,
        risk_level="mittel",
    )
    await db.flush()
    plan_usage = user.plan_usage
    return _subscription_to_response(subscription, plan_usage)


async def create_customer_portal(
    db: AsyncSession,
    user: User,
    return_url: str | None = None,
) -> PortalResponse:
    """Erstellt eine Stripe Customer-Portal-Session."""
    customer_id = await _ensure_stripe_customer(db, user)

    if not STRIPE_AVAILABLE:
        return PortalResponse(
            url=None,
            message="Stripe-Keys nicht konfiguriert — Customer Portal im Demo-Modus.",
        )

    return_url = return_url or "http://localhost:5173/einstellungen"
    session = stripe_lib.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return PortalResponse(url=session.url, message=None)


async def handle_checkout_completed(
    db: AsyncSession,
    session_obj: dict[str, Any],
) -> None:
    """Verarbeitet checkout.session.completed Webhook."""
    user_id_raw = session_obj.get("metadata", {}).get("user_id") or session_obj.get("client_reference_id")
    if not user_id_raw:
        return
    user_id = int(user_id_raw)
    user = await db.get(User, user_id)
    if not user:
        return

    subscription = await get_or_create_subscription(db, user)
    subscription.stripe_subscription_id = session_obj.get("subscription")
    subscription.stripe_customer_id = session_obj.get("customer")
    subscription.status = "active"
    if subscription.trial_ends_at is None:
        subscription.trial_ends_at = datetime.now(UTC) + timedelta(days=14)
    subscription.current_period_start = datetime.now(UTC)
    subscription.current_period_end = datetime.now(UTC) + timedelta(days=365)

    await audit_log(
        db,
        user_id=user.id,
        vermieter_id=user.id,
        action="checkout_completed",
        entity="subscriptions",
        entity_id=subscription.id,
        details={"session_id": session_obj.get("id")},
        risk_level="mittel",
    )
    await db.flush()


async def handle_invoice_paid(
    db: AsyncSession,
    invoice: dict[str, Any],
) -> None:
    """Verarbeitet invoice.paid Webhook."""
    subscription_id = invoice.get("subscription")
    if not subscription_id:
        return
    result = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    if not subscription:
        return

    subscription.status = "active"
    subscription.current_period_start = datetime.now(UTC)
    subscription.current_period_end = datetime.now(UTC) + timedelta(days=30)
    await audit_log(
        db,
        user_id=subscription.user_id,
        vermieter_id=subscription.user_id,
        action="invoice_paid",
        entity="subscriptions",
        entity_id=subscription.id,
        details={"invoice_id": invoice.get("id")},
        risk_level="niedrig",
    )
    await db.flush()


async def handle_invoice_payment_failed(
    db: AsyncSession,
    invoice: dict[str, Any],
) -> None:
    """Verarbeitet invoice.payment_failed Webhook."""
    subscription_id = invoice.get("subscription")
    if not subscription_id:
        return
    result = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    if not subscription:
        return

    subscription.status = "past_due"
    await audit_log(
        db,
        user_id=subscription.user_id,
        vermieter_id=subscription.user_id,
        action="invoice_payment_failed",
        entity="subscriptions",
        entity_id=subscription.id,
        details={"invoice_id": invoice.get("id")},
        risk_level="hoch",
    )
    await db.flush()


async def handle_subscription_deleted(
    db: AsyncSession,
    stripe_subscription: dict[str, Any],
) -> None:
    """Verarbeitet customer.subscription.deleted Webhook."""
    subscription_id = stripe_subscription.get("id")
    if not subscription_id:
        return
    result = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    if not subscription:
        return

    subscription.status = "cancelled"
    await audit_log(
        db,
        user_id=subscription.user_id,
        vermieter_id=subscription.user_id,
        action="subscription_deleted",
        entity="subscriptions",
        entity_id=subscription.id,
        details={"stripe_subscription_id": subscription_id},
        risk_level="mittel",
    )
    await db.flush()
