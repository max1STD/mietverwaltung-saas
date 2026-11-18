"""Mietvertrag-Routen — CRUD für Mietverträge."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import _get_client_ip, csrf_protect, get_current_user, require_role
from app.models.user import User
from app.routes._helpers import map_mietvertrag_response
from app.schemas.mietvertrag import (
    MietvertragCreate,
    MietvertragResponse,
    MietvertragUpdate,
)
from app.services.mietvertraege import (
    create_mietvertrag,
    delete_mietvertrag,
    get_mietvertrag,
    get_mietvertrag_for_user,
    list_mietvertraege,
    list_mietvertraege_for_user,
    update_mietvertrag,
)
from app.services.public_id_resolver import resolve_mietvertrag

router = APIRouter()


@router.post(
    "",
    response_model=MietvertragResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
async def create_mietvertrag_route(
    data: MietvertragCreate,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> MietvertragResponse:
    """Erstellt einen neuen Mietvertrag (nur Vermieter)."""
    try:
        vertrag = await create_mietvertrag(
            db,
            vermieter_id=user.id,
            user_id=user.id,
            data=data,
            ip=_get_client_ip(request),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return await map_mietvertrag_response(db, vertrag)


@router.get("", response_model=list[MietvertragResponse])
async def list_mietvertraege_route(
    einheit_id: int | None = None,
    mieter_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[MietvertragResponse]:
    """Listet Mietverträge für Vermieter oder eigenen Mieter-Account."""
    if user.role == "vermieter":
        vertraege = await list_mietvertraege(
            db,
            vermieter_id=user.id,
            einheit_id=einheit_id,
            mieter_id=mieter_id,
        )
    else:
        # Mieter sieht nur seine eigenen Verträge; Filter werden ignoriert.
        vertraege = await list_mietvertraege_for_user(db, user)
    return [await map_mietvertrag_response(db, v) for v in vertraege]


@router.get("/{vertrag_id}", response_model=MietvertragResponse)
async def get_mietvertrag_route(
    vertrag_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MietvertragResponse:
    """Gibt einen einzelnen Mietvertrag zurück (Vermieter oder eigener Mieter)."""
    if user.role == "vermieter":
        vertrag = await resolve_mietvertrag(db, vermieter_id=user.id, entity_id=vertrag_id)
    else:
        vertrag = await get_mietvertrag_for_user(db, user, vertrag_id)
    if not vertrag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mietvertrag nicht gefunden",
        )
    return await map_mietvertrag_response(db, vertrag)


@router.patch(
    "/{vertrag_id}",
    response_model=MietvertragResponse,
    dependencies=[Depends(csrf_protect)],
)
async def update_mietvertrag_route(
    vertrag_id: int,
    data: MietvertragUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> MietvertragResponse:
    """Aktualisiert einen Mietvertrag (nur Vermieter)."""
    vertrag = await resolve_mietvertrag(db, vermieter_id=user.id, entity_id=vertrag_id)
    if not vertrag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mietvertrag nicht gefunden",
        )
    updated = await update_mietvertrag(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        vertrag=vertrag,
        data=data,
        ip=_get_client_ip(request),
    )
    return await map_mietvertrag_response(db, updated)


@router.delete(
    "/{vertrag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(csrf_protect)],
)
async def delete_mietvertrag_route(
    vertrag_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> None:
    """Löscht einen Mietvertrag (Soft-Delete, nur Vermieter)."""
    vertrag = await resolve_mietvertrag(db, vermieter_id=user.id, entity_id=vertrag_id)
    if not vertrag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mietvertrag nicht gefunden",
        )
    await delete_mietvertrag(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        vertrag=vertrag,
        ip=_get_client_ip(request),
    )
    return None
