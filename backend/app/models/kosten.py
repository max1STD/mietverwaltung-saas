"""Kosten-Modell — Betriebskosten, Reparaturen und sonstige Ausgaben."""
from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.abrechnungen import Abrechnung
    from app.models.einheit import Einheit
    from app.models.kostenkategorien import Kostenkategorie
    from app.models.objekt import Objekt
    from app.models.user import User


class Kosten(Base, SoftDeleteMixin):
    """Eine einzelne Kostenposition mit optionaler Umlagefähigkeit."""

    __tablename__ = "kosten"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    objekt_id: Mapped[int | None] = mapped_column(
        ForeignKey("objekte.id"),
        nullable=True,
    )
    einheit_id: Mapped[int | None] = mapped_column(
        ForeignKey("einheiten.id"),
        nullable=True,
    )
    kategorie_id: Mapped[int | None] = mapped_column(
        ForeignKey("kostenkategorien.id"),
        nullable=True,
    )
    betrag: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    datum: Mapped[date] = mapped_column(Date, nullable=False)
    umlagefaehig: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    abrechnung_id: Mapped[int | None] = mapped_column(
        ForeignKey("abrechnungen.id"),
        nullable=True,
    )
    abgerechnet_am: Mapped[date | None] = mapped_column(Date, nullable=True)
    ki_kategorisiert: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    datev_konto: Mapped[str | None] = mapped_column(String(10), nullable=True)
    datev_buchungstext: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    vermieter: Mapped[User] = relationship("User", foreign_keys=[vermieter_id])
    objekt: Mapped[Objekt | None] = relationship("Objekt", foreign_keys=[objekt_id])
    einheit: Mapped[Einheit | None] = relationship(
        "Einheit",
        foreign_keys=[einheit_id],
    )
    kategorie: Mapped[Kostenkategorie | None] = relationship(
        "Kostenkategorie",
        foreign_keys=[kategorie_id],
    )
    abrechnung: Mapped[Abrechnung | None] = relationship(
        "Abrechnung",
        foreign_keys=[abrechnung_id],
        back_populates="kosten",
    )
