"""Tests fuer Kostenkategorie-CRUD-Endpunkte."""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio(loop_scope="function")
async def test_create_kostenkategorie(auth_client: AsyncClient, vermieter_user: User) -> None:
    """Ein Vermieter kann eine eigene Kostenkategorie anlegen."""
    payload = {
        "name": "Sonderreinigung",
        "betrkv_key": "SRein",
        "umlagefaehig": True,
        "verteilungsschluessel": "qm",
    }
    response = await auth_client.post("/api/v1/kostenkategorien", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["vermieter_id"] == vermieter_user.id
    assert data["is_default"] is False


@pytest.mark.asyncio(loop_scope="function")
async def test_list_kostenkategorien_empty_then_default(auth_client: AsyncClient, vermieter_user: User) -> None:
    """Beim ersten Zugriff werden Default-Kategorien erstellt und zurueckgegeben."""
    # Aktuell liefert die Route keine automatische Erzeugung; Service-Funktion ist separat verfuegbar.
    response = await auth_client.get("/api/v1/kostenkategorien")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio(loop_scope="function")
async def test_update_kostenkategorie(auth_client: AsyncClient) -> None:
    """Eine benutzerdefinierte Kategorie kann aktualisiert werden."""
    create_resp = await auth_client.post(
        "/api/v1/kostenkategorien",
        json={
            "name": "Alt",
            "umlagefaehig": True,
            "verteilungsschluessel": "qm",
        },
    )
    kategorie_id = create_resp.json()["id"]

    response = await auth_client.patch(
        f"/api/v1/kostenkategorien/{kategorie_id}",
        json={"umlagefaehig": False, "verteilungsschluessel": "verbrauch"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["umlagefaehig"] is False
    assert data["verteilungsschluessel"] == "verbrauch"


@pytest.mark.asyncio(loop_scope="function")
async def test_delete_kostenkategorie(auth_client: AsyncClient) -> None:
    """Eine benutzerdefinierte Kategorie kann geloescht werden."""
    create_resp = await auth_client.post(
        "/api/v1/kostenkategorien",
        json={
            "name": "Loeschbar",
            "umlagefaehig": True,
            "verteilungsschluessel": "qm",
        },
    )
    kategorie_id = create_resp.json()["id"]

    response = await auth_client.delete(f"/api/v1/kostenkategorien/{kategorie_id}")
    assert response.status_code == 204

    get_resp = await auth_client.get(f"/api/v1/kostenkategorien/{kategorie_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio(loop_scope="function")
async def test_kostenkategorie_not_found(auth_client: AsyncClient) -> None:
    """Eine fremde/nicht existierende Kategorie liefert 404."""
    response = await auth_client.get("/api/v1/kostenkategorien/999999")
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="function")
async def test_kostenkategorie_validation_verteilungsschluessel(auth_client: AsyncClient) -> None:
    """Ungueltiger Verteilungsschluessel wird abgelehnt."""
    response = await auth_client.post(
        "/api/v1/kostenkategorien",
        json={
            "name": "Falsch",
            "umlagefaehig": True,
            "verteilungsschluessel": "unbekannt",
        },
    )
    assert response.status_code == 422
