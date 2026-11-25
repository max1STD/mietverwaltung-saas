"""Mieter-Modell — Stammdaten einer Mieter-Person."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import BigInteger, Date, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, RetentionMixin, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.adresse import Adresse
    from app.models.bankverbindung import Bankverbindung
    from app.models.buergschaft import Buergschaft
    from app.models.mietvertraege import Mietvertrag
    from app.models.user import User


class Mieter(Base, TimestampMixin, SoftDeleteMixin, RetentionMixin):
    """Eine Mieter-Person mit Kontaktdaten und optionalem verschlüsseltem Geburtsdatum."""

    __tablename__ = "mieter"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        unique=True,
        server_default=sa.text("nextval('mieter_public_id_seq')"),
    )
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    org_id: Mapped[int | None] = mapped_column(
        ForeignKey("organisationen.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)
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
    adressen: Mapped[list[Adresse]] = relationship(
        "Adresse",
        back_populates="mieter",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    buergschaften: Mapped[list[Buergschaft]] = relationship(
        "Buergschaft",
        back_populates="mieter",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    bankverbindungen: Mapped[list["Bankverbindung"]] = relationship(
        "Bankverbindung",
        back_populates="mieter",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def full_name(self) -> str:
        """Vollständiger Name für Anzeige und Audit-Logs."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def name(self) -> str:
        """Frontend-kompatibler Name."""
        return self.full_name

    @property
    def telefon(self) -> str | None:
        return self.phone

    @property
    def geburtsdatum(self) -> date | None:
        from app.services.crypto import decrypt_value
        if self.birth_date_enc:
            decrypted = decrypt_value(self.birth_date_enc, context="mieter:birth_date")
            return date.fromisoformat(decrypted) if decrypted else None
        return None

    @property
    def adresse(self) -> str | None:
        return self.address

    @property
    def notizen(self) -> str | None:
        return self.notes
