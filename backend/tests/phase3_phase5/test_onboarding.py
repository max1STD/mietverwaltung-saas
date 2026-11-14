"""Tests für Onboarding-Endpunkte (Phase 3)."""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_onboarding_progress_initial(auth_client: AsyncClient, vermieter_user: User) -> None:
    """Initialer Fortschritt ist 0% und alle 6 Schritte sind vorhanden."""
    response = await auth_client.get("/api/v1/onboarding/progress")
    assert response.status_code == 200
    data = response.json()
    assert data["progress_percent"] == 0
    assert len(data["steps"]) == 6
    steps = {s["step"]: s for s in data["steps"]}
    assert all(not s["is_done"] for s in data["steps"])
    assert "Profil vervollständigt" in {s["label"] for s in data["steps"]}
    assert steps["profile_completed"]["label"] == "Profil vervollständigt"


@pytest.mark.asyncio
async def test_onboarding_complete_step(auth_client: AsyncClient, vermieter_user: User) -> None:
    """Das manuelle Abhaken eines Schritts erhöht den Fortschritt."""
    response = await auth_client.post(
        "/api/v1/onboarding/complete-step",
        json={"step": "profile_completed"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["progress_percent"] == 17
    step = next(s for s in data["steps"] if s["step"] == "profile_completed")
    assert step["is_done"] is True
    assert step["done_at"] is not None


@pytest.mark.asyncio
async def test_onboarding_progress_with_objekt(auth_client: AsyncClient, vermieter_user: User) -> None:
    """Anlegen eines Objekts schließt den Meilenstein 'Erstes Objekt' automatisch ab."""
    # Zuerst Profil-Schritt abhaken, damit der prozentuale Fortschritt konsistent bleibt.
    await auth_client.post(
        "/api/v1/onboarding/complete-step",
        json={"step": "profile_completed"},
    )

    objekt_resp = await auth_client.post(
        "/api/v1/objekte",
        json={
            "name": "Mein Haus",
            "address": "Musterstraße 1, 12345 Musterstadt",
            "typ": "einfamilienhaus",
        },
    )
    assert objekt_resp.status_code == 201

    response = await auth_client.get("/api/v1/onboarding/progress")
    assert response.status_code == 200
    data = response.json()
    steps = {s["step"]: s for s in data["steps"]}
    assert steps["first_objekt"]["is_done"] is True
    assert data["progress_percent"] >= 33


@pytest.mark.asyncio
async def test_onboarding_invalid_step(auth_client: AsyncClient) -> None:
    """Unbekannter Schritt wird mit 400 abgewiesen."""
    response = await auth_client.post(
        "/api/v1/onboarding/complete-step",
        json={"step": "non_existing"},
    )
    assert response.status_code == 400
    assert "Ungültiger" in response.json()["detail"]
