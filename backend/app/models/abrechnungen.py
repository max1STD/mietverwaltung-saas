"""Abrechnungs-Modell (für DSGVO-Aufbewahrungsprüfung)."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Abrechnung(Base, TimestampMixin, SoftDeleteMixin):
    """Nebenkostenabrechnung pro Einheit/Jahr."""

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
    zeitraum_von: Mapped[datetime] = mapped_column(Date, nullable=False)
    zeitraum_bis: Mapped[datetime] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="entwurf")

    vermieter: Mapped["User"] = relationship("User", foreign_keys=[vermieter_id])
