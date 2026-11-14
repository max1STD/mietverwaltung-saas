"""Bewerbungs-Routen — CRUD, Annahme und Ablehnung."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import _get_client_ip, csrf_protect, require_role
from app.models.bewerbungen import Bewerbung
from app.models.user import User
from app.routes._helpers import map_bewerbung_response
from app.schemas.bewerbungen import (
    BewerbungCreate,
    BewerbungDecisionRequest,
    BewerbungResponse,
    BewerbungUpdate,
)
from app.services.bewerbungen import (
    ablehnen,
    annehmen,
    create_bewerbung,
    delete_bewerbung,
    get_bewerbung,
    list_bewerbungen,
    update_bewerbung,
)

router = APIRouter()


def _ensure_ownership(bewerbung: Bewerbung | None, user: User) -> Bewerbung:
    if bewerbung is None or bewerbung.vermieter_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bewerbung nicht gefunden",
        )
    return bewerbung


@router.post(
    "",
    response_model=BewerbungResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
async def create_bewerbung_route(
    data: BewerbungCreate,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> BewerbungResponse:
    """Erstellt eine neue Mieter-Bewerbung."""
    bewerbung = await create_bewerbung(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        data=data,
        ip=_get_client_ip(request),
    )
    return await map_bewerbung_response(db, bewerbung)


@router.get("", response_model=list[BewerbungResponse])
async def list_bewerbungen_route(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> list[BewerbungResponse]:
    """Listet alle Bewerbungen des Vermieters."""
    bewerbungen = await list_bewerbungen(db, vermieter_id=user.id, status=status)
    return [await map_bewerbung_response(db, b) for b in bewerbungen]


@router.get("/{bewerbung_id}", response_model=BewerbungResponse)
async def get_bewerbung_route(
    bewerbung_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> BewerbungResponse:
    """Gibt eine einzelne Bewerbung zurück."""
    bewerbung = _ensure_ownership(await get_bewerbung(db, vermieter_id=user.id, bewerbung_id=bewerbung_id), user)
    return await map_bewerbung_response(db, bewerbung)


@router.patch(
    "/{bewerbung_id}",
    response_model=BewerbungResponse,
    dependencies=[Depends(csrf_protect)],
)
async def update_bewerbung_route(
    bewerbung_id: int,
    data: BewerbungUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> BewerbungResponse:
    """Aktualisiert Stammdaten einer Bewerbung."""
    bewerbung = _ensure_ownership(await get_bewerbung(db, vermieter_id=user.id, bewerbung_id=bewerbung_id), user)
    updated = await update_bewerbung(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        bewerbung=bewerbung,
        data=data,
        ip=_get_client_ip(request),
    )
    return await map_bewerbung_response(db, updated)


@router.delete(
    "/{bewerbung_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(csrf_protect)],
)
async def delete_bewerbung_route(
    bewerbung_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> None:
    """Löscht eine Bewerbung (Soft-Delete)."""
    bewerbung = _ensure_ownership(await get_bewerbung(db, vermieter_id=user.id, bewerbung_id=bewerbung_id), user)
    await delete_bewerbung(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        bewerbung=bewerbung,
        ip=_get_client_ip(request),
    )
    return None


@router.post(
    "/{bewerbung_id}/annehmen",
    response_model=dict,
    dependencies=[Depends(csrf_protect)],
)
async def annehmen_route(
    bewerbung_id: int,
    request: Request,
    data: BewerbungDecisionRequest = BewerbungDecisionRequest(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> dict:
    """Nimmt eine Bewerbung an und erzeugt optional Mieter + Mietvertrag."""
    bewerbung = _ensure_ownership(await get_bewerbung(db, vermieter_id=user.id, bewerbung_id=bewerbung_id), user)
    try:
        result = await annehmen(
            db,
            vermieter_id=user.id,
            user_id=user.id,
            bewerbung=bewerbung,
            decision=data,
            ip=_get_client_ip(request),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return result


@router.post(
    "/{bewerbung_id}/ablehnen",
    response_model=BewerbungResponse,
    dependencies=[Depends(csrf_protect)],
)
async def ablehnen_route(
    bewerbung_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> BewerbungResponse:
    """Lehnt eine Bewerbung ab."""
    bewerbung = _ensure_ownership(await get_bewerbung(db, vermieter_id=user.id, bewerbung_id=bewerbung_id), user)
    try:
        updated = await ablehnen(
            db,
            vermieter_id=user.id,
            user_id=user.id,
            bewerbung=bewerbung,
            ip=_get_client_ip(request),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return await map_bewerbung_response(db, updated)
