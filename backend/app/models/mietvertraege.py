"""Mietvertrag-Modell — Vertragsdaten zwischen Vermieter und Mieter."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import BigInteger, DECIMAL, Boolean, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, RetentionMixin, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.einheit import Einheit
    from app.models.mieter import Mieter
    from app.models.user import User


class Mietvertrag(Base, TimestampMixin, SoftDeleteMixin, RetentionMixin):
    """Mietvertrag zwischen Vermieter und Mieter für eine bestimmte Einheit."""

    __tablename__ = "mietvertraege"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        unique=True,
        server_default=sa.text("nextval('mietvertraege_public_id_seq')"),
    )
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    org_id: Mapped[int | None] = mapped_column(
        ForeignKey("organisationen.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    mieter_id: Mapped[int] = mapped_column(
        ForeignKey("mieter.id", ondelete="CASCADE"),
        nullable=False,
    )
    einheit_id: Mapped[int] = mapped_column(
        ForeignKey("einheiten.id"),
        nullable=False,
    )
    mietbeginn: Mapped[date] = mapped_column(Date, nullable=False)
    mietende: Mapped[date | None] = mapped_column(Date, nullable=True)
    miete_cold: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    nebenkosten_voraus: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    kaution: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True)
    kaution_hinterlegt: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="aktiv",
    )

    # Beziehungen
    vermieter: Mapped[User] = relationship("User", foreign_keys=[vermieter_id])
    mieter: Mapped[Mieter] = relationship("Mieter", back_populates="mietvertraege")
    einheit: Mapped[Einheit] = relationship("Einheit", back_populates="mietvertraege")
