"""Dokumenten-Modell — Verknüpfung zu Paperless-ngx oder lokalem Speicher."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Dokument(Base, TimestampMixin, SoftDeleteMixin):
    """Ein Dokument, das einem Vermieter und einer Entität zugeordnet ist.

    Der eigentliche Inhalt liegt entweder in Paperless-ngx (preferred)
    oder – bei PAPERLESS_ENABLED=false – auf dem lokalen Speicher.
    """

    __tablename__ = "dokumente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vermieter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entity_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )  # objekt | einheit | mieter | mietvertrag
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    paperless_document_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )
    paperless_user_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Status der Verarbeitung (relevant für async OCR)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="bereit",
    )  # pending | bereit | fehler

    typ: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="sonstiges",
    )  # mietvertrag | nebenkostenabrechnung | korrespondenz | foto | rechnung | sonstiges
    titel: Mapped[str] = mapped_column(String(255), nullable=False)
    jahr: Mapped[int | None] = mapped_column(Integer, nullable=True)

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Fallback-Pfad für lokale Speicherung, wenn Paperless deaktiviert ist.
    storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    upload_error: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Beziehungen
    vermieter: Mapped[User] = relationship("User", foreign_keys=[vermieter_id])

    __table_args__ = (
        # Schnelle Lookups pro Entität
        {"comment": "Dokumente, die Mieter, Objekte, Einheiten oder Verträgen zugeordnet sind."},
    )
