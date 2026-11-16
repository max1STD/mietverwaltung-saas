"""Pydantic-Schemas für das Ticket-System."""
from __future__ import annotations

from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

# Gültige Werte aus DB-Schema und Geschäftslogik
TICKET_STATUS = Literal[
    "offen",
    "in_bearbeitung",
    "wartend_auf_mieter",
    "wartend_auf_handwerker",
    "erledigt",
    "geschlossen",
    "abgelehnt",
]
TICKET_PRIORITY = Literal["niedrig", "normal", "hoch", "dringend"]
TICKET_CATEGORY = Literal[
    "heizung",
    "wasser",
    "elektrik",
    "schimmel",
    "sanitaer",
    "schluessel",
    "sauberkeit",
    "sonstiges",
]
AUTHOR_ROLE = Literal["vermieter", "mieter", "handwerker", "system"]


class TicketCommentCreate(BaseModel):
    """Schema zum Erstellen eines Ticket-Kommentars."""

    content: str = Field(..., min_length=1, max_length=5000)
    is_internal: bool = False


class TicketCommentResponse(BaseModel):
    """Öffentliche Darstellung eines Kommentars."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    author_id: int | None
    author_role: str
    content: str
    ist_ki_entwurf: bool
    is_internal: bool
    created_at: str | None = None


class TicketCommentInternalCreate(BaseModel):
    """Interner Kommentar (nur Vermieter/Team)."""

    content: str = Field(..., min_length=1, max_length=5000)
    is_internal: bool = True


class TicketCreate(BaseModel):
    """Schema zum Erstellen eines neuen Tickets."""

    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        alias="titel",
        validation_alias=AliasChoices("titel", "title"),
        serialization_alias="titel",
    )
    description: str | None = Field(
        None,
        max_length=5000,
        alias="beschreibung",
        validation_alias=AliasChoices("beschreibung", "description"),
        serialization_alias="beschreibung",
    )
    category: TICKET_CATEGORY | None = Field(
        None,
        alias="kategorie",
        validation_alias=AliasChoices("kategorie", "category"),
        serialization_alias="kategorie",
    )
    priority: TICKET_PRIORITY = Field(
        default="normal",
        alias="prioritaet",
        validation_alias=AliasChoices("prioritaet", "priority"),
        serialization_alias="prioritaet",
    )
    objekt_id: int | None = None
    mieter_id: int | None = None
    einheit_id: int | None = None
    assigned_to: int | None = None
    handwerker_id: int | None = None
    sla_id: int | None = None


class TicketUpdate(BaseModel):
    """Schema zum Aktualisieren eines bestehenden Tickets."""

    title: str | None = Field(
        None,
        min_length=3,
        max_length=200,
        alias="titel",
        validation_alias=AliasChoices("titel", "title"),
        serialization_alias="titel",
    )
    description: str | None = Field(
        None,
        max_length=5000,
        alias="beschreibung",
        validation_alias=AliasChoices("beschreibung", "description"),
        serialization_alias="beschreibung",
    )
    category: TICKET_CATEGORY | None = Field(
        None,
        alias="kategorie",
        validation_alias=AliasChoices("kategorie", "category"),
        serialization_alias="kategorie",
    )
    priority: TICKET_PRIORITY | None = Field(
        None,
        alias="prioritaet",
        validation_alias=AliasChoices("prioritaet", "priority"),
        serialization_alias="prioritaet",
    )
    status: TICKET_STATUS | None = None
    objekt_id: int | None = None
    mieter_id: int | None = None
    einheit_id: int | None = None
    assigned_to: int | None = None
    handwerker_id: int | None = None
    sla_id: int | None = None


class TicketResponse(BaseModel):
    """Öffentliche Darstellung eines Tickets inkl. Kommentare."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vermieter_id: int
    objekt_id: int | None
    mieter_id: int | None
    einheit_id: int | None
    ticket_number: str
    title: str
    description: str | None
    category: str | None
    priority: str
    status: str
    ki_kategorisiert: bool
    ki_prioritaet: bool
    assigned_to: int | None
    handwerker_id: int | None
    sla_id: int | None
    created_at: str | None = None
    updated_at: str | None = None
    closed_at: str | None = None
    comments: list[TicketCommentResponse] = []


class TicketListResponse(BaseModel):
    """Paginierte Liste von Tickets (ohne Kommentare)."""

    items: list[TicketResponse]
    total: int


class TicketSLABase(BaseModel):
    """Gemeinsame Felder für SLA-Schemas."""

    name: str = Field(..., min_length=1, max_length=50)
    response_time_hours: int = Field(..., ge=1, le=8760)
    resolution_time_hours: int = Field(..., ge=1, le=8760)
    biz_hours_only: bool = True
    biz_start: str | None = "09:00"
    biz_end: str | None = "17:00"
    biz_days: str = Field(default="mtwtf", pattern=r"^[mtwfs]+$", max_length=7)
    escalation_levels: dict | None = None
    is_active: bool = True


class TicketSLACreate(TicketSLABase):
    """Schema zum Erstellen einer SLA-Konfiguration."""

    pass


class TicketSLAUpdate(BaseModel):
    """Schema zum Aktualisieren einer SLA-Konfiguration."""

    name: str | None = Field(None, min_length=1, max_length=50)
    response_time_hours: int | None = Field(None, ge=1, le=8760)
    resolution_time_hours: int | None = Field(None, ge=1, le=8760)
    biz_hours_only: bool | None = None
    biz_start: str | None = None
    biz_end: str | None = None
    biz_days: str | None = Field(None, pattern=r"^[mtwfs]+$", max_length=7)
    escalation_levels: dict | None = None
    is_active: bool | None = None


class TicketSLAResponse(TicketSLABase):
    """Öffentliche Darstellung einer SLA-Konfiguration."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vermieter_id: int


class TicketTriggerBase(BaseModel):
    """Gemeinsame Felder für Trigger-Schemas."""

    name: str = Field(..., min_length=1, max_length=100)
    trigger_type: str = Field(..., min_length=1, max_length=20)
    condition: dict
    perform: dict
    is_active: bool = True


class TicketTriggerCreate(TicketTriggerBase):
    """Schema zum Erstellen einer Automatisierungsregel."""

    pass


class TicketTriggerUpdate(BaseModel):
    """Schema zum Aktualisieren einer Automatisierungsregel."""

    name: str | None = Field(None, min_length=1, max_length=100)
    trigger_type: str | None = Field(None, min_length=1, max_length=20)
    condition: dict | None = None
    perform: dict | None = None
    is_active: bool | None = None


class TicketTriggerResponse(TicketTriggerBase):
    """Öffentliche Darstellung einer Automatisierungsregel."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vermieter_id: int
    created_at: str | None = None


class MessageResponse(BaseModel):
    """Generische Statusnachricht."""

    message: str
