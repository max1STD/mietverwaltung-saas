"""Phase 1: Login-Tests."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pyotp
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


async def _login(client: AsyncClient, email: str, password: str, remember_me: bool = False) -> Response:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "remember_me": remember_me},
    )
    return response


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient) -> None:
    """Login mit korrekten Daten liefert 200. Bei erstem Login ohne 2FA kommt TokenResponse."""
    email = _unique_email("login_ok")
    password = "SicheresPasswort123!"
    await _register(async_client, email, password)

    response = await _login(async_client, email, password)
    assert response.status_code == 200, response.text
    payload = response.json()
    # 2FA ist optional: erster Login ohne TOTP liefert direkt vollen TokenResponse.
    if payload.get("requires_2fa"):
        assert "temp_token" in payload
        assert payload["temp_token"]
    else:
        assert "access_token" in payload
        assert payload["access_token"]
        assert payload["user"]["email"] == email


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_remember_me_sets_longer_refresh_cookie(async_client: AsyncClient) -> None:
    """Bei remember_me=True erhält das Refresh-Cookie eine längere Lebensdauer."""
    email = _unique_email("login_remember")
    await _register(async_client, email, "SicheresPasswort123!")

    response = await _login(async_client, email, "SicheresPasswort123!", remember_me=True)
    assert response.status_code == 200, response.text

    set_cookie_headers = response.headers.get_list("set-cookie")
    refresh_cookie_header = next(
        (h for h in set_cookie_headers if h.startswith("refresh_token=")), None
    )
    assert refresh_cookie_header is not None
    # Max-Age sollte ca. 30 Tage sein (2592000 Sekunden)
    assert "Max-Age=2592000" in refresh_cookie_header or "max-age=2592000" in refresh_cookie_header.lower()


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_and_2fa_verify(async_client: AsyncClient) -> None:
    """Login, dann 2FA-Setup/Verify, dann geschützte Route."""
    import pyotp

    email = _unique_email("login_2fa")
    password = "SicheresPasswort123!"
    await _register(async_client, email, password)

    # Erster Login ohne 2FA → direkter TokenResponse.
    resp = await _login(async_client, email, password)
    assert resp.status_code == 200
    csrf = await _ensure_csrf(async_client)

    # 2FA einrichten.
    setup_resp = await async_client.post(
        "/api/v1/auth/2fa/setup",
        json={},
        headers={"X-CSRF-Token": csrf},
    )
    assert setup_resp.status_code == 200, setup_resp.text
    secret = setup_resp.json()["secret"]

    # Logout.
    await async_client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf})

    # Nun Login → 2FA erforderlich.
    pre2fa = await _login(async_client, email, password)
    assert pre2fa.status_code == 200
    payload = pre2fa.json()
    assert payload["requires_2fa"] is True
    csrf = await _ensure_csrf(async_client)

    verify_resp = await async_client.post(
        "/api/v1/auth/2fa/verify",
        json={"code": pyotp.TOTP(secret).now()},
        headers={"X-CSRF-Token": csrf},
    )
    assert verify_resp.status_code == 200, verify_resp.text
    assert "access_token" in verify_resp.json()
    assert verify_resp.json()["user"]["email"] == email

    me = await async_client.get("/api/v1/auth/users/me")
    assert me.status_code == 200
    assert me.json()["email"] == email


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
