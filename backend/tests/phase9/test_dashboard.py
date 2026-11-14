"""Tests für das Dashboard-Service und die Dashboard-API."""
from __future__ import annotations

import pytest
from datetime import date

from httpx import AsyncClient

from app.models.einheit import Einheit
from app.models.fristen import Frist
from app.models.kosten import Kosten
from app.models.mieter import Mieter
from app.models.mietvertraege import Mietvertrag
from app.models.objekt import Objekt
from app.models.tickets import Ticket
from app.models.user import User
from app.services.dashboard import financials, insights, object_summary, summary


@pytest.mark.asyncio
async def test_summary_empty(auth_client: AsyncClient, vermieter_user: User) -> None:
    """Summary liefert 0-Werte für einen neuen Vermieter."""
    response = await auth_client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["objekte_count"] == 0
    assert data["einheiten_count"] == 0
    assert data["mieter_count"] == 0
    assert data["offene_tickets_count"] == 0
    assert data["subscription"]["status"] == "trial"


@pytest.mark.asyncio
async def test_summary_with_objekt_einheit_mieter(
    auth_client: AsyncClient,
    vermieter_user: User,
) -> None:
    """Summary zählt Objekte, Einheiten und Mieter korrekt."""
    session = auth_client.db_session

    objekt = Objekt(
        vermieter_id=vermieter_user.id,
        name="Testhaus",
        address="Musterstraße 1",
        typ="mehrfamilienhaus",
    )
    session.add(objekt)
    await session.flush()

    einheit = Einheit(
        vermieter_id=vermieter_user.id,
        objekt_id=objekt.id,
        name="Wohnung 1",
        size_qm=75,
        rooms=3,
        rent_cold=800,
    )
    session.add(einheit)
    await session.flush()

    mieter = Mieter(
        vermieter_id=vermieter_user.id,
        first_name="Max",
        last_name="Mustermann",
        email="max@example.de",
        status="aktiv",
    )
    session.add(mieter)
    await session.flush()

    vertrag = Mietvertrag(
        vermieter_id=vermieter_user.id,
        mieter_id=mieter.id,
        einheit_id=einheit.id,
        mietbeginn=date(2026, 1, 1),
        miete_cold=800,
        nebenkosten_voraus=150,
        status="aktiv",
    )
    session.add(vertrag)
    await session.flush()

    response = await auth_client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["objekte_count"] == 1
    assert data["einheiten_count"] == 1
    assert data["mieter_count"] == 1
    assert data["umsatz_diesen_monat"] > 0
    assert data["subscription"]["wohnungen_count"] == 1
    assert data["subscription"]["price_per_we"] == 9.75


