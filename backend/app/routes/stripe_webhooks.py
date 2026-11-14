"""Stripe-Webhook-Route — signaturverifizierte Event-Verarbeitung."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.services.billing import (
    STRIPE_AVAILABLE,
    handle_checkout_completed,
    handle_invoice_paid,
    handle_invoice_payment_failed,
    handle_subscription_deleted,
    stripe_lib,
)

router = APIRouter()


async def _verify_stripe_signature(request: Request) -> dict[str, Any]:
    """Prüft die Stripe-Signatur, falls ein Webhook-Secret konfiguriert ist."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    if not settings.STRIPE_WEBHOOK_SECRET or settings.STRIPE_WEBHOOK_SECRET.startswith("change-me"):
        # Dev-Modus: Signaturprüfung deaktiviert, aber Payload muss valides JSON sein.
        try:
            import json

            return json.loads(payload)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ungültiges Webhook-Payload",
            ) from exc

    if not STRIPE_AVAILABLE or stripe_lib is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe nicht verfügbar",
        )

    try:
        event = stripe_lib.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ungültige Stripe-Signatur: {exc}",
        ) from exc

    return event


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Empfängt Stripe-Webhooks und aktualisiert das Abo."""
    event = await _verify_stripe_signature(request)
    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        await handle_checkout_completed(db, data)
    elif event_type == "invoice.paid":
        await handle_invoice_paid(db, data)
    elif event_type == "invoice.payment_failed":
        await handle_invoice_payment_failed(db, data)
    elif event_type == "customer.subscription.deleted":
        await handle_subscription_deleted(db, data)
    else:
        # Nicht behandelte Events werden still ignoriert (idempotent).
        return {"received": True, "handled": False, "type": event_type}

    await db.commit()
    return {"received": True, "handled": True, "type": event_type}
