"""Pydantic-Schemas für Mieter."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class MieterBase(BaseModel):
    """Gemeinsame Felder für Mieter-Schemas."""

    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=30)
    birth_date: date | None = None
    status: str = Field(default="aktiv", pattern="^(aktiv|ehemalig|bewerber)$")
    since: date | None = None


class MieterCreate(MieterBase):
    """Payload für das Anlegen eines Mieters."""

    pass


class MieterUpdate(BaseModel):
    """Payload für das Aktualisieren eines Mieters (alle Felder optional)."""

    model_config = ConfigDict(extra="ignore")

    first_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str | None = Field(None, min_length=1, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=30)
    birth_date: date | None = None
    status: str | None = Field(None, pattern="^(aktiv|ehemalig|bewerber)$")
    since: date | None = None


class MieterNestedEinheit(BaseModel):
    """Kompakte Einheit-Info für die Mieter-Detailansicht."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    objekt_name: str


class MieterResponse(MieterBase):
    """Vollständige Mieter-Daten in API-Responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vermieter_id: int
    full_name: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    aktuelle_einheit: MieterNestedEinheit | None = None
