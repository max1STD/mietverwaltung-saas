"""Phase 1: Login-Tests."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

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


async def _register(
    client: AsyncClient,
    email: str,
    password: str = "SicheresPasswort123!",
) -> None:
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


async def _login(client: AsyncClient, email: str, password: str) -> dict:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return response


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient) -> None:
    """Login mit korrekten Daten liefert 200, requires_2fa und temp_token."""
    email = _unique_email("login_ok")
    password = "SicheresPasswort123!"
    await _register(async_client, email, password)

    response = await _login(async_client, email, password)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["requires_2fa"] is True
    assert "temp_token" in payload
    assert payload["temp_token"]


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_wrong_password(async_client: AsyncClient) -> None:
    """Login mit falschem Passwort liefert 401."""
    email = _unique_email("login_wrong")
    await _register(async_client, email, "SicheresPasswort123!")

    response = await _login(async_client, email, "FalschesPasswort123!")
    assert response.status_code == 401


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_nonexistent_email(async_client: AsyncClient) -> None:
    """Login mit nicht existierender E-Mail liefert 401 mit derselben Fehlermeldung."""
    response = await _login(async_client, _unique_email("login_missing"), "SicheresPasswort123!")
    assert response.status_code == 401
    wrong_pw = await _login(
        async_client,
        _unique_email("login_wrong_msg"),
        "SicheresPasswort123!",
    )
    assert wrong_pw.status_code == 401
    assert response.json()["detail"] == wrong_pw.json()["detail"]


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_sets_cookie(async_client: AsyncClient) -> None:
    """Login setzt ein temp_token-Cookie (oder bei Bypass ein access_token)."""
    email = _unique_email("login_cookie")
    await _register(async_client, email, "SicheresPasswort123!")

    response = await _login(async_client, email, "SicheresPasswort123!")
    assert response.status_code == 200
    cookie_names = {c.name for c in async_client.cookies.jar}
    assert "temp_token" in cookie_names or "access_token" in cookie_names


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
async def test_login_account_lock_after_five_failures(async_client: AsyncClient) -> None:
    """Nach 5 fehlgeschlagenen Login-Versuchen ist der Account 15 Minuten gesperrt."""
    email = _unique_email("login_lock")
    password = "SicheresPasswort123!"
    await _register(async_client, email, password)

    for _ in range(5):
        resp = await _login(async_client, email, "FalschesPasswort123!")
        assert resp.status_code == 401

    db: AsyncSession = async_client.db_session
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    assert user.failed_login_count == 5
    assert user.locked_until is not None
    assert user.locked_until > datetime.now(UTC)


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
async def test_login_rate_limit_sixth_attempt(async_client: AsyncClient) -> None:
    """Der 6. Login-Versuch von derselben IP führt zu 429."""
    email = _unique_email("login_rl")
    await _register(async_client, email, "SicheresPasswort123!")

    for _ in range(5):
        resp = await _login(async_client, email, "FalschesPasswort123!")
        assert resp.status_code == 401

    sixth = await _login(async_client, email, "FalschesPasswort123!")
    assert sixth.status_code == 429
    assert "Retry-After" in sixth.headers
    assert sixth.headers["Retry-After"].isdigit()
