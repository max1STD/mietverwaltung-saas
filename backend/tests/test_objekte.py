"""Tests für Objekt-CRUD-Endpunkte."""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_create_objekt(auth_client: AsyncClient, vermieter_user: User) -> None:
    """Ein Vermieter kann ein Objekt anlegen."""
    payload = {
        "name": "Mein Testhaus",
        "address": "Musterstraße 1, 12345 Musterstadt",
        "typ": "mehrfamilienhaus",
        "baujahr": 2010,
        "kaufpreis": "350000.00",
    }
    response = await auth_client.post("/api/v1/objekte", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["address"] == payload["address"]
    assert data["vermieter_id"] == vermieter_user.id
    assert data["baujahr"] == 2010


@pytest.mark.asyncio
async def test_list_objekte(auth_client: AsyncClient, vermieter_user: User) -> None:
    """Ein Vermieter sieht nur seine eigenen Objekte."""
    # Zwei Objekte anlegen
    for i in range(2):
        await auth_client.post(
            "/api/v1/objekte",
            json={
                "name": f"Objekt {i}",
                "address": f"Adresse {i}",
                "typ": "einfamilienhaus",
            },
        )

    response = await auth_client.get("/api/v1/objekte")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(item["vermieter_id"] == vermieter_user.id for item in data)


@pytest.mark.asyncio
async def test_get_objekt(auth_client: AsyncClient) -> None:
    """Ein einzelnes Objekt kann abgerufen werden."""
    create_resp = await auth_client.post(
        "/api/v1/objekte",
        json={
            "name": "Detail-Objekt",
            "address": "Detailstraße 2",
            "typ": "einfamilienhaus",
        },
    )
    objekt_id = create_resp.json()["id"]

    response = await auth_client.get(f"/api/v1/objekte/{objekt_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == objekt_id
    assert data["name"] == "Detail-Objekt"


@pytest.mark.asyncio
async def test_update_objekt(auth_client: AsyncClient) -> None:
    """Ein Objekt kann aktualisiert werden."""
    create_resp = await auth_client.post(
        "/api/v1/objekte",
        json={
            "name": "Alt",
            "address": "Altstraße 1",
            "typ": "einfamilienhaus",
        },
    )
    objekt_id = create_resp.json()["id"]

    response = await auth_client.patch(
        f"/api/v1/objekte/{objekt_id}",
        json={"name": "Neu", "baujahr": 2020},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Neu"
    assert data["baujahr"] == 2020
    assert data["address"] == "Altstraße 1"  # unverändert


@pytest.mark.asyncio
async def test_delete_objekt(auth_client: AsyncClient) -> None:
    """Ein Objekt kann gelöscht werden (Soft-Delete)."""
    create_resp = await auth_client.post(
        "/api/v1/objekte",
        json={
            "name": "Lösch-Objekt",
            "address": "Löschstraße 9",
            "typ": "einfamilienhaus",
        },
    )
    objekt_id = create_resp.json()["id"]

    response = await auth_client.delete(f"/api/v1/objekte/{objekt_id}")
    assert response.status_code == 204

    # Nach Soft-Delete nicht mehr in der Liste
    list_resp = await auth_client.get("/api/v1/objekte")
    assert all(item["id"] != objekt_id for item in list_resp.json())


@pytest.mark.asyncio
async def test_objekt_not_found(auth_client: AsyncClient) -> None:
    """Ein fremdes/nicht existierendes Objekt liefert 404."""
    response = await auth_client.get("/api/v1/objekte/999999")
    assert response.status_code == 404
