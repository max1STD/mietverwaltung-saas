"""Tests für Zähler- und Ablesungs-CRUD."""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.models.user import User


async def _create_objekt(client: AsyncClient) -> int:
    response = await client.post(
        "/api/v1/objekte",
        json={
            "name": "Zähler-Test-Objekt",
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
            "name": "WE-Zähler",
            "wohnflaeche_qm": "60.00",
            "etage": 2,
            "kaltmiete": "700.00",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


async def _create_zaehler(client: AsyncClient, einheit_id: int, typ: str = "strom") -> int:
    response = await client.post(
        "/api/v1/zaehler",
        json={
            "einheit_id": einheit_id,
            "bezeichnung": f"{typ.capitalize()}zähler",
            "zaehlernummer": f"{typ.upper()}-12345",
            "typ": typ,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


@pytest.mark.asyncio(loop_scope="function")
async def test_create_zaehler(auth_client: AsyncClient, vermieter_user: User) -> None:
    """Ein Vermieter kann einen Zähler anlegen."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)

    response = await auth_client.post(
        "/api/v1/zaehler",
        json={
            "einheit_id": einheit_id,
            "bezeichnung": "Stromzähler Haupt",
            "zaehlernummer": "ST-2026-001",
            "typ": "strom",
            "ist_hauptzaehler": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["bezeichnung"] == "Stromzähler Haupt"
    assert data["typ"] == "strom"
    assert data["einheit"] == "kwh"
    assert data["ist_hauptzaehler"] is True
    assert data["einheit_id"] == einheit_id
    assert data["vermieter_id"] == vermieter_user.id


@pytest.mark.asyncio(loop_scope="function")
async def test_list_zaehler(auth_client: AsyncClient) -> None:
    """Zähler können pro Einheit aufgelistet werden."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)
    await _create_zaehler(auth_client, einheit_id, "strom")
    await _create_zaehler(auth_client, einheit_id, "wasser")

    response = await auth_client.get(f"/api/v1/zaehler?einheit_id={einheit_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {z["typ"] for z in data} == {"strom", "wasser"}


@pytest.mark.asyncio(loop_scope="function")
async def test_update_zaehler(auth_client: AsyncClient) -> None:
    """Ein Zähler kann aktualisiert werden."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)
    zaehler_id = await _create_zaehler(auth_client, einheit_id, "gas")

    response = await auth_client.patch(
        f"/api/v1/zaehler/{zaehler_id}",
        json={"bezeichnung": "Gaszähler aktualisiert", "ist_hauptzaehler": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["bezeichnung"] == "Gaszähler aktualisiert"
    assert data["ist_hauptzaehler"] is True


@pytest.mark.asyncio(loop_scope="function")
async def test_delete_zaehler(auth_client: AsyncClient) -> None:
    """Ein Zähler kann inklusive Ablesungen gelöscht werden."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)
    zaehler_id = await _create_zaehler(auth_client, einheit_id, "strom")

    response = await auth_client.delete(f"/api/v1/zaehler/{zaehler_id}")
    assert response.status_code == 204

    get_resp = await auth_client.get(f"/api/v1/zaehler/{zaehler_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio(loop_scope="function")
async def test_create_ablesung_berechnet_verbrauch(auth_client: AsyncClient) -> None:
    """Eine Ablesung berechnet den Verbrauch gegenüber der Vorgänger-Ablesung."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)
    zaehler_id = await _create_zaehler(auth_client, einheit_id, "strom")

    response = await auth_client.post(
        f"/api/v1/zaehler/{zaehler_id}/ablesungen",
        json={
            "ablesedatum": "2026-01-01",
            "zaehlerstand": "1000.000",
            "ableser": "Vermieter",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["zaehlerstand"] == "1000.000"
    assert data["verbrauch"] is None

    response = await auth_client.post(
        f"/api/v1/zaehler/{zaehler_id}/ablesungen",
        json={
            "ablesedatum": "2026-12-31",
            "zaehlerstand": "2500.000",
            "ableser": "Vermieter",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["verbrauch"] == "1500.000"


@pytest.mark.asyncio(loop_scope="function")
async def test_list_ablesungen(auth_client: AsyncClient) -> None:
    """Ablesungen werden chronologisch absteigend sortiert."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)
    zaehler_id = await _create_zaehler(auth_client, einheit_id, "wasser")

    for monat, stand in [("2026-06-01", "120.000"), ("2026-07-01", "135.000")]:
        response = await auth_client.post(
            f"/api/v1/zaehler/{zaehler_id}/ablesungen",
            json={
                "ablesedatum": monat,
                "zaehlerstand": stand,
            },
        )
        assert response.status_code == 201

    response = await auth_client.get(f"/api/v1/zaehler/{zaehler_id}/ablesungen")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["ablesedatum"] == "2026-07-01"
    assert data[1]["ablesedatum"] == "2026-06-01"


@pytest.mark.asyncio(loop_scope="function")
async def test_update_ablesung_berechnet_verbrauch_neu(auth_client: AsyncClient) -> None:
    """Bei Änderung von Stand oder Datum wird der Verbrauch neu berechnet."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)
    zaehler_id = await _create_zaehler(auth_client, einheit_id, "strom")

    await auth_client.post(
        f"/api/v1/zaehler/{zaehler_id}/ablesungen",
        json={"ablesedatum": "2026-01-01", "zaehlerstand": "1000.000"},
    )
    resp2 = await auth_client.post(
        f"/api/v1/zaehler/{zaehler_id}/ablesungen",
        json={"ablesedatum": "2026-12-31", "zaehlerstand": "2500.000"},
    )
    ablesung_id = resp2.json()["id"]

    response = await auth_client.patch(
        f"/api/v1/zaehler/{zaehler_id}/ablesungen/{ablesung_id}",
        json={"zaehlerstand": "3000.000"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["verbrauch"] == "2000.000"


@pytest.mark.asyncio(loop_scope="function")
async def test_delete_ablesung(auth_client: AsyncClient) -> None:
    """Eine Ablesung kann gelöscht werden."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)
    zaehler_id = await _create_zaehler(auth_client, einheit_id, "strom")

    resp = await auth_client.post(
        f"/api/v1/zaehler/{zaehler_id}/ablesungen",
        json={"ablesedatum": "2026-01-01", "zaehlerstand": "1000.000"},
    )
    ablesung_id = resp.json()["id"]

    response = await auth_client.delete(
        f"/api/v1/zaehler/{zaehler_id}/ablesungen/{ablesung_id}"
    )
    assert response.status_code == 204

    get_resp = await auth_client.get(
        f"/api/v1/zaehler/{zaehler_id}/ablesungen/{ablesung_id}"
    )
    assert get_resp.status_code == 404


async def _create_mieter_entity(client: AsyncClient, email: str, vermieter_id: int) -> int:
    """Erstellt einen Mieter-Stammdatensatz."""
    response = await client.post(
        "/api/v1/mieter",
        json={
            "first_name": "Max",
            "last_name": "Mustermann",
            "email": email,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


async def _create_mietvertrag(
    client: AsyncClient,
    mieter_id: int,
    einheit_id: int,
    vermieter_id: int,
) -> int:
    """Erstellt einen aktiven Mietvertrag."""
    response = await client.post(
        "/api/v1/mietvertraege",
        json={
            "mieter_id": mieter_id,
            "einheit_id": einheit_id,
            "mietbeginn": "2024-01-01",
            "miete_cold": "750.00",
            "nebenkosten_voraus": "150.00",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def _as_mieter(client: AsyncClient, mieter_user: User) -> None:
    """Schaltet den Client vorübergehend auf Mieter-Authentifizierung um."""
    from app.main import app
    from app.middleware.auth import get_current_user

    async def override_get_current_user() -> User:
        return mieter_user

    app.dependency_overrides[get_current_user] = override_get_current_user
    client.user_id = mieter_user.id


async def _reset_auth(client: AsyncClient) -> None:
    """Setzt den Auth-Override zurück."""
    from app.main import app
    from app.middleware.auth import get_current_user

    app.dependency_overrides.pop(get_current_user, None)
    client.user_id = None


@pytest.mark.asyncio(loop_scope="function")
async def test_mieter_can_access_own_zaehler(
    auth_client: AsyncClient,
    mieter_user: User,
) -> None:
    """Ein Mieter sieht nur Zähler seiner eigenen Wohneinheit."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)
    zaehler_id = await _create_zaehler(auth_client, einheit_id, "strom")

    mieter_id = await _create_mieter_entity(auth_client, mieter_user.email, auth_client.user_id)
    await _create_mietvertrag(auth_client, mieter_id, einheit_id, auth_client.user_id)

    await _as_mieter(auth_client, mieter_user)
    try:
        response = await auth_client.get("/api/v1/zaehler")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == zaehler_id

        detail = await auth_client.get(f"/api/v1/zaehler/{zaehler_id}")
        assert detail.status_code == 200
        assert detail.json()["id"] == zaehler_id
    finally:
        await _reset_auth(auth_client)


@pytest.mark.asyncio(loop_scope="function")
async def test_mieter_can_create_ablesung(
    auth_client: AsyncClient,
    mieter_user: User,
) -> None:
    """Ein Mieter kann für seinen Zähler eine Ablesung erfassen."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)
    zaehler_id = await _create_zaehler(auth_client, einheit_id, "strom")

    mieter_id = await _create_mieter_entity(auth_client, mieter_user.email, auth_client.user_id)
    await _create_mietvertrag(auth_client, mieter_id, einheit_id, auth_client.user_id)

    await _as_mieter(auth_client, mieter_user)
    try:
        response = await auth_client.post(
            f"/api/v1/zaehler/{zaehler_id}/ablesungen",
            json={
                "ablesedatum": "2026-11-15",
                "zaehlerstand": "12345.000",
                "ableser": "Mieter",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["zaehlerstand"] == "12345.000"
        assert data["ableser"] == "Mieter"
        assert data["created_at"] is not None
    finally:
        await _reset_auth(auth_client)


@pytest.mark.asyncio(loop_scope="function")
async def test_mieter_cannot_access_other_tenant_zaehler(
    auth_client: AsyncClient,
    mieter_user: User,
) -> None:
    """Ein Mieter darf keine Zähler anderer Einheiten/Vermieter sehen."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)
    zaehler_id = await _create_zaehler(auth_client, einheit_id, "strom")

    await _as_mieter(auth_client, mieter_user)
    try:
        # Mieter hat KEINEN Mietvertrag zu dieser Einheit.
        list_resp = await auth_client.get("/api/v1/zaehler")
        assert list_resp.status_code == 200
        assert list_resp.json() == []

        detail_resp = await auth_client.get(f"/api/v1/zaehler/{zaehler_id}")
        assert detail_resp.status_code == 404

        create_resp = await auth_client.post(
            f"/api/v1/zaehler/{zaehler_id}/ablesungen",
            json={"ablesedatum": "2026-11-15", "zaehlerstand": "999.000"},
        )
        assert create_resp.status_code == 404
    finally:
        await _reset_auth(auth_client)


@pytest.mark.asyncio(loop_scope="function")
async def test_mieter_cannot_modify_zaehler(
    auth_client: AsyncClient,
    mieter_user: User,
) -> None:
    """Ein Mieter darf keine Zähler anlegen, bearbeiten oder löschen."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)
    zaehler_id = await _create_zaehler(auth_client, einheit_id, "strom")

    mieter_id = await _create_mieter_entity(auth_client, mieter_user.email, auth_client.user_id)
    await _create_mietvertrag(auth_client, mieter_id, einheit_id, auth_client.user_id)

    await _as_mieter(auth_client, mieter_user)
    try:
        create_resp = await auth_client.post(
            "/api/v1/zaehler",
            json={
                "einheit_id": einheit_id,
                "bezeichnung": "Unbefugt",
                "typ": "wasser",
            },
        )
        assert create_resp.status_code == 403

        patch_resp = await auth_client.patch(
            f"/api/v1/zaehler/{zaehler_id}",
            json={"bezeichnung": "Gehackt"},
        )
        assert patch_resp.status_code == 403

        delete_resp = await auth_client.delete(f"/api/v1/zaehler/{zaehler_id}")
        assert delete_resp.status_code == 403
    finally:
        await _reset_auth(auth_client)
