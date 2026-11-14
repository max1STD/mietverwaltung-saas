"""Abrechnungs-Modell — Nebenkostenabrechnung pro Einheit/Jahr."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.abrechnung_positionen import AbrechnungPosition
    from app.models.einheit import Einheit
    from app.models.kosten import Kosten
    from app.models.objekt import Objekt
    from app.models.user import User


class Abrechnung(Base, TimestampMixin, SoftDeleteMixin):
    """Nebenkostenabrechnung pro Einheit und Abrechnungsjahr."""

    __tablename__ = "abrechnungen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    einheit_id: Mapped[int] = mapped_column(
        ForeignKey("einheiten.id"),
        nullable=False,
    )
    objekt_id: Mapped[int | None] = mapped_column(
        ForeignKey("objekte.id"),
        nullable=True,
    )
    jahr: Mapped[int] = mapped_column(Integer, nullable=False)
    zeitraum_von: Mapped[date] = mapped_column(Date, nullable=False)
    zeitraum_bis: Mapped[date] = mapped_column(Date, nullable=False)
    einwendungsfrist_bis: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
    rechtskraeftig_seit: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="entwurf",
    )

    vermieter: Mapped[User] = relationship("User", foreign_keys=[vermieter_id])
    einheit: Mapped[Einheit] = relationship("Einheit", foreign_keys=[einheit_id])
    objekt: Mapped[Objekt | None] = relationship("Objekt", foreign_keys=[objekt_id])
    positionen: Mapped[list[AbrechnungPosition]] = relationship(
        "AbrechnungPosition",
        back_populates="abrechnung",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    kosten: Mapped[list[Kosten]] = relationship(
        "Kosten",
        back_populates="abrechnung",
        lazy="selectin",
    )
