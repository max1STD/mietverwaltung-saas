"""Pydantic-Schemas für Billing- und Subscription-Endpunkte."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PricePreviewRequest(BaseModel):
    """Eingabe für die Preisvorschau."""

    we: int = Field(..., ge=1, le=50)
    interval: str = Field(..., pattern="^(monthly|yearly)$")


class PricePreviewResponse(BaseModel):
    """Preisvorschau für eine WE-Anzahl und Abrechnungsperiode."""

    wohnungen_count: int
    price_per_we: Decimal
    interval: str
    total_monthly: Decimal
    total_yearly: Decimal
    yearly_discount_percent: int = 20
    currency: str = "eur"
    is_individual: bool = False
    message: str | None = None


class CheckoutSessionRequest(BaseModel):
    """Startet eine Stripe-Checkout-Session."""

    we_count: int = Field(..., ge=1, le=50)
    interval: str = Field(..., pattern="^(monthly|yearly)$")
    success_url: str | None = Field(None, max_length=1024)
    cancel_url: str | None = Field(None, max_length=1024)


class CheckoutSessionResponse(BaseModel):
    """Antwort mit Checkout-Session-URL."""

    session_url: str | None = None
    session_id: str | None = None
    mode: str = "stripe"
    message: str | None = None


class SubscriptionUpdateRequest(BaseModel):
    """Änderung der Abo-Parameter."""

    we_count: int = Field(..., ge=1, le=50)
    interval: str = Field(..., pattern="^(monthly|yearly)$")


class SubscriptionCancelRequest(BaseModel):
    """Kündigung eines Abonnements."""

    reason: str | None = Field(None, max_length=500)


class SubscriptionResponse(BaseModel):
    """Aktueller Abo-Status."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: str
    price_per_we: Decimal
    billing_cycle: str
    wohnungen_count: int
    total_monthly: Decimal
    total_yearly: Decimal
    trial_ends_at: datetime | None = None
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    stripe_subscription_id: str | None = None
    cancel_at_period_end: bool = False


class PortalResponse(BaseModel):
    """Stripe Customer Portal URL."""

    url: str | None = None
    message: str | None = None


class WebhookPayload(BaseModel):
    """Eingehendes Stripe-Webhook-Payload (wird manuell geprüft)."""

    pass
