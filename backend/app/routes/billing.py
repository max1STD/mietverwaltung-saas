"""Billing-Routen — Checkout, Abo-Verwaltung und Stripe-Portal."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.middleware.auth import _get_client_ip, csrf_protect, require_role
from app.models.user import User
from app.schemas.billing import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    PortalResponse,
    SubscriptionCancelRequest,
    SubscriptionResponse,
    SubscriptionUpdateRequest,
)
from app.services.billing import (
    cancel_subscription,
    create_customer_portal,
    create_stripe_checkout_session,
    get_current_subscription_response,
    get_price_preview,
    update_subscription_we_count,
)

router = APIRouter()


@router.get("/price-preview", response_model=dict)
async def price_preview(
    we: int,
    interval: str = "yearly",
) -> dict:
    """Berechnet die Preisvorschau für eine WE-Anzahl (öffentlich, keine Auth)."""
    try:
        return get_price_preview(we, interval).model_dump()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.post(
    "/checkout-session",
    response_model=CheckoutSessionResponse,
    dependencies=[Depends(csrf_protect)],
)
async def checkout_session(
    request: Request,
    data: CheckoutSessionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> CheckoutSessionResponse:
    """Startet eine Stripe-Checkout-Session für das aktuelle Abo."""
    return await create_stripe_checkout_session(
        db,
        user,
        we_count=data.we_count,
        interval=data.interval,
        success_url=data.success_url or f"{settings.CORS_ORIGINS[0]}/dashboard",
        cancel_url=data.cancel_url or f"{settings.CORS_ORIGINS[0]}/einstellungen",
        ip=_get_client_ip(request),
    )


@router.get("/subscription/me", response_model=SubscriptionResponse)
async def get_my_subscription(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> SubscriptionResponse:
    """Gibt das eigene Abonnement zurück."""
    return await get_current_subscription_response(db, user)


@router.patch(
    "/subscription/me",
    response_model=SubscriptionResponse,
    dependencies=[Depends(csrf_protect)],
)
async def update_my_subscription(
    request: Request,
    data: SubscriptionUpdateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> SubscriptionResponse:
    """Ändert WE-Anzahl und Abrechnungsintervall (Upgrade/Downgrade)."""
    return await update_subscription_we_count(
        db,
        user,
        we_count=data.we_count,
        interval=data.interval,
        ip=_get_client_ip(request),
    )


@router.post(
    "/subscription/me/cancel",
    response_model=SubscriptionResponse,
    dependencies=[Depends(csrf_protect)],
)
async def cancel_my_subscription(
    request: Request,
    data: SubscriptionCancelRequest | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> SubscriptionResponse:
    """Kündigt das eigene Abonnement zum Periodenende."""
    return await cancel_subscription(
        db,
        user,
        reason=data.reason if data else None,
        ip=_get_client_ip(request),
    )


@router.post(
    "/portal",
    response_model=PortalResponse,
    dependencies=[Depends(csrf_protect)],
)
async def billing_portal(
    request: Request,
    return_url: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> PortalResponse:
    """Erstellt eine Stripe Customer-Portal-Session."""
    return await create_customer_portal(
        db,
        user,
        return_url=return_url or f"{settings.CORS_ORIGINS[0]}/einstellungen",
    )
