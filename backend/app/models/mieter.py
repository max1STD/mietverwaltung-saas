"""Mieter-Modell — Stammdaten einer Mieter-Person."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.mietvertraege import Mietvertrag
    from app.models.user import User


class Mieter(Base, TimestampMixin, SoftDeleteMixin):
    """Eine Mieter-Person mit Kontaktdaten und optionalem verschlüsseltem Geburtsdatum."""

    __tablename__ = "mieter"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    birth_date_enc: Mapped[bytes | None] = mapped_column(BYTEA, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="aktiv",
    )
    since: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Beziehungen
    vermieter: Mapped[User] = relationship("User", foreign_keys=[vermieter_id])
    mietvertraege: Mapped[list[Mietvertrag]] = relationship(
        "Mietvertrag",
        back_populates="mieter",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def full_name(self) -> str:
        """Vollständiger Name für Anzeige und Audit-Logs."""
        return f"{self.first_name} {self.last_name}".strip()
