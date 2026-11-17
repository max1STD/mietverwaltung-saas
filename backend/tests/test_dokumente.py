"""Tests für Dokumenten-Upload und lokale Speicherung (Paperless deaktiviert)."""
from __future__ import annotations

from io import BytesIO

import pytest
from fastapi import status

from app.config import settings

pytestmark = pytest.mark.asyncio


async def test_upload_document_local_fallback(auth_client, db_session):
    """Wenn Paperless deaktiviert ist, wird das Dokument lokal gespeichert."""
    original = settings.PAPERLESS_ENABLED
    settings.PAPERLESS_ENABLED = False
    try:
        data = {
            "entity_type": "objekt",
            "entity_id": "1",
            "titel": "Test Dokument",
            "typ": "rechnung",
            "jahr": "2024",
        }
        files = {
            "file": ("test.pdf", BytesIO(b"%PDF-1.4 test content"), "application/pdf"),
        }
        resp = await auth_client.post("/api/v1/dokumente/upload", data=data, files=files)
        assert resp.status_code == status.HTTP_200_OK, resp.text
        result = resp.json()
        assert result["titel"] == "Test Dokument"
        assert result["entity_type"] == "objekt"
        assert result["entity_id"] == 1
        assert result["content_type"] == "application/pdf"
        assert result["storage_path"] is not None
        assert result["upload_error"] is not None  # "Paperless deaktiviert"

        # Liste prüfen
        list_resp = await auth_client.get("/api/v1/dokumente/?entity_type=objekt&entity_id=1")
        assert list_resp.status_code == 200
        assert len(list_resp.json()["items"]) >= 1
    finally:
        settings.PAPERLESS_ENABLED = original
