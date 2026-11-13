"""Kostenkategorie-Modell — Katalog für Betriebskosten nach BetrKV."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Kostenkategorie(Base):
    """Kostenkategorie für die Erfassung und Umlage von Betriebskosten."""

    __tablename__ = "kostenkategorien"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    betrvk_key: Mapped[str | None] = mapped_column(String(20), nullable=True)
    umlagefaehig: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    verteilungsschluessel: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="qm",
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    vermieter: Mapped[User] = relationship("User", foreign_keys=[vermieter_id])
