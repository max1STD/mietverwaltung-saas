"""Phase 1: JWT-Refresh- und Session-Tests."""
from __future__ import annotations

import uuid

import pyotp
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import UserSession
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


async def _register_and_login(client: AsyncClient, email: str, password: str) -> dict:
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

    if login.json().get("requires_2fa"):
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
        return verify.json()

    return login.json()


async def _register_and_login_with_2fa(client: AsyncClient, email: str, password: str) -> tuple[dict, str]:
    """Registriert, loggt ein, richtet 2FA ein und verifiziert.

    Gibt (verify_response, secret) zurück.
    """
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
    return verify.json(), secret


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_refresh_token_rotation(async_client: AsyncClient) -> None:
    """POST /refresh rotiert das Refresh-Token und setzt neue Cookies."""
    email = _unique_email("jwt_refresh")
    password = "SicheresPasswort123!"
    await _register_and_login(async_client, email, password)

    old_refresh = async_client.cookies.get("refresh_token")
    assert old_refresh, "Kein Refresh-Token nach Login"

    refresh = await async_client.post(
        "/api/v1/auth/refresh",
        headers={"X-CSRF-Token": await _ensure_csrf(async_client)},
    )
    assert refresh.status_code == 200, refresh.text

    new_refresh = async_client.cookies.get("refresh_token")
    assert new_refresh, "Neues Refresh-Token wurde nicht gesetzt"
    assert new_refresh != old_refresh


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_logout_clears_cookies_and_invalidates_session(async_client: AsyncClient) -> None:
    """Logout löscht Cookies und widerruft die Session."""
    email = _unique_email("jwt_logout")
    password = "SicheresPasswort123!"
    await _register_and_login_with_2fa(async_client, email, password)

    db: AsyncSession = async_client.db_session
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one()

    sessions_before = await db.execute(
        select(UserSession).where(
            UserSession.user_id == user.id,
            UserSession.revoked_at.is_(None),
        )
    )
    active_before = sessions_before.scalars().all()
    assert active_before

    logout = await async_client.post(
        "/api/v1/auth/logout",
        headers={"X-CSRF-Token": await _ensure_csrf(async_client)},
    )
    assert logout.status_code == 200, logout.text

    # Cookies sollten gelöscht sein.
    assert not async_client.cookies.get("access_token")

    sessions_after = await db.execute(
        select(UserSession).where(
            UserSession.user_id == user.id,
            UserSession.revoked_at.is_(None),
        )
    )
    active_after = sessions_after.scalars().all()
    assert not active_after


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_users_me_with_valid_token(async_client: AsyncClient) -> None:
    """GET /users/me mit gültigem Token liefert das eigene Profil."""
    email = _unique_email("jwt_me")
    password = "SicheresPasswort123!"
    await _register_and_login(async_client, email, password)

    me = await async_client.get("/api/v1/auth/users/me")
    assert me.status_code == 200, me.text
    assert me.json()["email"] == email


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_users_me_without_token(async_client: AsyncClient) -> None:
    """GET /users/me ohne Token liefert 401."""
    # Sicherstellen, dass keine Auth-Cookies vorhanden sind.
    for name in ("access_token", "refresh_token", "temp_token"):
        async_client.cookies.delete(name)

    me = await async_client.get("/api/v1/auth/users/me")
    assert me.status_code == 401
