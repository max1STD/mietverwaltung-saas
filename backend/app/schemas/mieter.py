"""Pydantic-Schemas für Mieter."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class MieterBase(BaseModel):
    """Gemeinsame Felder für Mieter-Schemas (Frontend-kompatibel)."""

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr | None = None
    telefon: str | None = Field(None, max_length=30)
    geburtsdatum: date | None = None
    adresse: str | None = Field(None, max_length=255)
    notizen: str | None = Field(None, max_length=2000)
    status: str = Field(default="aktiv", pattern="^(aktiv|ehemalig|bewerber)$")
    since: date | None = None


class MieterCreate(MieterBase):
    """Payload für das Anlegen eines Mieters."""

    pass


class MieterUpdate(BaseModel):
    """Payload für das Aktualisieren eines Mieters (alle Felder optional)."""

    model_config = ConfigDict(extra="ignore")

    name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    telefon: str | None = Field(None, max_length=30)
    geburtsdatum: date | None = None
    adresse: str | None = Field(None, max_length=255)
    notizen: str | None = Field(None, max_length=2000)
    status: str | None = Field(None, pattern="^(aktiv|ehemalig|bewerber)$")
    since: date | None = None


class MieterNestedEinheit(BaseModel):
    """Kompakte Einheit-Info für die Mieter-Detailansicht."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    objekt_name: str


class MieterResponse(BaseModel):
    """Vollständige Mieter-Daten in API-Responses (Frontend-kompatibel)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vermieter_id: int
    name: str
    email: str | None = None
    telefon: str | None = None
    geburtsdatum: date | None = None
    adresse: str | None = None
    notizen: str | None = None
    status: str
    since: date | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    aktuelle_einheit: MieterNestedEinheit | None = None
