"""Subscription-Modell — WE-basiertes Abo mit Stripe-IDs."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DECIMAL,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Subscription(Base, TimestampMixin):
    """Ein aktives Abonnement für einen Vermieter."""

    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Preisgestaltung
    price_per_we: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2),
        nullable=False,
    )
    billing_cycle: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="yearly",
    )

    # Stripe-Referenzen
    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Abo-Lebenszyklus
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="trial",
    )
    trial_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Beziehungen
    user: Mapped[User] = relationship("User", back_populates="subscription")
