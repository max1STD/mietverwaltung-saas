"""Phase 1: DSGVO- und Einwilligungs-Tests."""
from __future__ import annotations

import uuid

import pyotp
import pytest
from httpx import AsyncClient

CONSENT_TEXT = (
    "Ich stimme der Verarbeitung meiner Daten gemäß DSGVO und den AGB zu. "
    "Einwilligungen können jederzeit widerrufen werden."
)


def _unique_email(prefix: str = "test") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}@karthoff.de"


async def _ensure_csrf(client: AsyncClient) -> str:
    if not client.cookies.get("csrf_token"):
        await client.get("/health")
    return client.cookies.get("csrf_token") or ""


async def _authenticated_client(client: AsyncClient, email: str, password: str) -> None:
    csrf = await _ensure_csrf(client)
    register = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Test Vermieter",
            "consent_text": CONSENT_TEXT,
        },
        headers={"X-CSRF-Token": csrf},
    )
    assert register.status_code == 201, register.text

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200, login.text

    setup = await client.post(
        "/api/v1/auth/2fa/setup",
        json={},
        headers={"X-CSRF-Token": await _ensure_csrf(client)},
    )
    assert setup.status_code == 200, setup.text
    secret = setup.json()["secret"]

    verify = await client.post(
        "/api/v1/auth/2fa/verify",
        json={"code": pyotp.TOTP(secret).now()},
        headers={"X-CSRF-Token": await _ensure_csrf(client)},
    )
    assert verify.status_code == 200, verify.text


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_dsgvo_overview(async_client: AsyncClient) -> None:
    """GET /dsgvo/overview liefert eine Datenübersicht."""
    email = _unique_email("dsgvo_overview")
    await _authenticated_client(async_client, email, "SicheresPasswort123!")

    response = await async_client.get("/api/v1/dsgvo/overview")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert "user" in payload
    assert "sessions_count" in payload
    assert "einwilligungen_count" in payload
    assert "audit_logs_count" in payload


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_dsgvo_export(async_client: AsyncClient) -> None:
    """GET /dsgvo/export liefert einen JSON-Export der User-Daten."""
    email = _unique_email("dsgvo_export")
    await _authenticated_client(async_client, email, "SicheresPasswort123!")

    response = await async_client.get("/api/v1/dsgvo/export")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["export_format"] == "json"
    assert "exported_at" in payload
    assert "data" in payload
    assert payload["data"]["user"]["email"] == email


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_dsgvo_delete(async_client: AsyncClient) -> None:
    """DELETE /dsgvo/delete löscht den Account, falls keine Aufbewahrungsfristen greifen."""
    email = _unique_email("dsgvo_delete")
    await _authenticated_client(async_client, email, "SicheresPasswort123!")

    delete = await async_client.delete(
        "/api/v1/dsgvo/delete",
        headers={"X-CSRF-Token": await _ensure_csrf(async_client)},
    )
    assert delete.status_code == 200, delete.text
    payload = delete.json()
    assert payload["deleted"] is True

    # Nach dem Löschen ist der Endpunkt nicht mehr erreichbar.
    me = await async_client.get("/api/v1/auth/users/me")
    assert me.status_code == 401


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_einwilligungen_list(async_client: AsyncClient) -> None:
    """GET /einwilligungen liefert die Liste der Einwilligungen."""
    email = _unique_email("einwilligungen_list")
    await _authenticated_client(async_client, email, "SicheresPasswort123!")

    response = await async_client.get("/api/v1/einwilligungen")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert isinstance(payload, list)
    # Registrierung legt automatisch eine DSGVO-Einwilligung an.
    assert any(item["purpose"] == "dsgvo_terms" for item in payload)


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_einwilligungen_create_or_update(async_client: AsyncClient) -> None:
    """POST /einwilligungen aktualisiert eine Einwilligung."""
    email = _unique_email("einwilligungen_update")
    await _authenticated_client(async_client, email, "SicheresPasswort123!")

    response = await async_client.post(
        "/api/v1/einwilligungen",
        json={
            "purpose": "ki_dokumente",
            "consent_text": (
                "Ich stimme der Nutzung von KI zur Dokumentenverarbeitung zu. "
                "Details siehe Datenschutzerklärung."
            ),
            "version": 1,
        },
        headers={"X-CSRF-Token": await _ensure_csrf(async_client)},
    )
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["purpose"] == "ki_dokumente"
    assert payload["withdrawn_at"] is None
