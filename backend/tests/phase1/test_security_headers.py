"""Phase 1: Sicherheits-Header und Cookie-Tests."""
from __future__ import annotations

import uuid
from http.cookies import SimpleCookie

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


async def _authenticated_client(client: AsyncClient, email: str, password: str) -> Response:
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
    return verify


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_csp_header_contains_nonce(async_client: AsyncClient) -> None:
    """Jede Response enthält einen CSP-Header mit Nonce und frame-ancestors."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    csp = response.headers.get("content-security-policy")
    assert csp is not None
    assert "nonce-" in csp
    assert "frame-ancestors 'none'" in csp


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_csrf_cookie_present(async_client: AsyncClient) -> None:
    """Der Security-Header-Middleware setzt ein csrf_token-Cookie."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert "csrf_token" in {c.name for c in async_client.cookies.jar}


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_x_content_type_options_nosniff(async_client: AsyncClient) -> None:
    """X-Content-Type-Options ist auf nosniff gesetzt."""
    response = await async_client.get("/health")
    assert response.headers.get("x-content-type-options") == "nosniff"


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_frame_protection_present(async_client: AsyncClient) -> None:
    """X-Frame-Options oder frame-ancestors in CSP schützt gegen Clickjacking."""
    response = await async_client.get("/health")
    x_frame = response.headers.get("x-frame-options")
    csp = response.headers.get("content-security-policy", "")
    assert x_frame is not None or "frame-ancestors" in csp


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.asyncio
async def test_auth_cookies_have_security_attributes(async_client: AsyncClient) -> None:
    """Auth-Cookies sind HttpOnly und haben Secure oder SameSite."""
    email = _unique_email("sec_cookies")
    verify = await _authenticated_client(async_client, email, "SicheresPasswort123!")

    relevant = {"access_token", "refresh_token", "temp_token", "csrf_token"}
    found: set[str] = set()
    for raw in verify.headers.get_list("set-cookie"):
        parsed = SimpleCookie()
        parsed.load(raw)
        for name in parsed:
            if name not in relevant:
                continue
            found.add(name)
            morsel = parsed[name]
            has_httponly = morsel.get("httponly") is not None
            has_secure = morsel.get("secure") is not None
            has_samesite = morsel.get("samesite") is not None
            assert has_httponly or name == "csrf_token"
            assert has_secure or has_samesite, (
                f"Cookie {name} hat weder Secure noch SameSite"
            )
    # access_token und csrf_token müssen zumindest gesetzt worden sein.
    assert "access_token" in found
    assert "csrf_token" in found
