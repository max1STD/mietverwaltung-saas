"""Onboarding-Modell — Setup-Fortschritt pro User."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class OnboardingProgress(Base):
    """Ein abgeschlossener oder ausstehender Onboarding-Schritt pro User."""

    __tablename__ = "onboarding_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    step: Mapped[str] = mapped_column(String(50), nullable=False)
    is_done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    done_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    user: Mapped[User] = relationship("User", foreign_keys=[user_id])
