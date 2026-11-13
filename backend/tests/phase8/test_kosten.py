"""Integrationstests für Kosten- und Kostenkategorie-Endpunkte (Phase 8)."""
from __future__ import annotations

from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.kostenkategorien import Kostenkategorie


@pytest.mark.anyio
async def test_kosten_crud(auth_client: AsyncClient) -> None:
    """Erstellt, liest, aktualisiert und löscht eine Kostenposition."""
    session: AsyncSession = auth_client.db_session

    # Kostenkategorie anlegen
    kat = Kostenkategorie(
        vermieter_id=auth_client.user_id,
        name="Heizkosten",
        umlagefaehig=True,
        verteilungsschluessel="qm",
    )
    session.add(kat)
    await session.flush()
    await session.refresh(kat)

    # Objekt anlegen
    obj_response = await auth_client.post(
        "/api/v1/objekte",
        json={
            "name": "Testobjekt Kosten",
            "address": "Musterstraße 1, 12345 Berlin",
            "typ": "MFH",
        },
    )
    assert obj_response.status_code == 201
    objekt_id = obj_response.json()["id"]

    # Einheit anlegen
    ein_response = await auth_client.post(
        "/api/v1/einheiten",
        json={
            "objekt_id": objekt_id,
            "name": "WE-1",
            "size_qm": "50.00",
            "rooms": 2,
            "rent_cold": "500.00",
        },
    )
    assert ein_response.status_code == 201
    einheit_id = ein_response.json()["id"]

    # Kosten erstellen
    create_response = await auth_client.post(
        "/api/v1/kosten",
        json={
            "objekt_id": objekt_id,
            "einheit_id": einheit_id,
            "kategorie_id": kat.id,
            "betrag": "1200.00",
            "datum": "2026-06-15",
            "umlagefaehig": True,
            "datev_konto": "12345",
            "datev_buchungstext": "Heizkosten 2026",
        },
    )
    assert create_response.status_code == 201
    data = create_response.json()
    assert data["betrag"] == "1200.00"
    assert data["kategorie"]["name"] == "Heizkosten"
    kosten_id = data["id"]

    # Liste
    list_response = await auth_client.get("/api/v1/kosten")
    assert list_response.status_code == 200
    assert any(k["id"] == kosten_id for k in list_response.json())

    # Update
    patch_response = await auth_client.patch(
        f"/api/v1/kosten/{kosten_id}",
        json={"betrag": "1300.00"},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["betrag"] == "1300.00"

    # Scan-Stub
    scan_response = await auth_client.post(f"/api/v1/kosten/{kosten_id}/scan")
    assert scan_response.status_code == 200
    assert scan_response.json()["kategorie_name"] == "Heizkosten"

    # Delete
    delete_response = await auth_client.delete(f"/api/v1/kosten/{kosten_id}")
    assert delete_response.status_code == 204

    get_response = await auth_client.get(f"/api/v1/kosten/{kosten_id}")
    assert get_response.status_code == 404


@pytest.mark.anyio
async def test_kosten_filter_by_objekt(auth_client: AsyncClient) -> None:
    """Filtert Kosten nach Objekt-ID."""
    session: AsyncSession = auth_client.db_session

    kat = Kostenkategorie(
        vermieter_id=auth_client.user_id,
        name="Wasserkosten",
        umlagefaehig=True,
        verteilungsschluessel="verbrauch",
    )
    session.add(kat)
    await session.flush()
    await session.refresh(kat)

    obj_response = await auth_client.post(
        "/api/v1/objekte",
        json={
            "name": "Filterobjekt",
            "address": "Filterstraße 2, 12345 Berlin",
            "typ": "EFH",
        },
    )
    objekt_id = obj_response.json()["id"]

    create_response = await auth_client.post(
        "/api/v1/kosten",
        json={
            "objekt_id": objekt_id,
            "kategorie_id": kat.id,
            "betrag": "100.00",
            "datum": "2026-03-01",
        },
    )
    assert create_response.status_code == 201

    filtered = await auth_client.get(f"/api/v1/kosten?objekt_id={objekt_id}")
    assert filtered.status_code == 200
    assert len(filtered.json()) >= 1
    assert all(k["objekt_id"] == objekt_id for k in filtered.json())
