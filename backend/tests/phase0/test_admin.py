"""Tests fuer Admin-Endpunkte."""
from __future__ import annotations

import pytest

from app.models.user import User


@pytest.mark.asyncio(loop_scope="function")
async def test_admin_stats_requires_admin(admin_client):
    response = await admin_client.get("/api/v1/admin/stats")
    assert response.status_code == 200
    data = response.json()
    assert "vermieter_count" in data
    assert "mieter_count" in data


@pytest.mark.asyncio(loop_scope="function")
async def test_admin_list_users_requires_admin(admin_client):
    response = await admin_client.get("/api/v1/admin/users")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio(loop_scope="function")
async def test_admin_create_vermieter(admin_client):
    payload = {
        "email": "newvermieter@example.com",
        "password": "TestPassword123!",
        "full_name": "Neuer Vermieter",
        "role": "vermieter",
    }
    response = await admin_client.post("/api/v1/admin/users", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["role"] == "vermieter"
    assert data["is_active"] is True


@pytest.mark.asyncio(loop_scope="function")
async def test_admin_create_mieter_requires_vermieter(admin_client, vermieter_user):
    payload = {
        "email": "newmieter@example.com",
        "password": "TestPassword123!",
        "full_name": "Neuer Mieter",
        "role": "mieter",
        "vermieter_id": vermieter_user.id,
    }
    response = await admin_client.post("/api/v1/admin/users", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["role"] == "mieter"
    assert data["vermieter_id"] == vermieter_user.id


@pytest.mark.asyncio(loop_scope="function")
async def test_admin_update_user_status(admin_client, vermieter_user):
    response = await admin_client.patch(
        f"/api/v1/admin/users/{vermieter_user.id}",
        json={"is_active": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False


@pytest.mark.asyncio(loop_scope="function")
async def test_admin_reset_password(admin_client, vermieter_user):
    response = await admin_client.post(
        f"/api/v1/admin/users/{vermieter_user.id}/reset-password",
        json={"new_password": "NewSecurePass123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio(loop_scope="function")
async def test_admin_delete_user_soft_delete(admin_client, vermieter_user):
    response = await admin_client.delete(f"/api/v1/admin/users/{vermieter_user.id}")
    assert response.status_code == 204

    session = admin_client.db_session
    user = await session.get(User, vermieter_user.id)
    assert user.deleted_at is not None
    assert user.is_active is False


@pytest.mark.asyncio(loop_scope="function")
async def test_vermieter_cannot_access_admin(auth_client):
    response = await auth_client.get("/api/v1/admin/stats")
    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="function")
async def test_admin_cannot_delete_self(admin_client, admin_user):
    response = await admin_client.delete(f"/api/v1/admin/users/{admin_user.id}")
    assert response.status_code == 400
