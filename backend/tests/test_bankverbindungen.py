"""Tests fuer Bankverbindung-CRUD-Endpunkte."""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio(loop_scope="function")
async def test_create_bankverbindung(auth_client: AsyncClient, vermieter_user: User) -> None:
    """Ein Vermieter kann eine Bankverbindung anlegen."""
    payload = {
        "iban": "DE89 3704 0044 0532 0130 00",
        "bic": "COBADEFFXXX",
        "kontoinhaber": "Max Mustermann",
        "bankname": "Commerzbank",
        "is_default": True,
    }
    response = await auth_client.post("/api/v1/bankverbindungen", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["iban"] == "DE89370400440532013000"
    assert data["bic"] == payload["bic"]
    assert data["kontoinhaber"] == payload["kontoinhaber"]
    assert data["is_default"] is True
    assert data["vermieter_id"] == vermieter_user.id


@pytest.mark.asyncio(loop_scope="function")
async def test_list_bankverbindungen(auth_client: AsyncClient) -> None:
    """Bankverbindungen werden zurueckgegeben mit entschluesselter IBAN."""
    await auth_client.post(
        "/api/v1/bankverbindungen",
        json={
            "iban": "DE89 3704 0044 0532 0130 00",
            "kontoinhaber": "Max Mustermann",
        },
    )
    response = await auth_client.get("/api/v1/bankverbindungen")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["iban"] == "DE89370400440532013000"


@pytest.mark.asyncio(loop_scope="function")
async def test_update_bankverbindung(auth_client: AsyncClient) -> None:
    """Eine Bankverbindung kann aktualisiert werden."""
    create_resp = await auth_client.post(
        "/api/v1/bankverbindungen",
        json={
            "iban": "DE89 3704 0044 0532 0130 00",
            "kontoinhaber": "Alt",
        },
    )
    bankv_id = create_resp.json()["id"]

    response = await auth_client.patch(
        f"/api/v1/bankverbindungen/{bankv_id}",
        json={
            "kontoinhaber": "Neu",
            "bankname": "Neue Bank",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["kontoinhaber"] == "Neu"
    assert data["bankname"] == "Neue Bank"
    assert data["iban"] == "DE89370400440532013000"


@pytest.mark.asyncio(loop_scope="function")
async def test_delete_bankverbindung(auth_client: AsyncClient) -> None:
    """Eine Bankverbindung kann geloescht werden."""
    create_resp = await auth_client.post(
        "/api/v1/bankverbindungen",
        json={
            "iban": "DE89 3704 0044 0532 0130 00",
            "kontoinhaber": "Loeschbar",
        },
    )
    bankv_id = create_resp.json()["id"]

    response = await auth_client.delete(f"/api/v1/bankverbindungen/{bankv_id}")
    assert response.status_code == 204

    get_resp = await auth_client.get(f"/api/v1/bankverbindungen/{bankv_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio(loop_scope="function")
async def test_bankverbindung_not_found(auth_client: AsyncClient) -> None:
    """Eine fremde/nicht existierende Bankverbindung liefert 404."""
    response = await auth_client.get("/api/v1/bankverbindungen/999999")
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="function")
async def test_bankverbindung_iban_validation(auth_client: AsyncClient) -> None:
    """Zu kurze IBAN wird abgelehnt."""
    response = await auth_client.post(
        "/api/v1/bankverbindungen",
        json={
            "iban": "DE123",
            "kontoinhaber": "Test",
        },
    )
    assert response.status_code == 422
