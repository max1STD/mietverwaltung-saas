"""Phase 1: Registrierungstests."""
from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient, Response
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
    """Sicherstellen, dass ein csrf_token-Cookie gesetzt ist."""
    if not client.cookies.get("csrf_token"):
        await client.get("/health")
    token = client.cookies.get("csrf_token")
    assert token, "CSRF-Cookie wurde nicht gesetzt"
    return token


async def _register(
    client: AsyncClient,
    email: str,
    password: str = "SicheresPasswort123!",
    full_name: str = "Test Vermieter",
    consent_text: str = CONSENT_TEXT,
) -> dict:
    csrf = await _ensure_csrf(client)
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": full_name,
            "consent_text": consent_text,
        },
        headers={"X-CSRF-Token": csrf},
    )
    return response


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_valid_user(async_client: AsyncClient) -> None:
    """POST /register mit gültigen Daten liefert 201 und das User-Objekt."""
    email = _unique_email("register_valid")
    response = await _register(async_client, email)
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["email"] == email
    assert payload["role"] == "vermieter"
    assert payload["is_active"] is True


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_duplicate_email(async_client: AsyncClient) -> None:
    """Doppelte E-Mail-Adresse liefert einen Fehler."""
    email = _unique_email("register_dup")
    first = await _register(async_client, email)
    assert first.status_code == 201

    second = await _register(async_client, email)
    assert second.status_code == 409


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_missing_consent(async_client: AsyncClient) -> None:
    """Fehlender consent_text führt zu einem 422-Validierungsfehler."""
    email = _unique_email("register_noconsent")
    csrf = await _ensure_csrf(async_client)
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SicheresPasswort123!",
            "full_name": "Test Vermieter",
        },
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 422


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_consent_too_short(async_client: AsyncClient) -> None:
    """consent_text <20 Zeichen führt zu einem 422-Validierungsfehler."""
    email = _unique_email("register_shortconsent")
    csrf = await _ensure_csrf(async_client)
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SicheresPasswort123!",
            "full_name": "Test Vermieter",
            "consent_text": "zu kurz",
        },
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 422


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_invalid_email(async_client: AsyncClient) -> None:
    """Ungültiges E-Mail-Format führt zu einem 422-Validierungsfehler."""
    csrf = await _ensure_csrf(async_client)
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "keine-gueltige-email",
            "password": "SicheresPasswort123!",
            "full_name": "Test Vermieter",
            "consent_text": CONSENT_TEXT,
        },
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 422


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_password_too_short(async_client: AsyncClient) -> None:
    """Passwort <12 Zeichen führt zu einem 422-Validierungsfehler."""
    email = _unique_email("register_shortpw")
    csrf = await _ensure_csrf(async_client)
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "kurz",
            "full_name": "Test Vermieter",
            "consent_text": CONSENT_TEXT,
        },
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 422


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_registered_user_has_role_vermieter(async_client: AsyncClient) -> None:
    """Neu registrierte User erhalten die Rolle 'vermieter'."""
    email = _unique_email("register_role")
    response = await _register(async_client, email)
    assert response.status_code == 201
    assert response.json()["role"] == "vermieter"

    db: AsyncSession = async_client.db_session
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    assert user.role == "vermieter"


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_registered_user_has_dsgvo_consent_timestamp(async_client: AsyncClient) -> None:
    """dsgvo_consent_at ist nach der Registrierung gesetzt."""
    email = _unique_email("register_consent_at")
    response = await _register(async_client, email)
    assert response.status_code == 201
    assert response.json()["dsgvo_consent_at"] is not None

    db: AsyncSession = async_client.db_session
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    assert user.dsgvo_consent_at is not None


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_creates_audit_log(async_client: AsyncClient) -> None:
    """Registrierung schreibt einen Audit-Log-Eintrag."""
    email = _unique_email("register_audit")
    response = await _register(async_client, email)
    assert response.status_code == 201

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
