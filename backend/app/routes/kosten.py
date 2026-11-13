"""Kosten-Routen — CRUD für Kosten und KI-Scan-Stub."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import _get_client_ip, csrf_protect, require_role
from app.models.user import User
from app.routes._helpers import map_kosten_response
from app.schemas.kosten import KostenCreate, KostenResponse, KostenScanResponse, KostenUpdate
from app.services.kosten import create_kosten, delete_kosten, get_kosten, list_kosten, scan_kosten_stub, update_kosten

router = APIRouter()


@router.post(
    "",
    response_model=KostenResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
async def create_kosten_route(
    data: KostenCreate,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> KostenResponse:
    """Erstellt eine neue Kostenposition für den eingeloggten Vermieter."""
    kosten = await create_kosten(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        data=data,
        ip=_get_client_ip(request),
    )
    return await map_kosten_response(db, kosten)


@router.get("", response_model=list[KostenResponse])
async def list_kosten_route(
    objekt_id: int | None = None,
    einheit_id: int | None = None,
    kategorie_id: int | None = None,
    abrechnung_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> list[KostenResponse]:
    """Listet alle Kosten des Vermieters, optional gefiltert."""
    kosten_list = await list_kosten(
        db,
        vermieter_id=user.id,
        objekt_id=objekt_id,
        einheit_id=einheit_id,
        kategorie_id=kategorie_id,
        abrechnung_id=abrechnung_id,
    )
    return [await map_kosten_response(db, k) for k in kosten_list]


@router.get("/{kosten_id}", response_model=KostenResponse)
async def get_kosten_route(
    kosten_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> KostenResponse:
    """Gibt eine einzelne Kostenposition zurück."""
    kosten = await get_kosten(db, vermieter_id=user.id, kosten_id=kosten_id)
    if not kosten:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kosten nicht gefunden",
        )
    return await map_kosten_response(db, kosten)


@router.patch(
    "/{kosten_id}",
    response_model=KostenResponse,
    dependencies=[Depends(csrf_protect)],
)
async def update_kosten_route(
    kosten_id: int,
    data: KostenUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> KostenResponse:
    """Aktualisiert eine Kostenposition."""
    kosten = await get_kosten(db, vermieter_id=user.id, kosten_id=kosten_id)
    if not kosten:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kosten nicht gefunden",
        )
    updated = await update_kosten(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        kosten=kosten,
        data=data,
        ip=_get_client_ip(request),
    )
    return await map_kosten_response(db, updated)


@router.delete(
    "/{kosten_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(csrf_protect)],
)
async def delete_kosten_route(
    kosten_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> None:
    """Löscht eine Kostenposition (Soft-Delete)."""
    kosten = await get_kosten(db, vermieter_id=user.id, kosten_id=kosten_id)
    if not kosten:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kosten nicht gefunden",
        )
    await delete_kosten(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        kosten=kosten,
        ip=_get_client_ip(request),
    )
    return None


@router.post(
    "/{kosten_id}/scan",
    response_model=KostenScanResponse,
    dependencies=[Depends(csrf_protect)],
)
async def scan_kosten_route(
    kosten_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> KostenScanResponse:
    """Stub-Endpunkt für OCR/KI-Belegscan — liefert einen Vorschlag."""
    kosten = await get_kosten(db, vermieter_id=user.id, kosten_id=kosten_id)
    if not kosten:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kosten nicht gefunden",
        )
    return await scan_kosten_stub(db, vermieter_id=user.id)
