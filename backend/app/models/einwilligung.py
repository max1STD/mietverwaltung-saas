"""DSGVO-Einwilligungs-Modell (versioniert pro Verarbeitungszweck)."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Einwilligung(Base):
    """Eine erteilte oder widerrufene DSGVO-Einwilligung."""

    __tablename__ = "einwilligungen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    # Zweck: ki_anonymisierung, ki_dokumente, marketing, ...
    purpose: Mapped[str] = mapped_column(String(50), nullable=False)
    consent_text: Mapped[str] = mapped_column(Text, nullable=False)
    consented_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    withdrawn_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    user: Mapped["User"] = relationship("User", back_populates="einwilligungen")
