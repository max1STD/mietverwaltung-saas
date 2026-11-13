"""Pydantic-Schemas für Nebenkostenabrechnungen."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AbrechnungPositionBase(BaseModel):
    """Gemeinsame Felder für Abrechnungsposition-Schemas."""

    kategorie_id: int | None = None
    kosten_id: int | None = None
    betrag_total: Decimal = Field(..., ge=0)
    umlageanteil: Decimal = Field(..., ge=0)
    verteilungsschluessel: str = Field(
        ...,
        pattern="^(qm|personen|verbrauch)$",
    )
    datev_betrag: Decimal | None = None


class AbrechnungPositionResponse(AbrechnungPositionBase):
    """Vollständige Abrechnungsposition in API-Responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vermieter_id: int
    abrechnung_id: int
    created_at: datetime
    deleted_at: datetime | None = None


class AbrechnungBase(BaseModel):
    """Gemeinsame Felder für Abrechnungs-Schemas."""

    einheit_id: int
    objekt_id: int | None = None
    jahr: int = Field(..., ge=1900, le=2100)
    zeitraum_von: date
    zeitraum_bis: date
    einwendungsfrist_bis: date | None = None
    rechtskraeftig_seit: date | None = None
    status: str = Field(
        default="entwurf",
        pattern="^(entwurf|versendet|rechtskraeftig|angefochten)$",
    )


class AbrechnungCreate(AbrechnungBase):
    """Payload für das Anlegen einer Abrechnung."""

    pass


class AbrechnungUpdate(BaseModel):
    """Payload für das Aktualisieren einer Abrechnung (alle Felder optional)."""

    model_config = ConfigDict(extra="ignore")

    einheit_id: int | None = None
    objekt_id: int | None = None
    jahr: int | None = Field(None, ge=1900, le=2100)
    zeitraum_von: date | None = None
    zeitraum_bis: date | None = None
    einwendungsfrist_bis: date | None = None
    rechtskraeftig_seit: date | None = None
    status: str | None = Field(
        None,
        pattern="^(entwurf|versendet|rechtskraeftig|angefochten)$",
    )


class AbrechnungNestedEinheit(BaseModel):
    """Kompakte Einheit-Info für die Abrechnungs-Detailansicht."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    size_qm: Decimal


class AbrechnungResponse(AbrechnungBase):
    """Vollständige Abrechnungs-Daten in API-Responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vermieter_id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    positionen: list[AbrechnungPositionResponse] = []
    einheit: AbrechnungNestedEinheit | None = None