@pytest.mark.asyncio
async def test_object_summary_rendite(
    auth_client: AsyncClient,
    vermieter_user: User,
) -> None:
    """Objekt-Summary berechnet Vermietungsquote und Renditen."""
    session = auth_client.db_session

    objekt = Objekt(
        vermieter_id=vermieter_user.id,
        name="Renditehaus",
        address="Renditestraße 1",
        typ="mehrfamilienhaus",
        kaufpreis=350000,
    )
    session.add(objekt)
    await session.flush()

    einheit = Einheit(
        vermieter_id=vermieter_user.id,
        objekt_id=objekt.id,
        name="Wohnung 1",
        size_qm=80,
        rooms=3,
        rent_cold=1000,
    )
    session.add(einheit)
    await session.flush()

    mieter = Mieter(
        vermieter_id=vermieter_user.id,
        first_name="Anna",
        last_name="Müller",
        email="anna@example.de",
    )
    session.add(mieter)
    await session.flush()

    vertrag = Mietvertrag(
        vermieter_id=vermieter_user.id,
        mieter_id=mieter.id,
        einheit_id=einheit.id,
        mietbeginn=date(2026, 1, 1),
        miete_cold=1000,
        nebenkosten_voraus=200,
        status="aktiv",
    )
    session.add(vertrag)
    await session.flush()

    kosten = Kosten(
        vermieter_id=vermieter_user.id,
        objekt_id=objekt.id,
        betrag=1200,
        datum=date(2026, 1, 15),
    )
    session.add(kosten)
    await session.flush()

    response = await auth_client.get(f"/api/v1/dashboard/object/{objekt.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["einheiten_total"] == 1
    assert data["einheiten_vermietet"] == 1
    assert data["vermietungsquote"] == 100.0
    assert data["jahreskaltmiete"] == 12000.0
    assert data["bruttomietrendite"] > 0
    assert data["nettomietrendite"] < data["bruttomietrendite"]


@pytest.mark.asyncio
async def test_financials_12_months(
    auth_client: AsyncClient,
    vermieter_user: User,
) -> None:
    """Financials liefert 12 Monate mit Einnahmen aus aktiven Verträgen."""
    session = auth_client.db_session

    objekt = Objekt(
        vermieter_id=vermieter_user.id,
        name="Finanzen-Haus",
        address="Geldstraße 1",
        typ="einfamilienhaus",
    )
    session.add(objekt)
    await session.flush()

    einheit = Einheit(
        vermieter_id=vermieter_user.id,
        objekt_id=objekt.id,
        name="Wohnung 1",
        size_qm=60,
        rooms=2,
        rent_cold=700,
    )
    session.add(einheit)
    await session.flush()

    mieter = Mieter(
        vermieter_id=vermieter_user.id,
        first_name="Tim",
        last_name="Test",
        email="tim@example.de",
    )
    session.add(mieter)
    await session.flush()

    vertrag = Mietvertrag(
        vermieter_id=vermieter_user.id,
        mieter_id=mieter.id,
        einheit_id=einheit.id,
        mietbeginn=date(2026, 1, 1),
        miete_cold=700,
        nebenkosten_voraus=100,
        status="aktiv",
    )
    session.add(vertrag)
    await session.flush()

    response = await auth_client.get("/api/v1/dashboard/financials")
    assert response.status_code == 200
    data = response.json()
    assert len(data["monate"]) == 12
    assert data["summe_einnahmen"] > 0
    assert any(m["einnahmen"] > 0 for m in data["monate"])


@pytest.mark.asyncio
async def test_insights_leerstand_ticket(
    auth_client: AsyncClient,
    vermieter_user: User,
) -> None:
    """Insights erkennt Leerstand und offene Tickets."""
    session = auth_client.db_session

    objekt = Objekt(
        vermieter_id=vermieter_user.id,
        name="Insight-Haus",
        address="Smartstraße 1",
        typ="mehrfamilienhaus",
    )
    session.add(objekt)
    await session.flush()

    einheit = Einheit(
        vermieter_id=vermieter_user.id,
        objekt_id=objekt.id,
        name="Freie Wohnung",
        size_qm=50,
        rooms=2,
        rent_cold=600,
    )
    session.add(einheit)
    await session.flush()

    frist = Frist(
        vermieter_id=vermieter_user.id,
        deadline=date(2026, 12, 31),
        description="Nebenkostenabrechnung versenden",
    )
    session.add(frist)
    await session.flush()

    ticket = Ticket(
        vermieter_id=vermieter_user.id,
        ticket_number="TKT-2026-0001",
        title="Heizung defekt",
        priority="dringend",
        status="offen",
    )
    session.add(ticket)
    await session.flush()

    response = await auth_client.get("/api/v1/dashboard/insights")
    assert response.status_code == 200
    data = response.json()
    typen = {i["typ"] for i in data["insights"]}
    assert "leerstand" in typen
    assert "ticket" in typen
    assert "frist" in typen


@pytest.mark.asyncio
async def test_dashboard_requires_vermieter_role(
    async_client: AsyncClient,
    vermieter_user: User,
) -> None:
    """Nur Vermieter dürfen auf Dashboard-Endpunkte zugreifen."""
    from app.main import app
    from app.middleware.auth import get_current_user
    from app.models.user import User as UserModel

    mieter_user = UserModel(
        email="mieter@example.de",
        password_hash="x",
        full_name="Mieter Test",
        role="mieter",
        vermieter_id=vermieter_user.id,
        is_active=True,
    )
    async_client.db_session.add(mieter_user)
    await async_client.db_session.flush()
    await async_client.db_session.refresh(mieter_user)

    async def override_get_current_user() -> UserModel:
        return mieter_user

    app.dependency_overrides[get_current_user] = override_get_current_user
    try:
        response = await async_client.get("/api/v1/dashboard/summary")
        assert response.status_code == 403
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_object_summary_not_found(auth_client: AsyncClient) -> None:
    """Nicht existierendes Objekt liefert 404."""
    response = await auth_client.get("/api/v1/dashboard/object/999999")
    assert response.status_code == 404
