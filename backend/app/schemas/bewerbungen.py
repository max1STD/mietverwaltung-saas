"""Pydantic-Schemas für Mieter-Bewerbungen."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BewerbungBase(BaseModel):
    """Gemeinsame Felder für Bewerbungs-Schemas."""

    einheit_id: int
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=30)
    income_monthly: Decimal | None = Field(None, ge=0)
    schufa_score: int | None = Field(None, ge=0, le=1000)
    documents: dict[str, Any] | None = None


class BewerbungCreate(BewerbungBase):
    """Payload für das Anlegen einer Bewerbung."""

    pass


class BewerbungUpdate(BaseModel):
    """Payload für das Aktualisieren einer Bewerbung (nur Daten, kein Status)."""

    model_config = ConfigDict(extra="ignore")

    first_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str | None = Field(None, min_length=1, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=30)
    income_monthly: Decimal | None = Field(None, ge=0)
    schufa_score: int | None = Field(None, ge=0, le=1000)
    documents: dict[str, Any] | None = None


class BewerbungNestedEinheit(BaseModel):
    """Kompakte Einheit-Info für die Bewerbungs-Detailansicht."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    objekt_name: str = ""


class BewerbungResponse(BewerbungBase):
    """Vollständige Bewerbungs-Daten in API-Responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vermieter_id: int
    status: str
    applied_at: datetime
    decided_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    einheit: BewerbungNestedEinheit | None = None


class BewerbungDecisionRequest(BaseModel):
    """Optionale Parameter für die Annahme einer Bewerbung."""

    create_mieter_and_vertrag: bool = True
    mietbeginn: date | None = None
    miete_cold: Decimal | None = Field(None, ge=0)
    nebenkosten_voraus: Decimal | None = Field(None, ge=0)
    kaution: Decimal | None = Field(None, ge=0)
    status: str | None = None  # Falls ein anderer Endstatus gewünscht ist
