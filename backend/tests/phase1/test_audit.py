"""Phase 1: Audit-Logging-Tests."""
from __future__ import annotations

import uuid

import pyotp
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
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
async def test_registration_creates_register_audit_log(async_client: AsyncClient) -> None:
    """Registrierung erzeugt einen Audit-Log-Eintrag mit action='register'."""
    email = _unique_email("audit_register")
    csrf = await _ensure_csrf(async_client)
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SicheresPasswort123!",
            "full_name": "Test Vermieter",
            "consent_text": CONSENT_TEXT,
        },
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 201, response.text

    db: AsyncSession = async_client.db_session
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one()

    logs = await db.execute(
        select(AuditLog).where(
            AuditLog.user_id == user.id,
            AuditLog.action == "register",
        )
    )
    assert logs.scalars().first() is not None


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_creates_login_step_password_audit_log(async_client: AsyncClient) -> None:
    """Login erzeugt einen Audit-Log-Eintrag mit action='login_step_password'."""
    email = _unique_email("audit_login")
    await _authenticated_client(async_client, email, "SicheresPasswort123!")

    db: AsyncSession = async_client.db_session
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one()

    logs = await db.execute(
        select(AuditLog).where(
            AuditLog.user_id == user.id,
        )
    )
    actions = {log.action for log in logs.scalars().all()}
    assert "login_step_password" in actions


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_audit_log_has_user_ip_and_timestamp(async_client: AsyncClient) -> None:
    """Audit-Log-Einträge enthalten user_id, ip_address und created_at."""
    email = _unique_email("audit_meta")
    await _authenticated_client(async_client, email, "SicheresPasswort123!")

    db: AsyncSession = async_client.db_session
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one()

    logs = await db.execute(
        select(AuditLog).where(AuditLog.user_id == user.id)
    )
    entries = logs.scalars().all()
    assert entries
    assert any(log.ip_address is not None for log in entries)
    assert all(log.created_at is not None for log in entries)


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_audit_log_has_risk_level(async_client: AsyncClient) -> None:
    """Audit-Log-Einträge haben ein gesetztes risk_level."""
    email = _unique_email("audit_risk")
    await _authenticated_client(async_client, email, "SicheresPasswort123!")

    db: AsyncSession = async_client.db_session
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one()

    logs = await db.execute(
        select(AuditLog).where(AuditLog.user_id == user.id)
    )
    entries = logs.scalars().all()
    assert entries
    assert all(
        log.risk_level in {"niedrig", "mittel", "hoch"} for log in entries
    )
