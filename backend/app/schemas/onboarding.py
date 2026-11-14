"""Pydantic-Schemas für Onboarding-Fortschritt."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OnboardingStep(BaseModel):
    """Ein einzelner Onboarding-Schritt."""

    model_config = ConfigDict(from_attributes=True)

    step: str
    label: str
    is_done: bool
    done_at: datetime | None = None


class OnboardingProgressResponse(BaseModel):
    """Gesamter Onboarding-Fortschritt eines Users."""

    progress_percent: int
    steps: list[OnboardingStep]


class OnboardingCompleteRequest(BaseModel):
    """Payload zum Abhaken eines Onboarding-Schritts."""

    step: str
