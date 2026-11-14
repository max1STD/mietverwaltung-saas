"""DSGVO-Einwilligungs-Endpunkte (Art. 7 DSGVO)."""
from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import _get_client_ip, get_current_user
from app.middleware.auth import csrf_protect as auth_csrf
from app.models.einwilligung import Einwilligung
from app.models.user import User
from app.schemas.auth import ConsentRequest, ConsentResponse, MessageResponse

router = APIRouter()


def _to_response(e: Einwilligung) -> ConsentResponse:
    return ConsentResponse(
        id=e.id,
        purpose=e.purpose,
        version=e.version,
        consent_text=e.consent_text,
        consented_at=e.consented_at.isoformat() if e.consented_at else None,
        withdrawn_at=e.withdrawn_at.isoformat() if e.withdrawn_at else None,
    )


@router.get("", response_model=list[ConsentResponse])
async def list_consents(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ConsentResponse]:
    """Liste aller Einwilligungen des eingeloggten Users."""
    result = await db.execute(
        select(Einwilligung)
        .where(Einwilligung.user_id == user.id)
        .order_by(Einwilligung.created_at.desc())
    )
    return [_to_response(e) for e in result.scalars().all()]


@router.post(
    "",
    response_model=ConsentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(auth_csrf)],
)
async def create_or_update_consent(
    request: Request,
    data: ConsentRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ConsentResponse:
    """Erteilt eine neue oder aktualisierte Einwilligung."""
    # Bestehende offene Einwilligung für denselben Zweck widerrufen.
    existing = await db.execute(
        select(Einwilligung).where(
            Einwilligung.user_id == user.id,
            Einwilligung.purpose == data.purpose,
            Einwilligung.withdrawn_at.is_(None),
        )
    )
    for old in existing.scalars().all():
        old.withdrawn_at = datetime.now(UTC)

    consent = Einwilligung(
        user_id=user.id,
        purpose=data.purpose,
        consent_text=data.consent_text,
        version=data.version,
        consented_at=datetime.now(UTC),
        ip_address=_get_client_ip(request),
    )
    db.add(consent)
    await db.commit()
    await db.refresh(consent)
    return _to_response(consent)


@router.post(
    "/{purpose}/withdraw",
    response_model=MessageResponse,
    dependencies=[Depends(auth_csrf)],
)
async def withdraw_consent(
    purpose: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MessageResponse:
    """Widerruft alle aktiven Einwilligungen für einen Zweck."""
    result = await db.execute(
        select(Einwilligung).where(
            Einwilligung.user_id == user.id,
            Einwilligung.purpose == purpose,
            Einwilligung.withdrawn_at.is_(None),
        )
    )
    updated = 0
    for consent in result.scalars().all():
        consent.withdrawn_at = datetime.now(UTC)
        updated += 1
    await db.commit()
    if updated == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keine aktive Einwilligung für diesen Zweck",
        )
    return MessageResponse(message=f"{updated} Einwilligung(en) widerrufen")
