"""Abrechnungsposition-Modell — auf die Einheit umgelegte Kosten."""
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.abrechnungen import Abrechnung
    from app.models.kosten import Kosten
    from app.models.kostenkategorien import Kostenkategorie
    from app.models.user import User


class AbrechnungPosition(Base, SoftDeleteMixin):
    """Einzelne Position einer Nebenkostenabrechnung."""

    __tablename__ = "abrechnung_positionen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    abrechnung_id: Mapped[int] = mapped_column(
        ForeignKey("abrechnungen.id", ondelete="CASCADE"),
        nullable=False,
    )
    kategorie_id: Mapped[int | None] = mapped_column(
        ForeignKey("kostenkategorien.id"),
        nullable=True,
    )
    kosten_id: Mapped[int | None] = mapped_column(
        ForeignKey("kosten.id"),
        nullable=True,
    )
    betrag_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    umlageanteil: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    verteilungsschluessel: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    datev_betrag: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    vermieter: Mapped[User] = relationship("User", foreign_keys=[vermieter_id])
    abrechnung: Mapped[Abrechnung] = relationship(
        "Abrechnung",
        foreign_keys=[abrechnung_id],
        back_populates="positionen",
    )
    kategorie: Mapped[Kostenkategorie | None] = relationship(
        "Kostenkategorie",
        foreign_keys=[kategorie_id],
    )
    kosten: Mapped[Kosten | None] = relationship(
        "Kosten",
        foreign_keys=[kosten_id],
    )
