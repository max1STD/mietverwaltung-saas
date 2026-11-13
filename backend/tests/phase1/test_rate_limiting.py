"""Phase 1: Rate-Limiting-Tests."""
from __future__ import annotations

import uuid

import pytest
import redis.asyncio as aioredis
from httpx import AsyncClient, Response

from app.config import settings

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


async def _login(client: AsyncClient, email: str, password: str, ip: str | None = None) -> dict:
    headers = {}
    if ip:
        headers["X-Forwarded-For"] = ip
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
        headers=headers,
    )
    return response


async def _register(
    client: AsyncClient,
    email: str,
    ip: str | None = None,
) -> dict:
    csrf = await _ensure_csrf(client)
    headers = {"X-CSRF-Token": csrf}
    if ip:
        headers["X-Forwarded-For"] = ip
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SicheresPasswort123!",
            "full_name": "Test Vermieter",
            "consent_text": CONSENT_TEXT,
        },
        headers=headers,
    )
    return response


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
async def test_login_rate_limit_sixth_attempt(async_client: AsyncClient) -> None:
    """5 Login-Versuche sind erlaubt; der 6. liefert 429 mit Retry-After."""
    email = _unique_email("rl_login")
    password = "SicheresPasswort123!"
    csrf = await _ensure_csrf(async_client)
    register = await async_client.post(
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

    ip = "203.0.113.10"
    for _ in range(5):
        resp = await _login(async_client, email, "FalschesPasswort123!", ip=ip)
        assert resp.status_code == 401

    sixth = await _login(async_client, email, "FalschesPasswort123!", ip=ip)
    assert sixth.status_code == 429
    assert "Retry-After" in sixth.headers
    assert sixth.headers["Retry-After"].isdigit()


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
async def test_register_rate_limit_sixth_attempt(async_client: AsyncClient) -> None:
    """5 Registrierungen sind erlaubt; der 6. Versuch liefert 429."""
    ip = "203.0.113.20"
    for i in range(5):
        resp = await _register(async_client, _unique_email(f"rl_reg_{i}"), ip=ip)
        assert resp.status_code == 201, resp.text

    sixth = await _register(async_client, _unique_email("rl_reg_6"), ip=ip)
    assert sixth.status_code == 429
    assert "Retry-After" in sixth.headers


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
async def test_rate_limit_resets_after_redis_flush(async_client: AsyncClient) -> None:
    """Nach FLUSHDB ist das Rate-Limit zurückgesetzt."""
    ip = "203.0.113.30"
    for i in range(5):
        resp = await _register(async_client, _unique_email(f"rl_flush_{i}"), ip=ip)
        assert resp.status_code == 201, resp.text

    blocked = await _register(async_client, _unique_email("rl_flush_blocked"), ip=ip)
    assert blocked.status_code == 429

    r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        await r.flushdb()
    finally:
        await r.aclose()

    after_flush = await _register(async_client, _unique_email("rl_flush_after"), ip=ip)
    assert after_flush.status_code == 201, after_flush.text


@pytest.mark.phase1
@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
async def test_rate_limit_per_ip_independent(async_client: AsyncClient) -> None:
    """Rate-Limits sind pro IP isoliert."""
    ip_a = "203.0.113.40"
    ip_b = "203.0.113.41"

    # IP A: 5 erlaubte Registrierungen.
    for i in range(5):
        resp = await _register(async_client, _unique_email(f"rl_ip_a_{i}"), ip=ip_a)
        assert resp.status_code == 201, resp.text

    # IP A ist jetzt blockiert.
    blocked = await _register(async_client, _unique_email("rl_ip_a_blocked"), ip=ip_a)
    assert blocked.status_code == 429

    # IP B ist weiterhin erlaubt.
    allowed = await _register(async_client, _unique_email("rl_ip_b_allowed"), ip=ip_b)
    assert allowed.status_code == 201, allowed.text
