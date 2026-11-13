"""Phase 0: Health, Infrastruktur und Basis-API-Tests."""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
import redis.asyncio as aioredis
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import settings
from app.main import app as fastapi_app
from app.routes import health as health_module


EXPECTED_OPENAPI_PATHS = {
    "/health",
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/auth/2fa/setup",
    "/api/v1/auth/2fa/verify",
    "/api/v1/auth/refresh",
    "/api/v1/auth/logout",
    "/api/v1/auth/password-reset",
    "/api/v1/auth/sessions",
    "/api/v1/auth/users/me",
    "/api/v1/einwilligungen",
    "/api/v1/dsgvo/overview",
    "/api/v1/dsgvo/export",
    "/api/v1/dsgvo/delete",
    "/api/v1/objekte",
    "/api/v1/einheiten",
    "/api/v1/mieter",
    "/api/v1/mietvertraege",
    "/api/v1/tickets",
}


@pytest_asyncio.fixture
async def health_client(engine) -> AsyncIterator[AsyncClient]:
    """Isolierter HTTP-Client, der /health auf einem frischen Engine-Pool ausführt.

    Die globale app.database.async_session würde bei funktionsskopierten Event-Loops
    zu "attached to a different loop"-Fehlern führen. Daher wird die Session-Fabrik
    des Health-Routers temporär auf eine lokale Session umgebogen.
    """
    original_async_session = health_module.async_session
    local_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    health_module.async_session = local_session

    @asynccontextmanager
    async def _client_ctx():
        async with AsyncClient(
            transport=ASGITransport(app=fastapi_app),
            base_url="http://test",
        ) as client:
            yield client

    async with _client_ctx() as client:
        yield client

    health_module.async_session = original_async_session


@pytest.mark.phase0
@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_returns_ok(health_client: AsyncClient) -> None:
    """GET /health liefert 200 mit status=ok."""
    response = await health_client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["checks"]["database"] == "ok"
    assert payload["checks"]["redis"] == "ok"
    assert payload["version"] == "0.1.0"


@pytest.mark.phase0
@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_checks_database(health_client: AsyncClient) -> None:
    """Der Health-Check prüft explizit die Datenbank-Konnektivität."""
    response = await health_client.get("/health")
    assert response.status_code == 200
    checks = response.json()["checks"]
    assert "database" in checks
    assert checks["database"] == "ok"


@pytest.mark.phase0
@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_checks_redis(health_client: AsyncClient) -> None:
    """Der Health-Check prüft explizit die Redis-Konnektivität."""
    response = await health_client.get("/health")
    assert response.status_code == 200
    checks = response.json()["checks"]
    assert "redis" in checks
    assert checks["redis"] == "ok"


@pytest.mark.phase0
@pytest.mark.integration
@pytest.mark.asyncio
async def test_swagger_ui_accessible(async_client: AsyncClient) -> None:
    """Swagger UI unter /docs ist erreichbar und liefert HTML."""
    response = await async_client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "swagger" in response.text.lower() or "openapi" in response.text.lower()


@pytest.mark.phase0
@pytest.mark.integration
@pytest.mark.asyncio
async def test_openapi_json_valid(async_client: AsyncClient) -> None:
    """GET /openapi.json liefert eine gültige Spezifikation mit allen erwarteten Pfaden."""
    response = await async_client.get("/openapi.json")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/json"
    spec = response.json()
    assert "paths" in spec
    missing = EXPECTED_OPENAPI_PATHS - set(spec["paths"].keys())
    assert not missing, f"Fehlende OpenAPI-Pfade: {missing}"


@pytest.mark.phase0
@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_has_all_tables(db_session: AsyncSession) -> None:
    """Die Datenbank enthält mindestens die 33 erwarteten Tabellen (plus alembic_version)."""
    result = await db_session.execute(
        text("""
            SELECT COUNT(*)
            FROM pg_class
            WHERE relkind = 'r'
              AND relnamespace = 'public'::regnamespace
              AND relname NOT LIKE 'pg_%'
              AND relname NOT LIKE 'sql_%'
        """)
    )
    count = result.scalar_one()
    assert count >= 33, f"Erwartet >=33 Tabellen, gefunden {count}"


@pytest.mark.phase0
@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_has_pgcrypto(db_session: AsyncSession) -> None:
    """Die pgcrypto-Extension ist aktiviert."""
    result = await db_session.execute(
        text("SELECT extname FROM pg_extension WHERE extname = 'pgcrypto'")
    )
    assert result.scalar_one_or_none() == "pgcrypto"


@pytest.mark.phase0
@pytest.mark.integration
@pytest.mark.asyncio
async def test_redis_set_get(async_client: AsyncClient) -> None:
    """Redis SET/GET funktioniert über die konfigurierte URL."""
    r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        await r.set("phase0:test:key", "phase0:test:value", ex=10)
        value = await r.get("phase0:test:key")
        assert value == "phase0:test:value"
    finally:
        await r.aclose()


@pytest.mark.phase0
@pytest.mark.integration
@pytest.mark.asyncio
async def test_cors_headers_present(async_client: AsyncClient) -> None:
    """CORS-Header sind auf API-Antworten vorhanden."""
    origin = settings.CORS_ORIGINS[0]
    response = await async_client.get("/health", headers={"Origin": origin})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin
    assert response.headers.get("access-control-allow-credentials") == "true"
