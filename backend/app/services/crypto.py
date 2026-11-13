"""AES-256-GCM Verschlüsselung für sensitive Felder (IBAN, Steuernr, Geburtsdatum)."""
import base64
import os
import secrets
from typing import cast

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.config import settings


class EncryptionError(Exception):
    """Wird geworfen, wenn ein kryptographischer Vorgang fehlschlägt."""

    pass


def _get_key() -> bytes:
    """Lädt den 32-Byte AES-Schlüssel aus DB_ENCRYPTION_KEY (Base64)."""
    if not settings.DB_ENCRYPTION_KEY:
        raise EncryptionError("DB_ENCRYPTION_KEY nicht gesetzt")
    try:
        key = base64.b64decode(settings.DB_ENCRYPTION_KEY, validate=True)
    except Exception as exc:
        raise EncryptionError("DB_ENCRYPTION_KEY ist kein gültiges Base64") from exc
    if len(key) != 32:
        raise EncryptionError(f"AES-Schlüssel muss 32 Bytes haben, hat {len(key)}")
    return key


def encrypt_value(plaintext: str | None) -> bytes | None:
    """Verschlüsselt einen String mit AES-256-GCM.

    Format: nonce (12 Bytes) || ciphertext || tag (16 Bytes).
    """
    if plaintext is None:
        return None
    key = _get_key()
    nonce = secrets.token_bytes(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    # ciphertext enthält bereits den 16-Byte GCM-Tag am Ende
    return nonce + ciphertext


def decrypt_value(ciphertext: bytes | None) -> str | None:
    """Entschlüsselt AES-256-GCM Daten im Format nonce || ciphertext || tag."""
    if ciphertext is None:
        return None
    if len(ciphertext) < 28:  # 12 Nonce + mindestens 16 Tag
        raise EncryptionError("Ciphertext zu kurz")
    key = _get_key()
    nonce = bytes(ciphertext[:12])
    encrypted = bytes(ciphertext[12:])
    aesgcm = AESGCM(key)
    try:
        plaintext = aesgcm.decrypt(nonce, encrypted, None)
    except Exception as exc:
        raise EncryptionError("Entschlüsselung fehlgeschlagen") from exc
    return cast(str, plaintext.decode("utf-8"))


def generate_encryption_key() -> str:
    """Erzeugt einen neuen Base64-kodierten 32-Byte-Schlüssel."""
    return base64.b64encode(secrets.token_bytes(32)).decode("ascii")
