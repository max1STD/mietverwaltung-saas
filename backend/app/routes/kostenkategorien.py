"""Kostenkategorie-Routen — CRUD fuer den Betriebskosten-Katalog."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import _get_client_ip, csrf_protect, require_role
from app.models.user import User
from app.schemas.kosten import KostenkategorieCreate, KostenkategorieResponse, KostenkategorieUpdate
from app.services.kostenkategorien import (
    create_kostenkategorie,
    delete_kostenkategorie,
    ensure_default_kategorien,
    get_kostenkategorie,
    list_kostenkategorien,
    update_kostenkategorie,
)

router = APIRouter()


@router.post(
    "/default",
    response_model=list[KostenkategorieResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
async def create_default_kategorien_route(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> list[KostenkategorieResponse]:
    """Legt fuer den eingeloggten Vermieter die Default-Kostenkategorien an (idempotent)."""
    await ensure_default_kategorien(db, vermieter_id=user.id)
    await db.commit()
    kategorien = await list_kostenkategorien(db, vermieter_id=user.id)
    return [KostenkategorieResponse.model_validate(k) for k in kategorien]


@router.post(
    "",
    response_model=KostenkategorieResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
async def create_kostenkategorie_route(
    data: KostenkategorieCreate,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> KostenkategorieResponse:
    """Erstellt eine neue Kostenkategorie fuer den eingeloggten Vermieter."""
    kategorie = await create_kostenkategorie(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        data=data,
        ip=_get_client_ip(request),
    )
    return kategorie


@router.get("", response_model=list[KostenkategorieResponse])
async def list_kostenkategorien_route(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> list[KostenkategorieResponse]:
    """Listet alle Kostenkategorien des Vermieters auf."""
    await ensure_default_kategorien(db, vermieter_id=user.id)
    await db.commit()
    kategorien = await list_kostenkategorien(db, vermieter_id=user.id)
    return [KostenkategorieResponse.model_validate(k) for k in kategorien]


@router.get("/{kategorie_id}", response_model=KostenkategorieResponse)
async def get_kostenkategorie_route(
    kategorie_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> KostenkategorieResponse:
    """Gibt eine einzelne Kostenkategorie zurueck."""
    kategorie = await get_kostenkategorie(db, vermieter_id=user.id, kategorie_id=kategorie_id)
    if not kategorie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kostenkategorie nicht gefunden")
    return kategorie


@router.patch(
    "/{kategorie_id}",
    response_model=KostenkategorieResponse,
    dependencies=[Depends(csrf_protect)],
)
async def update_kostenkategorie_route(
    kategorie_id: int,
    data: KostenkategorieUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> KostenkategorieResponse:
    """Aktualisiert eine Kostenkategorie."""
    kategorie = await get_kostenkategorie(db, vermieter_id=user.id, kategorie_id=kategorie_id)
    if not kategorie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kostenkategorie nicht gefunden")
    updated = await update_kostenkategorie(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        kategorie=kategorie,
        data=data,
        ip=_get_client_ip(request),
    )
    return updated


@router.delete(
    "/{kategorie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(csrf_protect)],
)
async def delete_kostenkategorie_route(
    kategorie_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> None:
    """Loescht eine benutzerdefinierte Kostenkategorie (Default-Kategorien bleiben)."""
    kategorie = await get_kostenkategorie(db, vermieter_id=user.id, kategorie_id=kategorie_id)
    if not kategorie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kostenkategorie nicht gefunden")
    await delete_kostenkategorie(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        kategorie=kategorie,
        ip=_get_client_ip(request),
    )
