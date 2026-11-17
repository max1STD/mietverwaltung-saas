"""Pydantic-Schemas für Mietverträge."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, computed_field


class MietvertragBase(BaseModel):
    """Gemeinsame Felder für Mietvertrag-Schemas."""

    mieter_id: int
    einheit_id: int
    mietbeginn: date
    mietende: date | None = None
    miete_cold: Decimal = Field(
        ...,
        ge=0,
        validation_alias=AliasChoices("kaltmiete", "miete_cold"),
    )
    nebenkosten_voraus: Decimal = Field(
        ...,
        ge=0,
        validation_alias=AliasChoices("nebenkosten_vorschuss", "nebenkosten_voraus"),
    )
    kaution: Decimal | None = None
    kaution_hinterlegt: bool = False
    status: str = Field(default="aktiv", pattern="^(aktiv|gekuendigt|beendet)$")

    @computed_field
    @property
    def kaltmiete(self) -> Decimal:
        """Deutscher Alias für die Kaltmiete (Frontend-Kompatibilität)."""
        return self.miete_cold

    @computed_field
    @property
    def nebenkosten_vorschuss(self) -> Decimal:
        """Deutscher Alias für den Nebenkostenvorschuss (Frontend-Kompatibilität)."""
        return self.nebenkosten_voraus


class MietvertragCreate(MietvertragBase):
    """Payload für das Anlegen eines Mietvertrags."""

    pass


class MietvertragUpdate(BaseModel):
    """Payload für das Aktualisieren eines Mietvertrags (alle Felder optional)."""

    model_config = ConfigDict(extra="ignore")

    mietbeginn: date | None = None
    mietende: date | None = None
    miete_cold: Decimal | None = Field(
        None,
        ge=0,
        validation_alias=AliasChoices("kaltmiete", "miete_cold"),
    )
    nebenkosten_voraus: Decimal | None = Field(
        None,
        ge=0,
        validation_alias=AliasChoices("nebenkosten_vorschuss", "nebenkosten_voraus"),
    )
    kaution: Decimal | None = None
    kaution_hinterlegt: bool | None = None
    status: str | None = Field(None, pattern="^(aktiv|gekuendigt|beendet)$")

    @computed_field
    @property
    def kaltmiete(self) -> Decimal | None:
        return self.miete_cold

    @computed_field
    @property
    def nebenkosten_vorschuss(self) -> Decimal | None:
        return self.nebenkosten_voraus


class MietvertragNestedMieter(BaseModel):
    """Kompakte Mieter-Info für die Vertrags-Detailansicht."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class MietvertragNestedEinheit(BaseModel):
    """Kompakte Einheit-Info für die Vertrags-Detailansicht."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    objekt_name: str


class MietvertragResponse(MietvertragBase):
    """Vollständige Mietvertrag-Daten in API-Responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    public_id: int | None = None
    vermieter_id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    mieter: MietvertragNestedMieter | None = None
    einheit: MietvertragNestedEinheit | None = None
