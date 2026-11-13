"""Pydantic-Schemas für Kosten und Kostenkategorien."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class KostenkategorieBase(BaseModel):
    """Gemeinsame Felder für Kostenkategorie-Schemas."""

    name: str = Field(..., min_length=1, max_length=50)
    betrvk_key: str | None = Field(None, max_length=20)
    umlagefaehig: bool = True
    verteilungsschluessel: str = Field(
        default="qm",
        pattern="^(qm|personen|verbrauch)$",
    )


class KostenkategorieCreate(KostenkategorieBase):
    """Payload für das Anlegen einer Kostenkategorie."""

    pass


class KostenkategorieUpdate(BaseModel):
    """Payload für das Aktualisieren einer Kostenkategorie (alle Felder optional)."""

    model_config = ConfigDict(extra="ignore")

    name: str | None = Field(None, min_length=1, max_length=50)
    betrvk_key: str | None = Field(None, max_length=20)
    umlagefaehig: bool | None = None
    verteilungsschluessel: str | None = Field(
        None,
        pattern="^(qm|personen|verbrauch)$",
    )


class KostenkategorieResponse(KostenkategorieBase):
    """Vollständige Kostenkategorie-Daten in API-Responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vermieter_id: int
    is_default: bool


class KostenBase(BaseModel):
    """Gemeinsame Felder für Kosten-Schemas."""

    objekt_id: int | None = None
    einheit_id: int | None = None
    kategorie_id: int | None = None
    betrag: Decimal = Field(..., ge=0)
    datum: date
    umlagefaehig: bool = True
    abrechnung_id: int | None = None
    abgerechnet_am: date | None = None
    ki_kategorisiert: bool = False
    datev_konto: str | None = Field(None, max_length=10)
    datev_buchungstext: str | None = Field(None, max_length=100)


class KostenCreate(KostenBase):
    """Payload für das Anlegen einer Kostenposition."""

    pass


class KostenUpdate(BaseModel):
    """Payload für das Aktualisieren einer Kostenposition (alle Felder optional)."""

    model_config = ConfigDict(extra="ignore")

    objekt_id: int | None = None
    einheit_id: int | None = None
    kategorie_id: int | None = None
    betrag: Decimal | None = Field(None, ge=0)
    datum: date | None = None
    umlagefaehig: bool | None = None
    abrechnung_id: int | None = None
    abgerechnet_am: date | None = None
    ki_kategorisiert: bool | None = None
    datev_konto: str | None = Field(None, max_length=10)
    datev_buchungstext: str | None = Field(None, max_length=100)


class KostenNestedKategorie(BaseModel):
    """Kompakte Kategorien-Info für die Kosten-Detailansicht."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    verteilungsschluessel: str


class KostenResponse(KostenBase):
    """Vollständige Kosten-Daten in API-Responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vermieter_id: int
    created_at: datetime
    deleted_at: datetime | None = None
    kategorie: KostenNestedKategorie | None = None


class KostenScanResponse(BaseModel):
    """Vorschlag aus OCR/KI-Stub für einen Beleg-Scan."""

    kategorie_name: str | None = None
    betrag: Decimal | None = None
    datum: date | None = None
    umlagefaehig: bool | None = None
    konfidenz: str = "hoch"
    hinweis: str = "KI-Scan in dieser Phase ein Stub — Werte müssen geprüft werden."
