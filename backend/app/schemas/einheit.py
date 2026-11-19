"""Pydantic-Schemas fuer Wohneinheiten."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

EinheitZustand = Literal[
    "gut",
    "mittel",
    "renovierungsbeduerftig",
    "neuwertig",
    "abnutzungsspuren",
]
EinheitRenovierungsstatus = Literal[
    "keine_renovierung",
    "renoviert",
    "teilrenoviert",
    "renovierungsbeduerftig",
    "in_renovierung",
]
EinheitHeizungsart = Literal[
    "gasetagenheizung",
    "gaszentralheizung",
    "fernwaerme",
    "oelheizung",
    "waermepumpe",
    "holzheizung",
    "elektroheizung",
    "sonstige",
]
EinheitBauweise = Literal[
    "massiv",
    "fertigteil",
    "holz",
    "stahl",
    "sonstige",
]
EinheitEnergieausweisArt = Literal[
    "verbrauchsausweis",
    "bedarfsausweis",
]


class EinheitBase(BaseModel):
    """Gemeinsame Felder fuer Einheit-Schemas."""

    objekt_id: int
    name: str = Field(..., min_length=1, max_length=100)

    # Kern-Flaechen / Miete
    wohnflaeche_qm: Decimal = Field(..., gt=0)
    nutzflaeche_qm: Decimal | None = Field(None, gt=0)
    kaltmiete: Decimal = Field(..., ge=0)
    nebenkosten_vorschuss: Decimal | None = Field(None, ge=0)

    # Lage / Raumzahl
    etage: int | None = Field(None, ge=0)
    rooms: int | None = Field(None, ge=1)
    floor: str | None = Field(None, max_length=20)
    schlafzimmer: int | None = Field(None, ge=0)
    badezimmer: int | None = Field(None, ge=0)
    wohnzimmer: int | None = Field(None, ge=0)

    # Zusaetzliche Flaechen
    balkon_flaeche_qm: Decimal | None = Field(None, ge=0)
    terrasse_flaeche_qm: Decimal | None = Field(None, ge=0)
    garten_flaeche_qm: Decimal | None = Field(None, ge=0)
    gewerbeflaeche_qm: Decimal | None = Field(None, ge=0)

    # Ausstattung
    balkon: bool | None = None
    terrasse: bool | None = None
    garten: bool | None = None
    garage: bool | None = None
    stellplatz: bool | None = None
    keller: bool | None = None
    aufzug: bool | None = None
    barrierefrei: bool | None = None
    moebliert: bool | None = None

    # Energie / Bau
    energy_class: str | None = Field(None, max_length=2)
    baujahr_einheit: int | None = Field(None, ge=1500, le=2100)
    heizungsart: EinheitHeizungsart | None = None
    warmwasserbereitung: str | None = Field(None, max_length=50)
    fenster: str | None = Field(None, max_length=50)
    boden: str | None = Field(None, max_length=50)
    sanitaer: str | None = Field(None, max_length=50)
    kueche: str | None = Field(None, max_length=50)
    energieausweis_art: EinheitEnergieausweisArt | None = None
    energieverbrauch_kennwert: Decimal | None = Field(None, ge=0)
    energieverbrauch_klasse: str | None = Field(None, max_length=10)
    bauweise: EinheitBauweise | None = None

    # Rechtliches
    denkmalschutz: bool | None = None
    denkmalschutz_bis: date | None = None

    # Zustand / Historie
    last_renovation: date | None = None
    renovierungsstatus: EinheitRenovierungsstatus | None = None
    zustand: EinheitZustand | None = None
    available_from: date | None = None
    bewohnbar_ab: date | None = None
    anmerkungen: str | None = Field(None, max_length=4000)


class EinheitCreate(EinheitBase):
    """Payload fuer das Anlegen einer Einheit."""

    pass


class EinheitNestedCreate(BaseModel):
    """Payload fuer das Anlegen einer Einheit innerhalb eines Objekts (ohne objekt_id)."""

    name: str = Field(..., min_length=1, max_length=100)
    wohnflaeche_qm: Decimal = Field(..., gt=0)
    etage: int | None = Field(None, ge=0)
    kaltmiete: Decimal = Field(..., ge=0)
    nebenkosten_vorschuss: Decimal | None = Field(None, ge=0)
    rooms: int | None = Field(None, ge=1)
    floor: str | None = Field(None, max_length=20)
    energy_class: str | None = Field(None, max_length=2)
    last_renovation: date | None = None
    available_from: date | None = None


class EinheitUpdate(BaseModel):
    """Payload fuer das Aktualisieren einer Einheit (alle Felder optional)."""

    model_config = ConfigDict(extra="ignore")

    name: str | None = Field(None, min_length=1, max_length=100)
    wohnflaeche_qm: Decimal | None = Field(None, gt=0)
    nutzflaeche_qm: Decimal | None = Field(None, gt=0)
    kaltmiete: Decimal | None = Field(None, ge=0)
    nebenkosten_vorschuss: Decimal | None = Field(None, ge=0)
    etage: int | None = Field(None, ge=0)
    rooms: int | None = Field(None, ge=1)
    floor: str | None = Field(None, max_length=20)
    schlafzimmer: int | None = Field(None, ge=0)
    badezimmer: int | None = Field(None, ge=0)
    wohnzimmer: int | None = Field(None, ge=0)
    balkon_flaeche_qm: Decimal | None = Field(None, ge=0)
    terrasse_flaeche_qm: Decimal | None = Field(None, ge=0)
    garten_flaeche_qm: Decimal | None = Field(None, ge=0)
    gewerbeflaeche_qm: Decimal | None = Field(None, ge=0)
    balkon: bool | None = None
    terrasse: bool | None = None
    garten: bool | None = None
    garage: bool | None = None
    stellplatz: bool | None = None
    keller: bool | None = None
    aufzug: bool | None = None
    barrierefrei: bool | None = None
    moebliert: bool | None = None
    energy_class: str | None = Field(None, max_length=2)
    baujahr_einheit: int | None = Field(None, ge=1500, le=2100)
    heizungsart: EinheitHeizungsart | None = None
    warmwasserbereitung: str | None = Field(None, max_length=50)
    fenster: str | None = Field(None, max_length=50)
    boden: str | None = Field(None, max_length=50)
    sanitaer: str | None = Field(None, max_length=50)
    kueche: str | None = Field(None, max_length=50)
    energieausweis_art: EinheitEnergieausweisArt | None = None
    energieverbrauch_kennwert: Decimal | None = Field(None, ge=0)
    energieverbrauch_klasse: str | None = Field(None, max_length=10)
    bauweise: EinheitBauweise | None = None
    denkmalschutz: bool | None = None
    denkmalschutz_bis: date | None = None
    last_renovation: date | None = None
    renovierungsstatus: EinheitRenovierungsstatus | None = None
    zustand: EinheitZustand | None = None
    available_from: date | None = None
    bewohnbar_ab: date | None = None
    anmerkungen: str | None = Field(None, max_length=4000)


class EinheitNestedMieter(BaseModel):
    """Kompakte Mieter-Info fuer die Einheit-Detailansicht."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    status: str


class EinheitResponse(EinheitBase):
    """Vollstaendige Einheit-Daten in API-Responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    public_id: int | None = None
    vermieter_id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    aktueller_mieter: EinheitNestedMieter | None = None
    vermietungsstatus: str = "frei"
