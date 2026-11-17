"""Admin-Routen — zentrale Verwaltung fuer Vermieter, Mieter, Objekte, Einheiten."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import _get_client_ip, csrf_protect, require_role
from app.models.einheit import Einheit
from app.models.objekt import Objekt
from app.models.user import User
from app.routes._helpers import map_einheit_response, map_objekt_response
from app.schemas.admin import (
    AdminEinheitListResponse,
    AdminObjektListResponse,
    AdminStatsResponse,
    AdminUserCreateRequest,
    AdminUserListResponse,
    AdminUserUpdateRequest,
    AdminUserResponse,
    PasswordResetAdminRequest,
)
from app.services.audit_log import audit_log
from app.services.auth import AuthError, _get_user_by_email, hash_password, register
from app.services.einheiten import list_einheiten
from app.services.objekte import list_objekte

router = APIRouter()


async def _set_admin_rls(db: AsyncSession, admin: User) -> None:
    """RLS im Admin-Kontext: Admin darf alle Entitaeten sehen."""
    pass


def _user_to_admin_response(user: User) -> AdminUserResponse:
    return AdminUserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        email_verified=user.email_verified,
        phone=user.phone,
        firma=user.firma,
        vermieter_id=user.vermieter_id,
        created_at=user.created_at.isoformat() if user.created_at else None,
    )


@router.get("/stats", response_model=AdminStatsResponse)
async def admin_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> AdminStatsResponse:
    """Gibt Aggregationszahlen fuer das Admin-Dashboard zurueck."""
    await _set_admin_rls(db, admin)

    async def count(model: type) -> int:
        result = await db.execute(select(model).where(getattr(model, "deleted_at").is_(None)))
        return len(result.scalars().all())

    vermieter_count = await db.scalar(select(func.count()).select_from(select(User).where(User.role == "vermieter").subquery()))
    mieter_count = await db.scalar(select(func.count()).select_from(select(User).where(User.role == "mieter").subquery()))
    objekte_count = await count(Objekt)
    einheiten_count = await count(Einheit)

    return AdminStatsResponse(
        vermieter_count=vermieter_count or 0,
        mieter_count=mieter_count or 0,
        objekte_count=objekte_count,
        einheiten_count=einheiten_count,
    )


@router.get("/users", response_model=AdminUserListResponse)
async def admin_list_users(
    role: str | None = None,
    search: str | None = None,
    active_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> AdminUserListResponse:
    """Listet alle Nutzer auf (Vermieter/Mieter/Admins), mit Filter und Suche."""
    await _set_admin_rls(db, admin)

    query = select(User).where(User.deleted_at.is_(None))
    if role:
        query = query.where(User.role == role)
    if active_only:
        query = query.where(User.is_active.is_(True))
    if search:
        pattern = f"%{search}%"
        query = query.where(
            (User.email.ilike(pattern))
            | (User.full_name.ilike(pattern))
            | (User.firma.ilike(pattern))
        )

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0

    query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()

    return AdminUserListResponse(
        items=[_user_to_admin_response(u) for u in users],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/users", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(csrf_protect)])
async def admin_create_user(
    request: Request,
    data: AdminUserCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> AdminUserResponse:
    """Erstellt einen neuen Vermieter- oder Mieter-Account."""
    await _set_admin_rls(db, admin)

    if data.role not in {"vermieter", "mieter"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rolle muss 'vermieter' oder 'mieter' sein")

    if data.role == "mieter" and not data.vermieter_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mieter benoetigen vermieter_id")

    if data.vermieter_id:
        vermieter = await db.get(User, data.vermieter_id)
        if vermieter is None or vermieter.role != "vermieter" or vermieter.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ungueltiger Vermieter")

    existing = await _get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-Mail-Adresse bereits registriert")

    if data.role == "vermieter":
        user = await register(
            db,
            email=data.email,
            password=data.password,
            full_name=data.full_name,
            consent_text="Admin erstellt Account via /admin/users.",
        )
        # register setzt RLS auf neuen Vermieter; Admin-RLS wiederherstellen
        await _set_admin_rls(db, admin)
    else:
        user = User(
            email=data.email.lower().strip(),
            password_hash=hash_password(data.password),
            full_name=data.full_name.strip(),
            role="mieter",
            is_active=True,
            email_verified=False,
            vermieter_id=data.vermieter_id,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)

    await audit_log(
        db,
        user_id=admin.id,
        vermieter_id=user.vermieter_id if user.role == "mieter" else user.id,
        action="admin_create_user",
        entity="users",
        entity_id=user.id,
        details={"target_role": user.role, "email": user.email},
        ip=_get_client_ip(request),
        risk_level="hoch",
    )
    await db.commit()

    return _user_to_admin_response(user)


@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def admin_get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> AdminUserResponse:
    """Gibt Details eines einzelnen Nutzers zurueck."""
    await _set_admin_rls(db, admin)
    user = await db.get(User, user_id)
    if user is None or user.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutzer nicht gefunden")
    return _user_to_admin_response(user)


@router.patch("/users/{user_id}", response_model=AdminUserResponse, dependencies=[Depends(csrf_protect)])
async def admin_update_user(
    user_id: int,
    request: Request,
    data: AdminUserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> AdminUserResponse:
    """Aktualisiert Rolle/Status/Name eines Nutzers."""
    await _set_admin_rls(db, admin)
    user = await db.get(User, user_id)
    if user is None or user.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutzer nicht gefunden")

    if data.role is not None:
        if data.role not in {"admin", "vermieter", "mieter"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ungueltige Rolle")
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.full_name is not None:
        user.full_name = data.full_name.strip()
    if data.phone is not None:
        user.phone = data.phone.strip() or None
    if data.vermieter_id is not None and user.role == "mieter":
        vermieter = await db.get(User, data.vermieter_id)
        if vermieter is None or vermieter.role != "vermieter" or vermieter.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ungueltiger Vermieter")
        user.vermieter_id = data.vermieter_id

    await audit_log(
        db,
        user_id=admin.id,
        vermieter_id=user.vermieter_id if user.role == "mieter" else user.id,
        action="admin_update_user",
        entity="users",
        entity_id=user.id,
        details=data.model_dump(exclude_unset=True),
        ip=_get_client_ip(request),
        risk_level="hoch",
    )
    await db.commit()
    await db.refresh(user)

    return _user_to_admin_response(user)


@router.post("/users/{user_id}/reset-password", response_model=dict[str, Any], dependencies=[Depends(csrf_protect)])
async def admin_reset_password(
    user_id: int,
    request: Request,
    data: PasswordResetAdminRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Setzt das Passwort eines Nutzers direkt zurueck."""
    await _set_admin_rls(db, admin)
    user = await db.get(User, user_id)
    if user is None or user.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutzer nicht gefunden")

    user.password_hash = hash_password(data.new_password)
    user.failed_login_count = 0
    user.locked_until = None

    await audit_log(
        db,
        user_id=admin.id,
        vermieter_id=user.vermieter_id if user.role == "mieter" else user.id,
        action="admin_reset_password",
        entity="users",
        entity_id=user.id,
        details={},
        ip=_get_client_ip(request),
        risk_level="hoch",
    )
    await db.commit()

    return {"success": True, "message": "Passwort zurueckgesetzt"}


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(csrf_protect)])
async def admin_delete_user(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> None:
    """Soft-Delete eines Nutzers."""
    await _set_admin_rls(db, admin)
    user = await db.get(User, user_id)
    if user is None or user.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutzer nicht gefunden")
    if user.id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Eigener Account kann nicht geloescht werden")

    user.is_active = False
    user.deleted_at = user.updated_at  # type: ignore[assignment]

    await audit_log(
        db,
        user_id=admin.id,
        vermieter_id=user.vermieter_id if user.role == "mieter" else user.id,
        action="admin_delete_user",
        entity="users",
        entity_id=user.id,
        details={"email": user.email, "role": user.role},
        ip=_get_client_ip(request),
        risk_level="hoch",
    )
    await db.commit()


@router.get("/objekte", response_model=AdminObjektListResponse)
async def admin_list_objekte(
    vermieter_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> AdminObjektListResponse:
    """Listet alle Objekte systemweit auf."""
    await _set_admin_rls(db, admin)
    objekte = await list_objekte(db, vermieter_id=vermieter_id)
    total = len(objekte)
    paginated = objekte[skip : skip + limit]
    return AdminObjektListResponse(
        items=[await map_objekt_response(db, o) for o in paginated],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/einheiten", response_model=AdminEinheitListResponse)
async def admin_list_einheiten(
    objekt_id: int | None = None,
    vermieter_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> AdminEinheitListResponse:
    """Listet alle Einheiten systemweit auf."""
    await _set_admin_rls(db, admin)
    einheiten = await list_einheiten(db, vermieter_id=vermieter_id, objekt_id=objekt_id)
    total = len(einheiten)
    paginated = einheiten[skip : skip + limit]
    return AdminEinheitListResponse(
        items=[await map_einheit_response(db, e) for e in paginated],
        total=total,
        skip=skip,
        limit=limit,
    )
