"""Fristen-Modell — verwaltet anstehende Deadlines für Vermieter."""
from __future__ import annotations

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Frist(Base, TimestampMixin):
    """Eine anstehende Frist oder Deadline für einen Vermieter."""

    __tablename__ = "fristen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    entity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deadline: Mapped[date] = mapped_column(Date, nullable=False)
    warn_level: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="green",
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_done: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    vermieter: Mapped[User] = relationship("User", foreign_keys=[vermieter_id])
