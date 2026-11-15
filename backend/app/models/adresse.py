"""Adresse-Modell — strukturierte Adressen für Mieter, Objekte und Bürgen."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.mieter import Mieter


class Adresse(Base, TimestampMixin):
    """Eine strukturierte Adresse (Post, Wohn, Mietobjekt, Bürge)."""

    __tablename__ = "adressen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mieter_id: Mapped[int] = mapped_column(
        ForeignKey("mieter.id", ondelete="CASCADE"),
        nullable=False,
    )
    typ: Mapped[str] = mapped_column(String(20), nullable=False)
    strasse: Mapped[str] = mapped_column(String(255), nullable=False)
    hausnummer: Mapped[str | None] = mapped_column(String(20), nullable=True)
    plz: Mapped[str] = mapped_column(String(10), nullable=False)
    ort: Mapped[str] = mapped_column(String(100), nullable=False)
    land: Mapped[str] = mapped_column(String(2), nullable=False, default="DE")
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Beziehungen
    mieter: Mapped[Mieter] = relationship("Mieter", back_populates="adressen")

    def __repr__(self) -> str:
        return f"<Adresse {self.typ}: {self.strasse} {self.hausnummer or ''}, {self.plz} {self.ort}>"
