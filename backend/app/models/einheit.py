"""Einheit-Modell — Wohneinheiten (WE) innerhalb eines Objekts."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import BigInteger, Boolean, Date, DECIMAL, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.mietvertraege import Mietvertrag
    from app.models.objekt import Objekt
    from app.models.user import User


class Einheit(Base, TimestampMixin, SoftDeleteMixin):
    """Eine Wohneinheit innerhalb eines Objekts."""

    __tablename__ = "einheiten"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        unique=True,
        server_default=sa.text("nextval('einheiten_public_id_seq')"),
    )
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    objekt_id: Mapped[int] = mapped_column(
        ForeignKey("objekte.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Kern-Flaechen / Miete
    wohnflaeche_qm: Mapped[float] = mapped_column(DECIMAL(6, 2), nullable=False)
    nutzflaeche_qm: Mapped[float | None] = mapped_column(DECIMAL(8, 2), nullable=True)
    balkon_flaeche_qm: Mapped[float | None] = mapped_column(DECIMAL(6, 2), nullable=True)
    terrasse_flaeche_qm: Mapped[float | None] = mapped_column(DECIMAL(6, 2), nullable=True)
    garten_flaeche_qm: Mapped[float | None] = mapped_column(DECIMAL(8, 2), nullable=True)
    gewerbeflaeche_qm: Mapped[float | None] = mapped_column(DECIMAL(8, 2), nullable=True)

    # Lage / Raumzahl
    etage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    floor: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rooms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    schlafzimmer: Mapped[int | None] = mapped_column(Integer, nullable=True)
    badezimmer: Mapped[int | None] = mapped_column(Integer, nullable=True)
    wohnzimmer: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Miete / Vermietung
    kaltmiete: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    nebenkosten_vorschuss: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True)

    # Ausstattung (Boolean Badges)
    balkon: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    terrasse: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    garten: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    garage: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    stellplatz: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    keller: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    aufzug: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    barrierefrei: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    moebliert: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Energie / Bau
    energy_class: Mapped[str | None] = mapped_column(String(2), nullable=True)
    baujahr_einheit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    heizungsart: Mapped[str | None] = mapped_column(String(50), nullable=True)
    warmwasserbereitung: Mapped[str | None] = mapped_column(String(50), nullable=True)
    fenster: Mapped[str | None] = mapped_column(String(50), nullable=True)
    boden: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sanitaer: Mapped[str | None] = mapped_column(String(50), nullable=True)
    kueche: Mapped[str | None] = mapped_column(String(50), nullable=True)
    energieausweis_art: Mapped[str | None] = mapped_column(String(50), nullable=True)
    energieverbrauch_kennwert: Mapped[float | None] = mapped_column(DECIMAL(6, 2), nullable=True)
    energieverbrauch_klasse: Mapped[str | None] = mapped_column(String(10), nullable=True)
    bauweise: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Rechtliches / Denkmalschutz
    denkmalschutz: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    denkmalschutz_bis: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Zustand / Historie
    last_renovation: Mapped[date | None] = mapped_column(Date, nullable=True)
    renovierungsstatus: Mapped[str | None] = mapped_column(String(50), nullable=True)
    zustand: Mapped[str | None] = mapped_column(String(50), nullable=True)
    available_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    bewohnbar_ab: Mapped[date | None] = mapped_column(Date, nullable=True)
    anmerkungen: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Beziehungen
    vermieter: Mapped[User] = relationship("User", foreign_keys=[vermieter_id])
    objekt: Mapped[Objekt] = relationship("Objekt", back_populates="einheiten")
    mietvertraege: Mapped[list[Mietvertrag]] = relationship(
        "Mietvertrag",
        back_populates="einheit",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # Aktueller Mieter wird ueber den aktiven Mietvertrag ermittelt (Business-Logik).
