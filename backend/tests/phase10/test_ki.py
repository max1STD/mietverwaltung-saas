"""Tests für Phase 10: KI-Schicht."""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.services.ai.keyword_classifier import (
    classify_ticket,
    classify_ticket_priority,
    suggest_cost_category,
    suggest_cost_umlagefaehig,
)


@pytest.mark.phase10
@pytest.mark.integration
def test_keyword_classifier_ticket_category():
    cat, conf = classify_ticket("In der Küche tropft das Wasser aus dem Hahn")
    assert cat == "wasser"
    assert conf > 0


@pytest.mark.phase10
@pytest.mark.integration
def test_keyword_classifier_ticket_priority():
    prio, conf = classify_ticket_priority("Heizung ist komplett ausgefallen, es ist eiskalt")
    assert prio == "dringend"
    assert conf > 0


@pytest.mark.phase10
@pytest.mark.integration
def test_suggest_cost_category():
    cat, conf = suggest_cost_category("Rechnung Heizungswartung Januar")
    assert cat == "heizkosten"
    assert conf > 0


@pytest.mark.phase10
@pytest.mark.integration
def test_suggest_cost_umlagefaehig():
    assert suggest_cost_umlagefaehig("heizkosten") is True
    assert suggest_cost_umlagefaehig("möbel") is False


@pytest.mark.phase10
@pytest.mark.integration
async def test_ki_ticket_categorize_endpoint(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/api/v1/ki/ticket-kategorie",
        json={"text": "Wasser tropft aus dem Hahn in der Küche"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["kategorie"] in {"wasser", "sanitaer", "sonstiges"}
    assert data["prioritaet"] in {"dringend", "normal", "niedrig"}


@pytest.mark.phase10
@pytest.mark.integration
async def test_ki_antwort_entwurf_endpoint(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/api/v1/ki/antwort-entwurf",
        json={"text": "Die Heizung ist defekt"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "text" in data
    assert len(data["text"]) > 0


@pytest.mark.phase10
@pytest.mark.integration
async def test_ki_smart_insight_endpoint(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/api/v1/ki/smart-insight",
        json={"context": "Mietzahlung überfällig seit 5 Tagen"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "text" in data
    assert len(data["text"]) > 0
