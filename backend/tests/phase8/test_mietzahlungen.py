"""Integrationstests für Mietzahlungs-Endpunkte (Phase 8)."""
from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mieter import Mieter
from app.models.mietvertraege import Mietvertrag


@pytest.mark.asyncio
async def test_mietzahlung_crud_and_mark_paid(auth_client: AsyncClient) -> None:
    """Erstellt, markiert als bezahlt und löscht eine Mietzahlung."""
    session: AsyncSession = auth_client.db_session

    obj_response = await auth_client.post(
        "/api/v1/objekte",
        json={
            "name": "Zahlungsobjekt",
            "address": "Geldstraße 1, 12345 Berlin",
            "typ": "EFH",
        },
    )
    objekt_id = obj_response.json()["id"]

    ein_response = await auth_client.post(
        "/api/v1/einheiten",
        json={
            "objekt_id": objekt_id,
            "name": "WE-Z",
            "wohnflaeche_qm": "55.00",
            "etage": 2,
            "kaltmiete": "700.00",
        },
    )
    einheit_id = ein_response.json()["id"]

    mieter = Mieter(
        vermieter_id=auth_client.user_id,
        first_name="Max",
        last_name="Zahler",
        email="max@example.de",
    )
    session.add(mieter)
    await session.flush()
    await session.refresh(mieter)

    vertrag = Mietvertrag(
        vermieter_id=auth_client.user_id,
        mieter_id=mieter.id,
        einheit_id=einheit_id,
        mietbeginn=date(2026, 1, 1),
        miete_cold=Decimal("700.00"),
        nebenkosten_voraus=Decimal("150.00"),
    )
    session.add(vertrag)
    await session.flush()
    await session.refresh(vertrag)

    create_response = await auth_client.post(
        "/api/v1/mietzahlungen",
        json={
            "mieter_id": mieter.id,
            "vertrag_id": vertrag.id,
            "betrag_soll": "850.00",
        },
    )
    assert create_response.status_code == 201
    data = create_response.json()
    assert data["betrag_soll"] == "850.00"
    assert data["mieter"]["name"] == "Max Zahler"
    zahlung_id = data["id"]

    # mark-paid
    mark_response = await auth_client.post(
        f"/api/v1/mietzahlungen/{zahlung_id}/mark-paid",
        json={
            "betrag_ist": "850.00",
            "zahlungsdatum": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert mark_response.status_code == 200
    assert mark_response.json()["betrag_ist"] == "850.00"

    # Mahnstufe erhöhen
    mahn_response = await auth_client.post(
        f"/api/v1/mietzahlungen/{zahlung_id}/mahnstufe",
    )
    assert mahn_response.status_code == 200
    assert mahn_response.json()["mahnstufe"] == 1

    # Löschen
    del_response = await auth_client.delete(f"/api/v1/mietzahlungen/{zahlung_id}")
    assert del_response.status_code == 204

    get_response = await auth_client.get(f"/api/v1/mietzahlungen/{zahlung_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_mietzahlung_filter_by_vertrag(auth_client: AsyncClient) -> None:
    """Filtert Mietzahlungen nach Vertrag-ID."""
    session: AsyncSession = auth_client.db_session

    obj_response = await auth_client.post(
        "/api/v1/objekte",
        json={
            "name": "Filterobjekt Zahlung",
            "address": "Filtergasse 1, 12345 Berlin",
            "typ": "EFH",
        },
    )
    objekt_id = obj_response.json()["id"]

    ein_response = await auth_client.post(
        "/api/v1/einheiten",
        json={
            "objekt_id": objekt_id,
            "name": "WE-F",
            "wohnflaeche_qm": "40.00",
            "etage": 1,
            "kaltmiete": "400.00",
        },
    )
    einheit_id = ein_response.json()["id"]

    mieter = Mieter(
        vermieter_id=auth_client.user_id,
        first_name="Fiona",
        last_name="Filter",
    )
    session.add(mieter)
    await session.flush()
    await session.refresh(mieter)

    vertrag = Mietvertrag(
        vermieter_id=auth_client.user_id,
        mieter_id=mieter.id,
        einheit_id=einheit_id,
        mietbeginn=date(2026, 1, 1),
        miete_cold=Decimal("400.00"),
        nebenkosten_voraus=Decimal("100.00"),
    )
    session.add(vertrag)
    await session.flush()
    await session.refresh(vertrag)

    create_response = await auth_client.post(
        "/api/v1/mietzahlungen",
        json={
            "vertrag_id": vertrag.id,
            "betrag_soll": "500.00",
        },
    )
    assert create_response.status_code == 201

    filtered = await auth_client.get(f"/api/v1/mietzahlungen?vertrag_id={vertrag.id}")
    assert filtered.status_code == 200
    assert len(filtered.json()) >= 1
    assert all(z["vertrag_id"] == vertrag.id for z in filtered.json())
