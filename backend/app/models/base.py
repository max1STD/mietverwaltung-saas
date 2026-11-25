"""Gemeinsame SQLAlchemy-Basisklasse und Mixins für MietVerwaltung."""
from datetime import UTC, datetime

from sqlalchemy import DateTime, String
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


class RetentionMixin:
    """DSGVO-konforme Aufbewahrung: aktiv / gesperrt / geloescht.

    Erweitert Soft-Delete um eindeutige Lifecycle-Zustände, Löschklassen,
    Fristen und Legal-Hold. Nicht für Tabellen mit eigenem Status-Workflow.
    """

    lifecycle_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="aktiv",
    )  # aktiv | gesperrt | geloescht
    gesperrt_am: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    loeschklasse: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        default=None,
    )  # K1 .. K12
    loeschen_fruehestens_am: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    legal_hold: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )
