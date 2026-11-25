"""Berechtigungskatalog und zentrale Prüffunktionen.

Jede Berechtigung hat das Format ressource:aktion.
Rollen sind nur Bündel von Berechtigungen. Geprüft wird nie die Rolle,
sondern die Berechtigung.
"""
from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session
from app.models.organisation import OrganisationsMitglied

from fastapi import Depends, HTTPException, status

if TYPE_CHECKING:
    from app.core.db_context import DbContext


class Permission(str, Enum):
    MIETER_LIST = "mieter:list"
    ABRECHNUNG_DELETE = "abrechnung:delete"

    """Zentrale Berechtigungen."""

    # Objekte und Einheiten
    OBJEKT_READ = "objekt:read"
    OBJEKT_WRITE = "objekt:write"
    EINHEIT_READ = "einheit:read"
    EINHEIT_WRITE = "einheit:write"

    # Mieter und Verträge
    MIETER_READ = "mieter:read"
    MIETER_WRITE = "mieter:write"
    MIETVERTRAG_READ = "mietvertrag:read"
    MIETVERTRAG_WRITE = "mietvertrag:write"

    # Bank- und Zahlungsdaten
    BANKVERBINDUNG_READ = "bankverbindung:read"
    BANKVERBINDUNG_WRITE = "bankverbindung:write"
    ZAHLUNG_READ = "zahlung:read"
    ZAHLUNG_WRITE = "zahlung:write"

    # Zähler
    ZAEHLER_READ = "zaehler:read"
    ZAEHLER_WRITE = "zaehler:write"

    # Tickets
    TICKET_READ = "ticket:read"
    TICKET_WRITE = "ticket:write"

    # Dokumente
    DOKUMENT_READ = "dokument:read"
    DOKUMENT_WRITE = "dokument:write"

    # Nebenkostenabrechnung
    KOSTEN_READ = "kosten:read"
    KOSTEN_WRITE = "kosten:write"
    ABRECHNUNG_READ = "abrechnung:read"
    ABRECHNUNG_WRITE = "abrechnung:write"

    # Nutzer, Billing, Add-ons
    ORG_ADMIN = "org:admin"
    BILLING_READ = "billing:read"
    BILLING_WRITE = "billing:write"
    ORG_FEATURES = "org:features"

    # Audit
    AUDIT_READ = "audit:read"


ROLE_PERMISSIONS: dict[str, set[Permission]] = {
    "org_admin": {
        Permission.OBJEKT_READ,
        Permission.OBJEKT_WRITE,
        Permission.EINHEIT_READ,
        Permission.EINHEIT_WRITE,
        Permission.MIETER_READ,
        Permission.MIETER_WRITE,
        Permission.MIETVERTRAG_READ,
        Permission.MIETVERTRAG_WRITE,
        Permission.BANKVERBINDUNG_READ,
        Permission.BANKVERBINDUNG_WRITE,
        Permission.ZAHLUNG_READ,
        Permission.ZAHLUNG_WRITE,
        Permission.ZAEHLER_READ,
        Permission.ZAEHLER_WRITE,
        Permission.TICKET_READ,
        Permission.TICKET_WRITE,
        Permission.DOKUMENT_READ,
        Permission.DOKUMENT_WRITE,
        Permission.KOSTEN_READ,
        Permission.KOSTEN_WRITE,
        Permission.ABRECHNUNG_READ,
        Permission.ABRECHNUNG_WRITE,
        Permission.ORG_ADMIN,
        Permission.BILLING_READ,
        Permission.BILLING_WRITE,
        Permission.ORG_FEATURES,
        Permission.AUDIT_READ,
    },
    "sachbearbeiter": {
        Permission.OBJEKT_READ,
        Permission.OBJEKT_WRITE,
        Permission.EINHEIT_READ,
        Permission.EINHEIT_WRITE,
        Permission.MIETER_READ,
        Permission.MIETER_WRITE,
        Permission.MIETVERTRAG_READ,
        Permission.MIETVERTRAG_WRITE,
        Permission.ZAHLUNG_READ,
        Permission.ZAHLUNG_WRITE,
        Permission.ZAEHLER_READ,
        Permission.ZAEHLER_WRITE,
        Permission.TICKET_READ,
        Permission.TICKET_WRITE,
        Permission.DOKUMENT_READ,
        Permission.DOKUMENT_WRITE,
        Permission.KOSTEN_READ,
        Permission.KOSTEN_WRITE,
        Permission.ABRECHNUNG_READ,
        # Sachbearbeiter darf Abrechnungen NICHT schreiben/löschen
    },
    "buchhaltung": {
        Permission.ZAHLUNG_READ,
        Permission.ZAHLUNG_WRITE,
        Permission.KOSTEN_READ,
        Permission.KOSTEN_WRITE,
        Permission.ABRECHNUNG_READ,
        Permission.ABRECHNUNG_WRITE,
        Permission.DOKUMENT_READ,
        Permission.DOKUMENT_WRITE,
    },
    "eigentuemer": {
        Permission.OBJEKT_READ,
        Permission.EINHEIT_READ,
        Permission.MIETER_READ,
        Permission.MIETVERTRAG_READ,
        Permission.ZAEHLER_READ,
        Permission.TICKET_READ,
        Permission.DOKUMENT_READ,
        Permission.ABRECHNUNG_READ,
    },
}


def has_permission(context: DbContext, permission: Permission) -> bool:
    """Prüft, ob der aktuelle Kontext eine Berechtigung hat."""
    if not context.role:
        return False
    return permission in ROLE_PERMISSIONS.get(context.role, set())


def require_permission(permission: Permission):
    """FastAPI-Dependency: wirft 403, wenn Berechtigung fehlt."""

    def _check(ctx: DbContext = Depends(get_db_context)) -> DbContext:
        if not has_permission(ctx, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Berechtigung {permission.value} erforderlich.",
            )
        return ctx

    return _check


def get_db_context() -> DbContext:
    """Wird später durch Auth-Dependency ersetzt, die JWT auswertet."""
    # Placeholder: in App-Setup durch require_auth() verbunden.
    from app.core.db_context import DbContext

    return DbContext()


class PermissionService:
    """Kombiniert Rollenberechtigung mit Organisationsmitgliedschaft."""

    def __init__(self, db: Session, context: "DbContext"):
        self.db = db
        self.context = context

    async def may(self, permission: Permission) -> bool:
        if not self.context.role:
            return False
        perms = ROLE_PERMISSIONS.get(self.context.role, set())
        if permission not in perms:
            return False
        # verify org membership
        if not self.context.org_id or not self.context.user_id:
            return False
        from sqlalchemy import select
        result = await self.db.execute(
            select(OrganisationsMitglied).where(
                OrganisationsMitglied.user_id == self.context.user_id,
                OrganisationsMitglied.org_id == self.context.org_id,
            )
        )
        Mitglied = result.scalar_one_or_none()
        return Mitglied is not None and Mitglied.rolle.lower() == self.context.role.lower()

    async def require(self, permission: Permission) -> None:
        if not await self.may(permission):
            raise PermissionError(f"Berechtigung {permission.value} erforderlich.")
