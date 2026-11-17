"""Pydantic-Schemas fuer Objekte (Immobilien)."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.einheit import EinheitNestedMieter

ObjektZustand = Literal[
    "neuwertig",
    "gut",
    "mittel",
    "abnutzungsspuren",
    "renovierungsbeduerftig",
]
ObjektHeizungsart = Literal[
    "gasetagenheizung",
    "gaszentralheizung",
    "fernwaerme",
    "oelheizung",
    "waermepumpe",
    "holzheizung",
    "elektroheizung",
    "sonstige",
]
ObjektBauweise = Literal[
    "massiv",
    "fertigteil",
    "holz",
    "stahl",
    "sonstige",
]
ObjektEnergieausweisArt = Literal[
    "verbrauchsausweis",
    "bedarfsausweis",
]


class ObjektBase(BaseModel):
    """Gemeinsame Felder fuer Objekt-Schemas."""

    name: str = Field(..., min_length=1, max_length=100)
    address: str | None = Field(None, max_length=255)
    plz: str | None = Field(None, max_length=10)
    ort: str | None = Field(None, max_length=100)
    typ: str | None = Field(None, max_length=20)
    baujahr: int | None = Field(None, ge=1000, le=2100)
    foto_url: str | None = Field(None, max_length=500)

    # Flaechen
    grundstuecksflaeche_qm: Decimal | None = Field(None, ge=0)
    wohnflaeche_gesamt_qm: Decimal | None = Field(None, ge=0)
    nutzflaeche_gesamt_qm: Decimal | None = Field(None, ge=0)
    vermietbare_flaeche_qm: Decimal | None = Field(None, ge=0)

    # Verwaltung / Bau
    anzahl_einheiten: int | None = Field(None, ge=1)
    baujahr_objekt: int | None = Field(None, ge=1000, le=2100)
    bauweise: ObjektBauweise | None = None
    zustand: ObjektZustand | None = None
    denkmalschutz: bool | None = None
    denkmalschutz_bis: date | None = None

    # Energie
    energieausweis_art: ObjektEnergieausweisArt | None = None
    energieausweis_gueltig_bis: date | None = None
    energieverbrauch_kennwert: Decimal | None = Field(None, ge=0)
    energieverbrauch_klasse: str | None = Field(None, max_length=10)
    heizungsart: ObjektHeizungsart | None = None
    warmwasserbereitung: str | None = Field(None, max_length=50)
    solaranlage: bool | None = None

    # Adresse / Lage
    land: str | None = Field(None, max_length=2)
    adresszusatz: str | None = Field(None, max_length=100)
    lagebeschreibung: str | None = Field(None, max_length=4000)

    # Finanzen
    kaufpreis: Decimal | None = None
    kaufpreis_pro_qm: Decimal | None = None
    kaufdatum: date | None = None
    eigenkapital: Decimal | None = None
    darlehen_betrag: Decimal | None = None
    zinssatz: Decimal | None = Field(None, ge=0, le=100)
    tilgung: Decimal | None = Field(None, ge=0, le=100)
    monatliche_rate: Decimal | None = None
    gesamtmiete_ist: Decimal | None = None
    gesamtmiete_soll: Decimal | None = None

    # Ausstattung
    barrierefrei: bool | None = None
    aufzug: bool | None = None
    gartennutzung: bool | None = None

    # Notizen
    notizen: str | None = Field(None, max_length=2000)
    anmerkungen: str | None = Field(None, max_length=4000)


class ObjektCreate(ObjektBase):
    """Payload fuer das Anlegen eines Objekts."""

    pass


class ObjektUpdate(BaseModel):
    """Payload fuer das Aktualisieren eines Objekts (alle Felder optional)."""

    model_config = ConfigDict(extra="ignore")

    name: str | None = Field(None, min_length=1, max_length=100)
    address: str | None = Field(None, max_length=255)
    plz: str | None = Field(None, max_length=10)
    ort: str | None = Field(None, max_length=100)
    typ: str | None = Field(None, max_length=20)
    baujahr: int | None = Field(None, ge=1000, le=2100)
    foto_url: str | None = Field(None, max_length=500)
    grundstuecksflaeche_qm: Decimal | None = Field(None, ge=0)
    wohnflaeche_gesamt_qm: Decimal | None = Field(None, ge=0)
    nutzflaeche_gesamt_qm: Decimal | None = Field(None, ge=0)
    vermietbare_flaeche_qm: Decimal | None = Field(None, ge=0)
    anzahl_einheiten: int | None = Field(None, ge=1)
    baujahr_objekt: int | None = Field(None, ge=1000, le=2100)
    bauweise: ObjektBauweise | None = None
    zustand: ObjektZustand | None = None
    denkmalschutz: bool | None = None
    denkmalschutz_bis: date | None = None
    energieausweis_art: ObjektEnergieausweisArt | None = None
    energieausweis_gueltig_bis: date | None = None
    energieverbrauch_kennwert: Decimal | None = Field(None, ge=0)
    energieverbrauch_klasse: str | None = Field(None, max_length=10)
    heizungsart: ObjektHeizungsart | None = None
    warmwasserbereitung: str | None = Field(None, max_length=50)
    solaranlage: bool | None = None
    land: str | None = Field(None, max_length=2)
    adresszusatz: str | None = Field(None, max_length=100)
    lagebeschreibung: str | None = Field(None, max_length=4000)
    kaufpreis: Decimal | None = None
    kaufpreis_pro_qm: Decimal | None = None
    kaufdatum: date | None = None
    eigenkapital: Decimal | None = None
    darlehen_betrag: Decimal | None = None
    zinssatz: Decimal | None = Field(None, ge=0, le=100)
    tilgung: Decimal | None = Field(None, ge=0, le=100)
    monatliche_rate: Decimal | None = None
    gesamtmiete_ist: Decimal | None = None
    gesamtmiete_soll: Decimal | None = None
    barrierefrei: bool | None = None
    aufzug: bool | None = None
    gartennutzung: bool | None = None
    notizen: str | None = Field(None, max_length=2000)
    anmerkungen: str | None = Field(None, max_length=4000)


class ObjektNestedEinheit(BaseModel):
    """Kompakte Einheit-Info fuer die Objekt-Detailansicht."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    public_id: int | None = None
    name: str
    wohnflaeche_qm: Decimal | None = None
    etage: int | None = None
    kaltmiete: Decimal | None = None
    nebenkosten_vorschuss: Decimal | None = None
    status: str | None = None  # Vermietungsstatus aus Business-Logik
    aktueller_mieter: EinheitNestedMieter | None = None


class ObjektResponse(ObjektBase):
    """Vollstaendige Objekt-Daten in API-Responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    public_id: int | None = None
    vermieter_id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    einheiten: list[ObjektNestedEinheit] = []
