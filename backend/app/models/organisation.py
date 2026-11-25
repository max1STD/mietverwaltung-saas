"""Organisationsmodell — Mandant für Hausverwaltungen, Selbstverwalter und Partner."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Organisation(Base, TimestampMixin):
    """Ein Mandant (Organisation), dem alle fachlichen Daten zugeordnet sind."""

    __tablename__ = "organisationen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        unique=True,
        server_default=sa.text("nextval('organisationen_public_id_seq')"),
    )
    typ: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="selbstverwalter",
    )  # selbstverwalter | hausverwaltung | partner
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="aktiv",
    )  # aktiv | gesperrt | geloescht
    plan: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="basis",
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(String(100), nullable=True)


class OrganisationsMitglied(Base, TimestampMixin):
    """Zuordnung eines User-Accounts zu einer Organisation mit Rolle."""

    __tablename__ = "organisations_mitglieder"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(
        ForeignKey("organisationen.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rolle: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="sachbearbeiter",
    )  # org_admin | sachbearbeiter | buchhaltung | eigentuemer
    aktiv: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    eingeladen_von: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    letzter_org_switch: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=lambda: datetime.now(UTC),
    )

    org: Mapped[Organisation] = relationship("Organisation", foreign_keys=[org_id])
    user: Mapped[User] = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        sa.UniqueConstraint("org_id", "user_id", name="uq_organisations_mitglieder_org_user"),
    )


class Eigentuemer(Base, TimestampMixin):
    """Eigentümer innerhalb einer Organisation. Objekte gehören einem Eigentümer."""

    __tablename__ = "eigentuemer"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(
        ForeignKey("organisationen.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    kontakt_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    kontakt_telefon: Mapped[str | None] = mapped_column(String(30), nullable=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )  # optionaler Login
    notizen: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    org: Mapped[Organisation] = relationship("Organisation", foreign_keys=[org_id])
    user: Mapped[User | None] = relationship("User", foreign_keys=[user_id])


class MitgliedObjektScope(Base, TimestampMixin):
    """Optionaler Objekt-Scope für Sachbearbeiter."""

    __tablename__ = "mitglied_objekt_scope"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mitglied_id: Mapped[int] = mapped_column(
        ForeignKey("organisations_mitglieder.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    objekt_id: Mapped[int] = mapped_column(
        ForeignKey("objekte.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        sa.UniqueConstraint("mitglied_id", "objekt_id", name="uq_mitglied_objekt_scope"),
    )


class OrgFeature(Base, TimestampMixin):
    """Add-ons / Entitlements pro Organisation."""

    __tablename__ = "org_features"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(
        ForeignKey("organisationen.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    feature: Mapped[str] = mapped_column(String(50), nullable=False)
    aktiv_ab: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=lambda: datetime.now(UTC),
    )
    aktiv_bis: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        sa.UniqueConstraint("org_id", "feature", name="uq_org_features_org_feature"),
    )


class Einladung(Base, TimestampMixin):
    """Einladung für Mitarbeiter, Eigentümer oder Partner."""

    __tablename__ = "einladungen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    art: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )  # mitglied | eigentuemer | handwerker | partner
    org_id: Mapped[int] = mapped_column(
        ForeignKey("organisationen.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ziel_kontakt: Mapped[str] = mapped_column(String(255), nullable=False)
    rolle_oder_scope: Mapped[str | None] = mapped_column(String(50), nullable=True)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    gueltig_bis: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    angenommen_am: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PlattformAdmin(Base, TimestampMixin):
    """Betreiber-Account fuer die Admin-Oberflaeche."""

    __tablename__ = "plattform_admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    rolle: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="support",
    )  # owner | support | billing | compliance | ops | partner
    aktiv: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    passkey_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    letzte_anmeldung: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    eingeladen_von_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("plattform_admins.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    eingeladen_am: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=lambda: datetime.now(UTC)
    )


class PlattformAuditLog(Base):
    """Unveraenderliches Audit-Log fuer Betreiber-Aktionen."""

    __tablename__ = "plattform_audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("plattform_admins.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    aktion: Mapped[str] = mapped_column(String(100), nullable=False)
    ziel_typ: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ziel_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    begruendung: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    ergebnis: Mapped[str | None] = mapped_column(String(50), nullable=True)
    zeitpunkt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    ip_adresse: Mapped[str | None] = mapped_column(String(45), nullable=True)


class SupportFreigabe(Base, TimestampMixin):
    """Kunden-Freigabe fuer Support-Zugriff (Break-glass)."""

    __tablename__ = "support_freigaben"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(
        ForeignKey("organisationen.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ticket_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)
    grund: Mapped[str] = mapped_column(String(1000), nullable=False)
    umfang: Mapped[str] = mapped_column(String(500), nullable=False)
    gueltig_bis: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    widerrufen_am: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    erteilt_von_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )


class SupportZugriff(Base, TimestampMixin):
    """Protokolliert jeden Abruf im Rahmen einer Support-Freigabe."""

    __tablename__ = "support_zugriffe"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    freigabe_id: Mapped[int] = mapped_column(
        ForeignKey("support_freigaben.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("plattform_admins.id", ondelete="SET NULL"),
        nullable=True,
    )
    aktion: Mapped[str] = mapped_column(String(100), nullable=False)
    ziel: Mapped[str | None] = mapped_column(String(500), nullable=True)


class FreigabeAnfrage(Base, TimestampMixin):
    """Vier-Augen-Anfrage mit Zeitsperre fuer kritische Admin-Aktionen."""

    __tablename__ = "freigabe_anfragen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int | None] = mapped_column(
        ForeignKey("organisationen.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    aktion: Mapped[str] = mapped_column(String(100), nullable=False)
    angefordert_von_admin_id: Mapped[int] = mapped_column(
        ForeignKey("plattform_admins.id", ondelete="CASCADE"),
        nullable=False,
    )
    bestaetigt_von_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("plattform_admins.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ausstehend",
    )  # ausstehend | bestaetigt | abgelehnt | abgelaufen
    ausfuehren_ab: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ablauf: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OrgRichtlinie(Base, TimestampMixin):
    """Sicherheitsrichtlinien pro Organisation."""

    __tablename__ = "org_richtlinien"

    org_id: Mapped[int] = mapped_column(
        ForeignKey("organisationen.id", ondelete="CASCADE"),
        primary_key=True,
    )
    mfa_pflicht: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    mfa_pflicht_rollen: Mapped[str | None] = mapped_column(
        String(200), nullable=True, default="org_admin,admin,buchhaltung"
    )
    session_dauer_stunden: Mapped[int] = mapped_column(Integer, nullable=False, default=12)
    inaktivitaet_minuten: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    vier_augen_aktionen: Mapped[str | None] = mapped_column(
        String(500), nullable=True, default=""
    )
    massenexport_benachrichtigt: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    ip_freigabe: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sso_erlaubt: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sso_idp_metadata_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    zwei_fa_erforderlich: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    erweiterte_berichte: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    compliance_center_aktiv: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class OrgRolle(Base, TimestampMixin):
    """Benutzerdefinierte Rolle innerhalb einer Organisation (Phase A2)."""

    __tablename__ = "org_rollen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(
        ForeignKey("organisationen.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    berechtigungen: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
        default="",
    )  # comma-separated permission list


class Vertretung(Base, TimestampMixin):
    """Zeitlich begrenzte Rollen- oder Objekt-Vertretung."""

    __tablename__ = "vertretungen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(
        ForeignKey("organisationen.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    von_mitglied_id: Mapped[int] = mapped_column(
        ForeignKey("organisations_mitglieder.id", ondelete="CASCADE"),
        nullable=False,
    )
    an_mitglied_id: Mapped[int] = mapped_column(
        ForeignKey("organisations_mitglieder.id", ondelete="CASCADE"),
        nullable=False,
    )
    rolle: Mapped[str | None] = mapped_column(String(30), nullable=True)
    objekt_ids: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )  # comma-separated object ids
    von: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    bis: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SicherheitsEreignis(Base, TimestampMixin):
    """Auffaellige Sicherheitsereignisse pro Organisation."""

    __tablename__ = "sicherheits_ereignisse"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int | None] = mapped_column(
        ForeignKey("organisationen.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("plattform_admins.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    art: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    ernst: Mapped[str | None] = mapped_column(
        String(20), nullable=True, default="mittel"
    )  # niedrig | mittel | hoch
    gelesen_am: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    zeitpunkt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )


class BetroffenenAnfrage(Base, TimestampMixin):
    """DSGVO-Betroffenenanfragen (Löschen, Auskunft, Berichtigung)."""

    __tablename__ = "betroffenen_anfragen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(
        ForeignKey("organisationen.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    art: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="offen",
    )  # offen | in_bearbeitung | erledigt | abgelehnt
    frist_bis: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    beschreibung: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    antwort: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    bearbeitet_von_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
