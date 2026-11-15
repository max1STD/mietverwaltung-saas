"""Tests für Mieter-CRUD-Endpunkte."""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_create_mieter(auth_client: AsyncClient, vermieter_user: User) -> None:
    """Ein Vermieter kann einen Mieter anlegen."""
    payload = {
        "name": "Max Mustermann",
        "email": "max@example.de",
        "telefon": "+49 170 1234567",
        "geburtsdatum": "1985-06-15",
        "adresse": "Musterstraße 1, 12345 Musterstadt",
        "notizen": "Testnotizen",
        "status": "aktiv",
    }
    response = await auth_client.post("/api/v1/mieter", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Max Mustermann"
    assert data["email"] == "max@example.de"
    assert data["telefon"] == "+49 170 1234567"
    assert data["geburtsdatum"] == "1985-06-15"
    assert data["adresse"] == "Musterstraße 1, 12345 Musterstadt"
    assert data["notizen"] == "Testnotizen"
    assert data["vermieter_id"] == vermieter_user.id


@pytest.mark.asyncio
async def test_list_mieter(auth_client: AsyncClient) -> None:
    """Mieter werden korrekt aufgelistet."""
    for i in range(2):
        await auth_client.post(
            "/api/v1/mieter",
            json={
                "name": f"Mieter{i} Test",
                "email": f"mieter{i}@example.de",
            },
        )

    response = await auth_client.get("/api/v1/mieter")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_update_mieter(auth_client: AsyncClient) -> None:
    """Mieter-Daten können aktualisiert werden."""
    create_resp = await auth_client.post(
        "/api/v1/mieter",
        json={
            "name": "Erika Musterfrau",
            "email": "erika@example.de",
        },
    )
    mieter_id = create_resp.json()["id"]

    response = await auth_client.patch(
        f"/api/v1/mieter/{mieter_id}",
        json={"telefon": "+49 170 9999999", "status": "ehemalig"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["telefon"] == "+49 170 9999999"
    assert data["status"] == "ehemalig"


@pytest.mark.asyncio
async def test_delete_mieter(auth_client: AsyncClient) -> None:
    """Ein Mieter kann gelöscht werden (Soft-Delete)."""
    create_resp = await auth_client.post(
        "/api/v1/mieter",
        json={
            "name": "Lösch Mieter",
            "email": "loesch@example.de",
        },
    )
    mieter_id = create_resp.json()["id"]

    response = await auth_client.delete(f"/api/v1/mieter/{mieter_id}")
    assert response.status_code == 204

    get_resp = await auth_client.get(f"/api/v1/mieter/{mieter_id}")
    assert get_resp.status_code == 404
