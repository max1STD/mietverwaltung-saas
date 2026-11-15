"""Pydantic-Schemas für Objekte (Immobilien)."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ObjektBase(BaseModel):
    """Gemeinsame Felder für Objekt-Schemas."""

    name: str = Field(..., min_length=1, max_length=100)
    address: str | None = Field(None, max_length=255)
    plz: str | None = Field(None, max_length=10)
    ort: str | None = Field(None, max_length=100)
    typ: str | None = Field(None, max_length=20)
    baujahr: int | None = Field(None, ge=1000, le=2100)
    foto_url: str | None = Field(None, max_length=500)
    kaufpreis: Decimal | None = None
    kaufdatum: date | None = None
    eigenkapital: Decimal | None = None
    darlehen_betrag: Decimal | None = None
    zinssatz: Decimal | None = Field(None, ge=0, le=100)
    tilgung: Decimal | None = Field(None, ge=0, le=100)
    monatliche_rate: Decimal | None = None
    notizen: str | None = Field(None, max_length=2000)


class ObjektCreate(ObjektBase):
    """Payload für das Anlegen eines Objekts."""

    pass


class ObjektUpdate(BaseModel):
    """Payload für das Aktualisieren eines Objekts (alle Felder optional)."""

    model_config = ConfigDict(extra="ignore")

    name: str | None = Field(None, min_length=1, max_length=100)
    address: str | None = Field(None, max_length=255)
    plz: str | None = Field(None, max_length=10)
    ort: str | None = Field(None, max_length=100)
    typ: str | None = Field(None, max_length=20)
    baujahr: int | None = Field(None, ge=1000, le=2100)
    foto_url: str | None = Field(None, max_length=500)
    kaufpreis: Decimal | None = None
    kaufdatum: date | None = None
    eigenkapital: Decimal | None = None
    darlehen_betrag: Decimal | None = None
    zinssatz: Decimal | None = Field(None, ge=0, le=100)
    tilgung: Decimal | None = Field(None, ge=0, le=100)
    monatliche_rate: Decimal | None = None
    notizen: str | None = Field(None, max_length=2000)


class ObjektNestedEinheit(BaseModel):
    """Kompakte Einheit-Info für die Objekt-Detailansicht."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    public_id: int | None = None
    name: str
    wohnflaeche_qm: Decimal | None = None
    etage: int | None = None
    kaltmiete: Decimal | None = None
    nebenkosten_vorschuss: Decimal | None = None
    status: str | None = None  # Vermietungsstatus aus Business-Logik


class ObjektResponse(ObjektBase):
    """Vollständige Objekt-Daten in API-Responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    public_id: int | None = None
    vermieter_id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    einheiten: list[ObjektNestedEinheit] = []
