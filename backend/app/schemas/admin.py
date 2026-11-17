"""Pydantic-Schemas fuer Admin-Endpunkte."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.einheit import EinheitResponse
from app.schemas.objekt import ObjektResponse


class AdminStatsResponse(BaseModel):
    """Aggregationszahlen fuer das Admin-Dashboard."""

    vermieter_count: int
    mieter_count: int
    objekte_count: int
    einheiten_count: int


class AdminUserResponse(BaseModel):
    """User-Datensatz im Admin-Kontext."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    email_verified: bool
    phone: str | None = None
    firma: str | None = None
    vermieter_id: int | None = None
    created_at: str | None = None


class AdminUserListResponse(BaseModel):
    """Paginierte User-Liste fuer das Admin-Backend."""

    items: list[AdminUserResponse]
    total: int
    skip: int
    limit: int


class AdminUserCreateRequest(BaseModel):
    """Payload zum Anlegen eines neuen Nutzers durch einen Admin."""

    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: str = Field(..., pattern="^(vermieter|mieter)$")
    vermieter_id: int | None = None


class AdminUserUpdateRequest(BaseModel):
    """Payload zum Aktualisieren eines Nutzers durch einen Admin."""

    model_config = ConfigDict(extra="ignore")

    full_name: str | None = Field(None, min_length=2, max_length=100)
    phone: str | None = Field(None, max_length=30)
    role: str | None = Field(None, pattern="^(admin|vermieter|mieter)$")
    is_active: bool | None = None
    vermieter_id: int | None = None


class PasswordResetAdminRequest(BaseModel):
    """Direktes Passwort-Reset durch Admin."""

    new_password: str = Field(..., min_length=12, max_length=128)


class AdminObjektListResponse(BaseModel):
    """Paginierte Objekt-Liste fuer das Admin-Backend."""

    items: list[ObjektResponse]
    total: int
    skip: int
    limit: int


class AdminEinheitListResponse(BaseModel):
    """Paginierte Einheit-Liste fuer das Admin-Backend."""

    items: list[EinheitResponse]
    total: int
    skip: int
    limit: int


__all__ = [
    "AdminStatsResponse",
    "AdminUserResponse",
    "AdminUserListResponse",
    "AdminUserCreateRequest",
    "AdminUserUpdateRequest",
    "PasswordResetAdminRequest",
    "AdminObjektListResponse",
    "AdminEinheitListResponse",
]
