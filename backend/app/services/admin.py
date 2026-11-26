"""Admin-Konzept A0: Plattform-Admin-Management und zentrale Admin-Dienste."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import func, select

from app.models.organisation import (
    BetroffenenAnfrage,
    Einladung,
    FreigabeAnfrage,
    Organisation,
    OrganisationsMitglied,
    OrgRichtlinie,
    OrgRolle,
    PlattformAdmin,
    PlattformAuditLog,
    SicherheitsEreignis,
    SupportFreigabe,
    SupportZugriff,
    Vertretung,
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

    async def get_by_id(self, admin_id: int) -> PlattformAdmin | None:
        return await self.session.get(PlattformAdmin, admin_id)

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

    async def get(self, freigabe_id: int) -> SupportFreigabe | None:
        return await self.session.get(SupportFreigabe, freigabe_id)

    async def list_for_org(self, org_id: int) -> list[SupportFreigabe]:
        result = await self.session.execute(
            select(SupportFreigabe).where(SupportFreigabe.org_id == org_id).order_by(SupportFreigabe.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_read_scope(
        self,
        freigabe_id: int,
        org_id: int,
        admin_id: int,
    ) -> "DbContext":
        """Liefert einen read-only RLS-Kontext fuer gueltige Support-Freigaben."""
        from app.core.db_context import DbContext
        freigabe = await self.session.get(SupportFreigabe, freigabe_id)
        if freigabe is None or freigabe.org_id != org_id:
            raise ValueError("Freigabe nicht gefunden")
        if freigabe.widerrufen_am or freigabe.gueltig_bis <= datetime.now(UTC):
            raise ValueError("Freigabe ist nicht mehr gueltig")
        await self.log_access(freigabe_id, "read_scope", ziel=f"org:{org_id}")
        return DbContext(
            org_id=org_id,
            user_id=admin_id,
            role="support",
            support_freigabe_id=freigabe_id,
        )

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


class OrgRichtlinienService:
    """Verwaltet Sicherheitsrichtlinien, 2FA- und Session-Regeln pro Organisation (A1/A3)."""

    def __init__(self, session: AsyncSession, org_id: int):
        self.session = session
        self.org_id = org_id

    async def get_or_create(self) -> OrgRichtlinie:
        richtlinie = await self.session.get(OrgRichtlinie, self.org_id)
        if richtlinie is None:
            richtlinie = OrgRichtlinie(org_id=self.org_id)
            self.session.add(richtlinie)
            await self.session.flush()
        return richtlinie

    async def update(
        self,
        mfa_pflicht: bool | None = None,
        mfa_pflicht_rollen: str | None = None,
        session_dauer_stunden: int | None = None,
        inaktivitaet_minuten: int | None = None,
        vier_augen_aktionen: str | None = None,
        massenexport_benachrichtigt: bool | None = None,
        ip_freigabe: str | None = None,
        sso_erlaubt: bool | None = None,
        sso_idp_metadata_url: str | None = None,
        zwei_fa_erforderlich: bool | None = None,
        erweiterte_berichte: bool | None = None,
        compliance_center_aktiv: bool | None = None,
    ) -> OrgRichtlinie:
        richtlinie = await self.get_or_create()
        for attr, value in locals().items():
            if attr in {"self", "session"} or value is None:
                continue
            setattr(richtlinie, attr, value)
        await self.session.flush()
        await self.session.refresh(richtlinie)
        return richtlinie


class VertretungsService:
    """Zeitlich begrenzte Vertretungen (A1)."""

    def __init__(self, session: AsyncSession, org_id: int):
        self.session = session
        self.org_id = org_id

    async def create(
        self,
        von_mitglied_id: int,
        an_mitglied_id: int,
        rolle: str | None,
        objekt_ids: list[int] | None,
        von: datetime,
        bis: datetime,
    ) -> Vertretung:
        v = Vertretung(
            org_id=self.org_id,
            von_mitglied_id=von_mitglied_id,
            an_mitglied_id=an_mitglied_id,
            rolle=rolle,
            objekt_ids=",".join(str(x) for x in (objekt_ids or [])) if objekt_ids else None,
            von=von,
            bis=bis,
        )
        self.session.add(v)
        await self.session.flush()
        await self.session.refresh(v)
        return v

    async def list_active(self, now: datetime | None = None) -> list[Vertretung]:
        if now is None:
            now = datetime.now(UTC)
        result = await self.session.execute(
            select(Vertretung).where(
                Vertretung.org_id == self.org_id,
                Vertretung.von <= now,
                Vertretung.bis >= now,
            )
        )
        return list(result.scalars().all())

    async def revoke(self, vertretung_id: int) -> Vertretung | None:
        v = await self.session.get(Vertretung, vertretung_id)
        if v is None or v.org_id != self.org_id:
            return None
        v.bis = datetime.now(UTC)
        await self.session.flush()
        return v


class SicherheitsService:
    """Sicherheitsmeldungen und Auffaelligkeiten (A1/A2)."""

    def __init__(self, session: AsyncSession, org_id: int | None = None):
        self.session = session
        self.org_id = org_id

    async def log(
        self,
        art: str,
        details: str | None = None,
        user_id: int | None = None,
        admin_id: int | None = None,
        ernst: str = "mittel",
    ) -> SicherheitsEreignis:
        e = SicherheitsEreignis(
            org_id=self.org_id,
            art=art,
            details=details,
            user_id=user_id,
            admin_id=admin_id,
            ernst=ernst,
            zeitpunkt=datetime.now(UTC),
        )
        self.session.add(e)
        await self.session.flush()
        await self.session.refresh(e)
        return e

    async def list_unread(self) -> list[SicherheitsEreignis]:
        stmt = select(SicherheitsEreignis).where(SicherheitsEreignis.gelesen_am.is_(None))
        if self.org_id is not None:
            stmt = stmt.where(SicherheitsEreignis.org_id == self.org_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_read(self, ereignis_id: int) -> SicherheitsEreignis | None:
        e = await self.session.get(SicherheitsEreignis, ereignis_id)
        if e is None:
            return None
        if self.org_id is not None and e.org_id != self.org_id:
            return None
        e.gelesen_am = datetime.now(UTC)
        await self.session.flush()
        return e


class OrgRolleService:
    """Benutzerdefinierte Organisationsrollen (A2)."""

    def __init__(self, session: AsyncSession, org_id: int):
        self.session = session
        self.org_id = org_id

    async def create(self, name: str, berechtigungen: list[str]) -> OrgRolle:
        rolle = OrgRolle(
            org_id=self.org_id,
            name=name,
            berechtigungen=",".join(berechtigungen),
        )
        self.session.add(rolle)
        await self.session.flush()
        await self.session.refresh(rolle)
        return rolle

    async def list(self) -> list[OrgRolle]:
        result = await self.session.execute(
            select(OrgRolle).where(OrgRolle.org_id == self.org_id)
        )
        return list(result.scalars().all())

    async def get(self, rolle_id: int) -> OrgRolle | None:
        rolle = await self.session.get(OrgRolle, rolle_id)
        if rolle is None or rolle.org_id != self.org_id:
            return None
        return rolle


class BetroffenenAnfragenService:
    """DSGVO-Betroffenenanfragen mit Fristzaehler (A1/A2 Compliance-Center)."""

    def __init__(self, session: AsyncSession, org_id: int):
        self.session = session
        self.org_id = org_id

    async def create(
        self,
        art: str,
        frist_bis: datetime,
        beschreibung: str | None = None,
    ) -> BetroffenenAnfrage:
        anfrage = BetroffenenAnfrage(
            org_id=self.org_id,
            art=art,
            frist_bis=frist_bis,
            beschreibung=beschreibung,
        )
        self.session.add(anfrage)
        await self.session.flush()
        await self.session.refresh(anfrage)
        return anfrage

    async def list_open(self) -> list[BetroffenenAnfrage]:
        result = await self.session.execute(
            select(BetroffenenAnfrage).where(
                BetroffenenAnfrage.org_id == self.org_id,
                BetroffenenAnfrage.status.in_(["offen", "in_bearbeitung"]),
            ).order_by(BetroffenenAnfrage.frist_bis)
        )
        return list(result.scalars().all())

    async def update_status(
        self,
        anfrage_id: int,
        status: str,
        antwort: str | None = None,
        bearbeitet_von_id: int | None = None,
    ) -> BetroffenenAnfrage | None:
        anfrage = await self.session.get(BetroffenenAnfrage, anfrage_id)
        if anfrage is None or anfrage.org_id != self.org_id:
            return None
        anfrage.status = status
        if antwort is not None:
            anfrage.antwort = antwort
        if bearbeitet_von_id is not None:
            anfrage.bearbeitet_von_id = bearbeitet_von_id
        await self.session.flush()
        return anfrage


class VierAugenService:
    """Vier-Augen-Pruefung und Zeitsperre fuer kritische Aktionen (A2)."""

    def __init__(self, session: AsyncSession, admin_id: int | None = None):
        self.session = session
        self.admin_id = admin_id

    async def request(
        self,
        aktion: str,
        org_id: int | None,
        ausfuehren_ab: datetime,
        ablauf: datetime,
    ) -> FreigabeAnfrage:
        if self.admin_id is None:
            raise ValueError("Admin-Id erforderlich")
        fa = FreigabeAnfrage(
            org_id=org_id,
            aktion=aktion,
            angefordert_von_admin_id=self.admin_id,
            status="ausstehend",
            ausfuehren_ab=ausfuehren_ab,
            ablauf=ablauf,
        )
        self.session.add(fa)
        await self.session.flush()
        await self.session.refresh(fa)
        return fa

    async def confirm(self, anfrage_id: int, bestaetigender_admin_id: int) -> FreigabeAnfrage | None:
        fa = await self.session.get(FreigabeAnfrage, anfrage_id)
        if fa is None or fa.status != "ausstehend":
            return None
        if fa.angefordert_von_admin_id == bestaetigender_admin_id:
            raise ValueError("Selbstbestaetigung nicht erlaubt")
        fa.bestaetigt_von_admin_id = bestaetigender_admin_id
        fa.status = "bestaetigt"
        await self.session.flush()
        return fa

    async def reject(self, anfrage_id: int) -> FreigabeAnfrage | None:
        fa = await self.session.get(FreigabeAnfrage, anfrage_id)
        if fa is None or fa.status != "ausstehend":
            return None
        fa.status = "abgelehnt"
        await self.session.flush()
        return fa

    async def is_executable(self, anfrage_id: int, now: datetime | None = None) -> FreigabeAnfrage | None:
        if now is None:
            now = datetime.now(UTC)
        fa = await self.session.get(FreigabeAnfrage, anfrage_id)
        if fa is None or fa.status != "bestaetigt":
            return None
        if now < fa.ausfuehren_ab:
            return None
        if now > fa.ablauf:
            fa.status = "abgelaufen"
            await self.session.flush()
            return None
        return fa

class BillingStatusService:
    """Aggregiert Abrechnungsstatus fuer Plattform-Admin-Uebersicht (A0)."""

    def __init__(self, session: AsyncSession, org_id: int):
        self.session = session
        self.org_id = org_id

    async def get(self) -> dict:
        org = await self.session.get(Organisation, self.org_id)
        if org is None:
            raise ValueError("Organisation nicht gefunden")
        active_users = await self.session.scalar(
            select(func.count(OrganisationsMitglied.id)).where(
                OrganisationsMitglied.org_id == self.org_id,
                OrganisationsMitglied.aktiv.is_(True),
            )
        )
        return {
            "org_id": org.id,
            "public_id": org.public_id,
            "name": org.name,
            "status": org.status,
            "plan": org.plan,
            "stripe_customer_id": org.stripe_customer_id,
            "active_users": active_users,
        }


class OffboardingService:
    """Prueft offene Posten vor dem Entfernen eines Mitarbeiters (A1)."""

    def __init__(self, session: AsyncSession, org_id: int):
        self.session = session
        self.org_id = org_id

    async def check(self, mitglied_id: int) -> dict:
        mitglied = await self.session.get(OrganisationsMitglied, mitglied_id)
        if mitglied is None or mitglied.org_id != self.org_id:
            raise ValueError("Mitglied nicht gefunden")
        from app.models.tickets import Ticket
        open_tickets = await self.session.scalar(
            select(func.count(Ticket.id)).where(
                Ticket.org_id == self.org_id,
                Ticket.assigned_to == mitglied.user_id,
                Ticket.status != "geschlossen",
            )
        )
        is_owner = mitglied.rolle == "org_admin"
        return {
            "mitglied_id": mitglied.id,
            "user_id": mitglied.user_id,
            "rolle": mitglied.rolle,
            "open_tickets": open_tickets,
            "is_owner": is_owner,
            "can_remove": open_tickets == 0 and not is_owner,
        }
