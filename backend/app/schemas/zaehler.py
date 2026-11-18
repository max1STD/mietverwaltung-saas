"""Pydantic-Schemas für Zähler und Ablesungen."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ZaehlerBase(BaseModel):
    """Gemeinsame Felder für Zähler-Schemas."""

    bezeichnung: str = Field(..., min_length=1, max_length=100)
    zaehlernummer: str | None = Field(None, max_length=100)
    typ: str = Field(..., pattern="^(strom|gas|wasser|waerme|kaltwasser|sonstiges)$")
    einheit: str = Field(
        default="kwh",
        pattern="^(kwh|m3|litre|kwh_m3|sonstiges)$",
    )
    ist_hauptzaehler: bool = False


class ZaehlerCreate(ZaehlerBase):
    """Payload für das Anlegen eines Zählers."""

    einheit_id: int


class ZaehlerUpdate(BaseModel):
    """Payload für das Aktualisieren eines Zählers."""

    model_config = ConfigDict(extra="ignore")

    bezeichnung: str | None = Field(None, min_length=1, max_length=100)
    zaehlernummer: str | None = Field(None, max_length=100)
    typ: str | None = Field(
        None,
        pattern="^(strom|gas|wasser|waerme|kaltwasser|sonstiges)$",
    )
    einheit: str | None = Field(
        None,
        pattern="^(kwh|m3|litre|kwh_m3|sonstiges)$",
    )
    ist_hauptzaehler: bool | None = None


class ZaehlerResponse(ZaehlerBase):
    """Vollständiger Zähler in API-Responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vermieter_id: int
    einheit_id: int
    einheit_name: str | None = None
    objekt_name: str | None = None
    ablesedatum: date | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class ZaehlerablesungBase(BaseModel):
    """Gemeinsame Felder für Ablesungs-Schemas."""

    ablesedatum: date
    zaehlerstand: Decimal = Field(..., ge=0, decimal_places=3)
    ableser: str | None = Field(None, max_length=50)
    notizen: str | None = Field(None, max_length=500)
    ist_schaetzung: bool = False


class ZaehlerablesungCreate(ZaehlerablesungBase):
    """Payload für das Anlegen einer Ablesung."""

    pass


class ZaehlerablesungUpdate(BaseModel):
    """Payload für das Aktualisieren einer Ablesung."""

    model_config = ConfigDict(extra="ignore")

    ablesedatum: date | None = None
    zaehlerstand: Decimal | None = Field(None, ge=0, decimal_places=3)
    ableser: str | None = Field(None, max_length=50)
    notizen: str | None = Field(None, max_length=500)
    ist_schaetzung: bool | None = None


class ZaehlerablesungResponse(ZaehlerablesungBase):
    """Vollständige Ablesung in API-Responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vermieter_id: int
    zaehler_id: int
    verbrauch: Decimal | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class ZaehlerMitAblesungenResponse(ZaehlerResponse):
    """Zähler inklusive aller zugehörigen Ablesungen."""

    ablesungen: list[ZaehlerablesungResponse] = []
