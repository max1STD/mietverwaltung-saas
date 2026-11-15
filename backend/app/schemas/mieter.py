"""Pydantic-Schemas für Mieter."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class AdresseBase(BaseModel):
    """Gemeinsame Felder für Adress-Schemas."""

    typ: str = Field(..., pattern="^(postal|residential|rental_object|guarantor)$")
    strasse: str = Field(..., min_length=1, max_length=255)
    hausnummer: str | None = Field(None, max_length=20)
    plz: str = Field(..., min_length=3, max_length=10)
    ort: str = Field(..., min_length=1, max_length=100)
    land: str = Field(default="DE", max_length=2)
    is_primary: bool = False


class AdresseCreate(AdresseBase):
    """Payload für neue Adresse."""

    pass


class AdresseResponse(AdresseBase):
    """Adresse in API-Responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    mieter_id: int
    created_at: datetime
    updated_at: datetime


class BuergschaftBase(BaseModel):
    """Gemeinsame Felder für Bürgschaft-Schemas."""

    buerge_first_name: str = Field(..., min_length=1, max_length=50)
    buerge_last_name: str = Field(..., min_length=1, max_length=50)
    buerge_geburtsdatum: date | None = None
    buerge_phone: str | None = Field(None, max_length=30)
    buerge_email: EmailStr | None = None
    hoechstbetrag: Decimal | None = None
    gueltig_bis: date | None = None
    status: str = Field(default="aktiv", pattern="^(aktiv|inaktiv)$")
    notizen: str | None = Field(None, max_length=2000)


class BuergschaftCreate(BuergschaftBase):
    """Payload für neue Bürgschaft inkl. Adresse."""

    buerge_adresse: AdresseBase | None = None


class BuergschaftResponse(BuergschaftBase):
    """Bürgschaft in API-Responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    mieter_id: int
    vermieter_id: int
    buerge_adresse: AdresseResponse | None = None
    created_at: datetime
    updated_at: datetime


class MieterBase(BaseModel):
    """Gemeinsame Felder für Mieter-Schemas (Frontend-kompatibel)."""

    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr | None = None
    telefon: str | None = Field(None, max_length=30)
    geburtsdatum: date | None = None
    notizen: str | None = Field(None, max_length=2000)
    status: str = Field(default="aktiv", pattern="^(aktiv|ehemalig|bewerber)$")
    since: date | None = None
    adressen: list[AdresseCreate] = []
    buergschaften: list[BuergschaftCreate] = []

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class MieterCreate(MieterBase):
    """Payload für das Anlegen eines Mieters."""

    pass


class MieterUpdate(BaseModel):
    """Payload für das Aktualisieren eines Mieters (alle Felder optional)."""

    model_config = ConfigDict(extra="ignore")

    first_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str | None = Field(None, min_length=1, max_length=50)
    email: EmailStr | None = None
    telefon: str | None = Field(None, max_length=30)
    geburtsdatum: date | None = None
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
    first_name: str
    last_name: str
    name: str
    email: str | None = None
    telefon: str | None = None
    geburtsdatum: date | None = None
    adresse: str | None = None
    notizen: str | None = None
    status: str
    since: date | None = None
    adressen: list[AdresseResponse] = []
    buergschaften: list[BuergschaftResponse] = []
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    aktuelle_einheit: MieterNestedEinheit | None = None
