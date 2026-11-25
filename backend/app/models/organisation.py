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
