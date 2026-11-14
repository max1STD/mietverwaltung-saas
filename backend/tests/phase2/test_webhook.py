"""Phase 2: Stripe-Webhook-Tests."""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.models.subscription import Subscription


def _build_checkout_payload(user_id: int, subscription_id: str = "sub_test_123") -> dict:
    return {
        "id": "evt_test_checkout",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "metadata": {"user_id": str(user_id)},
                "subscription": subscription_id,
                "customer": "cus_test_123",
            }
        },
    }


@pytest.mark.phase2
@pytest.mark.asyncio
async def test_stripe_webhook_checkout_completed(
    auth_client: AsyncClient,
    vermieter_user,
) -> None:
    """checkout.session.completed aktiviert das Abo."""
    # Sicherstellen, dass ein Abo existiert.
    await auth_client.get("/api/v1/billing/subscription/me")
    assert vermieter_user.subscription is not None

    payload = _build_checkout_payload(vermieter_user.id)
    response = await auth_client.post(
        "/api/v1/webhooks/stripe",
        json=payload,
        headers={"stripe-signature": "test_sig"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["handled"] is True
    assert data["type"] == "checkout.session.completed"


@pytest.mark.phase2
@pytest.mark.asyncio
async def test_stripe_webhook_invoice_paid(
    auth_client: AsyncClient,
    vermieter_user,
) -> None:
    """invoice.paid aktualisiert den Abo-Status."""
    await auth_client.get("/api/v1/billing/subscription/me")
    assert vermieter_user.subscription is not None

    # Stripe-Subscription-ID simulieren
    session = auth_client.db_session
    sub = await session.get(Subscription, vermieter_user.subscription.id)
    sub.stripe_subscription_id = "sub_invoice_123"
    await session.flush()

    payload = {
        "id": "evt_test_invoice_paid",
        "type": "invoice.paid",
        "data": {
            "object": {
                "id": "in_test_123",
                "subscription": "sub_invoice_123",
            }
        },
    }
    response = await auth_client.post(
        "/api/v1/webhooks/stripe",
        json=payload,
        headers={"stripe-signature": "test_sig"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["handled"] is True
    assert data["type"] == "invoice.paid"


@pytest.mark.phase2
@pytest.mark.asyncio
async def test_stripe_webhook_invoice_payment_failed(
    auth_client: AsyncClient,
    vermieter_user,
) -> None:
    """invoice.payment_failed setzt Status auf past_due."""
    await auth_client.get("/api/v1/billing/subscription/me")
    assert vermieter_user.subscription is not None

    session = auth_client.db_session
    sub = await session.get(Subscription, vermieter_user.subscription.id)
    sub.stripe_subscription_id = "sub_failed_123"
    await session.flush()

    payload = {
        "id": "evt_test_invoice_failed",
        "type": "invoice.payment_failed",
        "data": {
            "object": {
                "id": "in_failed_123",
                "subscription": "sub_failed_123",
            }
        },
    }
    response = await auth_client.post(
        "/api/v1/webhooks/stripe",
        json=payload,
        headers={"stripe-signature": "test_sig"},
    )
    assert response.status_code == 200


@pytest.mark.phase2
@pytest.mark.asyncio
async def test_stripe_webhook_subscription_deleted(
    auth_client: AsyncClient,
    vermieter_user,
) -> None:
    """customer.subscription.deleted kündigt das Abo."""
    await auth_client.get("/api/v1/billing/subscription/me")
    assert vermieter_user.subscription is not None

    session = auth_client.db_session
    sub = await session.get(Subscription, vermieter_user.subscription.id)
    sub.stripe_subscription_id = "sub_deleted_123"
    await session.flush()

    payload = {
        "id": "evt_test_subscription_deleted",
        "type": "customer.subscription.deleted",
        "data": {
            "object": {
                "id": "sub_deleted_123",
            }
        },
    }
    response = await auth_client.post(
        "/api/v1/webhooks/stripe",
        json=payload,
        headers={"stripe-signature": "test_sig"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["handled"] is True


@pytest.mark.phase2
@pytest.mark.asyncio
async def test_stripe_webhook_ignores_unknown_events(auth_client: AsyncClient) -> None:
    """Unbekannte Events werden ignoriert."""
    payload = {
        "id": "evt_test_unknown",
        "type": "charge.succeeded",
        "data": {"object": {"id": "ch_test"}},
    }
    response = await auth_client.post(
        "/api/v1/webhooks/stripe",
        json=payload,
        headers={"stripe-signature": "test_sig"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["handled"] is False
    assert data["received"] is True
