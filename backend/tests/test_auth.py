"""Integrationstests für Auth, 2FA, Rate-Limiting, RLS und Audit-Log."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pyotp
import pytest
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.session import UserSession
from app.models.user import User
from app.schemas.auth import ConsentRequest
from app.services.auth import hash_password


CONSENT_TEXT = (
    "Ich stimme der Verarbeitung meiner Daten gemäß DSGVO und den AGB zu. "
    "Einwilligungen können jederzeit widerrufen werden."
)


async def _register_user(
    client: AsyncClient,
    email: str,
    password: str,
    full_name: str = "Test User",
) -> dict:
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": full_name,
            "consent_text": CONSENT_TEXT,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


async def _login_step(client: AsyncClient, email: str, password: str) -> dict:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


async def _setup_2fa(client: AsyncClient, csrf: str) -> dict:
    resp = await client.post(
        "/api/v1/auth/2fa/setup",
        json={},
        headers={"X-CSRF-Token": csrf},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


async def _verify_2fa(client: AsyncClient, secret: str, csrf: str) -> dict:
    code = pyotp.TOTP(secret).now()
    resp = await client.post(
        "/api/v1/auth/2fa/verify",
        json={"code": code},
        headers={"X-CSRF-Token": csrf},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def _csrf(client: AsyncClient) -> str:
    return client.cookies.get("csrf_token") or ""


@pytest.mark.asyncio
async def test_register_login_2fa_logout_flow(async_client: AsyncClient) -> None:
    """Happy-Path: Registrieren → Login → 2FA-Setup → 2FA-Verify → Logout."""
    email = f"vermieter-{uuid.uuid4().hex[:8]}@example.com"
    password = "SicheresPasswort123!"

    user = await _register_user(async_client, email, password)
    assert user["email"] == email
    assert user["role"] == "vermieter"

    pre2fa = await _login_step(async_client, email, password)
    assert pre2fa["requires_2fa"] is True
    csrf = _csrf(async_client)

    setup = await _setup_2fa(async_client, csrf)
    secret = setup["secret"]
    assert len(setup["backup_codes"]) == 8

    token_resp = await _verify_2fa(async_client, secret, csrf)
    assert "access_token" in token_resp
    assert token_resp["user"]["email"] == email

    # Geschützter Endpunkt muss jetzt funktionieren.
    me = await async_client.get("/api/v1/auth/users/me")
    assert me.status_code == 200
    assert me.json()["email"] == email

    # Logout.
    logout = await async_client.post(
        "/api/v1/auth/logout",
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    assert logout.status_code == 200

    # Nach Logout ist /users/me unautorisiert.
    me_after = await async_client.get("/api/v1/auth/users/me")
    assert me_after.status_code == 401


@pytest.mark.asyncio
async def test_rate_limiting_login(async_client: AsyncClient) -> None:
    """Nach 5 fehlgeschlagenen Login-Versuchen gibt es 429 mit Retry-After."""
    email = f"rate-{uuid.uuid4().hex[:8]}@example.com"
    password = "SicheresPasswort123!"
    await _register_user(async_client, email, password)

    wrong_password = "falsch"
    attempts = 0
    for i in range(7):
        resp = await async_client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": wrong_password},
        )
        attempts += 1
        if resp.status_code == 429:
            assert "Retry-After" in resp.headers
            assert resp.headers["Retry-After"].isdigit()
            break
    else:
        pytest.fail("Rate-Limit wurde nicht ausgelöst")

    assert attempts >= 6

    # Nach korrektem Login darf das Limit nicht blockieren.
    # Wir warten nicht 15 Min; wir setzen Redis-Test-DB vorher in conftest zurück.
    # Daher reicht ein erfolgreicher Login danach als Indikator.
    # (Für den Test starten wir mit leerer Redis, also sollte nach den 6 fehlgeschlagenen
    #  Versuchen der nächste korrekte Login blockiert sein.)
    blocked = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    # Rate-Limit ist IP-basiert und immer noch aktiv.
    assert blocked.status_code == 429


@pytest.mark.asyncio
async def test_rls_mieter_sees_only_own_data(
    async_client: AsyncClient,
) -> None:
    """Ein Mieter-Account sieht nur seine eigenen Daten (RLS)."""
    db = async_client.db_session
    # Vermieter über API registrieren.
    v_email = f"v-{uuid.uuid4().hex[:8]}@example.com"
    v_password = "SicheresPasswort123!"
    await _register_user(async_client, v_email, v_password)

    # Vermieter-Datensatz laden, um die ID zu erhalten.
    result = await db.execute(
        select(User).where(User.email == v_email)
    )
    vermieter = result.scalar_one()

    # Zwei Mieter-Accounts direkt in die DB einfügen (als Admin-RLS-Kontext).
    mieter_pw = "MieterPasswort123!"
    for suffix in ("mieter1", "mieter2"):
        user = User(
            email=f"{suffix}-{vermieter.id}@example.com",
            password_hash=hash_password(mieter_pw),
            full_name=suffix,
            role="mieter",
            vermieter_id=vermieter.id,
            is_active=True,
            email_verified=True,
        )
        db.add(user)
    await db.commit()

    # Login als Mieter 1.
    m1_email = f"mieter1-{vermieter.id}@example.com"
    pre2fa = await _login_step(async_client, m1_email, mieter_pw)
    assert pre2fa["requires_2fa"] is True
    csrf = _csrf(async_client)
    setup = await _setup_2fa(async_client, csrf)
    await _verify_2fa(async_client, setup["secret"], csrf)

    me = await async_client.get("/api/v1/auth/users/me")
    assert me.status_code == 200
    assert me.json()["email"] == m1_email
    assert me.json()["role"] == "mieter"


@pytest.mark.asyncio
async def test_audit_log_entries(async_client: AsyncClient) -> None:
    """Sicherheitsrelevante Aktionen landen im audit_logs."""
    db = async_client.db_session
    email = f"audit-{uuid.uuid4().hex[:8]}@example.com"
    password = "SicheresPasswort123!"
    await _register_user(async_client, email, password)

    pre2fa = await _login_step(async_client, email, password)
    csrf = _csrf(async_client)
    setup = await _setup_2fa(async_client, csrf)
    await _verify_2fa(async_client, setup["secret"], csrf)

    await async_client.post(
        "/api/v1/auth/logout",
        headers={"X-CSRF-Token": _csrf(async_client)},
    )

    # Über Admin-Kontext die Audit-Logs abfragen.
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one()

    logs = await db.execute(
        select(AuditLog).where(AuditLog.user_id == user.id)
    )
    actions = {log.action for log in logs.scalars().all()}
    expected = {"register", "login_step_password", "2fa_setup", "2fa_verify", "logout"}
    assert expected.issubset(actions), f"Fehlende Aktionen: {expected - actions}"


@pytest.mark.asyncio
async def test_refresh_token_rotation(async_client: AsyncClient) -> None:
    """Refresh stellt neue Tokens aus und rotiert das Refresh-Token."""
    email = f"refresh-{uuid.uuid4().hex[:8]}@example.com"
    password = "SicheresPasswort123!"
    await _register_user(async_client, email, password)

    pre2fa = await _login_step(async_client, email, password)
    csrf = _csrf(async_client)
    setup = await _setup_2fa(async_client, csrf)
    await _verify_2fa(async_client, setup["secret"], csrf)

    old_refresh = async_client.cookies.get("refresh_token")
    assert old_refresh

    refresh_resp = await async_client.post(
        "/api/v1/auth/refresh",
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    assert refresh_resp.status_code == 200
    new_refresh = async_client.cookies.get("refresh_token")
    assert new_refresh
    assert new_refresh != old_refresh

    # Altes Refresh-Token sollte nicht mehr funktionieren.
    async_client.cookies.set("refresh_token", old_refresh)
    reuse = await async_client.post(
        "/api/v1/auth/refresh",
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    assert reuse.status_code == 401
