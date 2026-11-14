"""Bewerbungs-Modell — Mieter-Bewerbung auf eine Wohneinheit."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DECIMAL, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.einheit import Einheit
    from app.models.user import User


class Bewerbung(Base, SoftDeleteMixin):
    """Bewerbung eines Interessenten auf eine vermietete Wohneinheit."""

    __tablename__ = "bewerbungen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    einheit_id: Mapped[int] = mapped_column(
        ForeignKey("einheiten.id", ondelete="CASCADE"),
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    income_monthly: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True)
    schufa_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    documents: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="offen",
    )
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    vermieter: Mapped[User] = relationship("User", foreign_keys=[vermieter_id])
    einheit: Mapped[Einheit] = relationship("Einheit", foreign_keys=[einheit_id])

    @property
    def full_name(self) -> str:
        """Vollständiger Name der bewerbenden Person."""
        return f"{self.first_name} {self.last_name}".strip()
