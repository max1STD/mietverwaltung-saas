"""Abrechnungs-Routen — CRUD, Berechnung und Finalisierung."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import _get_client_ip, csrf_protect, require_role
from app.models.user import User
from app.routes._helpers import map_abrechnung_response
from app.schemas.abrechnung import AbrechnungCreate, AbrechnungResponse, AbrechnungUpdate
from app.services.abrechnungen import (
    calculate_positions,
    create_abrechnung,
    delete_abrechnung,
    finalize_abrechnung,
    get_abrechnung,
    list_abrechnungen,
    update_abrechnung,
)

router = APIRouter()


@router.post(
    "",
    response_model=AbrechnungResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
async def create_abrechnung_route(
    data: AbrechnungCreate,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> AbrechnungResponse:
    """Erstellt eine neue Nebenkostenabrechnung."""
    abrechnung = await create_abrechnung(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        data=data,
        ip=_get_client_ip(request),
    )
    return await map_abrechnung_response(db, abrechnung)


@router.get("", response_model=list[AbrechnungResponse])
async def list_abrechnungen_route(
    einheit_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> list[AbrechnungResponse]:
    """Listet alle Abrechnungen des Vermieters, optional gefiltert nach Einheit."""
    abrechnungen = await list_abrechnungen(
        db,
        vermieter_id=user.id,
        einheit_id=einheit_id,
    )
    return [await map_abrechnung_response(db, a) for a in abrechnungen]


@router.get("/{abrechnung_id}", response_model=AbrechnungResponse)
async def get_abrechnung_route(
    abrechnung_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> AbrechnungResponse:
    """Gibt eine einzelne Abrechnung zurück."""
    abrechnung = await get_abrechnung(db, vermieter_id=user.id, abrechnung_id=abrechnung_id)
    if not abrechnung:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Abrechnung nicht gefunden",
        )
    return await map_abrechnung_response(db, abrechnung)


@router.patch(
    "/{abrechnung_id}",
    response_model=AbrechnungResponse,
    dependencies=[Depends(csrf_protect)],
)
async def update_abrechnung_route(
    abrechnung_id: int,
    data: AbrechnungUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> AbrechnungResponse:
    """Aktualisiert eine Abrechnung."""
    abrechnung = await get_abrechnung(db, vermieter_id=user.id, abrechnung_id=abrechnung_id)
    if not abrechnung:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Abrechnung nicht gefunden",
        )
    updated = await update_abrechnung(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        abrechnung=abrechnung,
        data=data,
        ip=_get_client_ip(request),
    )
    return await map_abrechnung_response(db, updated)


@router.delete(
    "/{abrechnung_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(csrf_protect)],
)
async def delete_abrechnung_route(
    abrechnung_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> None:
    """Löscht eine Abrechnung (Soft-Delete)."""
    abrechnung = await get_abrechnung(db, vermieter_id=user.id, abrechnung_id=abrechnung_id)
    if not abrechnung:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Abrechnung nicht gefunden",
        )
    await delete_abrechnung(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        abrechnung=abrechnung,
        ip=_get_client_ip(request),
    )
    return None


@router.post(
    "/{abrechnung_id}/calculate",
    response_model=AbrechnungResponse,
    dependencies=[Depends(csrf_protect)],
)
async def calculate_abrechnung_route(
    abrechnung_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> AbrechnungResponse:
    """Berechnet die Abrechnungspositionen für eine Abrechnung neu."""
    abrechnung = await get_abrechnung(db, vermieter_id=user.id, abrechnung_id=abrechnung_id)
    if not abrechnung:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Abrechnung nicht gefunden",
        )
    try:
        updated = await calculate_positions(
            db,
            vermieter_id=user.id,
            user_id=user.id,
            abrechnung=abrechnung,
            ip=_get_client_ip(request),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    return await map_abrechnung_response(db, updated)


@router.post(
    "/{abrechnung_id}/finalize",
    response_model=AbrechnungResponse,
    dependencies=[Depends(csrf_protect)],
)
async def finalize_abrechnung_route(
    abrechnung_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> AbrechnungResponse:
    """Finalisiert eine Abrechnung (status 'versendet', Kosten abgerechnet)."""
    abrechnung = await get_abrechnung(db, vermieter_id=user.id, abrechnung_id=abrechnung_id)
    if not abrechnung:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Abrechnung nicht gefunden",
        )
    finalized = await finalize_abrechnung(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        abrechnung=abrechnung,
        ip=_get_client_ip(request),
    )
    return await map_abrechnung_response(db, finalized)
