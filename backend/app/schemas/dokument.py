"""Schemas für Dokumenten-Generierung und Upload."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class DokumentGenerateRequest(BaseModel):
    template: str = Field(..., min_length=1)
    mieter_id: int = Field(..., ge=1)
    extra: dict | None = None


class DokumentGenerateResponse(BaseModel):
    dokument_id: int
    download_url: str
    template: str


class DokumentUploadResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    titel: str
    typ: str
    jahr: int | None
    file_name: str
    file_size: int
    content_type: str
    status: str
    storage_path: str | None = None
    created_at: datetime
    upload_error: str | None = None


class DokumentListResponse(BaseModel):
    items: list[DokumentUploadResponse]


class DokumentDeleteResponse(BaseModel):
    id: int
    deleted: bool = True
