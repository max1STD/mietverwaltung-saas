"""Mietzahlungs-Routen — CRUD, Zahlungsmarkierung und Mahnstufe."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import _get_client_ip, csrf_protect, get_current_user, require_role
from app.models.user import User
from app.routes._helpers import map_mietzahlung_response
from app.schemas.mietzahlung import MietzahlungCreate, MietzahlungResponse, MietzahlungUpdate
from app.services.mietzahlungen import (
    create_mietzahlung,
    delete_mietzahlung,
    erhoehe_mahnstufe,
    generate_mietzahlungen,
    get_mietzahlung,
    get_mietzahlung_for_user,
    list_mietzahlungen,
    list_mietzahlungen_for_user,
    mark_paid,
    update_mietzahlung,
)

router = APIRouter()


class MarkPaidRequest(BaseModel):
    """Payload für das Markieren einer Mietzahlung als bezahlt."""

    betrag_ist: Decimal = Field(..., ge=0)
    zahlungsdatum: datetime


class GenerateMietzahlungenRequest(BaseModel):
    """Payload für die Generierung von Mietzahlungen für einen Monat."""

    monat: date


@router.post(
    "",
    response_model=MietzahlungResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
async def create_mietzahlung_route(
    data: MietzahlungCreate,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> MietzahlungResponse:
    """Erstellt eine neue Mietzahlung für den eingeloggten Vermieter."""
    try:
        zahlung = await create_mietzahlung(
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
    return await map_mietzahlung_response(db, zahlung)


@router.get("", response_model=list[MietzahlungResponse])
async def list_mietzahlungen_route(
    mieter_id: int | None = None,
    vertrag_id: int | None = None,
    offen: bool | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[MietzahlungResponse]:
    """Listet Mietzahlungen für Vermieter oder eigenen Mieter-Account."""
    if user.role == "vermieter":
        zahlungen = await list_mietzahlungen(
            db,
            vermieter_id=user.id,
            mieter_id=mieter_id,
            vertrag_id=vertrag_id,
            offen=offen,
        )
    else:
        zahlungen = await list_mietzahlungen_for_user(db, user)
    return [await map_mietzahlung_response(db, z) for z in zahlungen]


@router.get("/{zahlung_id}", response_model=MietzahlungResponse)
async def get_mietzahlung_route(
    zahlung_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MietzahlungResponse:
    """Gibt eine einzelne Mietzahlung zurück (Vermieter oder eigener Mieter)."""
    if user.role == "vermieter":
        zahlung = await get_mietzahlung(db, vermieter_id=user.id, zahlung_id=zahlung_id)
    else:
        zahlung = await get_mietzahlung_for_user(db, user, zahlung_id)
    if not zahlung:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mietzahlung nicht gefunden",
        )
    return await map_mietzahlung_response(db, zahlung)


@router.patch(
    "/{zahlung_id}",
    response_model=MietzahlungResponse,
    dependencies=[Depends(csrf_protect)],
)
async def update_mietzahlung_route(
    zahlung_id: int,
    data: MietzahlungUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> MietzahlungResponse:
    """Aktualisiert eine Mietzahlung."""
    zahlung = await get_mietzahlung(db, vermieter_id=user.id, zahlung_id=zahlung_id)
    if not zahlung:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mietzahlung nicht gefunden",
        )
    try:
        updated = await update_mietzahlung(
            db,
            vermieter_id=user.id,
            user_id=user.id,
            zahlung=zahlung,
            data=data,
            ip=_get_client_ip(request),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return await map_mietzahlung_response(db, updated)


@router.delete(
    "/{zahlung_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(csrf_protect)],
)
async def delete_mietzahlung_route(
    zahlung_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> None:
    """Löscht eine Mietzahlung (Soft-Delete)."""
    zahlung = await get_mietzahlung(db, vermieter_id=user.id, zahlung_id=zahlung_id)
    if not zahlung:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mietzahlung nicht gefunden",
        )
    await delete_mietzahlung(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        zahlung=zahlung,
        ip=_get_client_ip(request),
    )
    return None


@router.post(
    "/{zahlung_id}/mark-paid",
    response_model=MietzahlungResponse,
    dependencies=[Depends(csrf_protect)],
)
async def mark_paid_route(
    zahlung_id: int,
    data: MarkPaidRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> MietzahlungResponse:
    """Markiert eine Mietzahlung als bezahlt."""
    zahlung = await get_mietzahlung(db, vermieter_id=user.id, zahlung_id=zahlung_id)
    if not zahlung:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mietzahlung nicht gefunden",
        )
    updated = await mark_paid(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        zahlung=zahlung,
        betrag_ist=data.betrag_ist,
        zahlungsdatum=data.zahlungsdatum,
        ip=_get_client_ip(request),
    )
    return await map_mietzahlung_response(db, updated)


@router.post(
    "/{zahlung_id}/mahnstufe",
    response_model=MietzahlungResponse,
    dependencies=[Depends(csrf_protect)],
)
async def erhoehe_mahnstufe_route(
    zahlung_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> MietzahlungResponse:
    """Erhöht die Mahnstufe einer Mietzahlung um eins."""
    zahlung = await get_mietzahlung(db, vermieter_id=user.id, zahlung_id=zahlung_id)
    if not zahlung:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mietzahlung nicht gefunden",
        )
    try:
        updated = await erhoehe_mahnstufe(
            db,
            vermieter_id=user.id,
            user_id=user.id,
            zahlung=zahlung,
            ip=_get_client_ip(request),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return await map_mietzahlung_response(db, updated)


@router.post(
    "/actions/generate",
    response_model=list[MietzahlungResponse],
    dependencies=[Depends(csrf_protect)],
)
async def generate_mietzahlungen_route(
    data: GenerateMietzahlungenRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> list[MietzahlungResponse]:
    """Generiert Mietzahlungen für alle aktiven Verträge eines Monats."""
    zahlungen = await generate_mietzahlungen(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        monat=data.monat,
        ip=_get_client_ip(request),
    )
    return [await map_mietzahlung_response(db, z) for z in zahlungen]
