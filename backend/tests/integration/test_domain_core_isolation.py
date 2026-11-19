"""Negative E2E-Tests für Domain-Core: Isolation, Validierung, Business-Regeln.

Paket 1: Domain-Core stabilisieren.
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.main import app
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.auth import hash_password

pytestmark = pytest.mark.asyncio


async def _create_vermieter(async_client: AsyncClient) -> User:
    """Legt einen zweiten Test-Vermieter an und gibt das ORM-Objekt zurück."""
    session = async_client.db_session
    user = User(
        email="anderer-vermieter@example.de",
        password_hash=hash_password("TestPasswort123!"),
        full_name="Anderer Vermieter",
        role="vermieter",
        is_active=True,
        email_verified=True,
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


async def _as_vermieter(client: AsyncClient, user: User) -> None:
    """Schaltet den Client vorübergehend auf einen anderen Vermieter um."""

    async def override_get_current_user() -> User:
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user
    client.user_id = user.id


async def _reset_auth(client: AsyncClient) -> None:
    """Setzt den Auth-Override zurück."""
    app.dependency_overrides.pop(get_current_user, None)
    client.user_id = None


async def _create_objekt(client: AsyncClient, name: str = "Testhaus") -> int:
    response = await client.post(
        "/api/v1/objekte",
        json={
            "name": name,
            "address": "Musterstraße 1, 12345 Musterstadt",
            "typ": "mehrfamilienhaus",
        },
    )
    assert response.status_code == 201, response.text
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
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def _create_mieter(client: AsyncClient, email: str) -> int:
    response = await client.post(
        "/api/v1/mieter",
        json={
            "first_name": "Max",
            "last_name": "Mustermann",
            "email": email,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def test_fremdes_objekt_nicht_zugaenglich(auth_client: AsyncClient, async_client: AsyncClient) -> None:
    """Ein anderer Vermieter darf fremde Objekte nicht sehen/bearbeiten/löschen."""
    objekt_id = await _create_objekt(auth_client)
    other = await _create_vermieter(async_client)

    await _as_vermieter(auth_client, other)
    try:
        assert (await auth_client.get(f"/api/v1/objekte/{objekt_id}")).status_code == 404
        assert (
            await auth_client.patch(f"/api/v1/objekte/{objekt_id}", json={"name": "Hack"})
        ).status_code == 404
        assert (await auth_client.delete(f"/api/v1/objekte/{objekt_id}")).status_code == 404
    finally:
        await _reset_auth(auth_client)


async def test_objekt_ohne_name_ist_ungueltig(auth_client: AsyncClient) -> None:
    """Objekt-Name ist Pflicht."""
    response = await auth_client.post(
        "/api/v1/objekte",
        json={"address": "Musterstraße 1", "typ": "einfamilienhaus"},
    )
    assert response.status_code == 422


async def test_einheit_ohne_objekt_id_ist_ungueltig(auth_client: AsyncClient) -> None:
    """Einheit braucht eine Objekt-ID."""
    response = await auth_client.post(
        "/api/v1/einheiten",
        json={"name": "WE 1", "wohnflaeche_qm": "60.00", "kaltmiete": "700.00"},
    )
    assert response.status_code == 422


async def test_fremde_einheit_nicht_zugaenglich(auth_client: AsyncClient, async_client: AsyncClient) -> None:
    """Ein anderer Vermieter darf fremde Einheiten nicht sehen/bearbeiten/löschen."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)
    other = await _create_vermieter(async_client)

    await _as_vermieter(auth_client, other)
    try:
        assert (await auth_client.get(f"/api/v1/einheiten/{einheit_id}")).status_code == 404
        assert (
            await auth_client.patch(f"/api/v1/einheiten/{einheit_id}", json={"name": "Hack"})
        ).status_code == 404
        assert (await auth_client.delete(f"/api/v1/einheiten/{einheit_id}")).status_code == 404
    finally:
        await _reset_auth(auth_client)


async def test_fremder_mieter_nicht_zugaenglich(auth_client: AsyncClient, async_client: AsyncClient) -> None:
    """Ein anderer Vermieter darf fremde Mieter nicht sehen/bearbeiten/löschen."""
    mieter_id = await _create_mieter(auth_client, "geschuetzt@example.de")
    other = await _create_vermieter(async_client)

    await _as_vermieter(auth_client, other)
    try:
        assert (await auth_client.get(f"/api/v1/mieter/{mieter_id}")).status_code == 404
        assert (
            await auth_client.patch(f"/api/v1/mieter/{mieter_id}", json={"first_name": "Hack"})
        ).status_code == 404
        assert (await auth_client.delete(f"/api/v1/mieter/{mieter_id}")).status_code == 404
    finally:
        await _reset_auth(auth_client)


