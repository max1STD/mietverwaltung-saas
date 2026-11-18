"""Mietzahlung-Modell — Soll- und Ist-Zahlungen pro Mietvertrag."""
from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.mieter import Mieter
    from app.models.mietvertraege import Mietvertrag
    from app.models.user import User


class Mietzahlung(Base):
    """Erfasste Mietzahlung mit Soll-/Ist-Vergleich und Mahnstufe."""

    __tablename__ = "mietzahlungen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    mieter_id: Mapped[int | None] = mapped_column(
        ForeignKey("mieter.id"),
        nullable=True,
    )
    vertrag_id: Mapped[int | None] = mapped_column(
        ForeignKey("mietvertraege.id"),
        nullable=True,
    )
    betrag_soll: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    betrag_ist: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )
    zahlungsdatum: Mapped[date | None] = mapped_column(Date, nullable=True)
    mahnstufe: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    zahlungsreferenz: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    vermieter: Mapped[User] = relationship("User", foreign_keys=[vermieter_id])
    mieter: Mapped[Mieter | None] = relationship("Mieter", foreign_keys=[mieter_id])
    vertrag: Mapped[Mietvertrag | None] = relationship(
        "Mietvertrag",
        foreign_keys=[vertrag_id],
    )
