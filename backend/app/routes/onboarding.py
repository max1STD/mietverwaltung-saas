"""Onboarding-Routen — Fortschritt und Setup-Checkliste."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import _get_client_ip, csrf_protect, require_role
from app.models.user import User
from app.schemas.onboarding import (
    OnboardingCompleteRequest,
    OnboardingProgressResponse,
    OnboardingStep,
)
from app.services.onboarding import get_progress, update_step

router = APIRouter()


@router.get("/progress", response_model=OnboardingProgressResponse)
async def get_progress_route(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> OnboardingProgressResponse:
    """Gibt den aktuellen Onboarding-Fortschritt zurück."""
    result = await get_progress(db, user_id=user.id)
    return OnboardingProgressResponse(
        progress_percent=result["progress_percent"],
        steps=[
            OnboardingStep(
                step=s["step"],
                label=s["label"],
                is_done=s["is_done"],
                done_at=s["done_at"],
            )
            for s in result["steps"]
        ],
    )


@router.post(
    "/complete-step",
    response_model=OnboardingProgressResponse,
    dependencies=[Depends(csrf_protect)],
)
async def complete_step_route(
    request: Request,
    data: OnboardingCompleteRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> OnboardingProgressResponse:
    """Markiert einen Onboarding-Schritt als erledigt."""
    try:
        await update_step(db, user_id=user.id, step=data.step)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    # Audit-Log über serverseitigen Aufruf mit Client-IP.
    _get_client_ip(request)

    result = await get_progress(db, user_id=user.id)
    return OnboardingProgressResponse(
        progress_percent=result["progress_percent"],
        steps=[
            OnboardingStep(
                step=s["step"],
                label=s["label"],
                is_done=s["is_done"],
                done_at=s["done_at"],
            )
            for s in result["steps"]
        ],
    )
