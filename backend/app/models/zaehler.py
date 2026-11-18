"""Zähler-Modell — Strom, Gas, Wasser etc. pro Einheit."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.einheit import Einheit
    from app.models.user import User


class Zaehler(Base, TimestampMixin, SoftDeleteMixin):
    """Ein Zähler (Strom, Gas, Wasser, etc.) der einer Einheit zugeordnet ist."""

    __tablename__ = "zaehler"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    einheit_id: Mapped[int] = mapped_column(
        ForeignKey("einheiten.id", ondelete="CASCADE"),
        nullable=False,
    )
    bezeichnung: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="",
    )
    zaehlernummer: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    typ: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    einheit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="kwh",
    )
    ist_hauptzaehler: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    ablesedatum: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    vermieter: Mapped[User] = relationship("User", foreign_keys=[vermieter_id])
    einheit_obj: Mapped[Einheit] = relationship(
        "Einheit",
        foreign_keys=[einheit_id],
    )
    ablesungen: Mapped[list[Zaehlerablesung]] = relationship(
        "Zaehlerablesung",
        back_populates="zaehler",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Zaehlerablesung.ablesedatum.desc(), Zaehlerablesung.created_at.desc()",
    )


class Zaehlerablesung(Base, TimestampMixin, SoftDeleteMixin):
    """Eine Ablesung eines Zählers mit Verbrauchsberechnung."""

    __tablename__ = "zaehlerablesungen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    zaehler_id: Mapped[int] = mapped_column(
        ForeignKey("zaehler.id", ondelete="CASCADE"),
        nullable=False,
    )
    ablesedatum: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    zaehlerstand: Mapped[Decimal] = mapped_column(
        Numeric(15, 3),
        nullable=False,
    )
    verbrauch: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 3),
        nullable=True,
    )
    ableser: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    notizen: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    ist_schaetzung: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    zaehlerwechsel: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    vermieter: Mapped[User] = relationship("User", foreign_keys=[vermieter_id])
    zaehler: Mapped[Zaehler] = relationship(
        "Zaehler",
        foreign_keys=[zaehler_id],
        back_populates="ablesungen",
    )
