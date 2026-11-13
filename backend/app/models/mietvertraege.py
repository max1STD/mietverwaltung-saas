"""Mietvertrag-Modell (für DSGVO-Aufbewahrungsprüfung)."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Mietvertrag(Base, TimestampMixin, SoftDeleteMixin):
    """Mietvertrag zwischen Vermieter und Mieter."""

    __tablename__ = "mietvertraege"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    mieter_id: Mapped[int] = mapped_column(
        ForeignKey("mieter.id", ondelete="CASCADE"),
        nullable=False,
    )
    einheit_id: Mapped[int] = mapped_column(
        ForeignKey("einheiten.id"),
        nullable=False,
    )
    mietbeginn: Mapped[datetime] = mapped_column(Date, nullable=False)
    mietende: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    miete_cold: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    nebenkosten_voraus: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    kaution: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="aktiv")

    vermieter: Mapped["User"] = relationship("User", foreign_keys=[vermieter_id])
