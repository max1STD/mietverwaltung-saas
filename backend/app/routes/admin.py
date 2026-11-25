"""Admin-Routen — zentrale Verwaltung fuer Vermieter, Mieter, Objekte, Einheiten."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import func, select
from sqlalchemy import select as sa_select
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

from app.services.admin import (
    AdminPermission,
    OrgAdminService,
    OrgMitgliedService,
    OrgRichtlinienService,
    OrgRolleService,
    PlattformAdminService,
    SupportFreigabeService,
    VertretungsService,
    VierAugenService,
)

router = APIRouter()
platform_router = APIRouter(prefix="/platform", tags=["platform-admin"])


class AdminAuthContext(BaseModel):
    admin_id: int
    rolle: str


class AdminCreateRequest(BaseModel):
    email: EmailStr
    rolle: str


class OrgStatusUpdateRequest(BaseModel):
    status: str  # aktiv | gesperrt | geloescht


class OrgListItem(BaseModel):
    id: int
    public_id: int
    name: str
    status: str
    plan: str
    einheiten_count: int
    mitglieder_count: int


class MemberInviteRequest(BaseModel):
    email: EmailStr
    rolle: str


class MemberRoleUpdateRequest(BaseModel):
    rolle: str


class RichtlinieUpdateRequest(BaseModel):
    mfa_pflicht: bool | None = None
    mfa_pflicht_rollen: str | None = None
    session_dauer_stunden: int | None = None
    inaktivitaet_minuten: int | None = None
    vier_augen_aktionen: str | None = None
    massenexport_benachrichtigt: bool | None = None
    ip_freigabe: str | None = None
    sso_erlaubt: bool | None = None
    sso_idp_metadata_url: str | None = None
    zwei_fa_erforderlich: bool | None = None
    erweiterte_berichte: bool | None = None
    compliance_center_aktiv: bool | None = None


class VertretungCreateRequest(BaseModel):
    von_mitglied_id: int
    an_mitglied_id: int
    rolle: str | None = None
    objekt_ids: list[int] | None = None
    von: datetime
    bis: datetime


class VierAugenRequest(BaseModel):
    aktion: str
    ausfuehren_ab: datetime
    ablauf: datetime


class VierAugenConfirmRequest(BaseModel):
    bestaetigt_von_admin_id: int


async def require_admin(
    x_admin_token: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> AdminAuthContext:
    """Platzhalter-Auth fuer den Start. Ersetzt spaeter Passkey-Login."""
    if not x_admin_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin-Token fehlt.")
    try:
        admin_id_str, rolle = x_admin_token.split(":", 1)
        admin_id = int(admin_id_str)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ungueltiger Token.") from exc
    service = PlattformAdminService(db)
    admin = await service.get_by_id(admin_id)
    if admin is None or not admin.aktiv or admin.rolle != rolle:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ungueltiger Admin.")
    return AdminAuthContext(admin_id=admin.id, rolle=admin.rolle)


def require_permission(permission: str):
    async def _check(
        ctx: AdminAuthContext = Depends(require_admin),
    ) -> AdminAuthContext:
        perms = ROLE_PERMISSIONS.get(ctx.rolle, set())
        if permission not in perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Berechtigung {permission} erforderlich.",
            )
        return ctx
    return _check


ROLE_PERMISSIONS: dict[str, set[str]] = {
    "owner": {
        AdminPermission.ORG_READ,
        AdminPermission.ORG_SUSPEND,
        AdminPermission.BILLING_READ,
        AdminPermission.BILLING_WRITE,
        AdminPermission.SUPPORT_VIEW,
        AdminPermission.AUDIT_READ,
    },
    "support": {
        AdminPermission.ORG_READ,
        AdminPermission.BILLING_READ,
        AdminPermission.SUPPORT_VIEW,
    },
    "billing": {
        AdminPermission.ORG_READ,
        AdminPermission.BILLING_READ,
        AdminPermission.BILLING_WRITE,
    },
    "compliance": {
        AdminPermission.ORG_READ,
        AdminPermission.AUDIT_READ,
    },
    "ops": {
        AdminPermission.ORG_READ,
        AdminPermission.AUDIT_READ,
    },
}


@platform_router.post("/admins", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_admin(
    req: AdminCreateRequest,
    ctx: AdminAuthContext = Depends(require_permission({})),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = PlattformAdminService(db, admin_id=ctx.admin_id)
    admin = await service.create_admin(req.email, req.rolle, ctx.admin_id)
    return {"id": admin.id, "email": admin.email, "rolle": admin.rolle}


@platform_router.get("/orgs", response_model=list[OrgListItem])
async def list_organisations(
    ctx: AdminAuthContext = Depends(require_permission(AdminPermission.ORG_READ)),
    db: AsyncSession = Depends(get_db),
) -> list[OrgListItem]:
    service = OrgAdminService(db)
    rows = await service.list_organisations(limit=50)
    return [
        OrgListItem(
            id=r["id"],
            public_id=r["public_id"],
            name=r["name"],
            status=r["status"],
            plan=r["plan"],
            einheiten_count=r.get("mitglieder_anzahl", 0),
            mitglieder_count=r.get("mitglieder_anzahl", 0),
        )
        for r in rows
    ]


@platform_router.patch("/orgs/{org_id}/status", response_model=dict)
async def update_org_status(
    org_id: int,
    req: OrgStatusUpdateRequest,
    ctx: AdminAuthContext = Depends(require_permission(AdminPermission.ORG_SUSPEND)),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = OrgAdminService(db, actor_id=ctx.admin_id)
    if req.status == "aktiv":
        org = await service.reactivate_organisation(org_id)
    elif req.status == "gesperrt":
        org = await service.suspend_organisation(org_id, "")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ungueltiger Status.")
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation nicht gefunden.")
    return {"id": org.id, "status": org.status}


@platform_router.get("/orgs/{org_id}/members")
async def list_org_members(
    org_id: int,
    ctx: AdminAuthContext = Depends(require_permission(AdminPermission.ORG_READ)),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    service = OrgMitgliedService(db, org_id)
    members = await service.list_members()
    return [
        {
            "id": m.id,
            "user_id": m.user_id,
            "rolle": m.rolle,
            "aktiv": m.aktiv,
        }
        for m in members
    ]


@platform_router.post("/orgs/{org_id}/members/invite", response_model=dict)
async def invite_org_member(
    org_id: int,
    req: MemberInviteRequest,
    ctx: AdminAuthContext = Depends(require_permission({})),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = OrgMitgliedService(db, org_id)
    einladung = await service.invite_member(req.email, req.rolle, ctx.admin_id)
    return {"id": einladung.id, "token": "per-email", "gueltig_bis": einladung.gueltig_bis}


@platform_router.patch("/orgs/{org_id}/members/{mitglied_id}/role", response_model=dict)
async def set_member_role(
    org_id: int,
    mitglied_id: int,
    req: MemberRoleUpdateRequest,
    ctx: AdminAuthContext = Depends(require_permission({})),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = OrgMitgliedService(db, org_id)
    Mitglied = await service.set_role(mitglied_id, req.rolle)
    if Mitglied is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rolle konnte nicht geaendert werden.")
    return {"id": Mitglied.id, "rolle": Mitglied.rolle}


@platform_router.post("/orgs/{org_id}/members/{mitglied_id}/deactivate", response_model=dict)
async def deactivate_member(
    org_id: int,
    mitglied_id: int,
    ctx: AdminAuthContext = Depends(require_permission({})),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = OrgMitgliedService(db, org_id)
    Mitglied = await service.deactivate_member(mitglied_id)
    if Mitglied is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mitarbeiter konnte nicht deaktiviert werden.")
    return {"id": Mitglied.id, "aktiv": Mitglied.aktiv}


@platform_router.get("/audit", response_model=list[dict])
async def list_audit_log(
    ctx: AdminAuthContext = Depends(require_permission({})),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
) -> list[dict]:
    stmt = select(PlattformAuditLog).order_by(PlattformAuditLog.zeitpunkt.desc()).limit(limit)
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [
        {
            "id": r.id,
            "admin_id": r.admin_id,
            "aktion": r.aktion,
            "ziel_typ": r.ziel_typ,
            "ziel_id": r.ziel_id,
            "zeitpunkt": r.zeitpunkt,
        }
        for r in rows
    ]


@platform_router.post("/support-freigaben", response_model=dict)
async def create_support_freigabe(
    org_id: int,
    grund: str,
    umfang: str,
    stunden: int = 24,
    ctx: AdminAuthContext = Depends(require_permission({})),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = SupportFreigabeService(db, admin_id=ctx.admin_id)
    sf = await service.create(org_id, None, grund, umfang, stunden, ctx.admin_id)
    return {"id": sf.id, "gueltig_bis": sf.gueltig_bis}




@platform_router.get("/orgs/{org_id}/richtlinien", response_model=dict)
async def get_org_richtlinien(
    org_id: int,
    ctx: AdminAuthContext = Depends(require_permission(AdminPermission.ORG_READ)),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = OrgRichtlinienService(db, org_id)
    r = await service.get_or_create()
    return {
        "org_id": r.org_id,
        "mfa_pflicht": r.mfa_pflicht,
        "mfa_pflicht_rollen": r.mfa_pflicht_rollen,
        "session_dauer_stunden": r.session_dauer_stunden,
        "inaktivitaet_minuten": r.inaktivitaet_minuten,
        "vier_augen_aktionen": r.vier_augen_aktionen,
        "massenexport_benachrichtigt": r.massenexport_benachrichtigt,
        "ip_freigabe": r.ip_freigabe,
        "sso_erlaubt": r.sso_erlaubt,
        "sso_idp_metadata_url": r.sso_idp_metadata_url,
        "zwei_fa_erforderlich": r.zwei_fa_erforderlich,
        "erweiterte_berichte": r.erweiterte_berichte,
        "compliance_center_aktiv": r.compliance_center_aktiv,
    }


@platform_router.patch("/orgs/{org_id}/richtlinien", response_model=dict)
async def update_org_richtlinien(
    org_id: int,
    req: RichtlinieUpdateRequest,
    ctx: AdminAuthContext = Depends(require_permission(AdminPermission.ORG_SUSPEND)),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = OrgRichtlinienService(db, org_id)
    r = await service.update(**req.model_dump(exclude_unset=True))
    return {"org_id": r.org_id, "updated": True}


@platform_router.post("/orgs/{org_id}/vertretungen", response_model=dict)
async def create_vertretung(
    org_id: int,
    req: VertretungCreateRequest,
    ctx: AdminAuthContext = Depends(require_permission(AdminPermission.ORG_SUSPEND)),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = VertretungsService(db, org_id)
    v = await service.create(
        req.von_mitglied_id,
        req.an_mitglied_id,
        req.rolle,
        req.objekt_ids,
        req.von,
        req.bis,
    )
    return {"id": v.id, "von": v.von, "bis": v.bis}


@platform_router.get("/orgs/{org_id}/vertretungen", response_model=list[dict])
async def list_vertretungen(
    org_id: int,
    ctx: AdminAuthContext = Depends(require_permission(AdminPermission.ORG_READ)),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    service = VertretungsService(db, org_id)
    rows = await service.list_active()
    return [{"id": r.id, "von_mitglied_id": r.von_mitglied_id, "an_mitglied_id": r.an_mitglied_id, "bis": r.bis} for r in rows]


@platform_router.post("/freigabe-anfragen", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_vier_augen_anfrage(
    req: VierAugenRequest,
    ctx: AdminAuthContext = Depends(require_permission(AdminPermission.ORG_SUSPEND)),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = VierAugenService(db, admin_id=ctx.admin_id)
    fa = await service.create(req.aktion, None, req.ausfuehren_ab, req.ablauf)
    return {"id": fa.id, "status": fa.status, "ausfuehren_ab": fa.ausfuehren_ab}


@platform_router.post("/freigabe-anfragen/{anfrage_id}/confirm", response_model=dict)
async def confirm_vier_augen_anfrage(
    anfrage_id: int,
    req: VierAugenConfirmRequest,
    ctx: AdminAuthContext = Depends(require_permission(AdminPermission.ORG_SUSPEND)),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = VierAugenService(db)
    fa = await service.confirm(anfrage_id, req.bestaetigt_von_admin_id)
    if fa is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bestaetigung nicht moeglich.")
    return {"id": fa.id, "status": fa.status}





@platform_router.post("/orgs/{org_id}/rollen", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_org_rolle(
    org_id: int,
    name: str,
    berechtigungen: list[str],
    ctx: AdminAuthContext = Depends(require_permission(AdminPermission.ORG_SUSPEND)),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = OrgRolleService(db, org_id)
    rolle = await service.create(name, berechtigungen)
    return {"id": rolle.id, "name": rolle.name, "berechtigungen": rolle.berechtigungen}


@platform_router.get("/orgs/{org_id}/rollen", response_model=list[dict])
async def list_org_rollen(
    org_id: int,
    ctx: AdminAuthContext = Depends(require_permission(AdminPermission.ORG_READ)),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    service = OrgRolleService(db, org_id)
    rows = await service.list()
    return [{"id": r.id, "name": r.name, "berechtigungen": r.berechtigungen} for r in rows]


@platform_router.get("/sicherheits-ereignisse", response_model=list[dict])
async def list_sicherheits_ereignisse(
    ctx: AdminAuthContext = Depends(require_permission(AdminPermission.AUDIT_READ)),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    from app.models.organisation import SicherheitsEreignis
    stmt = sa_select(SicherheitsEreignis).order_by(SicherheitsEreignis.zeitpunkt.desc()).limit(50)
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [{"id": r.id, "art": r.art, "ernst": r.ernst, "details": r.details, "zeitpunkt": r.zeitpunkt} for r in rows]



router.include_router(platform_router)


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
