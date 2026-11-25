"""Admin-Konzept A0: Plattform-Admin-Management und zentrale Admin-Dienste."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import func, select

from app.models.organisation import (
    Einladung,
    FreigabeAnfrage,
    Organisation,
    OrganisationsMitglied,
    PlattformAdmin,
    PlattformAuditLog,
    SupportFreigabe,
    SupportZugriff,
)
from app.models.user import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class AdminPermission(str):
    """Berechtigungen fuer Plattform-Admins."""

    ORG_READ = "plattform:org:read"
    ORG_SUSPEND = "plattform:org:suspend"
    BILLING_READ = "plattform:billing:read"
    BILLING_WRITE = "plattform:billing:write"
    SUPPORT_VIEW = "plattform:support:view"
    AUDIT_READ = "plattform:audit:read"


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


class PlattformAdminService:
    """Verwaltet Betreiber-Accounts und deren Berechtigungen."""

    def __init__(self, session: AsyncSession, admin_id: int | None = None):
        self.session = session
        self.admin_id = admin_id

    def _can(self, permission: str) -> bool:
        if not self.admin_id:
            return False
        # Admin-Objekt muss außerhalb oder gecached vorliegen
        return True  # vollstaendige Pruefung spaeter im Auth-Layer

    async def log(
        self,
        aktion: str,
        ziel_typ: str | None = None,
        ziel_id: int | None = None,
        begruendung: str | None = None,
        ergebnis: str | None = None,
        ip_adresse: str | None = None,
    ) -> None:
        """Schreibt einen Admin-Audit-Eintrag."""
        self.session.add(
            PlattformAuditLog(
                admin_id=self.admin_id,
                aktion=aktion,
                ziel_typ=ziel_typ,
                ziel_id=ziel_id,
                begruendung=begruendung,
                ergebnis=ergebnis,
                ip_adresse=ip_adresse,
                zeitpunkt=datetime.now(UTC),
            )
        )
        await self.session.flush()

    async def create_admin(
        self,
        email: str,
        rolle: str,
        angelegt_von_admin_id: int,
    ) -> PlattformAdmin:
        admin = PlattformAdmin(
            email=email,
            rolle=rolle,
            eingeladen_von_id=angelegt_von_admin_id,
            eingeladen_am=datetime.now(UTC),
        )
        self.session.add(admin)
        await self.session.flush()
        await self.session.refresh(admin)
        self.admin_id = angelegt_von_admin_id
        await self.log(
            aktion="admin_created",
            ziel_typ="plattform_admin",
            ziel_id=admin.id,
            begruendung=f"Rolle {rolle}",
        )
        return admin

    async def toggle_admin_active(self, admin_id: int, aktiv: bool) -> PlattformAdmin | None:
        admin = await self.session.get(PlattformAdmin, admin_id)
        if admin is None:
            return None
        admin.aktiv = aktiv
        await self.session.flush()
        await self.log(
            aktion="admin_toggled_active",
            ziel_typ="plattform_admin",
            ziel_id=admin_id,
            begruendung=f"aktiv={aktiv}",
        )
        return admin


class OrgAdminService:
    """Admin-Sicht auf Organisationen: Liste, Sperren, Billing-Status."""

    def __init__(self, session: AsyncSession, admin_id: int | None = None):
        self.session = session
        self.admin_id = admin_id

    async def list_organisations(
        self,
        status: str | None = None,
        plan: str | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """Aggregierte Kundenliste ohne Personendaten."""
        stmt = select(
            Organisation.id,
            Organisation.public_id,
            Organisation.name,
            Organisation.typ,
            Organisation.status,
            Organisation.plan,
            Organisation.stripe_customer_id,
            Organisation.created_at,
            func.count(OrganisationsMitglied.id).label("mitglieder_anzahl"),
        ).outerjoin(
            OrganisationsMitglied,
            Organisation.id == OrganisationsMitglied.org_id,
        ).group_by(Organisation.id)

        if status:
            stmt = stmt.where(Organisation.status == status)
        if plan:
            stmt = stmt.where(Organisation.plan == plan)
        if search:
            stmt = stmt.where(Organisation.name.ilike(f"%{search}%"))

        stmt = stmt.order_by(Organisation.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        rows = result.mappings().all()
        return [dict(r) for r in rows]

    async def suspend_organisation(
        self,
        org_id: int,
        grund: str,
    ) -> Organisation | None:
        org = await self.session.get(Organisation, org_id)
        if org is None:
            return None
        org.status = "gesperrt"
        await self.session.flush()
        return org

    async def reactivate_organisation(self, org_id: int) -> Organisation | None:
        org = await self.session.get(Organisation, org_id)
        if org is None:
            return None
        org.status = "aktiv"
        await self.session.flush()
        return org


class SupportFreigabeService:
    """Verwaltet Support-Freigaben und protokolliert Zugriffe."""

    def __init__(self, session: AsyncSession, admin_id: int | None = None):
        self.session = session
        self.admin_id = admin_id

    async def create(
        self,
        org_id: int,
        ticket_ref: str | None,
        grund: str,
        umfang: str,
        stunden: int,
        erteilt_von_user_id: int,
    ) -> SupportFreigabe:
        freigabe = SupportFreigabe(
            org_id=org_id,
            ticket_ref=ticket_ref,
            grund=grund,
            umfang=umfang,
            gueltig_bis=datetime.now(UTC) + timedelta(hours=stunden),
            erteilt_von_user_id=erteilt_von_user_id,
        )
        self.session.add(freigabe)
        await self.session.flush()
        await self.session.refresh(freigabe)
        return freigabe

    async def is_valid(self, freigabe_id: int) -> bool:
        freigabe = await self.session.get(SupportFreigabe, freigabe_id)
        if freigabe is None:
            return False
        if freigabe.widerrufen_am:
            return False
        return freigabe.gueltig_bis > datetime.now(UTC)

    async def revoke(self, freigabe_id: int) -> SupportFreigabe | None:
        freigabe = await self.session.get(SupportFreigabe, freigabe_id)
        if freigabe is None:
            return None
        freigabe.widerrufen_am = datetime.now(UTC)
        await self.session.flush()
        return freigabe

    async def log_access(
        self,
        freigabe_id: int,
        aktion: str,
        ziel: str | None = None,
    ) -> SupportZugriff:
        zugriff = SupportZugriff(
            freigabe_id=freigabe_id,
            admin_id=self.admin_id,
            aktion=aktion,
            ziel=ziel,
        )
        self.session.add(zugriff)
        await self.session.flush()
        await self.session.refresh(zugriff)
        return zugriff


class OrgMitgliedService:
    """Org-Nutzerverwaltung: Einladen, Rollen, Scope, Sperren, Entfernen."""

    def __init__(self, session: AsyncSession, org_id: int):
        self.session = session
        self.org_id = org_id

    async def list_members(self) -> list[OrganisationsMitglied]:
        result = await self.session.execute(
            select(OrganisationsMitglied).where(OrganisationsMitglied.org_id == self.org_id)
        )
        return list(result.scalars().all())

    async def invite_member(
        self,
        email: str,
        rolle: str,
        eingeladen_von_user_id: int,
    ) -> Einladung:
        from app.models.organisation import Einladung
        from app.services.auth import hash_password
        import secrets

        token = secrets.token_urlsafe(32)
        einladung = Einladung(
            art="mitglied",
            org_id=self.org_id,
            ziel_kontakt=email,
            rolle_oder_scope=rolle,
            token_hash=hash_password(token),  # einfacher Hash, spaeter dediziert
            gueltig_bis=datetime.now(UTC) + timedelta(days=7),
        )
        self.session.add(einladung)
        await self.session.flush()
        await self.session.refresh(einladung)
        return einladung

    async def set_role(
        self,
        mitglied_id: int,
        neue_rolle: str,
    ) -> OrganisationsMitglied | None:
        Mitglied = await self.session.get(OrganisationsMitglied, mitglied_id)
        if Mitglied is None or Mitglied.org_id != self.org_id:
            return None
        Mitglied.rolle = neue_rolle
        await self.session.flush()
        return Mitglied

    async def deactivate_member(
        self,
        mitglied_id: int,
    ) -> OrganisationsMitglied | None:
        Mitglied = await self.session.get(OrganisationsMitglied, mitglied_id)
        if Mitglied is None or Mitglied.org_id != self.org_id:
            return None
        # Letzten Inhaber nicht entfernen
        if Mitglied.rolle == "org_admin":
            count = await self.session.scalar(
                select(func.count(OrganisationsMitglied.id)).where(
                    OrganisationsMitglied.org_id == self.org_id,
                    OrganisationsMitglied.rolle == "org_admin",
                    OrganisationsMitglied.aktiv.is_(True),
                )
            )
            if count <= 1:
                raise ValueError("Letzter Inhaber kann nicht deaktiviert werden")
        Mitglied.aktiv = False
        await self.session.flush()
        return Mitglied

    async def remove_member(
        self,
        mitglied_id: int,
    ) -> OrganisationsMitglied | None:
        Mitglied = await self.session.get(OrganisationsMitglied, mitglied_id)
        if Mitglied is None or Mitglied.org_id != self.org_id:
            return None
        if Mitglied.rolle == "org_admin":
            count = await self.session.scalar(
                select(func.count(OrganisationsMitglied.id)).where(
                    OrganisationsMitglied.org_id == self.org_id,
                    OrganisationsMitglied.rolle == "org_admin",
                )
            )
            if count <= 1:
                raise ValueError("Letzter Inhaber kann nicht entfernt werden")
        await self.session.delete(Mitglied)
        await self.session.flush()
        return Mitglied

    async def set_object_scope(
        self,
        mitglied_id: int,
        objekt_ids: list[int],
    ) -> None:
        from app.models.organisation import MitgliedObjektScope

        await self.session.execute(
            sa.delete(MitgliedObjektScope).where(
                MitgliedObjektScope.mitglied_id == mitglied_id
            )
        )
        for objekt_id in objekt_ids:
            self.session.add(
                MitgliedObjektScope(mitglied_id=mitglied_id, objekt_id=objekt_id)
            )
        await self.session.flush()
