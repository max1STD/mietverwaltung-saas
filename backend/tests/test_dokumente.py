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
        # Objekt anlegen, an das das Dokument gebunden wird
        obj_resp = await auth_client.post(
            "/api/v1/objekte",
            json={
                "name": "Dokumenten-Testobjekt",
                "address": "Teststr. 1",
                "plz": "12345",
                "ort": "Teststadt",
            },
        )
        assert obj_resp.status_code == 201
        objekt_id = obj_resp.json()["id"]

        data = {
            "entity_type": "objekt",
            "entity_id": str(objekt_id),
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
        assert result["entity_id"] == objekt_id
        assert result["content_type"] == "application/pdf"
        assert result["storage_path"] is not None
        assert result["upload_error"] is not None  # "Paperless deaktiviert"

        # Liste prüfen
        list_resp = await auth_client.get(f"/api/v1/dokumente/?entity_type=objekt&entity_id={objekt_id}")
        assert list_resp.status_code == 200
        assert len(list_resp.json()["items"]) >= 1
    finally:
        settings.PAPERLESS_ENABLED = original



async def test_upload_to_fremdes_objekt_scheitert(auth_client, db_session, vermieter_user):
    """Dokument-Upload an ein fremdes/nicht existentes Objekt wird abgelehnt."""
    original = settings.PAPERLESS_ENABLED
    settings.PAPERLESS_ENABLED = False
    try:
        data = {
            "entity_type": "objekt",
            "entity_id": "999999",
            "titel": "Fremdes Objekt",
            "typ": "sonstiges",
        }
        files = {
            "file": ("test.pdf", BytesIO(b"%PDF-1.4 test content"), "application/pdf"),
        }
        resp = await auth_client.post("/api/v1/dokumente/upload", data=data, files=files)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "Objekt nicht gefunden" in str(resp.json()["detail"])
    finally:
        settings.PAPERLESS_ENABLED = original
