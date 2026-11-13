"""Mieter-Service — CRUD-Logik für Mieter-Stammdaten."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.einheit import Einheit
from app.models.mieter import Mieter
from app.schemas.mieter import MieterCreate, MieterUpdate
from app.services.audit_log import audit_log
from app.services.crypto import encrypt_value


async def create_mieter(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    data: MieterCreate,
    ip: str | None = None,
) -> Mieter:
    """Legt einen neuen Mieter für einen Vermieter an."""
    payload = data.model_dump()
    birth_date = payload.pop("birth_date", None)

    mieter = Mieter(
        vermieter_id=vermieter_id,
        first_name=payload["first_name"],
        last_name=payload["last_name"],
        email=payload.get("email"),
        phone=payload.get("phone"),
        birth_date_enc=encrypt_value(birth_date.isoformat() if birth_date else None),
        status=payload.get("status", "aktiv"),
        since=payload.get("since"),
    )
    db.add(mieter)
    await db.flush()
    await db.refresh(mieter)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="mieter_create",
        entity="mieter",
        entity_id=mieter.id,
        details={"name": mieter.full_name},
        ip=ip,
        risk_level="niedrig",
    )
    return mieter


async def list_mieter(
    db: AsyncSession,
    vermieter_id: int,
) -> list[Mieter]:
    """Liste aller nicht gelöschten Mieter eines Vermieters."""
    result = await db.execute(
        select(Mieter)
        .where(
            Mieter.vermieter_id == vermieter_id,
            Mieter.deleted_at.is_(None),
        )
        .order_by(Mieter.last_name.asc(), Mieter.first_name.asc())
    )
    return list(result.scalars().all())


async def get_mieter(
    db: AsyncSession,
    vermieter_id: int,
    mieter_id: int,
) -> Mieter | None:
    """Liefert einen Mieter, falls er dem Vermieter gehört."""
    result = await db.execute(
        select(Mieter).where(
            Mieter.id == mieter_id,
            Mieter.vermieter_id == vermieter_id,
            Mieter.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def update_mieter(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    mieter: Mieter,
    data: MieterUpdate,
    ip: str | None = None,
) -> Mieter:
    """Aktualisiert einen Mieter mit den übergebenen Feldern."""
    update_fields = data.model_dump(exclude_unset=True)

    # Geburtsdatum wird verschlüsselt in der DB abgelegt.
    if "birth_date" in update_fields:
        birth_date = update_fields.pop("birth_date")
        mieter.birth_date_enc = encrypt_value(
            birth_date.isoformat() if birth_date else None
        )

    for field, value in update_fields.items():
        setattr(mieter, field, value)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="mieter_update",
        entity="mieter",
        entity_id=mieter.id,
        details={"updated_fields": list(update_fields.keys())},
        ip=ip,
        risk_level="niedrig",
    )
    await db.flush()
    await db.refresh(mieter)
    return mieter


async def get_aktuelle_einheit(
    db: AsyncSession,
    mieter_id: int,
) -> Einheit | None:
    """Ermittelt die aktuell vermietete Einheit eines Mieters."""
    from datetime import date

    from app.models.mietvertraege import Mietvertrag

    result = await db.execute(
        select(Mietvertrag, Einheit)
        .join(Einheit, Mietvertrag.einheit_id == Einheit.id)
        .where(
            Mietvertrag.mieter_id == mieter_id,
            Mietvertrag.status == "aktiv",
            Mietvertrag.deleted_at.is_(None),
            Einheit.deleted_at.is_(None),
        )
        .order_by(Mietvertrag.mietbeginn.desc())
        .limit(1)
    )
    row = result.first()
    if not row:
        return None
    vertrag, einheit = row
    if vertrag.mietende and vertrag.mietende < date.today():
        # Technisch abgelaufen, aber noch aktiv eingestuft.
        return einheit
    return einheit


async def delete_mieter(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    mieter: Mieter,
    ip: str | None = None,
) -> None:
    """Markiert einen Mieter als gelöscht (Soft-Delete)."""
    from datetime import UTC, datetime

    mieter.deleted_at = datetime.now(UTC)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="mieter_delete",
        entity="mieter",
        entity_id=mieter.id,
        details={"name": mieter.full_name},
        ip=ip,
        risk_level="mittel",
    )
    await db.flush()
