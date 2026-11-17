"""User-Modell — zentrale Login-Accounts (Vermieter, Mieter, Admin)."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import BYTEA, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.audit import AuditLog
from app.models.base import Base, SoftDeleteMixin, TimestampMixin
from app.models.einwilligung import Einwilligung
from app.models.plan_usage import PlanUsage
from app.models.session import UserSession
from app.models.subscription import Subscription

if TYPE_CHECKING:
    from app.models.bankverbindung import Bankverbindung


class User(Base, TimestampMixin, SoftDeleteMixin):
    """Ein Login-Account. Rolle bestimmt Berechtigungen und Sichtbarkeit."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="vermieter",
    )
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # Mieter-Zuordnung: Bei role='mieter' muss vermieter_id gesetzt sein.
    vermieter_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    # 2FA / Sicherheit
    totp_secret: Mapped[str | None] = mapped_column(String(64), nullable=True)
    backup_codes: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    email_code: Mapped[str | None] = mapped_column(String(6), nullable=True)
    # DB-Spalte heißt email_code_expires (v4.1); Modell-Attribut als _at.
    email_code_expires_at: Mapped[datetime | None] = mapped_column(
        "email_code_expires",
        DateTime(timezone=True),
        nullable=True,
    )
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Status
    is_active: Mapped[bool] = mapped_column(default=True)
    email_verified: Mapped[bool] = mapped_column(default=False)
    dsgvo_consent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Vermieter-Stammdaten für Briefkopf, Mahnungen, XRechnung/ZUGFeRD
    firma: Mapped[str | None] = mapped_column(String(200), nullable=True)
    steuernr_enc: Mapped[bytes | None] = mapped_column(BYTEA, nullable=True)
    rechnungs_strasse: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rechnungs_hausnr: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rechnungs_plz: Mapped[str | None] = mapped_column(String(10), nullable=True)
    rechnungs_ort: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ust_id: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Paperless-ngx DMS-Integration (pro Vermieter eigener Account)
    paperless_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    paperless_token_enc: Mapped[bytes | None] = mapped_column(BYTEA, nullable=True)

    @property
    def paperless_token(self) -> str | None:
        """Entschlüsselter Paperless-API-Token."""
        from app.services.crypto import decrypt_value
        return decrypt_value(self.paperless_token_enc)

    def set_paperless_token(self, token: str | None) -> None:
        """Verschlüsselt und speichert den Paperless-API-Token."""
        from app.services.crypto import encrypt_value
        self.paperless_token_enc = encrypt_value(token)

    # Beziehungen
    sessions: Mapped[list[UserSession]] = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    einwilligungen: Mapped[list[Einwilligung]] = relationship(
        "Einwilligung",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    audit_logs: Mapped[list[AuditLog]] = relationship(
        "AuditLog",
        foreign_keys=[AuditLog.user_id],
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    subscription: Mapped[Subscription | None] = relationship(
        "Subscription",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        uselist=False,
    )
    plan_usage: Mapped[PlanUsage | None] = relationship(
        "PlanUsage",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        uselist=False,
    )
    bankverbindungen: Mapped[list["Bankverbindung"]] = relationship(
        "Bankverbindung",
        back_populates="vermieter",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
