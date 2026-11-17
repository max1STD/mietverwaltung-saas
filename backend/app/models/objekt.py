"""Objekt-Modell — Immobilien mit Finanzierungsdaten fuer Rendite-Berechnung."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import BigInteger, Boolean, Date, DECIMAL, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.einheit import Einheit
    from app.models.user import User


class Objekt(Base, TimestampMixin, SoftDeleteMixin):
    """Eine Immobilie (Haus, Mehrfamilienhaus, etc.) mit Adresse und Finanzdaten."""

    __tablename__ = "objekte"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        unique=True,
        server_default=sa.text("nextval('objekte_public_id_seq')"),
    )
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    plz: Mapped[str | None] = mapped_column(String(10), nullable=True)
    ort: Mapped[str | None] = mapped_column(String(100), nullable=True)
    typ: Mapped[str | None] = mapped_column(String(20), nullable=True)
    baujahr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    foto_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Flaechen (gesamtobjekt)
    grundstuecksflaeche_qm: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True)
    wohnflaeche_gesamt_qm: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True)
    nutzflaeche_gesamt_qm: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True)
    vermietbare_flaeche_qm: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True)

    # Verwaltung / Bau
    anzahl_einheiten: Mapped[int | None] = mapped_column(Integer, nullable=True)
    baujahr_objekt: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bauweise: Mapped[str | None] = mapped_column(String(50), nullable=True)
    zustand: Mapped[str | None] = mapped_column(String(50), nullable=True)
    denkmalschutz: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    denkmalschutz_bis: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Energie
    energieausweis_art: Mapped[str | None] = mapped_column(String(50), nullable=True)
    energieausweis_gueltig_bis: Mapped[date | None] = mapped_column(Date, nullable=True)
    energieverbrauch_kennwert: Mapped[float | None] = mapped_column(DECIMAL(6, 2), nullable=True)
    energieverbrauch_klasse: Mapped[str | None] = mapped_column(String(10), nullable=True)
    heizungsart: Mapped[str | None] = mapped_column(String(50), nullable=True)
    warmwasserbereitung: Mapped[str | None] = mapped_column(String(50), nullable=True)
    solaranlage: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Adresse / Lage
    land: Mapped[str | None] = mapped_column(String(2), nullable=True)
    adresszusatz: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lagebeschreibung: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Finanzen (erweitert)
    kaufpreis: Mapped[float | None] = mapped_column(DECIMAL(12, 2), nullable=True)
    kaufpreis_pro_qm: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True)
    kaufdatum: Mapped[date | None] = mapped_column(Date, nullable=True)
    eigenkapital: Mapped[float | None] = mapped_column(DECIMAL(12, 2), nullable=True)
    darlehen_betrag: Mapped[float | None] = mapped_column(DECIMAL(12, 2), nullable=True)
    zinssatz: Mapped[float | None] = mapped_column(DECIMAL(5, 2), nullable=True)
    tilgung: Mapped[float | None] = mapped_column(DECIMAL(5, 2), nullable=True)
    monatliche_rate: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True)
    gesamtmiete_ist: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True)
    gesamtmiete_soll: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True)

    # Ausstattung / Sonstiges
    barrierefrei: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    aufzug: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    gartennutzung: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    notizen: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    anmerkungen: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Beziehungen
    vermieter: Mapped[User] = relationship("User", foreign_keys=[vermieter_id])
    einheiten: Mapped[list[Einheit]] = relationship(
        "Einheit",
        back_populates="objekt",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
