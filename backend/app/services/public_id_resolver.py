"""Hilfsfunktionen zum Aufloesen von oeffentlichen IDs auf interne Datensaetze."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.einheit import Einheit
from app.models.mieter import Mieter
from app.models.mietvertraege import Mietvertrag
from app.models.objekt import Objekt


async def resolve_objekt(db: AsyncSession, vermieter_id: int, entity_id: int) -> Objekt | None:
    """Loesst Objekt-ID auf: zuerst interne ID, dann public_id."""
    obj = await db.get(Objekt, entity_id)
    if obj and obj.vermieter_id == vermieter_id and obj.deleted_at is None:
        return obj
    result = await db.execute(
        select(Objekt).where(
            Objekt.public_id == entity_id,
            Objekt.vermieter_id == vermieter_id,
            Objekt.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def resolve_einheit(db: AsyncSession, vermieter_id: int, entity_id: int) -> Einheit | None:
    """Loesst Einheit-ID auf: zuerst interne ID, dann public_id."""
    einheit = await db.get(Einheit, entity_id)
    if einheit and einheit.vermieter_id == vermieter_id and einheit.deleted_at is None:
        return einheit
    result = await db.execute(
        select(Einheit).where(
            Einheit.public_id == entity_id,
            Einheit.vermieter_id == vermieter_id,
            Einheit.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def resolve_mieter(db: AsyncSession, vermieter_id: int, entity_id: int) -> Mieter | None:
    """Loesst Mieter-ID auf: zuerst interne ID, dann public_id."""
    mieter = await db.get(Mieter, entity_id)
    if mieter and mieter.vermieter_id == vermieter_id and mieter.deleted_at is None:
        return mieter
    result = await db.execute(
        select(Mieter).where(
            Mieter.public_id == entity_id,
            Mieter.vermieter_id == vermieter_id,
            Mieter.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def resolve_mietvertrag(db: AsyncSession, vermieter_id: int, entity_id: int) -> Mietvertrag | None:
    """Loesst Mietvertrag-ID auf: zuerst interne ID, dann public_id."""
    vertrag = await db.get(Mietvertrag, entity_id)
    if vertrag and vertrag.vermieter_id == vermieter_id and vertrag.deleted_at is None:
        return vertrag
    result = await db.execute(
        select(Mietvertrag).where(
            Mietvertrag.public_id == entity_id,
            Mietvertrag.vermieter_id == vermieter_id,
            Mietvertrag.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()
