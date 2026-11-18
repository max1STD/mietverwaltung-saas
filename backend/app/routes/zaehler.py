"""API-Routen für Zähler und Ablesungen."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import csrf_protect, get_current_user, require_role
from app.models.user import User
from app.models.zaehler import Zaehler, Zaehlerablesung
from app.schemas.zaehler import (
    ZaehlerCreate,
    ZaehlerResponse,
    ZaehlerUpdate,
    ZaehlerablesungCreate,
    ZaehlerablesungResponse,
    ZaehlerablesungUpdate,
    ZaehlerMitAblesungenResponse,
)
from app.services.zaehler import (
    AblesePlausibilitaetError,
    ablesung_response_data,
    create_ablesung,
    create_ablesung_for_user,
    create_zaehler,
    delete_ablesung,
    delete_zaehler,
    get_ablesung,
    get_zaehler,
    get_zaehler_for_user,
    list_ablesungen,
    list_zaehler,
    list_zaehler_for_user,
    update_ablesung,
    update_zaehler,
    zaehler_response_data,
)

router = APIRouter()


def _get_client_ip(request: Request) -> str | None:
    """Ermittelt die Client-IP aus dem Request."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


@router.post(
    "",
    response_model=ZaehlerResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
async def create_zaehler_route(
    request: Request,
    data: ZaehlerCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> ZaehlerResponse:
    """Legt einen neuen Zähler für eine Einheit an (nur Vermieter)."""
    try:
        zaehler = await create_zaehler(
            db,
            vermieter_id=user.id,
            user_id=user.id,
            data=data,
            ip=_get_client_ip(request),
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    # Eager-geladenes Objekt holen, damit Einheit/Objekt-Name im Response stehen.
    zaehler = await get_zaehler(db, vermieter_id=user.id, zaehler_id=zaehler.id)
    return ZaehlerResponse.model_validate(zaehler_response_data(zaehler))


@router.get("", response_model=list[ZaehlerResponse])
async def list_zaehler_route(
    einheit_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ZaehlerResponse]:
    """Listet Zähler für Vermieter oder berechtigte Mieter."""
    zaehler = await list_zaehler_for_user(
        db,
        user_id=user.id,
        user_role=user.role,
        einheit_id=einheit_id,
    )
    return [ZaehlerResponse.model_validate(zaehler_response_data(z)) for z in zaehler]


@router.get("/{zaehler_id}", response_model=ZaehlerMitAblesungenResponse)
async def get_zaehler_route(
    zaehler_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ZaehlerMitAblesungenResponse:
    """Gibt einen Zähler inklusive Ablesungen für Vermieter oder Mieter zurück."""
    zaehler = await get_zaehler_for_user(db, user_id=user.id, user_role=user.role, zaehler_id=zaehler_id)
    if zaehler is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zähler nicht gefunden.")
    data = zaehler_response_data(zaehler)
    data["ablesungen"] = [ZaehlerablesungResponse.model_validate(ablesung_response_data(a)).model_dump() for a in zaehler.ablesungen]
    return ZaehlerMitAblesungenResponse.model_validate(data)


@router.patch("/{zaehler_id}", response_model=ZaehlerResponse)
async def update_zaehler_route(
    request: Request,
    zaehler_id: int,
    data: ZaehlerUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> ZaehlerResponse:
    """Aktualisiert einen Zähler (nur Vermieter)."""
    zaehler = await get_zaehler(db, vermieter_id=user.id, zaehler_id=zaehler_id)
    if zaehler is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zähler nicht gefunden.")
    await update_zaehler(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        zaehler=zaehler,
        data=data,
        ip=_get_client_ip(request),
    )
    # Eager-geladenes Objekt holen, damit Einheit/Objekt-Name im Response stehen.
    zaehler = await get_zaehler(db, vermieter_id=user.id, zaehler_id=zaehler_id)
    return ZaehlerResponse.model_validate(zaehler_response_data(zaehler))


@router.delete("/{zaehler_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_zaehler_route(
    request: Request,
    zaehler_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> None:
    """Löscht einen Zähler inklusive aller Ablesungen (nur Vermieter)."""
    zaehler = await get_zaehler(db, vermieter_id=user.id, zaehler_id=zaehler_id)
    if zaehler is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zähler nicht gefunden.")
    await delete_zaehler(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        zaehler=zaehler,
        ip=_get_client_ip(request),
    )
    await db.commit()


@router.post(
    "/{zaehler_id}/ablesungen",
    response_model=ZaehlerablesungResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_ablesung_route(
    request: Request,
    zaehler_id: int,
    data: ZaehlerablesungCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Zaehlerablesung:
    """Legt eine neue Ablesung an (Vermieter oder berechtigter Mieter)."""
    try:
        ablesung = await create_ablesung_for_user(
            db,
            user_id=user.id,
            user_role=user.role,
            zaehler_id=zaehler_id,
            data=data,
            ip=_get_client_ip(request),
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AblesePlausibilitaetError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return ablesung


@router.get("/{zaehler_id}/ablesungen", response_model=list[ZaehlerablesungResponse])
async def list_ablesungen_route(
    zaehler_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ZaehlerablesungResponse]:
    """Listet alle Ablesungen eines Zählers (Vermieter oder berechtigter Mieter)."""
    zaehler = await get_zaehler_for_user(db, user_id=user.id, user_role=user.role, zaehler_id=zaehler_id)
    if zaehler is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zähler nicht gefunden.")
    ablesungen = await list_ablesungen(db, vermieter_id=zaehler.vermieter_id, zaehler_id=zaehler_id)
    return [ZaehlerablesungResponse.model_validate(ablesung_response_data(a)) for a in ablesungen]


@router.get("/{zaehler_id}/ablesungen/{ablesung_id}", response_model=ZaehlerablesungResponse)
async def get_ablesung_route(
    zaehler_id: int,
    ablesung_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ZaehlerablesungResponse:
    """Gibt eine einzelne Ablesung zurück."""
    zaehler = await get_zaehler_for_user(db, user_id=user.id, user_role=user.role, zaehler_id=zaehler_id)
    if zaehler is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zähler nicht gefunden.")
    ablesung = await get_ablesung(db, vermieter_id=zaehler.vermieter_id, ablesung_id=ablesung_id)
    if ablesung is None or ablesung.zaehler_id != zaehler_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ablesung nicht gefunden.",
        )
    return ZaehlerablesungResponse.model_validate(ablesung_response_data(ablesung))


@router.patch("/{zaehler_id}/ablesungen/{ablesung_id}", response_model=ZaehlerablesungResponse)
async def update_ablesung_route(
    request: Request,
    zaehler_id: int,
    ablesung_id: int,
    data: ZaehlerablesungUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> ZaehlerablesungResponse:
    """Aktualisiert eine Ablesung (nur Vermieter)."""
    zaehler = await get_zaehler(db, vermieter_id=user.id, zaehler_id=zaehler_id)
    if zaehler is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zähler nicht gefunden.")
    ablesung = await get_ablesung(db, vermieter_id=user.id, ablesung_id=ablesung_id)
    if ablesung is None or ablesung.zaehler_id != zaehler_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ablesung nicht gefunden.",
        )
    try:
        ablesung = await update_ablesung(
            db,
            vermieter_id=user.id,
            user_id=user.id,
            ablesung=ablesung,
            data=data,
            ip=_get_client_ip(request),
        )
    except AblesePlausibilitaetError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return ZaehlerablesungResponse.model_validate(ablesung_response_data(ablesung))


@router.delete(
    "/{zaehler_id}/ablesungen/{ablesung_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_ablesung_route(
    request: Request,
    zaehler_id: int,
    ablesung_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> None:
    """Löscht eine Ablesung (nur Vermieter)."""
    zaehler = await get_zaehler(db, vermieter_id=user.id, zaehler_id=zaehler_id)
    if zaehler is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zähler nicht gefunden.")
    ablesung = await get_ablesung(db, vermieter_id=user.id, ablesung_id=ablesung_id)
    if ablesung is None or ablesung.zaehler_id != zaehler_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ablesung nicht gefunden.",
        )
    await delete_ablesung(
        db,
        vermieter_id=user.id,
        user_id=user.id,
        ablesung=ablesung,
        ip=_get_client_ip(request),
    )
    await db.commit()
