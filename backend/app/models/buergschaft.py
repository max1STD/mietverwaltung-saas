"""Buergschaft-Modell — Mietbürgschaft nach § 765 BGB."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.adresse import Adresse
    from app.models.mieter import Mieter
    from app.models.user import User


class Buergschaft(Base, TimestampMixin):
    """Eine Mietbürgschaft mit Bezug zum Mieter und Bürgen."""

    __tablename__ = "buergschaften"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mieter_id: Mapped[int] = mapped_column(
        ForeignKey("mieter.id", ondelete="CASCADE"),
        nullable=False,
    )
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Bürgen-Stammdaten
    buerge_first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    buerge_last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    buerge_geburtsdatum: Mapped[date | None] = mapped_column(Date, nullable=True)
    buerge_adresse_id: Mapped[int | None] = mapped_column(
        ForeignKey("adressen.id", ondelete="SET NULL"),
        nullable=True,
    )
    buerge_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    buerge_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Vertragsmerkmale (§ 765 BGB)
    hoechstbetrag: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    gueltig_bis: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="aktiv")
    notizen: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    # Beziehungen
    mieter: Mapped[Mieter] = relationship("Mieter", back_populates="buergschaften")
    vermieter: Mapped[User] = relationship("User", foreign_keys=[vermieter_id])
    buerge_adresse: Mapped[Adresse | None] = relationship("Adresse", foreign_keys=[buerge_adresse_id])

    @property
    def buerge_full_name(self) -> str:
        return f"{self.buerge_first_name} {self.buerge_last_name}".strip()

    def __repr__(self) -> str:
        return f"<Buergschaft {self.id}: {self.buerge_full_name} für Mieter {self.mieter_id}>"
