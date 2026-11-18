"""Tests für Verschlüsselungsfunktionen."""
from __future__ import annotations

import base64
import os

import pytest

from app.services.crypto import (
    EncryptionError,
    decrypt_value,
    encrypt_value,
    generate_encryption_key,
    reencrypt_value,
)


def test_generate_encryption_key_is_valid() -> None:
    """Generierter Schlüssel ist 32 Bytes Base64."""
    key = generate_encryption_key()
    decoded = base64.b64decode(key, validate=True)
    assert len(decoded) == 32


def test_encrypt_decrypt_roundtrip(monkeypatch) -> None:
    """Verschlüsselung und Entschlüsselung mit AAD liefern Original."""
    key = generate_encryption_key()
    monkeypatch.setenv("DB_ENCRYPTION_KEY", key)
    # app.config wird beim Import geladen; Settings-Instanz neu laden
    from app.config import Settings

    settings = Settings()
    monkeypatch.setattr("app.services.crypto.settings", settings)

    plaintext = "DE89370400440532013000"
    ciphertext = encrypt_value(plaintext, context="bankverbindungen:iban")
    assert ciphertext is not None
    assert len(ciphertext) > 28
    assert decrypt_value(ciphertext, context="bankverbindungen:iban") == plaintext


def test_decrypt_with_wrong_context_fails(monkeypatch) -> None:
    """AAD bindet den Ciphertext an den Kontext."""
    key = generate_encryption_key()
    monkeypatch.setenv("DB_ENCRYPTION_KEY", key)
    from app.config import Settings

    settings = Settings()
    monkeypatch.setattr("app.services.crypto.settings", settings)

    ciphertext = encrypt_value("secret", context="users:steuernr")
    with pytest.raises(EncryptionError):
        decrypt_value(ciphertext, context="bankverbindungen:iban")


def test_legacy_decrypt_without_header(monkeypatch) -> None:
    """Alte Ciphertexte ohne Versions-Header lassen sich weiterhin entschlüsseln."""
    key = generate_encryption_key()
    monkeypatch.setenv("DB_ENCRYPTION_KEY", key)
    from app.config import Settings

    settings = Settings()
    monkeypatch.setattr("app.services.crypto.settings", settings)

    # Manuell Legacy-Format bauen: nonce(12) || ciphertext+tag
    import secrets
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    raw_key = base64.b64decode(key)
    nonce = secrets.token_bytes(12)
    aesgcm = AESGCM(raw_key)
    encrypted = aesgcm.encrypt(nonce, b"legacy-value", None)
    legacy = nonce + encrypted

    assert decrypt_value(legacy) == "legacy-value"


def test_reencrypt_value(monkeypatch) -> None:
    """Reencrypt liefert neuen, gültigen Ciphertext."""
    key = generate_encryption_key()
    monkeypatch.setenv("DB_ENCRYPTION_KEY", key)
    from app.config import Settings

    settings = Settings()
    monkeypatch.setattr("app.services.crypto.settings", settings)

    ciphertext = encrypt_value("value", context="ctx:old")
    new = reencrypt_value(ciphertext, old_context="ctx:old", new_context="ctx:new")
    assert decrypt_value(new, context="ctx:new") == "value"


def test_missing_key_raises(monkeypatch) -> None:
    """Ohne Schlüssel wird EncryptionError geworfen."""
    monkeypatch.setenv("DB_ENCRYPTION_KEY", "")
    from app.config import Settings

    settings = Settings()
    monkeypatch.setattr("app.services.crypto.settings", settings)

    with pytest.raises(EncryptionError):
        encrypt_value("x")


def test_invalid_key_length_raises(monkeypatch) -> None:
    """Schlüssel falscher Länge wird abgelehnt."""
    monkeypatch.setenv("DB_ENCRYPTION_KEY", base64.b64encode(b"short").decode())
    from app.config import Settings

    settings = Settings()
    monkeypatch.setattr("app.services.crypto.settings", settings)

    with pytest.raises(EncryptionError):
        encrypt_value("x")
