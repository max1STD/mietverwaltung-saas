"""Tests für Bewerbungs-Endpunkte (Phase 5)."""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_create_bewerbung(auth_client: AsyncClient, vermieter_user: User) -> None:
    """Eine Bewerbung kann für eine Einheit angelegt werden."""
    objekt_resp = await auth_client.post(
        "/api/v1/objekte",
        json={
            "name": "Bewerbungsobjekt",
            "address": "Testweg 2",
            "typ": "mehrfamilienhaus",
        },
    )
    assert objekt_resp.status_code == 201
    objekt_id = objekt_resp.json()["id"]

    einheit_resp = await auth_client.post(
        f"/api/v1/objekte/{objekt_id}/einheiten",
        json={
            "name": "Wohnung 1",
            "wohnflaeche_qm": 75.00,
            "etage": 3,
            "kaltmiete": 800.00,
        },
    )
    assert einheit_resp.status_code == 201
    einheit_id = einheit_resp.json()["id"]

    response = await auth_client.post(
        "/api/v1/bewerbungen",
        json={
            "einheit_id": einheit_id,
            "first_name": "Anna",
            "last_name": "Bewerber",
            "email": "anna@example.de",
            "phone": "+49 170 1111111",
            "income_monthly": "2500.00",
            "schufa_score": 95,
            "documents": {
                "ausweis": {"filename": "ausweis.pdf", "uploaded": True},
                "lohnabrechnung": {"filename": "lohn.pdf", "uploaded": True},
                "schufa": {"filename": "schufa.pdf", "uploaded": True},
            },
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Anna"
    assert data["status"] == "offen"
    assert data["einheit_id"] == einheit_id
    assert data["documents"]["schufa"]["uploaded"] is True


@pytest.mark.asyncio
async def test_list_and_get_bewerbung(auth_client: AsyncClient, vermieter_user: User) -> None:
    """Bewerbungen werden aufgelistet und Detailansicht liefert Daten."""
    objekt_resp = await auth_client.post(
        "/api/v1/objekte",
        json={"name": "Objekt B", "address": "B-Weg 1", "typ": "einfamilienhaus"},
    )
    einheit_resp = await auth_client.post(
        f"/api/v1/objekte/{objekt_resp.json()['id']}/einheiten",
        json={"name": "WE B", "wohnflaeche_qm": 50.00, "etage": 2, "kaltmiete": 500.00},
    )
    einheit_id = einheit_resp.json()["id"]

    create_resp = await auth_client.post(
        "/api/v1/bewerbungen",
        json={
            "einheit_id": einheit_id,
            "first_name": "Tom",
            "last_name": "Tester",
            "income_monthly": "1800.00",
        },
    )
    bewerbung_id = create_resp.json()["id"]

    list_resp = await auth_client.get("/api/v1/bewerbungen")
    assert list_resp.status_code == 200
    assert any(b["id"] == bewerbung_id for b in list_resp.json())

    detail_resp = await auth_client.get(f"/api/v1/bewerbungen/{bewerbung_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["first_name"] == "Tom"


@pytest.mark.asyncio
async def test_bewerbung_annehmen(auth_client: AsyncClient, vermieter_user: User) -> None:
    """Annahme erzeugt Mieter und Mietvertrag."""
    objekt_resp = await auth_client.post(
        "/api/v1/objekte",
        json={"name": "Objekt C", "address": "C-Weg 1", "typ": "einfamilienhaus"},
    )
    einheit_resp = await auth_client.post(
        f"/api/v1/objekte/{objekt_resp.json()['id']}/einheiten",
        json={"name": "WE C", "wohnflaeche_qm": 60.00, "etage": 2, "kaltmiete": 600.00},
    )
    einheit_id = einheit_resp.json()["id"]

    create_resp = await auth_client.post(
        "/api/v1/bewerbungen",
        json={
            "einheit_id": einheit_id,
            "first_name": "Lisa",
            "last_name": "Angenommen",
            "email": "lisa@example.de",
            "income_monthly": "2200.00",
        },
    )
    bewerbung_id = create_resp.json()["id"]

    response = await auth_client.post(
        f"/api/v1/bewerbungen/{bewerbung_id}/annehmen",
        json={
            "create_mieter_and_vertrag": True,
            "miete_cold": "600.00",
            "nebenkosten_voraus": "120.00",
            "kaution": "1800.00",
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "angenommen"
    assert result["mieter_id"] is not None
    assert result["vertrag_id"] is not None

    # Bewerbungs-Detail zeigt neuen Status
    detail_resp = await auth_client.get(f"/api/v1/bewerbungen/{bewerbung_id}")
    assert detail_resp.json()["status"] == "angenommen"

    # Einheit ist jetzt vermietet
    einheit_detail = await auth_client.get(f"/api/v1/einheiten/{einheit_id}")
    assert einheit_detail.json()["vermietungsstatus"] == "vermietet"


@pytest.mark.asyncio
async def test_bewerbung_ablehnen(auth_client: AsyncClient, vermieter_user: User) -> None:
    """Ablehnung setzt den Status ohne Mieter/Vertrag-Erstellung."""
    objekt_resp = await auth_client.post(
        "/api/v1/objekte",
        json={"name": "Objekt D", "address": "D-Weg 1", "typ": "einfamilienhaus"},
    )
    einheit_resp = await auth_client.post(
        f"/api/v1/objekte/{objekt_resp.json()['id']}/einheiten",
        json={"name": "WE D", "wohnflaeche_qm": 55.00, "etage": 2, "kaltmiete": 550.00},
    )
    einheit_id = einheit_resp.json()["id"]

    create_resp = await auth_client.post(
        "/api/v1/bewerbungen",
        json={
            "einheit_id": einheit_id,
            "first_name": "Max",
            "last_name": "Abgelehnt",
        },
    )
    bewerbung_id = create_resp.json()["id"]

    response = await auth_client.post(f"/api/v1/bewerbungen/{bewerbung_id}/ablehnen")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "abgelehnt"

    # Zweite Ablehnung darf nicht funktionieren
    second = await auth_client.post(f"/api/v1/bewerbungen/{bewerbung_id}/ablehnen")
    assert second.status_code == 400


@pytest.mark.asyncio
async def test_delete_bewerbung(auth_client: AsyncClient, vermieter_user: User) -> None:
    """Bewerbung kann gelöscht werden (Soft-Delete)."""
    objekt_resp = await auth_client.post(
        "/api/v1/objekte",
        json={"name": "Objekt E", "address": "E-Weg 1", "typ": "einfamilienhaus"},
    )
    einheit_resp = await auth_client.post(
        f"/api/v1/objekte/{objekt_resp.json()['id']}/einheiten",
        json={"name": "WE E", "wohnflaeche_qm": 40.00, "etage": 1, "kaltmiete": 400.00},
    )
    einheit_id = einheit_resp.json()["id"]

    create_resp = await auth_client.post(
        "/api/v1/bewerbungen",
        json={
            "einheit_id": einheit_id,
            "first_name": "Eva",
            "last_name": "Entfernt",
        },
    )
    bewerbung_id = create_resp.json()["id"]

    delete_resp = await auth_client.delete(f"/api/v1/bewerbungen/{bewerbung_id}")
    assert delete_resp.status_code == 204

    get_resp = await auth_client.get(f"/api/v1/bewerbungen/{bewerbung_id}")
    assert get_resp.status_code == 404
