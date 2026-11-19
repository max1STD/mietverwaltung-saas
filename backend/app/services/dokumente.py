"""Dokumenten-Service — Orchestration zwischen Paperless-ngx und lokalem Speicher.

Wenn `PAPERLESS_ENABLED=true`, werden Dokumente in Paperless-ngx abgelegt.
Pro Vermieter wird ein Paperless-Benutzer erstellt; der Token wird verschlüsselt
in der User-Tabelle gespeichert.

Wenn Paperless deaktiviert ist, wird das Dokument lokal im Dateisystem abgelegt.
Das Frontend merkt den Unterschied nicht.
"""
from __future__ import annotations

import logging
import os
import uuid
from datetime import date
from io import BytesIO
from pathlib import Path
from typing import Any

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.dokument import Dokument
from app.models.einheit import Einheit
from app.models.objekt import Objekt
from app.models.user import User
from app.services.crypto import decrypt_value, encrypt_value
from app.services.dokument_ocr import run_ocr_for_dokument
from app.services.paperless import PaperlessAPIError, PaperlessClient, PaperlessConfigError

logger = logging.getLogger(__name__)

ALLOWED_CONTENT_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/msword": ".doc",
    "text/plain": ".txt",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class DokumentValidationError(Exception):
    """Validierungsfehler beim Upload."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(message)


class DokumentService:
    """Zentrale Schnittstelle für Dokument-Uploads, Liste, Download, Löschen."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.local_storage_root = Path(
            os.environ.get("DOKUMENT_STORAGE_PATH", "/var/lib/mietverwaltung/dokumente")
        )
        self.paperless_enabled = settings.PAPERLESS_ENABLED
        self.paperless = PaperlessClient() if self.paperless_enabled else None

    async def _get_vermieter(self, vermieter_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == vermieter_id))
        return result.scalar_one_or_none()

    async def _validate_entity_ownership(
        self,
        vermieter_id: int,
        entity_type: str,
        entity_id: int,
    ) -> None:
        """Stellt sicher, dass die Zielentität dem Vermieter gehört."""
        if entity_type == "objekt":
            result = await self.db.execute(
                select(Objekt).where(
                    Objekt.id == entity_id,
                    Objekt.vermieter_id == vermieter_id,
                    Objekt.deleted_at.is_(None),
                )
            )
            if result.scalar_one_or_none() is None:
                raise DokumentValidationError(
                    "entity_id", "Objekt nicht gefunden oder nicht berechtigt"
                )
        elif entity_type == "einheit":
            result = await self.db.execute(
                select(Einheit).where(
                    Einheit.id == entity_id,
                    Einheit.vermieter_id == vermieter_id,
                    Einheit.deleted_at.is_(None),
                )
            )
            if result.scalar_one_or_none() is None:
                raise DokumentValidationError(
                    "entity_id", "Einheit nicht gefunden oder nicht berechtigt"
                )

    async def _get_or_create_paperless_user(self, user: User) -> tuple[int, str]:
        if user.paperless_user_id and user.paperless_token_enc:
            token = decrypt_value(user.paperless_token_enc, context="users:paperless_token")
            if token:
                return user.paperless_user_id, token
        if not self.paperless:
            raise PaperlessConfigError("Paperless nicht aktiviert")
        pl_user = await self.paperless.get_or_create_user(
            vermieter_id=user.id,
            email=user.email or f"vermieter_{user.id}@mietverwaltung.local",
            first_name=user.first_name or "",
            last_name=user.last_name or "",
        )
        encrypted_token = encrypt_value(pl_user.token, context="users:paperless_token")
        user.paperless_user_id = pl_user.id
        user.paperless_token_enc = encrypted_token
        await self.db.flush()
        return pl_user.id, pl_user.token

    async def _ensure_local_storage(self) -> None:
        self.local_storage_root.mkdir(parents=True, exist_ok=True)

    def _local_path(self, vermieter_id: int, entity_type: str, entity_id: int, filename: str) -> Path:
        folder = self.local_storage_root / f"vermieter_{vermieter_id}" / entity_type / str(entity_id)
        folder.mkdir(parents=True, exist_ok=True)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        return folder / unique_name

    async def upload(
        self,
        vermieter_id: int,
        entity_type: str,
        entity_id: int,
        upload: UploadFile,
        titel: str,
        typ: str = "sonstiges",
        jahr: int | None = None,
    ) -> Dokument:
        """Speichert ein Dokument (Paperless oder lokal) und legt den DB-Eintrag an."""
        if entity_type not in {"objekt", "einheit", "mieter", "mietvertrag", "ticket"}:
            raise DokumentValidationError("entity_type", "Ungültiger Entitätstyp")
        if not upload.filename:
            raise DokumentValidationError("file", "Dateiname fehlt")
        content = await upload.read()
        if len(content) == 0:
            raise DokumentValidationError("file", "Datei ist leer")
        if len(content) > MAX_FILE_SIZE:
            raise DokumentValidationError("file", "Datei zu groß (max. 10 MB)")
        if upload.content_type not in ALLOWED_CONTENT_TYPES:
            raise DokumentValidationError("file", "Dateityp nicht erlaubt")

        await self._validate_entity_ownership(vermieter_id, entity_type, entity_id)

        user = await self._get_vermieter(vermieter_id)
        if not user:
            raise DokumentValidationError("vermieter_id", "Vermieter nicht gefunden")

        extension = ALLOWED_CONTENT_TYPES[upload.content_type]
        safe_filename = f"{Path(upload.filename).stem}{extension}"

        paperless_document_id: int | None = None
        paperless_user_id: int | None = None
        storage_path: str | None = None
        upload_error: str | None = None

        if self.paperless_enabled and self.paperless:
            try:
                pl_user_id, pl_token = await self._get_or_create_paperless_user(user)
                paperless_user_id = pl_user_id
                tags = await self.paperless.ensure_tags([entity_type, typ])
                result = await self.paperless.upload_document(
                    user_token=pl_token,
                    file=BytesIO(content),
                    filename=safe_filename,
                    title=titel,
                    tag_ids=tags,
                    created_at=date.today().isoformat(),
                )
                # Paperless liefert bei async-Upload task_id; id bei direktem Upload
                raw_id = result.get("id") or result.get("task_id")
                paperless_document_id = int(raw_id) if raw_id is not None else None
            except (PaperlessAPIError, PaperlessConfigError) as exc:
                logger.error("Paperless upload failed, falling back to local: %s", exc)
                upload_error = f"Paperless-Fehler: {exc}"
        else:
            upload_error = "Paperless deaktiviert"

        if not paperless_document_id:
            await self._ensure_local_storage()
            local_path = self._local_path(vermieter_id, entity_type, entity_id, safe_filename)
            with open(local_path, "wb") as f:
                f.write(content)
            storage_path = str(local_path)

        dokument = Dokument(
            vermieter_id=vermieter_id,
            entity_type=entity_type,
            entity_id=entity_id,
            paperless_document_id=paperless_document_id,
            paperless_user_id=paperless_user_id,
            status="pending" if paperless_document_id and not upload_error else "bereit",
            ocr_status="pending",
            typ=typ,
            titel=titel,
            jahr=jahr,
            file_name=safe_filename,
            file_size=len(content),
            content_type=upload.content_type,
            storage_path=storage_path,
            upload_error=upload_error,
        )

        # Lokale OCR fuer alle Dokumente (Paperless uebernimmt spaeter)
        try:
            await run_ocr_for_dokument(self.db, dokument, content)
        except Exception as exc:
            logger.error("OCR failed for uploaded dokument: %s", exc)
            dokument.ocr_status = "error"

        self.db.add(dokument)
        await self.db.flush()
        await self.db.refresh(dokument)
        return dokument

    async def list_documents(
        self,
        vermieter_id: int,
        entity_type: str | None = None,
        entity_id: int | None = None,
    ) -> list[Dokument]:
        query = select(Dokument).where(
            Dokument.vermieter_id == vermieter_id,
            Dokument.deleted_at.is_(None),
        )
        if entity_type:
            query = query.where(Dokument.entity_type == entity_type)
        if entity_id is not None:
            query = query.where(Dokument.entity_id == entity_id)
        result = await self.db.execute(query.order_by(Dokument.created_at.desc()))
        return list(result.scalars().all())

    async def get_document(self, vermieter_id: int, dokument_id: int) -> Dokument | None:
        result = await self.db.execute(
            select(Dokument).where(
                Dokument.id == dokument_id,
                Dokument.vermieter_id == vermieter_id,
                Dokument.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def download(self, dokument: Dokument) -> tuple[bytes, str]:
        """Liefert die Rohbytes und den Content-Type eines Dokuments."""
        if dokument.paperless_document_id and dokument.paperless_user_id and self.paperless:
            user = await self._get_vermieter(dokument.vermieter_id)
            if user and user.paperless_token_enc:
                token = decrypt_value(user.paperless_token_enc, context="users:paperless_token")
                if token:
                    content = await self.paperless.download_document(token, dokument.paperless_document_id)
                    return content, dokument.content_type
        if dokument.storage_path and Path(dokument.storage_path).exists():
            with open(dokument.storage_path, "rb") as f:
                return f.read(), dokument.content_type
        raise FileNotFoundError("Dokument nicht gefunden")

    async def preview(self, dokument: Dokument) -> tuple[bytes, str]:
        """Liefert eine Vorschau (PDF/PNG) des Dokuments."""
        if dokument.paperless_document_id and dokument.paperless_user_id and self.paperless:
            user = await self._get_vermieter(dokument.vermieter_id)
            if user and user.paperless_token_enc:
                token = decrypt_value(user.paperless_token_enc, context="users:paperless_token")
                if token:
                    content = await self.paperless.preview_document(token, dokument.paperless_document_id)
                    return content, "application/pdf"
        if dokument.content_type.startswith("image/") and dokument.storage_path:
            with open(dokument.storage_path, "rb") as f:
                return f.read(), dokument.content_type
        raise FileNotFoundError("Vorschau nicht verfügbar")

    async def delete(self, dokument: Dokument) -> None:
        """Löscht ein Dokument physisch und aus der DB."""
        if dokument.paperless_document_id and dokument.paperless_user_id and self.paperless:
            user = await self._get_vermieter(dokument.vermieter_id)
            if user and user.paperless_token_enc:
                try:
                    token = decrypt_value(user.paperless_token_enc, context="users:paperless_token")
                    if token:
                        await self.paperless.delete_document(token, dokument.paperless_document_id)
                except Exception as exc:
                    logger.error("Paperless delete failed: %s", exc)
        if dokument.storage_path and Path(dokument.storage_path).exists():
            try:
                Path(dokument.storage_path).unlink()
            except Exception as exc:
                logger.error("Local file delete failed: %s", exc)
        await self.db.delete(dokument)
        await self.db.flush()
