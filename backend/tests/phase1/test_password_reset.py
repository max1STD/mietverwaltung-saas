"""Phase 1: Passwort-Reset-Tests."""
from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

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


async def _register(client: AsyncClient, email: str, password: str) -> None:
    csrf = await _ensure_csrf(client)
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Test Vermieter",
            "consent_text": CONSENT_TEXT,
        },
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 201, response.text


async def _request_reset(client: AsyncClient, email: str) -> dict:
    csrf = await _ensure_csrf(client)
    response = await client.post(
        "/api/v1/auth/password-reset",
        json={"email": email},
        headers={"X-CSRF-Token": csrf},
    )
    return response


async def _confirm_reset(
    client: AsyncClient,
    email: str,
    code: str,
    new_password: str,
) -> dict:
    csrf = await _ensure_csrf(client)
    response = await client.post(
        "/api/v1/auth/password-reset",
        json={"email": email, "code": code, "new_password": new_password},
        headers={"X-CSRF-Token": csrf},
    )
    return response


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_password_reset_request_existing_email(async_client: AsyncClient) -> None:
    """Reset-Anforderung für existierende E-Mail liefert Erfolg."""
    email = _unique_email("pw_reset_existing")
    await _register(async_client, email, "SicheresPasswort123!")

    response = await _request_reset(async_client, email)
    assert response.status_code == 200, response.text
    assert "versandt" in response.json()["message"].lower()

    db: AsyncSession = async_client.db_session
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    assert user.email_code is not None
    assert len(user.email_code) == 6


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_password_reset_request_nonexistent_email(async_client: AsyncClient) -> None:
    """Reset-Anforderung für nicht existierende E-Mail liefert dieselbe Erfolgsmeldung."""
    email = _unique_email("pw_reset_missing")
    response = await _request_reset(async_client, email)
    assert response.status_code == 200, response.text
    assert "versandt" in response.json()["message"].lower()


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_password_reset_confirm_valid_code(async_client: AsyncClient) -> None:
    """Reset-Bestätigung mit gültigem Code ändert das Passwort."""
    email = _unique_email("pw_reset_confirm")
    old_password = "SicheresPasswort123!"
    new_password = "NeuesSicheresPasswort456!"
    await _register(async_client, email, old_password)

    await _request_reset(async_client, email)
    db: AsyncSession = async_client.db_session
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    code = user.email_code
    assert code is not None

    confirm = await _confirm_reset(async_client, email, code, new_password)
    assert confirm.status_code == 200, confirm.text

    # Altes Passwort funktioniert nicht mehr.
    old_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": old_password},
    )
    assert old_login.status_code == 401


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_password_reset_confirm_invalid_code(async_client: AsyncClient) -> None:
    """Reset-Bestätigung mit ungültigem Code schlägt fehl."""
    email = _unique_email("pw_reset_invalid")
    await _register(async_client, email, "SicheresPasswort123!")
    await _request_reset(async_client, email)

    confirm = await _confirm_reset(
        async_client,
        email,
        "000000",
        "NeuesSicheresPasswort456!",
    )
    assert confirm.status_code == 400


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_with_new_password_after_reset(async_client: AsyncClient) -> None:
    """Nach erfolgreichem Reset gelingt der Login mit dem neuen Passwort."""
    email = _unique_email("pw_reset_login")
    old_password = "SicheresPasswort123!"
    new_password = "NeuesSicheresPasswort456!"
    await _register(async_client, email, old_password)

    await _request_reset(async_client, email)
    db: AsyncSession = async_client.db_session
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one()

    confirm = await _confirm_reset(async_client, email, user.email_code, new_password)
    assert confirm.status_code == 200, confirm.text

    login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": new_password},
    )
    assert login.status_code == 200, login.text
    assert login.json()["requires_2fa"] is True
