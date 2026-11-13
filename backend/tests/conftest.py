"""Pytest-Konfiguration mit transaktionaler DB-Fixture und Async-HTTP-Client."""
from __future__ import annotations

import os
import subprocess
import sys
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Sicherstellen, dass Secrets für Tests gesetzt sind, bevor app.config geladen wird.
from app.services.crypto import generate_encryption_key

os.environ.setdefault("DB_ENCRYPTION_KEY", generate_encryption_key())
os.environ.setdefault("JWT_SECRET", "test-secret-do-not-use-in-production-32bytes")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:6379/15")

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _run_alembic() -> None:
    """Führt Alembic-Migrationen auf der aktuellen DB aus."""
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Alembic upgrade failed:\n{result.stderr}")


@pytest_asyncio.fixture(scope="session", autouse=True)
async def migrate_db() -> None:
    """Session-scoped: Datenbank-Schema auf aktuellen Stand bringen."""
    _run_alembic()
    yield


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest_asyncio.fixture(scope="function")
async def engine() -> AsyncIterator:
    """Async Engine für Tests (gleiche DB wie App)."""
    from app.config import settings

    test_engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=5,
        max_overflow=10,
    )
    yield test_engine
    await test_engine.dispose()


async def _set_admin_rls(conn) -> None:
    """RLS-Session-Variablen für Admin-Zugriff (Direkt-DB-Operationen in Tests)."""
    await conn.execute(text("SET LOCAL app.current_user_id = '0'"))
    await conn.execute(text("SET LOCAL app.current_user_role = 'admin'"))
    await conn.execute(text("SET LOCAL app.current_vermieter_id = '0'"))


# Audit-Middleware nutzt im Test dieselbe transaktionale Session wie der Request,
# damit Audit-Einträge dieselben Daten sehen und am Ende mitgerollbackt werden.
@asynccontextmanager
async def _shared_session_ctx(session: AsyncSession):
    yield session


def _patch_audit_session(session: AsyncSession) -> None:
    import app.middleware.audit as audit_mod

    audit_mod.async_session = lambda: _shared_session_ctx(session)


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncIterator[AsyncSession]:
    """Transaktionale Session, die am Ende zurückgerollt wird."""
    async with engine.begin() as conn:
        await _set_admin_rls(conn)
        trans = await conn.begin_nested()
        session_maker = async_sessionmaker(
            bind=conn,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        async with session_maker() as session:
            yield session
        await trans.rollback()


@pytest_asyncio.fixture
async def async_client(engine) -> AsyncIterator[AsyncClient]:
    """HTTP-Client mit überschriebenem get_db in einer Nested-Transaction."""
    from app.config import settings

    # Redis-Test-DB leeren.
    import redis.asyncio as aioredis

    r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    await r.flushdb()
    await r.aclose()

    from app.database import get_db
    from app.main import app

    async with engine.begin() as conn:
        await _set_admin_rls(conn)
        trans = await conn.begin_nested()
        session_maker = async_sessionmaker(
            bind=conn,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        session = session_maker()

        async def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db

        # Für FastAPI nutzen wir den nativen ASGITransport.
        from httpx import ASGITransport

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            client.db_session = session  # für Tests mit direkten DB-Abfragen
            _patch_audit_session(session)
            yield client

        app.dependency_overrides.clear()
        _patch_audit_session(app_async_session)
        await session.close()
        await trans.rollback()


@pytest.fixture
def csrf_header(async_client: AsyncClient) -> dict[str, str]:
    """Gibt den aktuellen CSRF-Token als Header zurück."""
    token = async_client.cookies.get("csrf_token")
    return {"X-CSRF-Token": token or ""}
