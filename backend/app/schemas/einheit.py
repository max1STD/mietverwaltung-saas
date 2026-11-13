"""Pydantic-Schemas für Wohneinheiten."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class EinheitBase(BaseModel):
    """Gemeinsame Felder für Einheit-Schemas."""

    objekt_id: int
    name: str = Field(..., min_length=1, max_length=100)
    size_qm: Decimal = Field(..., gt=0)
    rooms: int = Field(..., ge=1)
    rent_cold: Decimal = Field(..., ge=0)
    floor: str | None = Field(None, max_length=20)
    energy_class: str | None = Field(None, max_length=2)
    last_renovation: date | None = None
    available_from: date | None = None


class EinheitCreate(EinheitBase):
    """Payload für das Anlegen einer Einheit."""

    pass


class EinheitUpdate(BaseModel):
    """Payload für das Aktualisieren einer Einheit (alle Felder optional)."""

    model_config = ConfigDict(extra="ignore")

    name: str | None = Field(None, min_length=1, max_length=100)
    size_qm: Decimal | None = Field(None, gt=0)
    rooms: int | None = Field(None, ge=1)
    rent_cold: Decimal | None = Field(None, ge=0)
    floor: str | None = Field(None, max_length=20)
    energy_class: str | None = Field(None, max_length=2)
    last_renovation: date | None = None
    available_from: date | None = None


class EinheitNestedMieter(BaseModel):
    """Kompakte Mieter-Info für die Einheit-Detailansicht."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    status: str


class EinheitResponse(EinheitBase):
    """Vollständige Einheit-Daten in API-Responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vermieter_id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    aktueller_mieter: EinheitNestedMieter | None = None
    vermietungsstatus: str = "frei"
