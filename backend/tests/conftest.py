"""Pytest-Konfiguration mit transaktionaler DB-Fixture und Async-HTTP-Client."""
from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager

# ── Test-Datenbank setzen BEVOR app.config geladen wird ──
os.environ["DATABASE_URL"] = (
    "postgresql+asyncpg://mv:mietverwaltung_dev_2026@127.0.0.1:5432/mietverwaltung_test_utf8"
)

import base64
import secrets

os.environ.setdefault(
    "DB_ENCRYPTION_KEY",
    base64.b64encode(secrets.token_bytes(32)).decode("ascii"),
)
os.environ.setdefault("JWT_SECRET", "test-secret-do-not-use-in-production-32bytes")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:6379/15")

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.user import User  # noqa: E402

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


def _disable_rls() -> None:
    """Schaltet RLS auf allen Tabellen der Test-DB ab (dev-Setup)."""
    db_url = os.environ["DATABASE_URL"].replace("postgresql+asyncpg://", "postgresql://")
    sql = (
        "DO $$ DECLARE r RECORD; BEGIN "
        "FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP "
        "EXECUTE format('ALTER TABLE %I DISABLE ROW LEVEL SECURITY', r.tablename); "
        "END LOOP; END $$;"
    )
    result = subprocess.run(
        ["psql", db_url, "-c", sql],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"RLS disable failed:\n{result.stderr}")


@pytest.fixture(scope="session", autouse=True)
def migrate_db() -> Iterator[None]:
    """Session-scoped: Datenbank-Schema auf aktuellen Stand bringen."""
    _run_alembic()
    _disable_rls()
    yield


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest_asyncio.fixture(scope="function", loop_scope="function")
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


@pytest_asyncio.fixture(loop_scope="function")
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


@pytest_asyncio.fixture(loop_scope="function")
async def async_client(engine) -> AsyncIterator[AsyncClient]:
    """HTTP-Client mit überschriebenem get_db in einer Nested-Transaction."""
    # Redis-Test-DB leeren.
    import redis.asyncio as aioredis

    from app.config import settings

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

        # Audit-Middleware im Test auf dieselbe transaktionale Session umleiten.
        import app.middleware.audit as audit_mod

        _original_audit_session = audit_mod.async_session
        _patch_audit_session(session)

        # Für FastAPI nutzen wir den nativen ASGITransport.
        from httpx import ASGITransport

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="https://test",
        ) as client:
            client.db_session = session  # für Tests mit direkten DB-Abfragen
            yield client

        app.dependency_overrides.clear()
        audit_mod.async_session = _original_audit_session
        await session.close()
        await trans.rollback()


@pytest.fixture
def csrf_header(async_client: AsyncClient) -> dict[str, str]:
    """Gibt den aktuellen CSRF-Token als Header zurück."""
    token = async_client.cookies.get("csrf_token")
    return {"X-CSRF-Token": token or ""}


@pytest_asyncio.fixture(loop_scope="function")
async def vermieter_user(async_client: AsyncClient) -> User:
    """Erstellt einen Test-Vermieter in der Client-Session."""
    from app.models.user import User
    from app.services.auth import hash_password

    session: AsyncSession = async_client.db_session
    user = User(
        email="test-vermieter@example.de",
        password_hash=hash_password("TestPasswort123!"),
        full_name="Test Vermieter",
        role="vermieter",
        is_active=True,
        email_verified=True,
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture(loop_scope="function")
async def admin_user(async_client: AsyncClient) -> User:
    """Erstellt einen Test-Admin in der Client-Session."""
    from app.models.user import User
    from app.services.auth import hash_password

    session: AsyncSession = async_client.db_session
    user = User(
        email="test-admin@example.de",
        password_hash=hash_password("TestPasswort123!"),
        full_name="Test Admin",
        role="admin",
        is_active=True,
        email_verified=True,
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture(loop_scope="function")
async def admin_client(
    async_client: AsyncClient,
    admin_user: User,
) -> AsyncClient:
    """Authentifizierter Client als Test-Admin."""
    from app.main import app
    from app.middleware.auth import get_current_user

    async def override_get_current_user() -> User:
        return admin_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    csrf_token = async_client.cookies.get("csrf_token") or "test-csrf-token"
    async_client.cookies.set("csrf_token", csrf_token)
    async_client.headers["X-CSRF-Token"] = csrf_token
    async_client.user_id = admin_user.id

    yield async_client

    app.dependency_overrides.pop(get_current_user, None)
    async_client.headers.pop("X-CSRF-Token", None)


@pytest_asyncio.fixture(loop_scope="function")
async def auth_client(
    async_client: AsyncClient,
    vermieter_user: User,
) -> AsyncClient:
    """Authentifizierter Client als Test-Vermieter."""
    from app.main import app
    from app.middleware.auth import get_current_user

    async def override_get_current_user() -> User:
        return vermieter_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    # CSRF-Double-Submit-Cookie initialisieren, falls noch nicht gesetzt.
    csrf_token = async_client.cookies.get("csrf_token") or "test-csrf-token"
    async_client.cookies.set("csrf_token", csrf_token)
    async_client.headers["X-CSRF-Token"] = csrf_token
    async_client.user_id = vermieter_user.id

    yield async_client

    app.dependency_overrides.pop(get_current_user, None)
    async_client.headers.pop("X-CSRF-Token", None)
