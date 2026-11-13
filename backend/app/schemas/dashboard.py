"""Dashboard-Schemas — Response-DTOs für KPIs, Finanzen und Insights."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DashboardSubscriptionInfo(BaseModel):
    """Abo-Status für das Dashboard-Widget."""

    status: str = "trial"  # trial | active | past_due | cancelled
    billing_cycle: str = "monthly"
    wohnungen_count: int = 0
    price_per_we: Decimal = Decimal("0.00")
    total_monthly: Decimal = Decimal("0.00")
    trial_ends_at: date | None = None
    is_trial: bool = True


class DashboardSummary(BaseModel):
    """Gesamtübersicht eines Vermieters."""

    objekte_count: int
    einheiten_count: int
    mieter_count: int
    offene_tickets_count: int
    subscription: DashboardSubscriptionInfo
    umsatz_diesen_monat: Decimal
    kosten_diesen_monat: Decimal


class ObjectRendite(BaseModel):
    """Rendite-Kennzahlen pro Objekt."""

    objekt_id: int
    name: str
    kaufpreis: Decimal | None
    einheiten_total: int
    einheiten_vermietet: int
    vermietungsquote: Decimal = Field(..., ge=0, le=100)
    jahreskaltmiete: Decimal
    jahreskosten: Decimal
    bruttomietrendite: Decimal | None
    nettomietrendite: Decimal | None


class MonthlyFinance(BaseModel):
    """Ein Monat im Finanz-Chart."""

    monat: str  # z. B. "2026-11"
    label: str  # z. B. "Nov 26"
    einnahmen: Decimal
    kosten: Decimal
    netto: Decimal


class DashboardFinancials(BaseModel):
    """12-Monats-Finanzverlauf."""

    monate: list[MonthlyFinance]
    summe_einnahmen: Decimal
    summe_kosten: Decimal
    summe_netto: Decimal


class DashboardInsight(BaseModel):
    """Ein Smart-Insight für den Vermieter."""

    typ: str  # leerstand | ticket | mahnung | frist | info
    titel: str
    beschreibung: str
    link: str | None = None
    prioritaet: str = "normal"  # niedrig | normal | hoch | dringend
    entity_id: int | None = None


class DashboardInsights(BaseModel):
    """Liste generierter Smart Insights."""

    insights: list[DashboardInsight]


class DashboardObjectSummary(BaseModel):
    """Detail-Kennzahlen für ein einzelnes Objekt."""

    objekt_id: int
    name: str
    einheiten_total: int
    einheiten_vermietet: int
    vermietungsquote: Decimal
    jahreskaltmiete: Decimal
    jahreskosten: Decimal
    kaufpreis: Decimal | None
    bruttomietrendite: Decimal | None
    nettomietrendite: Decimal | None


class DashboardPhotoUploadResponse(BaseModel):
    """Antwort nach erfolgreichem Foto-Upload."""

    foto_url: str
    message: str = "Foto erfolgreich hochgeladen"
