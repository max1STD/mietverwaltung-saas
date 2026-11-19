"""End-to-End-Tests für den Domain-Core: Objekt → Einheit → Mieter → Mietvertrag.

Paket 1: Domain-Core stabilisieren.
"""
from __future__ import annotations

from datetime import date

import pytest
from httpx import AsyncClient

from app.models.user import User

pytestmark = pytest.mark.asyncio


async def _create_objekt(client: AsyncClient, name: str = "Testhaus") -> int:
    response = await client.post(
        "/api/v1/objekte",
        json={
            "name": name,
            "address": "Musterstraße 1, 12345 Musterstadt",
            "typ": "mehrfamilienhaus",
            "baujahr": 2010,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def _create_einheit(client: AsyncClient, objekt_id: int, name: str = "WE 1") -> int:
    response = await client.post(
        "/api/v1/einheiten",
        json={
            "objekt_id": objekt_id,
            "name": name,
            "wohnflaeche_qm": "65.00",
            "etage": 2,
            "kaltmiete": "750.00",
            "nebenkosten_vorschuss": "150.00",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def _create_mieter(client: AsyncClient, email: str) -> int:
    response = await client.post(
        "/api/v1/mieter",
        json={
            "first_name": "Max",
            "last_name": "Mustermann",
            "email": email,
            "telefon": "+49 170 1234567",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def _create_mietvertrag(client: AsyncClient, mieter_id: int, einheit_id: int) -> int:
    response = await client.post(
        "api/v1/mietvertraege",
        json={
            "mieter_id": mieter_id,
            "einheit_id": einheit_id,
            "mietbeginn": "2024-01-01",
            "miete_cold": "750.00",
            "nebenkosten_voraus": "150.00",
            "kaution": "2250.00",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def test_objekt_einheit_mieter_mietvertrag_flow(auth_client: AsyncClient) -> None:
    """Vollständiger Kreislauf vom Objekt bis zum Mietvertrag."""
    # 1. Objekt anlegen
    objekt_id = await _create_objekt(auth_client, "E2E-Haus")

    # 2. Einheit an Objekt anlegen
    einheit_id = await _create_einheit(auth_client, objekt_id, "E2E-Wohnung")

    # 3. Einheit in Objekt-Liste finden
    response = await auth_client.get(f"/api/v1/objekte/{objekt_id}")
    assert response.status_code == 200
    objekt = response.json()
    einheiten = objekt.get("einheiten", [])
    assert any(e["id"] == einheit_id for e in einheiten)

    # 4. Mieter anlegen
    mieter_id = await _create_mieter(auth_client, "e2e-mieter@example.de")

    # 5. Mietvertrag erstellen
    vertrag_id = await _create_mietvertrag(auth_client, mieter_id, einheit_id)

    # 6. Vertrag lesen und Verknüpfungen prüfen
    response = await auth_client.get(f"/api/v1/mietvertraege/{vertrag_id}")
    assert response.status_code == 200
    vertrag = response.json()
    assert vertrag["mieter_id"] == mieter_id
    assert vertrag["einheit_id"] == einheit_id
    assert vertrag["einheit"]["objekt_name"] == "E2E-Haus"
    assert vertrag["mieter"]["name"] == "Max Mustermann"
    assert vertrag["miete_cold"] == "750.00"

    # 7. Einheit zeigt aktuellen Mieter an
    response = await auth_client.get(f"/api/v1/einheiten/{einheit_id}")
    assert response.status_code == 200
    einheit = response.json()
    assert einheit["vermietungsstatus"] == "vermietet"
    assert einheit["aktueller_mieter"]["id"] == mieter_id
    assert einheit["aktueller_mieter"]["name"] == "Max Mustermann"

    # 8. Zweiter Vertrag an derselben Einheit wird verhindert (Doppelvermietung)
    mieter2_id = await _create_mieter(auth_client, "e2e-mieter2@example.de")
    blocked = await auth_client.post(
        "api/v1/mietvertraege",
        json={
            "mieter_id": mieter2_id,
            "einheit_id": einheit_id,
            "mietbeginn": "2025-01-01",
            "miete_cold": "800.00",
            "nebenkosten_voraus": "160.00",
        },
    )
    assert blocked.status_code in {400, 409}, blocked.text

    # 11. Objekt-Löschung mit aktivem Vertrag wird verhindert
    response = await auth_client.delete(f"/api/v1/objekte/{objekt_id}")
    assert response.status_code == 409
    assert "aktive Mietverträge" in response.json()["detail"]

    # 12. Einheit-Löschung mit aktivem Vertrag wird verhindert
    response = await auth_client.delete(f"/api/v1/einheiten/{einheit_id}")
    assert response.status_code == 409
    assert "aktiver Mietvertrag" in response.json()["detail"]

    # 13. Vertrag kündigen / beenden
    response = await auth_client.patch(
        f"/api/v1/mietvertraege/{vertrag_id}",
        json={
            "status": "gekuendigt",
            "mietende": str(date.today()),
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "gekuendigt"

    # 14. Einheit ist danach wieder frei
    response = await auth_client.get(f"/api/v1/einheiten/{einheit_id}")
    assert response.status_code == 200
    einheit = response.json()
    assert einheit["vermietungsstatus"] == "frei"
    assert einheit.get("aktueller_mieter") is None

    # 15. Erst nach Vertragsende kann Einheit und dann Objekt gelöscht werden
    response = await auth_client.delete(f"/api/v1/einheiten/{einheit_id}")
    assert response.status_code == 204

    response = await auth_client.delete(f"/api/v1/objekte/{objekt_id}")
    assert response.status_code == 204


async def test_objekt_delete_cascade_respects_einheit_with_contract(auth_client: AsyncClient) -> None:
    """Objekt-Löschung mit aktivem Mietvertrag wird mit 409 abgelehnt."""
    objekt_id = await _create_objekt(auth_client, "Zu-löschendes-Haus")
    einheit_id = await _create_einheit(auth_client, objekt_id)
    mieter_id = await _create_mieter(auth_client, "geschuetzt@example.de")
    await _create_mietvertrag(auth_client, mieter_id, einheit_id)

    response = await auth_client.delete(f"/api/v1/objekte/{objekt_id}")
    assert response.status_code == 409, response.text
    assert "aktive Mietverträge" in response.json()["detail"]

    # Objekt ist weiterhin lesbar
    assert (await auth_client.get(f"/api/v1/objekte/{objekt_id}")).status_code == 200