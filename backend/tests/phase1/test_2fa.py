"""Phase 1: 2FA-Tests."""
from __future__ import annotations

import re
import uuid

import pyotp
import pytest
from httpx import AsyncClient, Response

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
    assert response.status_code == 200, response.text
    return response.json()


async def _setup_2fa(client: AsyncClient) -> dict:
    csrf = await _ensure_csrf(client)
    response = await client.post(
        "/api/v1/auth/2fa/setup",
        json={},
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 200, response.text
    return response.json()


async def _verify_2fa(client: AsyncClient, code: str) -> dict:
    csrf = await _ensure_csrf(client)
    response = await client.post(
        "/api/v1/auth/2fa/verify",
        json={"code": code},
        headers={"X-CSRF-Token": csrf},
    )
    return response


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_2fa_setup_returns_secret_and_qr(async_client: AsyncClient) -> None:
    """POST /2fa/setup liefert Secret, Backup-Codes und otpauth:// QR-URL."""
    email = _unique_email("2fa_setup")
    await _register(async_client, email)
    await _login(async_client, email, "SicheresPasswort123!")

    setup = await _setup_2fa(async_client)
    assert "secret" in setup
    assert "backup_codes" in setup
    assert len(setup["backup_codes"]) == 8
    assert "otpauth_uri" in setup
    assert setup["otpauth_uri"].startswith("otpauth://totp/")


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_2fa_verify_valid_code(async_client: AsyncClient) -> None:
    """Verifizierung mit gültigem TOTP-Code schließt den Login erfolgreich ab."""
    email = _unique_email("2fa_valid")
    await _register(async_client, email)
    await _login(async_client, email, "SicheresPasswort123!")

    setup = await _setup_2fa(async_client)
    code = pyotp.TOTP(setup["secret"]).now()
    response = await _verify_2fa(async_client, code)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert "access_token" in payload
    assert payload["user"]["email"] == email


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_2fa_verify_invalid_code(async_client: AsyncClient) -> None:
    """Verifizierung mit ungültigem Code schlägt fehl."""
    email = _unique_email("2fa_invalid")
    await _register(async_client, email)
    await _login(async_client, email, "SicheresPasswort123!")
    await _setup_2fa(async_client)

    response = await _verify_2fa(async_client, "000000")
    assert response.status_code == 401


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_requires_2fa_after_setup(async_client: AsyncClient) -> None:
    """Nach Einrichtung von 2FA verlangt der Login einen 2FA-Code."""
    email = _unique_email("2fa_required")
    await _register(async_client, email)
    await _login(async_client, email, "SicheresPasswort123!")
    await _setup_2fa(async_client)

    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SicheresPasswort123!"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["requires_2fa"] is True


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_totp_secret_is_valid_base32(async_client: AsyncClient) -> None:
    """Das zurückgegebene TOTP-Secret ist ein gültiger Base32-String."""
    email = _unique_email("2fa_base32")
    await _register(async_client, email)
    await _login(async_client, email, "SicheresPasswort123!")

    setup = await _setup_2fa(async_client)
    secret = setup["secret"]
    assert re.fullmatch(r"[A-Z2-7=]+", secret) is not None
    # pyotp akzeptiert das Secret als valide Base32.
    assert pyotp.TOTP(secret).now() is not None
