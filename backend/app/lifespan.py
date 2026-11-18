"""Application lifespan: startup and shutdown events."""
from __future__ import annotations

import structlog
from fastapi import FastAPI

from app.config import settings
from app.services.crypto import EncryptionError, _get_key, _is_default_key

logger = structlog.get_logger()


async def startup(app: FastAPI) -> None:
    """Wird beim Start der Anwendung ausgefuehrt."""
    logger.info("app.starting", environment=settings.ENVIRONMENT)

    # Production: DB_ENCRYPTION_KEY muss ein echter, 32-Byte Base64-Schluessel sein.
    if settings.ENVIRONMENT == "production":
        if not settings.DB_ENCRYPTION_KEY:
            raise EncryptionError(
                "DB_ENCRYPTION_KEY ist in Production nicht gesetzt. "
                "Die Anwendung kann ohne verschluesselte Daten nicht starten."
            )
        try:
            key = _get_key()
            if len(key) != 32:
                raise EncryptionError("AES-Schluessel muss 32 Bytes haben")
        except Exception as exc:
            raise EncryptionError(
                "DB_ENCRYPTION_KEY ist ungueltig oder kein 32-Byte Base64-Schluessel"
            ) from exc

        if _is_default_key():
            raise EncryptionError(
                "DB_ENCRYPTION_KEY sieht in Production nach einem Platzhalter aus. "
                "Bitte einen frisch generierten Schluessel setzen."
            )

    # Development/Test: Key-Validitaet pruefen, aber App trotzdem starten.
    else:
        try:
            _get_key()
        except EncryptionError:
            logger.warning(
                "db_encryption_key_missing_or_invalid",
                environment=settings.ENVIRONMENT,
                message="DB_ENCRYPTION_KEY fehlt oder ist ungueltig — Verschlüsselung wird bei Verwendung fehlschlagen.",
            )


async def shutdown(app: FastAPI) -> None:
    logger.info("app.stopping")
