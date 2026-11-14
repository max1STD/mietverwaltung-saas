"""Mietzahlungen-Service — CRUD, Zahlungsmarkierung und Mahnstufe."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mietzahlungen import Mietzahlung
from app.schemas.mietzahlung import MietzahlungCreate, MietzahlungUpdate
from app.services.audit_log import audit_log


async def create_mietzahlung(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    data: MietzahlungCreate,
    ip: str | None = None,
) -> Mietzahlung:
    """Legt eine neue Mietzahlung an."""
    zahlung = Mietzahlung(
        vermieter_id=vermieter_id,
        **data.model_dump(),
    )
    db.add(zahlung)
    await db.flush()
    await db.refresh(zahlung)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="mietzahlung_create",
        entity="mietzahlungen",
        entity_id=zahlung.id,
        details={
            "betrag_soll": str(zahlung.betrag_soll),
            "betrag_ist": str(zahlung.betrag_ist) if zahlung.betrag_ist else None,
            "vertrag_id": zahlung.vertrag_id,
        },
        ip=ip,
        risk_level="niedrig",
    )
    return zahlung


async def list_mietzahlungen(
    db: AsyncSession,
    vermieter_id: int,
    mieter_id: int | None = None,
    vertrag_id: int | None = None,
) -> list[Mietzahlung]:
    """Liste aller Mietzahlungen eines Vermieters, optional gefiltert."""
    query = select(Mietzahlung).where(Mietzahlung.vermieter_id == vermieter_id)
    if mieter_id is not None:
        query = query.where(Mietzahlung.mieter_id == mieter_id)
    if vertrag_id is not None:
        query = query.where(Mietzahlung.vertrag_id == vertrag_id)

    query = query.order_by(Mietzahlung.zahlungsdatum.desc().nullslast())
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_mietzahlung(
    db: AsyncSession,
    vermieter_id: int,
    zahlung_id: int,
) -> Mietzahlung | None:
    """Liefert eine einzelne Mietzahlung, falls sie dem Vermieter gehört."""
    result = await db.execute(
        select(Mietzahlung).where(
            Mietzahlung.id == zahlung_id,
            Mietzahlung.vermieter_id == vermieter_id,
        )
    )
    return result.scalar_one_or_none()


async def update_mietzahlung(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    zahlung: Mietzahlung,
    data: MietzahlungUpdate,
    ip: str | None = None,
) -> Mietzahlung:
    """Aktualisiert eine Mietzahlung mit den übergebenen Feldern."""
    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(zahlung, field, value)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="mietzahlung_update",
        entity="mietzahlungen",
        entity_id=zahlung.id,
        details={"updated_fields": list(update_fields.keys())},
        ip=ip,
        risk_level="niedrig",
    )
    await db.flush()
    await db.refresh(zahlung)
    return zahlung


async def delete_mietzahlung(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    zahlung: Mietzahlung,
    ip: str | None = None,
) -> None:
    """Löscht eine Mietzahlung physisch (kein Soft-Delete in der DB)."""
    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="mietzahlung_delete",
        entity="mietzahlungen",
        entity_id=zahlung.id,
        details={"betrag_soll": str(zahlung.betrag_soll)},
        ip=ip,
        risk_level="mittel",
    )
    await db.delete(zahlung)
    await db.flush()


async def mark_paid(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    zahlung: Mietzahlung,
    betrag_ist: Decimal,
    zahlungsdatum: datetime,
    ip: str | None = None,
) -> Mietzahlung:
    """Markiert eine Mietzahlung als bezahlt."""
    zahlung.betrag_ist = betrag_ist
    zahlung.zahlungsdatum = zahlungsdatum

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="mietzahlung_mark_paid",
        entity="mietzahlungen",
        entity_id=zahlung.id,
        details={
            "betrag_ist": str(betrag_ist),
            "zahlungsdatum": zahlungsdatum.isoformat(),
        },
        ip=ip,
        risk_level="niedrig",
    )
    await db.flush()
    await db.refresh(zahlung)
    return zahlung


async def erhoehe_mahnstufe(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    zahlung: Mietzahlung,
    ip: str | None = None,
) -> Mietzahlung:
    """Erhöht die Mahnstufe einer Mietzahlung um eins."""
    zahlung.mahnstufe = (zahlung.mahnstufe or 0) + 1

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="mietzahlung_mahnstufe",
        entity="mietzahlungen",
        entity_id=zahlung.id,
        details={"mahnstufe": zahlung.mahnstufe},
        ip=ip,
        risk_level="mittel",
    )
    await db.flush()
    await db.refresh(zahlung)
    return zahlung
