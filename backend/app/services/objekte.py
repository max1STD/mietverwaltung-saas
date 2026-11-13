"""Objekt-Service — CRUD-Logik für Immobilien."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.objekt import Objekt
from app.schemas.objekt import ObjektCreate, ObjektUpdate
from app.services.audit_log import audit_log


async def create_objekt(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    data: ObjektCreate,
    ip: str | None = None,
) -> Objekt:
    """Legt ein neues Objekt für einen Vermieter an."""
    objekt = Objekt(
        vermieter_id=vermieter_id,
        **data.model_dump(),
    )
    db.add(objekt)
    await db.flush()
    await db.refresh(objekt)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="objekt_create",
        entity="objekte",
        entity_id=objekt.id,
        details={"name": objekt.name},
        ip=ip,
        risk_level="niedrig",
    )
    return objekt


async def list_objekte(
    db: AsyncSession,
    vermieter_id: int,
) -> list[Objekt]:
    """Liste aller nicht gelöschten Objekte eines Vermieters."""
    result = await db.execute(
        select(Objekt)
        .where(
            Objekt.vermieter_id == vermieter_id,
            Objekt.deleted_at.is_(None),
        )
        .order_by(Objekt.name.asc())
    )
    return list(result.scalars().all())


async def get_objekt(
    db: AsyncSession,
    vermieter_id: int,
    objekt_id: int,
) -> Objekt | None:
    """Liefert ein einzelnes Objekt, falls es dem Vermieter gehört."""
    result = await db.execute(
        select(Objekt).where(
            Objekt.id == objekt_id,
            Objekt.vermieter_id == vermieter_id,
            Objekt.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def update_objekt(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    objekt: Objekt,
    data: ObjektUpdate,
    ip: str | None = None,
) -> Objekt:
    """Aktualisiert ein Objekt mit den übergebenen Feldern."""
    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(objekt, field, value)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="objekt_update",
        entity="objekte",
        entity_id=objekt.id,
        details={"updated_fields": list(update_fields.keys())},
        ip=ip,
        risk_level="niedrig",
    )
    await db.flush()
    await db.refresh(objekt)
    return objekt


async def delete_objekt(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    objekt: Objekt,
    ip: str | None = None,
) -> None:
    """Markiert ein Objekt als gelöscht (Soft-Delete)."""
    from datetime import UTC, datetime

    objekt.deleted_at = datetime.now(UTC)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="objekt_delete",
        entity="objekte",
        entity_id=objekt.id,
        details={"name": objekt.name},
        ip=ip,
        risk_level="mittel",
    )
    await db.flush()
