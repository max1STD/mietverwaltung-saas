"""Schemas für Dokumenten-Generierung."""
from __future__ import annotations

from pydantic import BaseModel, Field


class DokumentGenerateRequest(BaseModel):
    template: str = Field(..., min_length=1)
    mieter_id: int = Field(..., ge=1)
    extra: dict | None = None


class DokumentGenerateResponse(BaseModel):
    dokument_id: int
    download_url: str
    template: str
