"""Tests für Einheit-CRUD-Endpunkte."""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.models.user import User


async def _create_objekt(client: AsyncClient) -> int:
    """Helper: legt ein Objekt an und gibt die ID zurück."""
    response = await client.post(
        "/api/v1/objekte",
        json={
            "name": "Test-Objekt",
            "address": "Musterstraße 1",
            "typ": "mehrfamilienhaus",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


@pytest.mark.asyncio
async def test_create_einheit(auth_client: AsyncClient, vermieter_user: User) -> None:
    """Ein Vermieter kann eine Einheit anlegen."""
    objekt_id = await _create_objekt(auth_client)
    payload = {
        "objekt_id": objekt_id,
        "name": "Wohnung 1.OG links",
        "size_qm": "75.50",
        "rooms": 3,
        "rent_cold": "850.00",
        "floor": "1.OG",
    }
    response = await auth_client.post("/api/v1/einheiten", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["objekt_id"] == objekt_id
    assert data["vermieter_id"] == vermieter_user.id
    assert data["vermietungsstatus"] == "frei"


@pytest.mark.asyncio
async def test_list_einheiten(auth_client: AsyncClient) -> None:
    """Einheiten können nach Objekt gefiltert werden."""
    objekt_id = await _create_objekt(auth_client)
    for i in range(2):
        await auth_client.post(
            "/api/v1/einheiten",
            json={
                "objekt_id": objekt_id,
                "name": f"WE {i}",
                "size_qm": "50.00",
                "rooms": 2,
                "rent_cold": "600.00",
            },
        )

    response = await auth_client.get(f"/api/v1/einheiten?objekt_id={objekt_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_update_einheit(auth_client: AsyncClient) -> None:
    """Eine Einheit kann aktualisiert werden."""
    objekt_id = await _create_objekt(auth_client)
    create_resp = await auth_client.post(
        "/api/v1/einheiten",
        json={
            "objekt_id": objekt_id,
            "name": "Alt",
            "size_qm": "50.00",
            "rooms": 2,
            "rent_cold": "500.00",
        },
    )
    einheit_id = create_resp.json()["id"]

    response = await auth_client.patch(
        f"/api/v1/einheiten/{einheit_id}",
        json={"rent_cold": "650.00", "energy_class": "B"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rent_cold"] == "650.00"
    assert data["energy_class"] == "B"


@pytest.mark.asyncio
async def test_delete_einheit(auth_client: AsyncClient) -> None:
    """Eine Einheit kann gelöscht werden."""
    objekt_id = await _create_objekt(auth_client)
    create_resp = await auth_client.post(
        "/api/v1/einheiten",
        json={
            "objekt_id": objekt_id,
            "name": "Lösch-WE",
            "size_qm": "40.00",
            "rooms": 1,
            "rent_cold": "400.00",
        },
    )
    einheit_id = create_resp.json()["id"]

    response = await auth_client.delete(f"/api/v1/einheiten/{einheit_id}")
    assert response.status_code == 204

    get_resp = await auth_client.get(f"/api/v1/einheiten/{einheit_id}")
    assert get_resp.status_code == 404
