"""Objekt-Routen — CRUD für Immobilien."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import _get_client_ip, csrf_protect, require_role
from app.models.user import User
from app.routes._helpers import map_einheit_response, map_objekt_response
from app.schemas.einheit import EinheitCreate, EinheitNestedCreate, EinheitResponse
from app.schemas.objekt import ObjektCreate, ObjektResponse, ObjektUpdate
from app.services.einheiten import create_einheit, list_einheiten
from app.services.objekte import create_objekt, delete_objekt, get_objekt, list_objekte, update_objekt

router = APIRouter()


@router.post(
    "",
    response_model=ObjektResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
async def create_objekt_route(
    data: ObjektCreate,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> ObjektResponse:
    """Erstellt ein neues Objekt für den eingeloggten Vermieter."""
    objekt = await create_objekt(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        data=data,
        ip=_get_client_ip(request),
    )
    return await map_objekt_response(db, objekt)


@router.get("", response_model=list[ObjektResponse])
async def list_objekte_route(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> list[ObjektResponse]:
    """Listet alle Objekte des eingeloggten Vermieters."""
    objekte = await list_objekte(db, vermieter_id=user.id)
    return [await map_objekt_response(db, o) for o in objekte]


@router.get("/{objekt_id}", response_model=ObjektResponse)
async def get_objekt_route(
    objekt_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> ObjektResponse:
    """Gibt ein einzelnes Objekt zurück."""
    objekt = await get_objekt(db, vermieter_id=user.id, objekt_id=objekt_id)
    if not objekt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objekt nicht gefunden",
        )
    return await map_objekt_response(db, objekt)


@router.patch(
    "/{objekt_id}",
    response_model=ObjektResponse,
    dependencies=[Depends(csrf_protect)],
)
async def update_objekt_route(
    objekt_id: int,
    data: ObjektUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> ObjektResponse:
    """Aktualisiert ein Objekt."""
    objekt = await get_objekt(db, vermieter_id=user.id, objekt_id=objekt_id)
    if not objekt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objekt nicht gefunden",
        )
    updated = await update_objekt(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        objekt=objekt,
        data=data,
        ip=_get_client_ip(request),
    )
    return await map_objekt_response(db, updated)


@router.delete(
    "/{objekt_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(csrf_protect)],
)
async def delete_objekt_route(
    objekt_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> None:
    """Löscht ein Objekt (Soft-Delete)."""
    objekt = await get_objekt(db, vermieter_id=user.id, objekt_id=objekt_id)
    if not objekt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objekt nicht gefunden",
        )
    await delete_objekt(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        objekt=objekt,
        ip=_get_client_ip(request),
    )
    return None


@router.post(
    "/{objekt_id}/einheiten",
    response_model=EinheitResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
async def create_einheit_nested_route(
    objekt_id: int,
    data: EinheitNestedCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> EinheitResponse:
    """Erstellt eine Einheit innerhalb eines bestimmten Objekts."""
    objekt = await get_objekt(db, vermieter_id=user.id, objekt_id=objekt_id)
    if not objekt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objekt nicht gefunden",
        )
    payload = data.model_dump()
    payload["objekt_id"] = objekt_id
    einheit = await create_einheit(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        data=EinheitCreate(**payload),
        ip=_get_client_ip(request),
    )
    return await map_einheit_response(db, einheit)


@router.get(
    "/{objekt_id}/einheiten",
    response_model=list[EinheitResponse],
)
async def list_einheiten_nested_route(
    objekt_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> list[EinheitResponse]:
    """Listet alle Einheiten eines Objekts auf."""
    objekt = await get_objekt(db, vermieter_id=user.id, objekt_id=objekt_id)
    if not objekt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objekt nicht gefunden",
        )
    einheiten = await list_einheiten(db, vermieter_id=user.id, objekt_id=objekt_id)
    return [await map_einheit_response(db, e) for e in einheiten]
