"""Einheit-Service — CRUD-Logik für Wohneinheiten."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.einheit import Einheit
from app.models.mietvertraege import Mietvertrag
from app.schemas.einheit import EinheitCreate, EinheitUpdate
from app.services.audit_log import audit_log


async def create_einheit(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    data: EinheitCreate,
    ip: str | None = None,
) -> Einheit:
    """Legt eine neue Wohneinheit innerhalb eines Objekts an."""
    from sqlalchemy import text

    result = await db.execute(text("SELECT nextval('einheiten_public_id_seq')"))
    public_id = result.scalar()

    einheit = Einheit(
        vermieter_id=vermieter_id,
        public_id=public_id,
        **data.model_dump(),
    )
    db.add(einheit)
    await db.flush()
    await db.refresh(einheit)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="einheit_create",
        entity="einheiten",
        entity_id=einheit.id,
        details={"name": einheit.name, "objekt_id": einheit.objekt_id, "public_id": public_id},
        ip=ip,
        risk_level="niedrig",
    )
    return einheit


async def list_einheiten(
    db: AsyncSession,
    vermieter_id: int | None = None,
    objekt_id: int | None = None,
) -> list[Einheit]:
    """Liste aller nicht gelöschten Einheiten eines Vermieters (optional gefiltert nach Objekt)."""
    query = select(Einheit).where(
        Einheit.vermieter_id == vermieter_id if vermieter_id is not None else True,
        Einheit.deleted_at.is_(None),
    )
    if objekt_id is not None:
        query = query.where(Einheit.objekt_id == objekt_id)
    query = query.order_by(Einheit.name.asc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_einheit(
    db: AsyncSession,
    vermieter_id: int,
    einheit_id: int,
) -> Einheit | None:
    """Liefert eine Einheit, falls sie dem Vermieter gehört."""
    result = await db.execute(
        select(Einheit).where(
            Einheit.id == einheit_id,
            Einheit.vermieter_id == vermieter_id,
            Einheit.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def update_einheit(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    einheit: Einheit,
    data: EinheitUpdate,
    ip: str | None = None,
) -> Einheit:
    """Aktualisiert eine Einheit mit den übergebenen Feldern."""
    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(einheit, field, value)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="einheit_update",
        entity="einheiten",
        entity_id=einheit.id,
        details={"updated_fields": list(update_fields.keys())},
        ip=ip,
        risk_level="niedrig",
    )
    await db.flush()
    await db.refresh(einheit)
    return einheit


async def delete_einheit(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    einheit: Einheit,
    ip: str | None = None,
) -> None:
    """Markiert eine Einheit als gelöscht (Soft-Delete), sofern kein aktiver Mietvertrag besteht."""
    from datetime import UTC, datetime

    # Harte Regel: Einheiten mit aktivem Mietvertrag dürfen nicht gelöscht werden.
    active_contract = await db.execute(
        select(Mietvertrag).where(
            Mietvertrag.einheit_id == einheit.id,
            Mietvertrag.status == "aktiv",
            Mietvertrag.deleted_at.is_(None),
        ).limit(1)
    )
    if active_contract.scalar_one_or_none() is not None:
        raise ValueError(
            "Einheit kann nicht gelöscht werden, da noch ein aktiver Mietvertrag besteht."
        )

    einheit.deleted_at = datetime.now(UTC)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="einheit_delete",
        entity="einheiten",
        entity_id=einheit.id,
        details={"name": einheit.name},
        ip=ip,
        risk_level="mittel",
    )
    await db.flush()


async def get_aktueller_mieter(
    db: AsyncSession,
    einheit_id: int,
) -> Mietvertrag | None:
    """Ermittelt den aktiven Mietvertrag (aktueller Mieter) einer Einheit."""
    from datetime import date

    result = await db.execute(
        select(Mietvertrag)
        .where(
            Mietvertrag.einheit_id == einheit_id,
            Mietvertrag.status == "aktiv",
            Mietvertrag.deleted_at.is_(None),
        )
        .order_by(Mietvertrag.mietbeginn.desc())
        .limit(1)
    )
    vertrag = result.scalar_one_or_none()
    if vertrag and vertrag.mietende and vertrag.mietende < date.today():
        # Vertrag ist zeitlich abgelaufen, gilt aber noch als aktiv bis Kündigung.
        return vertrag
    return vertrag


async def is_einheit_vermietet(
    db: AsyncSession,
    einheit_id: int,
) -> bool:
    """Prüft, ob eine Einheit aktuell vermietet ist."""
    vertrag = await get_aktueller_mieter(db, einheit_id)
    return vertrag is not None
