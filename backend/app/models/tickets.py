"""Ticket-System Modelle: Tickets, Kommentare, SLA und Trigger."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.handwerker import Handwerker

if TYPE_CHECKING:
    from app.models.user import User


class Ticket(Base, TimestampMixin):
    """Störungsmeldung / Service-Ticket in MietVerwaltung."""

    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    mieter_id: Mapped[int | None] = mapped_column(
        ForeignKey("mieter.id"),
        nullable=True,
    )
    einheit_id: Mapped[int | None] = mapped_column(
        ForeignKey("einheiten.id"),
        nullable=True,
    )
    ticket_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    priority: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="normal",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="offen",
    )
    ki_kategorisiert: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    ki_prioritaet: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    assigned_to: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )
    handwerker_id: Mapped[int | None] = mapped_column(
        ForeignKey("handwerker.id"),
        nullable=True,
    )
    sla_id: Mapped[int | None] = mapped_column(
        ForeignKey("ticket_sla.id"),
        nullable=True,
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Beziehungen
    vermieter: Mapped["User"] = relationship(
        "User",
        foreign_keys=[vermieter_id],
    )
    comments: Mapped[list["TicketComment"]] = relationship(
        "TicketComment",
        back_populates="ticket",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="TicketComment.created_at.asc()",
    )


class TicketComment(Base):
    """Ein Kommentar oder Verlaufseintrag zu einem Ticket."""

    __tablename__ = "ticket_kommentare"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
    )
    author_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )
    author_role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="vermieter",
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    ist_ki_entwurf: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    is_internal: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    # Beziehungen
    ticket: Mapped["Ticket"] = relationship(
        "Ticket",
        back_populates="comments",
    )
    author: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[author_id],
    )


class TicketSLA(Base):
    """Service-Level-Agreement Konfiguration pro Vermieter."""

    __tablename__ = "ticket_sla"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    response_time_hours: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=48,
    )
    resolution_time_hours: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=168,
    )
    biz_hours_only: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    biz_start: Mapped[datetime] = mapped_column(
        Time,
        nullable=False,
        default=datetime.strptime("09:00", "%H:%M").time,
    )
    biz_end: Mapped[datetime] = mapped_column(
        Time,
        nullable=False,
        default=datetime.strptime("17:00", "%H:%M").time,
    )
    biz_days: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
        default="mtwtf",
    )
    escalation_levels: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )


class TicketTrigger(Base):
    """Automatisierungsregel für Tickets (condition -> perform)."""

    __tablename__ = "ticket_trigger"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(20), nullable=False)
    condition: Mapped[dict] = mapped_column(JSONB, nullable=False)
    perform: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
