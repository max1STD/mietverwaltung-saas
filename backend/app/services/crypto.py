"""AES-256-GCM Verschlüsselung für sensitive Felder (IBAN, BIC, Steuernr, Geburtsdatum).

Neue Ciphertexte enthalten einen Versions-Header, der Schlüsselrotation und
zukünftige Algorithmus-Wechsel ermöglicht:

    [1 Byte Version] [12 Byte Nonce] [Ciphertext + 16 Byte GCM-Tag]

Version 1 (0x01) verwendet AES-256-GCM mit zufälliger Nonce und optionalem AAD.
Alte Ciphertexte ohne Header werden weiterhin erkannt und entschlüsselt,
sofern sie mindestens 28 Bytes lang sind.
"""
from __future__ import annotations

import base64
import hmac
import secrets
import warnings
from typing import cast

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.config import settings


class EncryptionError(Exception):
    """Wird geworfen, wenn ein kryptographischer Vorgang fehlschlägt."""

    pass


_CURRENT_CIPHER_VERSION = 1
_MIN_HEADER_LEN = 13  # 1 Version + 12 Nonce
_MIN_CIPHERTEXT_LEN = 28  # 12 Nonce + 16 Tag (Legacy, ohne Header)


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


def _is_default_key() -> bool:
    """Heuristischer Check, ob der konfigurierte Key ein Dummy/Beispiel ist."""
    raw = (settings.DB_ENCRYPTION_KEY or "").strip()
    if not raw:
        return True
    lowered = raw.lower()
    dummy_tokens = {
        "change-me",
        "changeme",
        "placeholder",
        "example",
        "default",
        "test",
        "secret",
        "your-key",
        "your_key",
        "todo",
    }
    return any(token in lowered for token in dummy_tokens) or len(raw) < 20


def _warn_if_insecure_key() -> None:
    """Warnt im Dev-Modus, wenn ein offensichtlich unsicherer Key verwendet wird."""
    if _is_default_key() and settings.ENVIRONMENT != "production":
        warnings.warn(
            "DB_ENCRYPTION_KEY sieht nach einem Platzhalter aus. "
            "Für Production muss ein echter 32-Byte Base64-Schlüssel gesetzt werden.",
            stacklevel=4,
        )


def _derive_aad(context: str | None) -> bytes | None:
    """Berechnet AAD aus einem optionalen Kontext-String.

    AAD schützt vor Context-Confusion: ein Ciphertext, der z. B. für die
    Spalte `users.steuernr_enc` erstellt wurde, kann nicht als `iban_enc`
    eingeschleust werden, weil das GCM-Tag nicht mehr passt.
    """
    if context is None:
        return None
    return f"mietverwaltung:v1:{context}".encode("utf-8")


def encrypt_value(plaintext: str | None, context: str | None = None) -> bytes | None:
    """Verschlüsselt einen String mit AES-256-GCM (Version 1).

    Args:
        plaintext: Der zu verschlüsselnde Klartext.
        context: Optionaler Kontext (z. B. Tabellen- und Spaltenname), der in
            das GCM-AAD einfließt, um Context-Confusion zu verhindern.

    Returns:
        bytes im Format [version:1][nonce:12][ciphertext+tag] oder None.
    """
    if plaintext is None:
        return None
    _warn_if_insecure_key()
    key = _get_key()
    nonce = secrets.token_bytes(12)
    aad = _derive_aad(context)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), aad)
    # ciphertext enthält bereits den 16-Byte GCM-Tag am Ende
    return bytes([_CURRENT_CIPHER_VERSION]) + nonce + ciphertext


def decrypt_value(ciphertext: bytes | None, context: str | None = None) -> str | None:
    """Entschlüsselt AES-256-GCM Daten im neuen (und Legacy-)Format.

    Args:
        ciphertext: Verschlüsselte Daten mit oder ohne Versions-Header.
        context: Optionaler Kontext, der beim Verschlüsseln verwendet wurde.

    Returns:
        Entschlüsselter Klartext oder None.

    Raises:
        EncryptionError: Bei beschädigtem/verfälschtem Ciphertext oder falschem Key.
    """
    if ciphertext is None:
        return None
    _warn_if_insecure_key()

    if len(ciphertext) < _MIN_CIPHERTEXT_LEN:
        raise EncryptionError("Ciphertext zu kurz")

    key = _get_key()
    aad = _derive_aad(context)

    # Neues Format mit Versions-Header?
    version = ciphertext[0]
    if version == _CURRENT_CIPHER_VERSION and len(ciphertext) >= _MIN_HEADER_LEN + 16:
        nonce = bytes(ciphertext[1:13])
        encrypted = bytes(ciphertext[13:])
    else:
        # Legacy-Format: alles ist Nonce + Ciphertext + Tag
        version = 0
        nonce = bytes(ciphertext[:12])
        encrypted = bytes(ciphertext[12:])

    # Zukünftige Versionen ablehnen (Migration erforderlich)
    if version not in (0, _CURRENT_CIPHER_VERSION):
        raise EncryptionError(f"Nicht unterstützte Ciphertext-Version: {version}")

    aesgcm = AESGCM(key)
    try:
        plaintext = aesgcm.decrypt(nonce, encrypted, aad)
    except Exception as exc:
        raise EncryptionError("Entschlüsselung fehlgeschlagen") from exc
    return cast(str, plaintext.decode("utf-8"))


def generate_encryption_key() -> str:
    """Erzeugt einen neuen Base64-kodierten 32-Byte-Schlüssel."""
    return base64.b64encode(secrets.token_bytes(32)).decode("ascii")


def reencrypt_value(
    ciphertext: bytes | None,
    old_context: str | None = None,
    new_context: str | None = None,
) -> bytes | None:
    """Entschlüsselt und verschlüsselt einen Wert neu (z. B. nach Key-Rotation).

    Returns:
        Neu verschlüsselter Ciphertext oder None.
    """
    if ciphertext is None:
        return None
    plaintext = decrypt_value(ciphertext, context=old_context)
    return encrypt_value(plaintext, context=new_context)


def constant_time_compare(a: bytes, b: bytes) -> bool:
    """Zeitkonstanter Byte-Vergleich — nützlich für interne Prüfsummen/Token."""
    return hmac.compare_digest(a, b)
