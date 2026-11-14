"""Plan-Usage-Modell — zählt aktive Wohneinheiten pro Vermieter."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class PlanUsage(Base):
    """Live-Nutzung des Pro-WE-Tarifs für einen Account."""

    __tablename__ = "plan_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    wohnungen_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    last_checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    # Beziehungen
    user: Mapped[User] = relationship("User", back_populates="plan_usage")
