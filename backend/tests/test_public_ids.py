"""Tests fuer oeffentliche IDs (Paket 2)."""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_mieter_bekommt_public_id(auth_client: AsyncClient) -> None:
    """Beim Anlegen eines Mieters wird eine fortlaufende public_id vergeben."""
    response = await auth_client.post(
        "/api/v1/mieter",
        json={
            "first_name": "Max",
            "last_name": "Mustermann",
            "email": "max.public@example.de",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "public_id" in data
    assert isinstance(data["public_id"], int)
    assert data["public_id"] >= 1001


@pytest.mark.asyncio
async def test_mietvertrag_bekommt_public_id(auth_client: AsyncClient) -> None:
    """Beim Anlegen eines Mietvertrags wird eine fortlaufende public_id vergeben."""
    # Objekt + Einheit anlegen
    obj_resp = await auth_client.post(
        "/api/v1/objekte",
        json={
            "name": "Public-ID Testobjekt",
            "address": "Teststr. 1",
            "plz": "12345",
            "ort": "Teststadt",
        },
    )
    assert obj_resp.status_code == 201
    obj_id = obj_resp.json()["id"]

    ein_resp = await auth_client.post(
        "/api/v1/einheiten",
        json={
            "objekt_id": obj_id,
            "name": "WE 1",
            "wohnflaeche_qm": "55.00",
            "kaltmiete": "600.00",
        },
    )
    assert ein_resp.status_code == 201
    einheit_id = ein_resp.json()["id"]

    # Mieter anlegen
    mieter_resp = await auth_client.post(
        "/api/v1/mieter",
        json={
            "first_name": "Maria",
            "last_name": "Musterfrau",
            "email": "maria.public@example.de",
        },
    )
    assert mieter_resp.status_code == 201
    mieter_id = mieter_resp.json()["id"]

    # Mietvertrag anlegen
    vertrag_resp = await auth_client.post(
        "/api/v1/mietvertraege",
        json={
            "mieter_id": mieter_id,
            "einheit_id": einheit_id,
            "mietbeginn": "2026-01-01",
            "kaltmiete": "600.00",
            "nebenkosten_vorschuss": "100.00",
        },
    )
    assert vertrag_resp.status_code == 201
    data = vertrag_resp.json()
    assert "public_id" in data
    assert isinstance(data["public_id"], int)
    assert data["public_id"] >= 1001


@pytest.mark.asyncio
async def test_objekt_route_akzeptiert_public_id(auth_client: AsyncClient) -> None:
    """GET /api/v1/objekte/{public_id} funktioniert neben interner ID."""
    create_resp = await auth_client.post(
        "/api/v1/objekte",
        json={
            "name": "Public-ID Objekt",
            "address": "Teststr. 2",
            "plz": "12345",
            "ort": "Teststadt",
        },
    )
    assert create_resp.status_code == 201
    data = create_resp.json()
    public_id = data["public_id"]
    internal_id = data["id"]

    get_by_public = await auth_client.get(f"/api/v1/objekte/{public_id}")
    assert get_by_public.status_code == 200
    assert get_by_public.json()["id"] == internal_id


@pytest.mark.asyncio
async def test_einheit_route_akzeptiert_public_id(auth_client: AsyncClient) -> None:
    """GET /api/v1/einheiten/{public_id} funktioniert neben interner ID."""
    obj_resp = await auth_client.post(
        "/api/v1/objekte",
        json={
            "name": "Public-ID Objekt 2",
            "address": "Teststr. 3",
            "plz": "12345",
            "ort": "Teststadt",
        },
    )
    obj_id = obj_resp.json()["id"]

    ein_resp = await auth_client.post(
        "/api/v1/einheiten",
        json={
            "objekt_id": obj_id,
            "name": "WE Public",
            "wohnflaeche_qm": "45.00",
            "kaltmiete": "500.00",
        },
    )
    assert ein_resp.status_code == 201
    data = ein_resp.json()
    public_id = data["public_id"]
    internal_id = data["id"]

    get_by_public = await auth_client.get(f"/api/v1/einheiten/{public_id}")
    assert get_by_public.status_code == 200
    assert get_by_public.json()["id"] == internal_id


@pytest.mark.asyncio
async def test_mieter_route_akzeptiert_public_id(auth_client: AsyncClient) -> None:
    """GET /api/v1/mieter/{public_id} funktioniert neben interner ID."""
    create_resp = await auth_client.post(
        "/api/v1/mieter",
        json={
            "first_name": "Public",
            "last_name": "ID",
            "email": "public.id@example.de",
        },
    )
    assert create_resp.status_code == 201
    data = create_resp.json()
    public_id = data["public_id"]
    internal_id = data["id"]

    get_by_public = await auth_client.get(f"/api/v1/mieter/{public_id}")
    assert get_by_public.status_code == 200
    assert get_by_public.json()["id"] == internal_id



@pytest.mark.asyncio
async def test_zaehler_bekommt_public_id(auth_client: AsyncClient) -> None:
    """Beim Anlegen eines Zaehlers wird eine fortlaufende public_id vergeben."""
    # Objekt + Einheit anlegen
    obj_resp = await auth_client.post(
        "/api/v1/objekte",
        json={
            "name": "Zaehler Public-ID Objekt",
            "address": "Zaehlerstr. 1",
            "plz": "12345",
            "ort": "Teststadt",
        },
    )
    assert obj_resp.status_code == 201
    obj_id = obj_resp.json()["id"]

    ein_resp = await auth_client.post(
        "/api/v1/einheiten",
        json={
            "objekt_id": obj_id,
            "name": "WE Zaehler",
            "wohnflaeche_qm": "45.00",
            "kaltmiete": "500.00",
        },
    )
    assert ein_resp.status_code == 201
    einheit_id = ein_resp.json()["id"]

    zaehler_resp = await auth_client.post(
        "/api/v1/zaehler",
        json={
            "einheit_id": einheit_id,
            "bezeichnung": "Hauptzaehler Wasser",
            "zaehlernummer": "W123456",
            "typ": "wasser",
            "einheit": "m3",
            "ist_hauptzaehler": False,
        },
    )
    assert zaehler_resp.status_code == 201
    data = zaehler_resp.json()
    assert "public_id" in data
    assert isinstance(data["public_id"], int)
    assert data["public_id"] >= 1001
