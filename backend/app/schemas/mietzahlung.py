"""Pydantic-Schemas für Mietzahlungen."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, computed_field


class MietzahlungBase(BaseModel):
    """Gemeinsame Felder für Mietzahlungs-Schemas."""

    mieter_id: int | None = None
    vertrag_id: int | None = None
    betrag_soll: Decimal = Field(..., ge=0)
    betrag_ist: Decimal | None = Field(None, ge=0)
    zahlungsdatum: date | None = None
    mahnstufe: int = Field(default=0, ge=0, le=3)
    zahlungsreferenz: str | None = Field(None, max_length=50)

    @computed_field
    @property
    def offener_betrag(self) -> Decimal:
        """Differenz zwischen Soll- und Ist-Betrag."""
        return self.betrag_soll - (self.betrag_ist or Decimal("0.00"))


class MietzahlungCreate(MietzahlungBase):
    """Payload für das Anlegen einer Mietzahlung."""

    pass


class MietzahlungUpdate(BaseModel):
    """Payload für das Aktualisieren einer Mietzahlung (alle Felder optional)."""

    model_config = ConfigDict(extra="ignore")

    mieter_id: int | None = None
    vertrag_id: int | None = None
    betrag_soll: Decimal | None = Field(None, ge=0)
    betrag_ist: Decimal | None = Field(None, ge=0)
    zahlungsdatum: date | None = None
    mahnstufe: int | None = Field(None, ge=0, le=3)
    zahlungsreferenz: str | None = Field(None, max_length=50)


class MietzahlungNestedMieter(BaseModel):
    """Kompakte Mieter-Info für die Zahlungs-Detailansicht."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class MietzahlungNestedEinheit(BaseModel):
    """Kompakte Einheit-Info für die Zahlungs-Detailansicht."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    objekt_name: str


class MietzahlungNestedVertrag(BaseModel):
    """Kompakte Vertrags-Info für die Zahlungs-Detailansicht."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    miete_cold: Decimal
    nebenkosten_voraus: Decimal


class MietzahlungResponse(MietzahlungBase):
    """Vollständige Mietzahlungs-Daten in API-Responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vermieter_id: int
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    mieter: MietzahlungNestedMieter | None = None
    einheit: MietzahlungNestedEinheit | None = None
    vertrag: MietzahlungNestedVertrag | None = None
