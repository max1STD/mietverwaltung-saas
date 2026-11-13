"""DSGVO-Endpunkte: Auskunft (Art. 15), Export (Art. 20), Löschung (Art. 17/21)."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import _get_client_ip, csrf_protect as auth_csrf, get_current_user
from app.models.abrechnungen import Abrechnung  # noqa: F401
from app.models.einwilligung import Einwilligung
from app.models.mietvertraege import Mietvertrag  # noqa: F401
from app.models.session import UserSession
from app.models.user import User
from app.schemas.auth import DsgvoDeletionResponse, DsgvoExportResponse, DsgvoOverviewResponse
from app.services.crypto import decrypt_value
from app.services.jwt import clear_auth_cookies

router = APIRouter()


def _user_export_dict(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "phone": user.phone,
        "email_verified": user.email_verified,
        "is_active": user.is_active,
        "dsgvo_consent_at": user.dsgvo_consent_at.isoformat() if user.dsgvo_consent_at else None,
        "firma": user.firma,
        "steuernr": decrypt_value(user.steuernr_enc) if user.steuernr_enc else None,
        "rechnungs_adresse": {
            "strasse": user.rechnungs_strasse,
            "hausnr": user.rechnungs_hausnr,
            "plz": user.rechnungs_plz,
            "ort": user.rechnungs_ort,
        },
        "ust_id": user.ust_id,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


async def _gather_counts(db: AsyncSession, user: User) -> dict:
    """Ermittelt die Anzahl der vorhandenen Datensätze pro Kategorie."""
    from sqlalchemy import func

    sessions = await db.scalar(
        select(func.count(UserSession.id)).where(UserSession.user_id == user.id)
    )
    einwilligungen = await db.scalar(
        select(func.count(Einwilligung.id)).where(Einwilligung.user_id == user.id)
    )
    # Audit-Logs zählen (RLS limitiert sichtbare Zeilen auf User/Vermieter).
    from app.models.audit import AuditLog

    audit_logs = await db.scalar(
        select(func.count(AuditLog.id)).where(AuditLog.user_id == user.id)
    )

    # Mietverträge und Abrechnungen zählen (nur für Vermieter sichtbar).
    from app.models.mietvertraege import Mietvertrag
    from app.models.abrechnungen import Abrechnung

    mietvertraege = 0
    abrechnungen = 0
    if user.role == "vermieter":
        mietvertraege = await db.scalar(
            select(func.count(Mietvertrag.id)).where(Mietvertrag.vermieter_id == user.id)
        )
        abrechnungen = await db.scalar(
            select(func.count(Abrechnung.id)).where(Abrechnung.vermieter_id == user.id)
        )
    return {
        "sessions_count": sessions or 0,
        "einwilligungen_count": einwilligungen or 0,
        "audit_logs_count": audit_logs or 0,
        "mietvertraege_count": mietvertraege,
        "abrechnungen_count": abrechnungen,
    }


async def _retention_blockers(db: AsyncSession, user: User) -> list[dict]:
    """Prüft Aufbewahrungsfristen und gibt blockierende Datensätze zurück."""
    blockers: list[dict] = []
    now = datetime.now(UTC)

    # Mietvertragsdaten: 10 Jahre nach Mietbeginn (§147 AO)
    from app.models.mietvertraege import Mietvertrag

    if user.role == "vermieter":
        ten_years_ago = now - timedelta(days=365 * 10)
        result = await db.execute(
            select(Mietvertrag).where(
                Mietvertrag.vermieter_id == user.id,
                Mietvertrag.mietbeginn >= ten_years_ago.date(),
            )
        )
        for mv in result.scalars().all():
            blockers.append(
                {
                    "type": "mietvertrag",
                    "id": mv.id,
                    "reason": "Aufbewahrung Mietvertragsdaten 10 Jahre (§147 AO)",
                    "retention_until": (mv.mietbeginn + timedelta(days=365 * 10)).isoformat(),
                }
            )

        # Abrechnungen: 6 Jahre nach Abrechnungsjahr
        from app.models.abrechnungen import Abrechnung

        six_years_ago = now - timedelta(days=365 * 6)
        result = await db.execute(
            select(Abrechnung).where(
                Abrechnung.vermieter_id == user.id,
                Abrechnung.jahr >= six_years_ago.year,
            )
        )
        for ab in result.scalars().all():
            blockers.append(
                {
                    "type": "abrechnung",
                    "id": ab.id,
                    "reason": "Aufbewahrung Abrechnungen 6 Jahre",
                    "retention_until": f"{ab.jahr + 6}-12-31",
                }
            )

    return blockers


@router.get("/overview", response_model=DsgvoOverviewResponse)
async def dsgvo_overview(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DsgvoOverviewResponse:
    """Übersicht: Welche Daten haben wir über den User?"""
    counts = await _gather_counts(db, user)
    return DsgvoOverviewResponse(
        user=_user_export_dict(user),
        sessions_count=counts["sessions_count"],
        einwilligungen_count=counts["einwilligungen_count"],
        audit_logs_count=counts["audit_logs_count"],
        mietvertraege_count=counts["mietvertraege_count"],
        abrechnungen_count=counts["abrechnungen_count"],
    )


@router.get("/export", response_model=DsgvoExportResponse)
async def dsgvo_export(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DsgvoExportResponse:
    """Exportiert alle personenbezogenen Daten als JSON (Art. 15/20 DSGVO)."""
    counts = await _gather_counts(db, user)
    einwilligungen = await db.execute(
        select(Einwilligung).where(Einwilligung.user_id == user.id)
    )
    from app.models.audit import AuditLog

    audit_logs = await db.execute(
        select(AuditLog).where(AuditLog.user_id == user.id)
    )
    sessions = await db.execute(
        select(UserSession).where(UserSession.user_id == user.id)
    )

    data = {
        "user": _user_export_dict(user),
        "einwilligungen": [
            {
                "purpose": e.purpose,
                "version": e.version,
                "consent_text": e.consent_text,
                "consented_at": e.consented_at.isoformat() if e.consented_at else None,
                "withdrawn_at": e.withdrawn_at.isoformat() if e.withdrawn_at else None,
            }
            for e in einwilligungen.scalars().all()
        ],
        "audit_logs": [
            {
                "action": a.action,
                "risk_level": a.risk_level,
                "details": a.details,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in audit_logs.scalars().all()
        ],
        "sessions": [
            {
                "device_info": s.device_info,
                "ip_address": s.ip_address,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "expires_at": s.expires_at.isoformat() if s.expires_at else None,
                "revoked_at": s.revoked_at.isoformat() if s.revoked_at else None,
            }
            for s in sessions.scalars().all()
        ],
        "counts": counts,
    }
    return DsgvoExportResponse(
        export_format="json",
        exported_at=datetime.now(UTC).isoformat(),
        data=data,
    )


@router.delete("/delete", response_model=DsgvoDeletionResponse, dependencies=[Depends(auth_csrf)])
async def dsgvo_delete(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DsgvoDeletionResponse:
    """Löschantrag gemäß Art. 17 DSGVO — nur wenn keine Aufbewahrungsfrist greift."""
    blockers = await _retention_blockers(db, user)
    if blockers:
        return DsgvoDeletionResponse(
            deleted=False,
            message="Löschung aktuell nicht möglich: Aufbewahrungsfristen greifen.",
            retained=blockers,
        )

    # Soft-Delete des Users und Widerruf aller Sessions.
    user.deleted_at = datetime.now(UTC)
    user.is_active = False
    user.email = f"deleted.{user.id}.anonymous@localhost"
    user.full_name = "Gelöschter User"
    # Personenbezogene Vermieter-Stammdaten entfernen.
    user.phone = None
    user.firma = None
    user.steuernr_enc = None
    user.rechnungs_strasse = None
    user.rechnungs_hausnr = None
    user.rechnungs_plz = None
    user.rechnungs_ort = None
    user.ust_id = None

    await db.execute(
        select(UserSession).where(
            UserSession.user_id == user.id,
            UserSession.revoked_at.is_(None),
        )
    )
    from sqlalchemy import update

    await db.execute(
        update(UserSession)
        .where(
            UserSession.user_id == user.id,
            UserSession.revoked_at.is_(None),
        )
        .values(revoked_at=datetime.now(UTC))
    )

    from app.services.auth import _audit

    await _audit(
        db,
        user_id=user.id,
        action="deletion_request",
        vermieter_id=user.vermieter_id if user.role == "mieter" else user.id,
        ip=_get_client_ip(request),
        risk_level="hoch",
        entity="users",
        entity_id=user.id,
    )
    await db.commit()
    clear_auth_cookies(response)
    return DsgvoDeletionResponse(
        deleted=True,
        message="Account wurde zur Löschung vorgemerkt (Soft-Delete).",
        retained=None,
    )
