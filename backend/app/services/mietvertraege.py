"""Mietvertrag-Service — CRUD-Logik für Mietverträge."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.einheit import Einheit
from app.models.mieter import Mieter
from app.models.mietvertraege import Mietvertrag
from app.schemas.mietvertrag import MietvertragCreate, MietvertragUpdate
from app.services.audit_log import audit_log
from app.services.einheiten import get_aktueller_mieter


async def create_mietvertrag(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    data: MietvertragCreate,
    ip: str | None = None,
) -> Mietvertrag:
    """Legt einen neuen Mietvertrag an.

    Prüft vorab, dass Mieter und Einheit dem Vermieter gehören und
    die Einheit nicht bereits aktiv vermietet ist (Überbelegung verhindern).
    """
    # Eigentümerschaft validieren
    mieter = await db.get(Mieter, data.mieter_id)
    einheit = await db.get(Einheit, data.einheit_id)

    if not mieter or mieter.vermieter_id != vermieter_id or mieter.deleted_at is not None:
        raise ValueError("Mieter nicht gefunden oder nicht berechtigt")
    if not einheit or einheit.vermieter_id != vermieter_id or einheit.deleted_at is not None:
        raise ValueError("Einheit nicht gefunden oder nicht berechtigt")

    # Doppelbelegung verhindern: nur ein aktiver Vertrag pro Einheit.
    existing = await get_aktueller_mieter(db, data.einheit_id)
    if existing and existing.id is not None and existing.status == "aktiv":
        raise ValueError("Einheit ist bereits aktiv vermietet")

    vertrag = Mietvertrag(
        vermieter_id=vermieter_id,
        **data.model_dump(exclude={"kaltmiete", "nebenkosten_vorschuss"}),
    )
    db.add(vertrag)
    await db.flush()
    await db.refresh(vertrag)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="mietvertrag_create",
        entity="mietvertraege",
        entity_id=vertrag.id,
        details={
            "mieter_id": vertrag.mieter_id,
            "einheit_id": vertrag.einheit_id,
            "mietbeginn": str(vertrag.mietbeginn),
        },
        ip=ip,
        risk_level="niedrig",
    )
    return vertrag


async def list_mietvertraege(
    db: AsyncSession,
    vermieter_id: int,
    einheit_id: int | None = None,
    mieter_id: int | None = None,
) -> list[Mietvertrag]:
    """Liste aller nicht gelöschten Mietverträge eines Vermieters."""
    query = select(Mietvertrag).where(
        Mietvertrag.vermieter_id == vermieter_id,
        Mietvertrag.deleted_at.is_(None),
    )
    if einheit_id is not None:
        query = query.where(Mietvertrag.einheit_id == einheit_id)
    if mieter_id is not None:
        query = query.where(Mietvertrag.mieter_id == mieter_id)
    query = query.order_by(Mietvertrag.mietbeginn.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_mietvertrag(
    db: AsyncSession,
    vermieter_id: int,
    vertrag_id: int,
) -> Mietvertrag | None:
    """Liefert einen Mietvertrag, falls er dem Vermieter gehört."""
    result = await db.execute(
        select(Mietvertrag).where(
            Mietvertrag.id == vertrag_id,
            Mietvertrag.vermieter_id == vermieter_id,
            Mietvertrag.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def update_mietvertrag(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    vertrag: Mietvertrag,
    data: MietvertragUpdate,
    ip: str | None = None,
) -> Mietvertrag:
    """Aktualisiert einen Mietvertrag mit den übergebenen Feldern."""
    update_fields = data.model_dump(exclude_unset=True, exclude={"kaltmiete", "nebenkosten_vorschuss"})
    for field, value in update_fields.items():
        setattr(vertrag, field, value)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="mietvertrag_update",
        entity="mietvertraege",
        entity_id=vertrag.id,
        details={"updated_fields": list(update_fields.keys())},
        ip=ip,
        risk_level="niedrig",
    )
    await db.flush()
    await db.refresh(vertrag)
    return vertrag


async def delete_mietvertrag(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    vertrag: Mietvertrag,
    ip: str | None = None,
) -> None:
    """Markiert einen Mietvertrag als gelöscht (Soft-Delete)."""
    from datetime import UTC, datetime

    vertrag.deleted_at = datetime.now(UTC)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="mietvertrag_delete",
        entity="mietvertraege",
        entity_id=vertrag.id,
        details={"mieter_id": vertrag.mieter_id, "einheit_id": vertrag.einheit_id},
        ip=ip,
        risk_level="mittel",
    )
    await db.flush()
