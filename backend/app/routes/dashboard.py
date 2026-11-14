"""Dashboard-Routen — KPIs, Finanzen und Smart Insights."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import require_role
from app.models.user import User
from app.schemas.dashboard import (
    DashboardFinancials,
    DashboardInsights,
    DashboardObjectSummary,
    DashboardSummary,
)
from app.services.dashboard import (
    financials,
    insights,
    object_summary,
    summary,
)

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> DashboardSummary:
    """Aggregierte Dashboard-Übersicht für den eingeloggten Vermieter."""
    return await summary(db, user.id)


@router.get("/object/{objekt_id}", response_model=DashboardObjectSummary)
async def get_object_summary(
    objekt_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> DashboardObjectSummary:
    """Kennzahlen und Vermietungsquote für ein einzelnes Objekt."""
    try:
        return await object_summary(db, user.id, objekt_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objekt nicht gefunden",
        )


@router.get("/financials", response_model=DashboardFinancials)
async def get_financials(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> DashboardFinancials:
    """Mieteinnahmen vs. Kosten der letzten 12 Monate."""
    return await financials(db, user.id)


@router.get("/insights", response_model=DashboardInsights)
async def get_insights(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> DashboardInsights:
    """Smart Insights für den Vermieter."""
    return await insights(db, user.id)
