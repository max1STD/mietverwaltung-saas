"""Tests für Mietzahlung-CRUD und Generierung."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from httpx import AsyncClient

from app.models.mietvertraege import Mietvertrag


@pytest.mark.asyncio(loop_scope="function")
async def test_create_mietzahlung(
    auth_client: AsyncClient,
    vermieter_user: object,
) -> None:
    """Ein Vermieter kann eine Mietzahlung anlegen."""
    # Setup: Objekt, Einheit, Mieter, Vertrag
    objekt = await auth_client.post("/api/v1/objekte", json={"name": "Haus A", "address": "Musterweg 1", "plz": "12345", "ort": "Musterstadt"})
    objekt_id = objekt.json()["id"]
    einheit = await auth_client.post("/api/v1/einheiten", json={
        "objekt_id": objekt_id,
        "name": "Wohnung 1",
        "wohnflaeche_qm": "60.00",
        "kaltmiete": "700.00",
        "nebenkosten_vorschuss": "150.00",
        "rooms": 3,
    })
    einheit_id = einheit.json()["id"]
    mieter = await auth_client.post("/api/v1/mieter", json={
        "first_name": "Max",
        "last_name": "Mustermann",
        "email": "mietzahlung@example.com",
    })
    mieter_id = mieter.json()["id"]
    vertrag = await auth_client.post("/api/v1/mietvertraege", json={
        "mieter_id": mieter_id,
        "einheit_id": einheit_id,
        "mietbeginn": "2024-01-01",
        "miete_cold": "700.00",
        "nebenkosten_voraus": "150.00",
    })
    vertrag_id = vertrag.json()["id"]

    response = await auth_client.post("/api/v1/mietzahlungen", json={
        "vertrag_id": vertrag_id,
        "mieter_id": mieter_id,
        "betrag_soll": "850.00",
        "zahlungsdatum": "2024-01-01",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["betrag_soll"] == "850.00"
    assert data["betrag_ist"] is None
    assert data["offener_betrag"] == "850.00"
    assert data["mahnstufe"] == 0
    assert data["mieter"]["name"] == "Max Mustermann"


@pytest.mark.asyncio(loop_scope="function")
async def test_list_mietzahlungen_offen_filter(auth_client: AsyncClient) -> None:
    """Der offen-Filter zeigt nur unbezahlte Zahlungen."""
    # Setup über create helper, dann Test
    objekt = await auth_client.post("/api/v1/objekte", json={"name": "Haus B", "address": "Musterweg 2", "plz": "12345", "ort": "Musterstadt"})
    objekt_id = objekt.json()["id"]
    einheit = await auth_client.post("/api/v1/einheiten", json={
        "objekt_id": objekt_id,
        "name": "Wohnung 2",
        "wohnflaeche_qm": "50.00",
        "kaltmiete": "600.00",
        "nebenkosten_vorschuss": "100.00",
        "rooms": 2,
    })
    einheit_id = einheit.json()["id"]
    mieter = await auth_client.post("/api/v1/mieter", json={
        "first_name": "Offen",
        "last_name": "Test",
        "email": "offen@example.com",
    })
    mieter_id = mieter.json()["id"]
    vertrag = await auth_client.post("/api/v1/mietvertraege", json={
        "mieter_id": mieter_id,
        "einheit_id": einheit_id,
        "mietbeginn": "2024-02-01",
        "miete_cold": "600.00",
        "nebenkosten_voraus": "100.00",
    })
    vertrag_id = vertrag.json()["id"]

    await auth_client.post("/api/v1/mietzahlungen", json={
        "vertrag_id": vertrag_id,
        "mieter_id": mieter_id,
        "betrag_soll": "700.00",
        "betrag_ist": "700.00",
        "zahlungsdatum": "2024-02-01",
    })
    await auth_client.post("/api/v1/mietzahlungen", json={
        "vertrag_id": vertrag_id,
        "mieter_id": mieter_id,
        "betrag_soll": "700.00",
        "zahlungsdatum": "2024-03-01",
    })

    response = await auth_client.get("/api/v1/mietzahlungen?offen=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["offener_betrag"] == "700.00"


@pytest.mark.asyncio(loop_scope="function")
async def test_mark_paid(auth_client: AsyncClient) -> None:
    """Eine Zahlung kann als bezahlt markiert werden."""
    objekt = await auth_client.post("/api/v1/objekte", json={"name": "Haus C", "address": "Musterweg 3", "plz": "12345", "ort": "Musterstadt"})
    objekt_id = objekt.json()["id"]
    einheit = await auth_client.post("/api/v1/einheiten", json={
        "objekt_id": objekt_id,
        "name": "Wohnung 3",
        "wohnflaeche_qm": "70.00",
        "kaltmiete": "800.00",
        "nebenkosten_vorschuss": "200.00",
        "rooms": 4,
    })
    einheit_id = einheit.json()["id"]
    mieter = await auth_client.post("/api/v1/mieter", json={
        "first_name": "Bezahlt",
        "last_name": "Test",
        "email": "bezahlt@example.com",
    })
    mieter_id = mieter.json()["id"]
    vertrag = await auth_client.post("/api/v1/mietvertraege", json={
        "mieter_id": mieter_id,
        "einheit_id": einheit_id,
        "mietbeginn": "2024-04-01",
        "miete_cold": "800.00",
        "nebenkosten_voraus": "200.00",
    })
    vertrag_id = vertrag.json()["id"]

    create_resp = await auth_client.post("/api/v1/mietzahlungen", json={
        "vertrag_id": vertrag_id,
        "mieter_id": mieter_id,
        "betrag_soll": "1000.00",
        "zahlungsdatum": "2024-04-01",
    })
    zahlung_id = create_resp.json()["id"]

    response = await auth_client.post(f"/api/v1/mietzahlungen/{zahlung_id}/mark-paid", json={
        "betrag_ist": "1000.00",
        "zahlungsdatum": "2024-04-05T10:00:00",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["betrag_ist"] == "1000.00"
    assert data["offener_betrag"] == "0.00"


@pytest.mark.asyncio(loop_scope="function")
async def test_generate_mietzahlungen(auth_client: AsyncClient) -> None:
    """Mietzahlungen werden aus aktiven Verträgen generiert."""
    objekt = await auth_client.post("/api/v1/objekte", json={"name": "Haus D", "address": "Musterweg 4", "plz": "12345", "ort": "Musterstadt"})
    objekt_id = objekt.json()["id"]
    einheit = await auth_client.post("/api/v1/einheiten", json={
        "objekt_id": objekt_id,
        "name": "Wohnung 4",
        "wohnflaeche_qm": "55.00",
        "kaltmiete": "500.00",
        "nebenkosten_vorschuss": "100.00",
        "rooms": 2,
    })
    einheit_id = einheit.json()["id"]
    mieter = await auth_client.post("/api/v1/mieter", json={
        "first_name": "Gen",
        "last_name": "Test",
        "email": "gen@example.com",
    })
    mieter_id = mieter.json()["id"]
    await auth_client.post("/api/v1/mietvertraege", json={
        "mieter_id": mieter_id,
        "einheit_id": einheit_id,
        "mietbeginn": "2024-05-01",
        "miete_cold": "500.00",
        "nebenkosten_voraus": "100.00",
    })

    response = await auth_client.post("/api/v1/mietzahlungen/actions/generate", json={
        "monat": "2024-05-01",
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["betrag_soll"] == "600.00"
    assert data[0]["einheit"]["name"] == "Wohnung 4"


@pytest.mark.asyncio(loop_scope="function")
async def test_mahnstufe_erhoehen(auth_client: AsyncClient) -> None:
    """Eine offene Zahlung kann in die nächste Mahnstufe versetzt werden."""
    objekt = await auth_client.post("/api/v1/objekte", json={"name": "Haus E", "address": "Musterweg 5", "plz": "12345", "ort": "Musterstadt"})
    objekt_id = objekt.json()["id"]
    einheit = await auth_client.post("/api/v1/einheiten", json={
        "objekt_id": objekt_id,
        "name": "Wohnung 5",
        "wohnflaeche_qm": "80.00",
        "kaltmiete": "900.00",
        "nebenkosten_vorschuss": "150.00",
        "rooms": 5,
    })
    einheit_id = einheit.json()["id"]
    mieter = await auth_client.post("/api/v1/mieter", json={
        "first_name": "Mahn",
        "last_name": "Test",
        "email": "mahn@example.com",
    })
    mieter_id = mieter.json()["id"]
    vertrag = await auth_client.post("/api/v1/mietvertraege", json={
        "mieter_id": mieter_id,
        "einheit_id": einheit_id,
        "mietbeginn": "2024-06-01",
        "miete_cold": "900.00",
        "nebenkosten_voraus": "150.00",
    })
    vertrag_id = vertrag.json()["id"]

    create_resp = await auth_client.post("/api/v1/mietzahlungen", json={
        "vertrag_id": vertrag_id,
        "mieter_id": mieter_id,
        "betrag_soll": "1050.00",
        "zahlungsdatum": "2024-06-01",
    })
    zahlung_id = create_resp.json()["id"]

    response = await auth_client.post(f"/api/v1/mietzahlungen/{zahlung_id}/mahnstufe")
    assert response.status_code == 200
    assert response.json()["mahnstufe"] == 1

    response = await auth_client.post(f"/api/v1/mietzahlungen/{zahlung_id}/mahnstufe")
    assert response.status_code == 200
    assert response.json()["mahnstufe"] == 2
