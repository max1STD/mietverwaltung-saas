"""Bankverbindung-Routen — CRUD mit verschlüsselter IBAN."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import _get_client_ip, csrf_protect, require_role
from app.models.user import User
from app.schemas.bankverbindung import (
    BankverbindungCreate,
    BankverbindungResponse,
    BankverbindungUpdate,
)
from app.services.bankverbindungen import (
    create_bankverbindung,
    delete_bankverbindung,
    get_bankverbindung,
    get_iban,
    list_bankverbindungen,
    update_bankverbindung,
)

router = APIRouter()


def _serialize(bv) -> dict:
    """Mappt eine Bankverbindung auf das Response-Schema + entschlüsselte IBAN."""
    return {
        "id": bv.id,
        "vermieter_id": bv.vermieter_id,
        "mieter_id": bv.mieter_id,
        "iban": get_iban(bv),
        "bic": bv.bic,
        "kontoinhaber": bv.kontoinhaber,
        "bankname": bv.bankname,
        "is_default": bv.is_default,
    }


@router.post(
    "",
    response_model=BankverbindungResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
async def create_bankverbindung_route(
    data: BankverbindungCreate,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> BankverbindungResponse:
    """Erstellt eine neue Bankverbindung fuer den eingeloggten Vermieter."""
    bv = await create_bankverbindung(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        data=data,
        ip=_get_client_ip(request),
    )
    return _serialize(bv)


@router.get("", response_model=list[BankverbindungResponse])
async def list_bankverbindungen_route(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> list[BankverbindungResponse]:
    """Listet alle Bankverbindungen des Vermieters auf."""
    items = await list_bankverbindungen(db, vermieter_id=user.id)
    return [_serialize(item) for item in items]


@router.get("/{bankverbindung_id}", response_model=BankverbindungResponse)
async def get_bankverbindung_route(
    bankverbindung_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> BankverbindungResponse:
    """Gibt eine einzelne Bankverbindung zurueck."""
    bv = await get_bankverbindung(db, vermieter_id=user.id, bankverbindung_id=bankverbindung_id)
    if not bv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bankverbindung nicht gefunden")
    return _serialize(bv)


@router.patch(
    "/{bankverbindung_id}",
    response_model=BankverbindungResponse,
    dependencies=[Depends(csrf_protect)],
)
async def update_bankverbindung_route(
    bankverbindung_id: int,
    data: BankverbindungUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> BankverbindungResponse:
    """Aktualisiert eine Bankverbindung."""
    bv = await get_bankverbindung(db, vermieter_id=user.id, bankverbindung_id=bankverbindung_id)
    if not bv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bankverbindung nicht gefunden")
    updated = await update_bankverbindung(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        bankverbindung=bv,
        data=data,
        ip=_get_client_ip(request),
    )
    return _serialize(updated)


@router.delete(
    "/{bankverbindung_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(csrf_protect)],
)
async def delete_bankverbindung_route(
    bankverbindung_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> None:
    """Loescht eine Bankverbindung (Soft-Delete)."""
    bv = await get_bankverbindung(db, vermieter_id=user.id, bankverbindung_id=bankverbindung_id)
    if not bv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bankverbindung nicht gefunden")
    await delete_bankverbindung(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        bankverbindung=bv,
        ip=_get_client_ip(request),
    )
