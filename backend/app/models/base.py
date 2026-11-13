"""Gemeinsame SQLAlchemy-Basisklasse und Mixins für MietVerwaltung."""
from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative Base für alle ORM-Modelle."""

    pass


class TimestampMixin:
    """Automatische created_at / updated_at Zeitstempel (UTC)."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class SoftDeleteMixin:
    """Soft-Delete: Datensätze werden nicht physisch gelöscht."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
