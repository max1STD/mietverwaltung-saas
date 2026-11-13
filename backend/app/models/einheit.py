"""Einheit-Modell — Wohneinheiten (WE) innerhalb eines Objekts."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, Date, ForeignKey, Integer, String
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
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    objekt_id: Mapped[int] = mapped_column(
        ForeignKey("objekte.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    size_qm: Mapped[float] = mapped_column(DECIMAL(6, 2), nullable=False)
    rooms: Mapped[int] = mapped_column(Integer, nullable=False)
    rent_cold: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    floor: Mapped[str | None] = mapped_column(String(20), nullable=True)
    energy_class: Mapped[str | None] = mapped_column(String(2), nullable=True)
    last_renovation: Mapped[date | None] = mapped_column(Date, nullable=True)
    available_from: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Beziehungen
    vermieter: Mapped[User] = relationship("User", foreign_keys=[vermieter_id])
    objekt: Mapped[Objekt] = relationship("Objekt", back_populates="einheiten")
    mietvertraege: Mapped[list[Mietvertrag]] = relationship(
        "Mietvertrag",
        back_populates="einheit",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # Aktueller Mieter wird über den aktiven Mietvertrag ermittelt (Business-Logik).
