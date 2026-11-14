"""Tests für Mietvertrag-CRUD-Endpunkte."""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.models.user import User


async def _create_objekt(client: AsyncClient) -> int:
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


async def _create_einheit(client: AsyncClient, objekt_id: int) -> int:
    response = await client.post(
        "/api/v1/einheiten",
        json={
            "objekt_id": objekt_id,
            "name": "WE 1",
            "wohnflaeche_qm": "60.00",
            "etage": 2,
            "kaltmiete": "700.00",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


async def _create_mieter(client: AsyncClient) -> int:
    response = await client.post(
        "/api/v1/mieter",
        json={
            "first_name": "Max",
            "last_name": "Mustermann",
            "email": "max@example.de",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


@pytest.mark.asyncio
async def test_create_mietvertrag(auth_client: AsyncClient, vermieter_user: User) -> None:
    """Ein Vermieter kann einen Mietvertrag anlegen."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)
    mieter_id = await _create_mieter(auth_client)

    payload = {
        "mieter_id": mieter_id,
        "einheit_id": einheit_id,
        "mietbeginn": "2024-01-01",
        "miete_cold": "750.00",
        "nebenkosten_voraus": "150.00",
        "kaution": "2250.00",
    }
    response = await auth_client.post("/api/v1/mietvertraege", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["mieter_id"] == mieter_id
    assert data["einheit_id"] == einheit_id
    assert data["miete_cold"] == "750.00"
    assert data["vermieter_id"] == vermieter_user.id
    assert data["mieter"]["full_name"] == "Max Mustermann"
    assert data["einheit"]["name"] == "WE 1"


@pytest.mark.asyncio
async def test_mietvertrag_prevents_double_rental(auth_client: AsyncClient) -> None:
    """Eine bereits vermietete Einheit kann nicht erneut vergeben werden."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)
    mieter_1 = await _create_mieter(auth_client)
    mieter_2 = await _create_mieter(auth_client)

    # Erster Vertrag
    first_resp = await auth_client.post(
        "/api/v1/mietvertraege",
        json={
            "mieter_id": mieter_1,
            "einheit_id": einheit_id,
            "mietbeginn": "2024-01-01",
            "miete_cold": "700.00",
            "nebenkosten_voraus": "150.00",
        },
    )
    assert first_resp.status_code == 201

    # Zweiter Vertrag auf dieselbe Einheit muss scheitern
    second_resp = await auth_client.post(
        "/api/v1/mietvertraege",
        json={
            "mieter_id": mieter_2,
            "einheit_id": einheit_id,
            "mietbeginn": "2024-02-01",
            "miete_cold": "800.00",
            "nebenkosten_voraus": "200.00",
        },
    )
    assert second_resp.status_code == 400


@pytest.mark.asyncio
async def test_update_mietvertrag(auth_client: AsyncClient) -> None:
    """Ein Mietvertrag kann aktualisiert werden."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)
    mieter_id = await _create_mieter(auth_client)

    create_resp = await auth_client.post(
        "/api/v1/mietvertraege",
        json={
            "mieter_id": mieter_id,
            "einheit_id": einheit_id,
            "mietbeginn": "2024-01-01",
            "miete_cold": "700.00",
            "nebenkosten_voraus": "150.00",
        },
    )
    vertrag_id = create_resp.json()["id"]

    response = await auth_client.patch(
        f"/api/v1/mietvertraege/{vertrag_id}",
        json={"miete_cold": "750.00", "status": "gekuendigt"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["miete_cold"] == "750.00"
    assert data["status"] == "gekuendigt"


@pytest.mark.asyncio
async def test_delete_mietvertrag(auth_client: AsyncClient) -> None:
    """Ein Mietvertrag kann gelöscht werden."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)
    mieter_id = await _create_mieter(auth_client)

    create_resp = await auth_client.post(
        "/api/v1/mietvertraege",
        json={
            "mieter_id": mieter_id,
            "einheit_id": einheit_id,
            "mietbeginn": "2024-01-01",
            "miete_cold": "700.00",
            "nebenkosten_voraus": "150.00",
        },
    )
    vertrag_id = create_resp.json()["id"]

    response = await auth_client.delete(f"/api/v1/mietvertraege/{vertrag_id}")
    assert response.status_code == 204

    get_resp = await auth_client.get(f"/api/v1/mietvertraege/{vertrag_id}")
    assert get_resp.status_code == 404
