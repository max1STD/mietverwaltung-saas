"""Löschregel- und Löschprotokoll-Modelle für DSGVO-konforme Aufbewahrung."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.organisation import Organisation


class Loeschregel(Base, TimestampMixin):
    """Konfigurierbare Aufbewahrungsfrist für eine Löschklasse.

    Standardwerte werden beim Setup angelegt. Organisationen können eigene,
    nie kürzere Fristen definieren.
    """

    __tablename__ = "loeschregeln"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int | None] = mapped_column(
        ForeignKey("organisationen.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )  # NULL = System-Default
    klasse: Mapped[str] = mapped_column(String(20), nullable=False)  # K1 .. K12
    datenart: Mapped[str] = mapped_column(String(100), nullable=False)
    frist_monate: Mapped[int] = mapped_column(Integer, nullable=False)
    startpunkt: Mapped[str] = mapped_column(String(200), nullable=False)
    rechtsgrundlage: Mapped[str] = mapped_column(String(255), nullable=False)
    mindestfrist_monate: Mapped[int] = mapped_column(Integer, nullable=False)
    vom_vermieter_aenderbar: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    gueltig_ab: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    org: Mapped[Organisation | None] = relationship("Organisation", foreign_keys=[org_id])

    __table_args__ = (
        sa.UniqueConstraint(
            "org_id", "klasse", "version",
            name="uq_loeschregeln_org_klasse_version",
        ),
    )


class Loeschprotokoll(Base, TimestampMixin):
    """Nachweis gelöschter oder gesperrter Datensätze (ohne Inhalte)."""

    __tablename__ = "loeschprotokoll"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int | None] = mapped_column(
        ForeignKey("organisationen.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    tabelle: Mapped[str] = mapped_column(String(50), nullable=False)
    datensatz_id: Mapped[int] = mapped_column(Integer, nullable=False)
    public_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    klasse: Mapped[str | None] = mapped_column(String(20), nullable=True)
    aktion: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )  # gesperrt | vorwarnung | geloescht | anonymisiert
    zeitpunkt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    ausloeser: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # system | user | legal_hold | manuell
    grund: Mapped[str | None] = mapped_column(Text, nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)

    org: Mapped[Organisation | None] = relationship("Organisation", foreign_keys=[org_id])

    __table_args__ = (
        sa.Index("ix_loeschprotokoll_lookup", "tabelle", "datensatz_id"),
    )
