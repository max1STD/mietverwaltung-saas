"""Mieter-Routen — CRUD für Mieter-Stammdaten."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import _get_client_ip, csrf_protect, require_role
from app.models.user import User
from app.routes._helpers import map_mieter_response
from app.schemas.mieter import MieterCreate, MieterResponse, MieterUpdate
from app.services.mieter import (
    create_mieter,
    delete_mieter,
    get_aktuelle_einheit,
    get_mieter,
    list_mieter,
    update_mieter,
)

router = APIRouter()


@router.post(
    "",
    response_model=MieterResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
async def create_mieter_route(
    data: MieterCreate,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> MieterResponse:
    """Erstellt einen neuen Mieter für den eingeloggten Vermieter."""
    mieter = await create_mieter(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        data=data,
        ip=_get_client_ip(request),
    )
    aktuelle_einheit = await get_aktuelle_einheit(db, mieter.id)
    return await map_mieter_response(db, mieter, aktuelle_einheit)


@router.get("", response_model=list[MieterResponse])
async def list_mieter_route(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> list[MieterResponse]:
    """Listet alle Mieter des eingeloggten Vermieters."""
    mieter_liste = await list_mieter(db, vermieter_id=user.id)
    result: list[MieterResponse] = []
    for m in mieter_liste:
        aktuelle_einheit = await get_aktuelle_einheit(db, m.id)
        result.append(await map_mieter_response(db, m, aktuelle_einheit))
    return result


@router.get("/{mieter_id}", response_model=MieterResponse)
async def get_mieter_route(
    mieter_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> MieterResponse:
    """Gibt einen einzelnen Mieter zurück."""
    mieter = await get_mieter(db, vermieter_id=user.id, mieter_id=mieter_id)
    if not mieter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mieter nicht gefunden",
        )
    aktuelle_einheit = await get_aktuelle_einheit(db, mieter.id)
    return await map_mieter_response(db, mieter, aktuelle_einheit)


@router.patch(
    "/{mieter_id}",
    response_model=MieterResponse,
    dependencies=[Depends(csrf_protect)],
)
async def update_mieter_route(
    mieter_id: int,
    data: MieterUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> MieterResponse:
    """Aktualisiert einen Mieter."""
    mieter = await get_mieter(db, vermieter_id=user.id, mieter_id=mieter_id)
    if not mieter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mieter nicht gefunden",
        )
    updated = await update_mieter(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        mieter=mieter,
        data=data,
        ip=_get_client_ip(request),
    )
    aktuelle_einheit = await get_aktuelle_einheit(db, updated.id)
    return await map_mieter_response(db, updated, aktuelle_einheit)


@router.delete(
    "/{mieter_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(csrf_protect)],
)
async def delete_mieter_route(
    mieter_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> None:
    """Löscht einen Mieter (Soft-Delete)."""
    mieter = await get_mieter(db, vermieter_id=user.id, mieter_id=mieter_id)
    if not mieter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mieter nicht gefunden",
        )
    await delete_mieter(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        mieter=mieter,
        ip=_get_client_ip(request),
    )
    return None
