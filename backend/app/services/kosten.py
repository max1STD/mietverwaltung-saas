"""Kosten-Service — CRUD, Soft-Delete und KI-Scan-Stub für Kosten."""
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.kosten import Kosten
from app.models.kostenkategorien import Kostenkategorie
from app.schemas.kosten import KostenCreate, KostenScanResponse, KostenUpdate
from app.services.audit_log import audit_log


async def create_kosten(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    data: KostenCreate,
    ip: str | None = None,
) -> Kosten:
    """Legt eine neue Kostenposition an."""
    kosten = Kosten(
        vermieter_id=vermieter_id,
        **data.model_dump(),
    )
    db.add(kosten)
    await db.flush()
    await db.refresh(kosten)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="kosten_create",
        entity="kosten",
        entity_id=kosten.id,
        details={
            "betrag": str(kosten.betrag),
            "datum": kosten.datum.isoformat(),
            "kategorie_id": kosten.kategorie_id,
        },
        ip=ip,
        risk_level="niedrig",
    )
    return kosten


async def list_kosten(
    db: AsyncSession,
    vermieter_id: int,
    objekt_id: int | None = None,
    einheit_id: int | None = None,
    kategorie_id: int | None = None,
    abrechnung_id: int | None = None,
) -> list[Kosten]:
    """Liste aller nicht gelöschten Kosten eines Vermieters, optional gefiltert."""
    query = select(Kosten).where(
        Kosten.vermieter_id == vermieter_id,
        Kosten.deleted_at.is_(None),
    )
    if objekt_id is not None:
        query = query.where(Kosten.objekt_id == objekt_id)
    if einheit_id is not None:
        query = query.where(Kosten.einheit_id == einheit_id)
    if kategorie_id is not None:
        query = query.where(Kosten.kategorie_id == kategorie_id)
    if abrechnung_id is not None:
        query = query.where(Kosten.abrechnung_id == abrechnung_id)

    query = query.order_by(Kosten.datum.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_kosten(
    db: AsyncSession,
    vermieter_id: int,
    kosten_id: int,
) -> Kosten | None:
    """Liefert eine einzelne Kostenposition, falls sie dem Vermieter gehört."""
    result = await db.execute(
        select(Kosten).where(
            Kosten.id == kosten_id,
            Kosten.vermieter_id == vermieter_id,
            Kosten.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def update_kosten(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    kosten: Kosten,
    data: KostenUpdate,
    ip: str | None = None,
) -> Kosten:
    """Aktualisiert eine Kostenposition mit den übergebenen Feldern."""
    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(kosten, field, value)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="kosten_update",
        entity="kosten",
        entity_id=kosten.id,
        details={"updated_fields": list(update_fields.keys())},
        ip=ip,
        risk_level="niedrig",
    )
    await db.flush()
    await db.refresh(kosten)
    return kosten


async def delete_kosten(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    kosten: Kosten,
    ip: str | None = None,
) -> None:
    """Markiert eine Kostenposition als gelöscht (Soft-Delete)."""
    kosten.deleted_at = datetime.now(UTC)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="kosten_delete",
        entity="kosten",
        entity_id=kosten.id,
        details={"betrag": str(kosten.betrag)},
        ip=ip,
        risk_level="mittel",
    )
    await db.flush()


async def scan_kosten_stub(
    _db: AsyncSession,
    vermieter_id: int,
) -> KostenScanResponse:
    """Stub für OCR/KI-Belegscan — liefert einen festen Vorschlag zurück."""
    _ = vermieter_id
    return KostenScanResponse(
        kategorie_name="Heizkosten",
        betrag=Decimal("245.80"),
        datum=datetime.now(UTC).date(),
        umlagefaehig=True,
        konfidenz="mittel",
    )


async def get_or_create_default_kategorien(
    db: AsyncSession,
    vermieter_id: int,
) -> list[Kostenkategorie]:
    """Legt die Standard-Kostenkategorien für einen Vermieter an, falls sie fehlen."""
    defaults = [
        {
            "name": "Heizkosten",
            "betrkv_key": "heizung",
            "umlagefaehig": True,
            "verteilungsschluessel": "qm",
        },
        {
            "name": "Wasserkosten",
            "betrkv_key": "wasser",
            "umlagefaehig": True,
            "verteilungsschluessel": "verbrauch",
        },
        {
            "name": "Stromkosten",
            "betrkv_key": "strom",
            "umlagefaehig": True,
            "verteilungsschluessel": "qm",
        },
        {
            "name": "Versicherung",
            "betrkv_key": "versicherung",
            "umlagefaehig": True,
            "verteilungsschluessel": "qm",
        },
        {
            "name": "Müllgebühren",
            "betrkv_key": "muell",
            "umlagefaehig": True,
            "verteilungsschluessel": "personen",
        },
        {
            "name": "Grundsteuer",
            "betrkv_key": "grundsteuer",
            "umlagefaehig": True,
            "verteilungsschluessel": "qm",
        },
        {
            "name": "Garten/Pflege",
            "betrkv_key": "garten",
            "umlagefaehig": True,
            "verteilungsschluessel": "qm",
        },
        {
            "name": "Schornsteinfeger",
            "betrkv_key": "schornstein",
            "umlagefaehig": True,
            "verteilungsschluessel": "qm",
        },
    ]

    result = await db.execute(
        select(Kostenkategorie).where(
            Kostenkategorie.vermieter_id == vermieter_id,
            Kostenkategorie.is_default.is_(True),
        )
    )
    existing = {cat.name for cat in result.scalars().all()}
    created: list[Kostenkategorie] = []

    for item in defaults:
        if item["name"] not in existing:
            cat = Kostenkategorie(
                vermieter_id=vermieter_id,
                name=item["name"],
                betrvk_key=item["betrkv_key"],
                umlagefaehig=item["umlagefaehig"],
                verteilungsschluessel=item["verteilungsschluessel"],
                is_default=True,
            )
            db.add(cat)
            created.append(cat)

    if created:
        await db.flush()
        for cat in created:
            await db.refresh(cat)

    return created
