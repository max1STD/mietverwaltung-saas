"""Phase 2: Billing- und Preisberechnungstests."""
from __future__ import annotations

import pytest
from decimal import Decimal
from httpx import AsyncClient

from app.models.user import User
from app.services.billing import calculate_we_price, get_price_preview


@pytest.mark.phase2
@pytest.mark.asyncio
async def test_price_tier_1_to_5() -> None:
    """1-5 WE kosten 9,75 €/WE/Monat."""
    price_per_we, total_monthly, total_yearly = calculate_we_price(3, "monthly")
    assert price_per_we == 9.75
    assert total_monthly == 29.25
    assert total_yearly == 292.50


@pytest.mark.phase2
@pytest.mark.asyncio
async def test_price_tier_6_to_25() -> None:
    """6-25 WE kosten 7,50 €/WE/Monat."""
    price_per_we, total_monthly, total_yearly = calculate_we_price(10, "yearly")
    assert price_per_we == 7.50
    assert total_monthly == 75.00
    assert total_yearly == 750.00


@pytest.mark.phase2
@pytest.mark.asyncio
async def test_price_tier_26_to_49() -> None:
    """26-49 WE kosten 5,90 €/WE/Monat."""
    price_per_we, total_monthly, total_yearly = calculate_we_price(30, "yearly")
    assert price_per_we == Decimal("5.90")
    assert total_monthly == Decimal("177.00")
    assert total_yearly == Decimal("1770.00")


@pytest.mark.phase2
@pytest.mark.asyncio
async def test_price_50_plus_raises() -> None:
    """Ab 50 WE wird ein Fehler geworfen (Custom Pricing)."""
    with pytest.raises(ValueError, match="Angebot anfragen"):
        calculate_we_price(50, "yearly")


@pytest.mark.phase2
@pytest.mark.asyncio
async def test_price_preview_response(auth_client: AsyncClient) -> None:
    """GET /billing/price-preview liefert korrekte Preise."""
    response = await auth_client.get("/api/v1/billing/price-preview?we=7&interval=yearly")
    assert response.status_code == 200
    data = response.json()
    assert data["wohnungen_count"] == 7
    assert data["price_per_we"] == "7.50"
    assert data["total_monthly"] == "52.50"
    assert data["total_yearly"] == "525.00"


@pytest.mark.phase2
@pytest.mark.asyncio
async def test_get_my_subscription(auth_client: AsyncClient, vermieter_user: User) -> None:
    """GET /billing/subscription/me legt bei Bedarf ein Trial-Abo an."""
    response = await auth_client.get("/api/v1/billing/subscription/me")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == vermieter_user.id
    assert data["status"] == "trial"
    assert data["billing_cycle"] == "yearly"


@pytest.mark.phase2
@pytest.mark.asyncio
async def test_update_subscription(auth_client: AsyncClient, vermieter_user: User) -> None:
    """PATCH /billing/subscription/me aktualisiert WE-Anzahl und Intervall."""
    response = await auth_client.patch(
        "/api/v1/billing/subscription/me",
        json={"we_count": 8, "interval": "monthly"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["wohnungen_count"] == 8
    assert data["billing_cycle"] == "monthly"
    assert data["price_per_we"] == "7.50"
    assert data["total_monthly"] == "60.00"


@pytest.mark.phase2
@pytest.mark.asyncio
async def test_cancel_subscription(auth_client: AsyncClient, vermieter_user: User) -> None:
    """POST /billing/subscription/me/cancel kündigt das Abo."""
    response = await auth_client.post(
        "/api/v1/billing/subscription/me/cancel",
        json={"reason": "Zu teuer"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"


@pytest.mark.phase2
@pytest.mark.asyncio
async def test_checkout_session_stub(auth_client: AsyncClient) -> None:
    """POST /billing/checkout-session ohne Stripe-Keys liefert Demo-Stub."""
    response = await auth_client.post(
        "/api/v1/billing/checkout-session",
        json={"we_count": 5, "interval": "yearly"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "stripe"
    assert "Stub" in data["message"] or "Demo" in data["message"] or data["message"] is None


@pytest.mark.phase2
@pytest.mark.asyncio
async def test_portal_stub(auth_client: AsyncClient) -> None:
    """POST /billing/portal ohne Stripe-Keys liefert Demo-Stub."""
    response = await auth_client.post("/api/v1/billing/portal", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["url"] is None or isinstance(data["url"], str)
