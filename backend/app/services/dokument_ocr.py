"""OCR-Orchestration fuer Dokumente — nutzt app.services.ocr.tesseract."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dokument import Dokument
from app.services.ocr.tesseract import extract_text

logger = logging.getLogger(__name__)


async def run_ocr_for_dokument(
    db: AsyncSession,
    dokument: Dokument,
    content: bytes | None = None,
) -> None:
    """Fuehrt OCR fuer ein Dokument durch und aktualisiert DB-Eintrag."""
    from datetime import UTC, datetime

    if dokument.content_type not in {"application/pdf"} and not dokument.content_type.startswith("image/"):
        dokument.ocr_status = "error"
        dokument.ocr_text = None
        dokument.ocr_engine = "tesseract"
        return

    try:
        if content is None and dokument.storage_path:
            text = extract_text(dokument.storage_path, dokument.content_type)
        elif content is not None:
            # Temporaere Datei anlegen, weil tesseract-Wrapper Pfad erwartet
            import tempfile  # noqa: PLC0415

            suffix = ".pdf" if dokument.content_type == "application/pdf" else ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            try:
                text = extract_text(tmp_path, dokument.content_type)
            finally:
                Path(tmp_path).unlink(missing_ok=True)
        else:
            dokument.ocr_status = "error"
            return

        dokument.ocr_text = text if text else None
        dokument.ocr_status = "done" if text else "error"
        dokument.ocr_engine = "tesseract"
        dokument.ocr_finished_at = datetime.now(UTC)
    except Exception as exc:
        logger.error("OCR failed for dokument %s: %s", dokument.id, exc)
        dokument.ocr_status = "error"
        dokument.ocr_engine = "tesseract"
        dokument.ocr_finished_at = datetime.now(UTC)

    await db.flush()
    await db.refresh(dokument)


__all__ = ["run_ocr_for_dokument"]
