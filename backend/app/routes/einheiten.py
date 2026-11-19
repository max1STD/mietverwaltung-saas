"""Einheit-Routen — CRUD für Wohneinheiten."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import _get_client_ip, csrf_protect, require_role
from app.models.user import User
from app.routes._helpers import map_einheit_response
from app.schemas.einheit import EinheitCreate, EinheitResponse, EinheitUpdate
from app.services.einheiten import (
    create_einheit,
    delete_einheit,
    get_einheit,
    list_einheiten,
    update_einheit,
)
from app.services.public_id_resolver import resolve_einheit

router = APIRouter()


@router.post(
    "",
    response_model=EinheitResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
async def create_einheit_route(
    data: EinheitCreate,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> EinheitResponse:
    """Erstellt eine neue Wohneinheit innerhalb eines Objekts."""
    einheit = await create_einheit(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        data=data,
        ip=_get_client_ip(request),
    )
    return await map_einheit_response(db, einheit)


@router.get("", response_model=list[EinheitResponse])
async def list_einheiten_route(
    objekt_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> list[EinheitResponse]:
    """Listet alle Einheiten des Vermieters, optional gefiltert nach Objekt."""
    einheiten = await list_einheiten(
        db,
        vermieter_id=user.id,
        objekt_id=objekt_id,
    )
    return [await map_einheit_response(db, e) for e in einheiten]


@router.get("/{einheit_id}", response_model=EinheitResponse)
async def get_einheit_route(
    einheit_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> EinheitResponse:
    """Gibt eine einzelne Einheit zurück."""
    einheit = await resolve_einheit(db, vermieter_id=user.id, entity_id=einheit_id)
    if not einheit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Einheit nicht gefunden",
        )
    return await map_einheit_response(db, einheit)


@router.patch(
    "/{einheit_id}",
    response_model=EinheitResponse,
    dependencies=[Depends(csrf_protect)],
)
async def update_einheit_route(
    einheit_id: int,
    data: EinheitUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> EinheitResponse:
    """Aktualisiert eine Einheit."""
    einheit = await resolve_einheit(db, vermieter_id=user.id, entity_id=einheit_id)
    if not einheit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Einheit nicht gefunden",
        )
    updated = await update_einheit(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        einheit=einheit,
        data=data,
        ip=_get_client_ip(request),
    )
    return await map_einheit_response(db, updated)


@router.delete(
    "/{einheit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(csrf_protect)],
)
async def delete_einheit_route(
    einheit_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> None:
    """Löscht eine Einheit (Soft-Delete)."""
    einheit = await resolve_einheit(db, vermieter_id=user.id, entity_id=einheit_id)
    if not einheit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Einheit nicht gefunden",
        )
    try:
        await delete_einheit(
            db,
            vermieter_id=user.id,
            user_id=user.id,
            einheit=einheit,
            ip=_get_client_ip(request),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return None