async def test_mietvertrag_mit_fremdem_mieter_scheitert(auth_client: AsyncClient) -> None:
    """Ein Vertrag kann nur mit eigenem Mieter und eigener Einheit erstellt werden."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)

    response = await auth_client.post(
        "/api/v1/mietvertraege",
        json={
            "mieter_id": 999999,
            "einheit_id": einheit_id,
            "mietbeginn": "2024-01-01",
            "miete_cold": "700.00",
            "nebenkosten_vorschuss": "150.00",
        },
    )
    assert response.status_code in {400, 404, 422}, response.text


async def test_mietvertrag_mit_fremder_einheit_scheitert(auth_client: AsyncClient) -> None:
    """Ein Vertrag kann nur mit eigener Einheit erstellt werden."""
    mieter_id = await _create_mieter(auth_client, "mieter-einheit@example.de")
    response = await auth_client.post(
        "/api/v1/mietvertraege",
        json={
            "mieter_id": mieter_id,
            "einheit_id": 999999,
            "mietbeginn": "2024-01-01",
            "miete_cold": "700.00",
            "nebenkosten_vorschuss": "150.00",
        },
    )
    assert response.status_code in {400, 404, 422}, response.text


async def test_fremder_mietvertrag_nicht_zugaenglich(
    auth_client: AsyncClient,
    async_client: AsyncClient,
) -> None:
    """Ein anderer Vermieter darf fremde Mietverträge nicht sehen/bearbeiten/löschen."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)
    mieter_id = await _create_mieter(auth_client, "vertrag@example.de")

    create_resp = await auth_client.post(
        "/api/v1/mietvertraege",
        json={
            "mieter_id": mieter_id,
            "einheit_id": einheit_id,
            "mietbeginn": "2024-01-01",
            "miete_cold": "700.00",
            "nebenkosten_vorschuss": "150.00",
        },
    )
    vertrag_id = create_resp.json()["id"]
    other = await _create_vermieter(async_client)

    await _as_vermieter(auth_client, other)
    try:
        assert (await auth_client.get(f"/api/v1/mietvertraege/{vertrag_id}")).status_code == 404
        assert (
            await auth_client.patch(
                f"/api/v1/mietvertraege/{vertrag_id}",
                json={"miete_cold": "1.00"},
            )
        ).status_code == 404
        assert (await auth_client.delete(f"/api/v1/mietvertraege/{vertrag_id}")).status_code == 404
    finally:
        await _reset_auth(auth_client)


async def test_einheit_mit_aktivem_vertrag_nicht_loeschbar(auth_client: AsyncClient) -> None:
    """Einheit-Löschung mit aktivem Vertrag liefert 409."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)
    mieter_id = await _create_mieter(auth_client, "aktiv@example.de")

    create_resp = await auth_client.post(
        "/api/v1/mietvertraege",
        json={
            "mieter_id": mieter_id,
            "einheit_id": einheit_id,
            "mietbeginn": "2024-01-01",
            "miete_cold": "700.00",
            "nebenkosten_vorschuss": "150.00",
        },
    )
    assert create_resp.status_code == 201, create_resp.text

    response = await auth_client.delete(f"/api/v1/einheiten/{einheit_id}")
    assert response.status_code == 409
    assert "aktiver Mietvertrag" in response.json()["detail"]


async def test_objekt_mit_aktivem_vertrag_nicht_loeschbar(auth_client: AsyncClient) -> None:
    """Objekt-Löschung mit aktivem Vertrag liefert 409."""
    objekt_id = await _create_objekt(auth_client)
    einheit_id = await _create_einheit(auth_client, objekt_id)
    mieter_id = await _create_mieter(auth_client, "objekt-aktiv@example.de")

    create_resp = await auth_client.post(
        "/api/v1/mietvertraege",
        json={
            "mieter_id": mieter_id,
            "einheit_id": einheit_id,
            "mietbeginn": "2024-01-01",
            "miete_cold": "700.00",
            "nebenkosten_vorschuss": "150.00",
        },
    )
    assert create_resp.status_code == 201, create_resp.text

    response = await auth_client.delete(f"/api/v1/objekte/{objekt_id}")
    assert response.status_code == 409
    assert "aktive Mietverträge" in response.json()["detail"]
