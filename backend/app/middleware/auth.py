"""Auth-Dependency: User aus JWT-Cookie laden + RLS-Kontext setzen + Rollenprüfung."""
from __future__ import annotations

from functools import partial
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserResponse
from app.services.jwt import verify_access_token


def csrf_protect(request: Request) -> None:
    """Double-Submit-Cookie: Header muss mit Cookie übereinstimmen."""
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return
    cookie = request.cookies.get("csrf_token")
    header = request.headers.get("x-csrf-token")
    if not cookie or not header or cookie != header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF-Token fehlt oder ungültig",
        )


def _get_client_ip(request: Request) -> str:
    """Extrahiert die Client-IP aus Request-Headern (Proxy-tolerant)."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def decode_access_cookie(request: Request) -> dict[str, Any] | None:
    """Liest und validiert das Access-Token Cookie."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    return verify_access_token(token)


def get_user_id_from_cookie(request: Request) -> int | None:
    """Hilfsfunktion für Audit-Middleware: User-ID ohne DB-Lookup."""
    payload = decode_access_cookie(request)
    if not payload:
        return None
    return int(payload.get("sub"))


async def set_rls_context(db: AsyncSession, user: User) -> None:
    """Setzt PostgreSQL-Session-Variablen für Row-Level Security."""
    if user.role == "mieter":
        vermieter_id = user.vermieter_id
    else:
        vermieter_id = user.id

    # Sichere Typ-Casts, bevor wir in das SQL-Statement einbauen.
    user_id = int(user.id)
    role = str(user.role)
    vermieter_id_int = int(vermieter_id) if vermieter_id else 0

    await db.execute(text(f"SET LOCAL app.current_user_id = '{user_id}'"))
    await db.execute(text(f"SET LOCAL app.current_user_role = '{role}'"))
    await db.execute(text(f"SET LOCAL app.current_vermieter_id = '{vermieter_id_int}'"))


async def set_system_rls_context(db: AsyncSession) -> None:
    """Deaktiviert RLS für System-Operationen (Registrierung, Login, Passwort-Reset).

    Diese Operationen laufen ohne eingeloggten User ab und müssen
    auf die users-Tabelle zugreifen können, bevor ein RLS-Kontext
    existiert. Verwendet SET (Session-Level) statt SET LOCAL,
    da SQLAlchemy ggf. auto-commit und die LOCAL-Einstellung verloren geht.
    """
    await db.execute(text("SET row_security = off"))
    await db.execute(text("SET app.current_user_id = '0'"))
    await db.execute(text("SET app.current_user_role = 'system'"))
    await db.execute(text("SET app.current_vermieter_id = '0'"))


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Lädt den aktuellen User aus dem JWT-Access-Cookie."""
    payload = decode_access_cookie(request)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nicht authentifiziert",
        )

    user_id = int(payload.get("sub"))
    user = await db.get(User, user_id)
    if user is None or not user.is_active or user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger Account",
        )

    # RLS-Kontext für alle folgenden DB-Operationen im Request setzen.
    await set_rls_context(db, user)
    return user


async def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    """Alias für geschützte Routen."""
    return user


def require_role(*allowed_roles: str):
    """Dependency-Factory: erlaubt nur bestimmte Rollen."""

    async def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unzureichende Berechtigungen",
            )
        return user

    return checker


async def to_user_response(user: User) -> UserResponse:
    """Mappt ein User-ORM-Objekt auf das öffentliche Response-Schema."""
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        phone=user.phone,
        email_verified=user.email_verified,
        is_active=user.is_active,
        dsgvo_consent_at=user.dsgvo_consent_at.isoformat() if user.dsgvo_consent_at else None,
        firma=user.firma,
        rechnungs_strasse=user.rechnungs_strasse,
        rechnungs_hausnr=user.rechnungs_hausnr,
        rechnungs_plz=user.rechnungs_plz,
        rechnungs_ort=user.rechnungs_ort,
        ust_id=user.ust_id,
    )
