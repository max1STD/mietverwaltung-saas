"""Bankverbindung-Modell — IBAN/BIC werden verschlüsselt in der DB gespeichert."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.mieter import Mieter
    from app.models.user import User


class Bankverbindung(Base, TimestampMixin, SoftDeleteMixin):
    """Bankverbindung eines Vermieters oder zugeordnetem Mieter."""

    __tablename__ = "bankverbindungen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    mieter_id: Mapped[int | None] = mapped_column(
        ForeignKey("mieter.id", ondelete="SET NULL"),
        nullable=True,
    )

    # IBAN liegt verschlüsselt in der Datenbank (Spalte iban_enc BYTEA).
    iban_enc: Mapped[bytes] = mapped_column("iban_enc", nullable=False)
    bic: Mapped[str | None] = mapped_column(String(11), nullable=True)
    kontoinhaber: Mapped[str] = mapped_column(String(100), nullable=False)
    bankname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    vermieter: Mapped["User"] = relationship("User", back_populates="bankverbindungen")
    mieter: Mapped["Mieter | None"] = relationship("Mieter", back_populates="bankverbindungen")
