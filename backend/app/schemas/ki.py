"""Pydantic-Schemas für KI-Endpunkte."""
from __future__ import annotations

from pydantic import BaseModel, Field


class KITicketCategorizeRequest(BaseModel):
    text: str = Field(..., min_length=1)


class KITicketCategorizeResponse(BaseModel):
    kategorie: str
    kategorie_confidence: float
    prioritaet: str
    prioritaet_confidence: float


class KISimpleRequest(BaseModel):
    text: str = Field(..., min_length=1)


class KISimpleResponse(BaseModel):
    text: str


class KIMahnungRequest(BaseModel):
    text: str = Field(..., min_length=1)
    stufe: int = Field(..., ge=1, le=3)
    betrag: float = Field(..., ge=0)
    faellig_seit: str = Field(..., min_length=1)
    mieter_name: str = Field(..., min_length=1)


class KISmartInsightRequest(BaseModel):
    context: str = Field(..., min_length=1)


class KIReceiptResponse(BaseModel):
    rohtext: str
    betrag: float
    kategorie: str
    umlagefaehig: bool
    verteilungsschluessel: str
