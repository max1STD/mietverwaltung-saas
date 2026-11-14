"""Integrationstests für Abrechnungs-Endpunkte (Phase 8)."""
from __future__ import annotations

from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.kostenkategorien import Kostenkategorie


@pytest.mark.asyncio
async def test_abrechnung_berechnung_qm(auth_client: AsyncClient) -> None:
    """Berechnet Heizkosten 1200 Euro / 100 qm * 50 qm = 600 Euro für WE."""
    session: AsyncSession = auth_client.db_session

    # Objekt mit zwei Einheiten á 50 qm = 100 qm Gesamt
    obj_response = await auth_client.post(
        "/api/v1/objekte",
        json={
            "name": "Abrechnungsobjekt",
            "address": "Rechnungsstraße 1, 12345 Berlin",
            "typ": "MFH",
        },
    )
    assert obj_response.status_code == 201
    objekt_id = obj_response.json()["id"]

    ein1_response = await auth_client.post(
        "/api/v1/einheiten",
        json={
            "objekt_id": objekt_id,
            "name": "WE-A",
            "wohnflaeche_qm": "50.00",
            "etage": 2,
            "kaltmiete": "500.00",
        },
    )
    assert ein1_response.status_code == 201
    einheit_a_id = ein1_response.json()["id"]

    ein2_response = await auth_client.post(
        "/api/v1/einheiten",
        json={
            "objekt_id": objekt_id,
            "name": "WE-B",
            "wohnflaeche_qm": "50.00",
            "etage": 2,
            "kaltmiete": "500.00",
        },
    )
    assert ein2_response.status_code == 201

    kat = Kostenkategorie(
        vermieter_id=auth_client.user_id,
        name="Heizkosten",
        umlagefaehig=True,
        verteilungsschluessel="qm",
    )
    session.add(kat)
    await session.flush()
    await session.refresh(kat)

    kosten_response = await auth_client.post(
        "/api/v1/kosten",
        json={
            "objekt_id": objekt_id,
            "kategorie_id": kat.id,
            "betrag": "1200.00",
            "datum": "2026-06-15",
            "umlagefaehig": True,
        },
    )
    assert kosten_response.status_code == 201

    abr_response = await auth_client.post(
        "/api/v1/abrechnungen",
        json={
            "einheit_id": einheit_a_id,
            "jahr": 2026,
            "zeitraum_von": "2026-01-01",
            "zeitraum_bis": "2026-12-31",
        },
    )
    assert abr_response.status_code == 201
    abrechnung_id = abr_response.json()["id"]
    assert abr_response.json()["objekt_id"] == objekt_id

    calc_response = await auth_client.post(f"/api/v1/abrechnungen/{abrechnung_id}/calculate")
    assert calc_response.status_code == 200
    data = calc_response.json()
    assert len(data["positionen"]) == 1
    pos = data["positionen"][0]
    assert pos["betrag_total"] == "1200.00"
    assert pos["umlageanteil"] == "600.00"
    assert pos["verteilungsschluessel"] == "qm"

    # Finalisierung
    fin_response = await auth_client.post(f"/api/v1/abrechnungen/{abrechnung_id}/finalize")
    assert fin_response.status_code == 200
    assert fin_response.json()["status"] == "versendet"


@pytest.mark.asyncio
async def test_abrechnung_update_and_delete(auth_client: AsyncClient) -> None:
    """Aktualisiert und löscht eine Abrechnung."""
    obj_response = await auth_client.post(
        "/api/v1/objekte",
        json={
            "name": "Abrechnungsobjekt 2",
            "address": "Löschstraße 3, 12345 Berlin",
            "typ": "EFH",
        },
    )
    objekt_id = obj_response.json()["id"]

    ein_response = await auth_client.post(
        "/api/v1/einheiten",
        json={
            "objekt_id": objekt_id,
            "name": "WE-C",
            "wohnflaeche_qm": "60.00",
            "etage": 2,
            "kaltmiete": "600.00",
        },
    )
    einheit_id = ein_response.json()["id"]

    abr_response = await auth_client.post(
        "/api/v1/abrechnungen",
        json={
            "einheit_id": einheit_id,
            "jahr": 2025,
            "zeitraum_von": "2025-01-01",
            "zeitraum_bis": "2025-12-31",
        },
    )
    abrechnung_id = abr_response.json()["id"]

    patch_response = await auth_client.patch(
        f"/api/v1/abrechnungen/{abrechnung_id}",
        json={
            "einwendungsfrist_bis": "2026-02-28",
            "status": "versendet",
        },
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["einwendungsfrist_bis"] == "2026-02-28"

    del_response = await auth_client.delete(f"/api/v1/abrechnungen/{abrechnung_id}")
    assert del_response.status_code == 204

    get_response = await auth_client.get(f"/api/v1/abrechnungen/{abrechnung_id}")
    assert get_response.status_code == 404
