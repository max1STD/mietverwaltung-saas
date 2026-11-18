"""Mietzahlungen-Service — CRUD, Fälligkeiten und Mahnstufen."""
from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.einheit import Einheit
from app.models.mietvertraege import Mietvertrag
from app.models.mietzahlungen import Mietzahlung
from app.models.user import User
from app.schemas.mietzahlung import MietzahlungCreate, MietzahlungUpdate
from app.services.audit_log import audit_log
from app.services.mietvertraege import _resolve_mieter_for_user


def _vertrag_gueltig(vertrag: Mietvertrag | None, vermieter_id: int) -> bool:
    """Prüft, ob der Vertrag existiert und dem Vermieter gehört."""
    return bool(
        vertrag
        and vertrag.vermieter_id == vermieter_id
        and vertrag.deleted_at is None
    )


async def create_mietzahlung(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    data: MietzahlungCreate,
    ip: str | None = None,
) -> Mietzahlung:
    """Legt eine neue Mietzahlung an."""
    vertrag: Mietvertrag | None = None
    if data.vertrag_id:
        vertrag = await db.get(Mietvertrag, data.vertrag_id)
        if not _vertrag_gueltig(vertrag, vermieter_id):
            raise ValueError("Mietvertrag nicht gefunden oder nicht berechtigt")

    mieter_id = data.mieter_id or (vertrag.mieter_id if vertrag else None)

    zahlung = Mietzahlung(
        vermieter_id=vermieter_id,
        mieter_id=mieter_id,
        vertrag_id=data.vertrag_id,
        betrag_soll=data.betrag_soll,
        betrag_ist=data.betrag_ist,
        zahlungsdatum=data.zahlungsdatum,
        mahnstufe=data.mahnstufe or 0,
        zahlungsreferenz=data.zahlungsreferenz,
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
            "vertrag_id": data.vertrag_id,
            "betrag_soll": str(data.betrag_soll),
            "mahnstufe": zahlung.mahnstufe,
        },
        ip=ip,
        risk_level="mittel",
    )
    return zahlung


async def list_mietzahlungen(
    db: AsyncSession,
    vermieter_id: int,
    mieter_id: int | None = None,
    vertrag_id: int | None = None,
    offen: bool | None = None,
) -> list[Mietzahlung]:
    """Liste aller Mietzahlungen eines Vermieters, optional gefiltert."""
    query = select(Mietzahlung).options(
        joinedload(Mietzahlung.mieter),
        joinedload(Mietzahlung.vertrag).joinedload(Mietvertrag.einheit).joinedload(Einheit.objekt),
    ).where(
        Mietzahlung.vermieter_id == vermieter_id,
        Mietzahlung.deleted_at.is_(None),
    )
    if mieter_id is not None:
        query = query.where(Mietzahlung.mieter_id == mieter_id)
    if vertrag_id is not None:
        query = query.where(Mietzahlung.vertrag_id == vertrag_id)
    if offen:
        query = query.where(
            (Mietzahlung.betrag_ist.is_(None))
            | (Mietzahlung.betrag_soll > Mietzahlung.betrag_ist)
        )

    query = query.order_by(
        Mietzahlung.zahlungsdatum.desc().nullslast(),
        Mietzahlung.created_at.desc(),
    )
    result = await db.execute(query)
    return list(result.scalars().unique().all())


async def list_mietzahlungen_for_user(
    db: AsyncSession,
    user: User,
) -> list[Mietzahlung]:
    """Listet Zahlungen für den eingeloggten Mieter."""
    mieter = await _resolve_mieter_for_user(db, user)
    if mieter is None:
        return []

    result = await db.execute(
        select(Mietzahlung).options(
            joinedload(Mietzahlung.mieter),
            joinedload(Mietzahlung.vertrag).joinedload(Mietvertrag.einheit).joinedload(Einheit.objekt),
        ).where(
            Mietzahlung.mieter_id == mieter.id,
            Mietzahlung.deleted_at.is_(None),
        ).order_by(
            Mietzahlung.zahlungsdatum.desc().nullslast(),
            Mietzahlung.created_at.desc(),
        )
    )
    return list(result.unique().scalars().all())


async def get_mietzahlung(
    db: AsyncSession,
    vermieter_id: int,
    zahlung_id: int,
) -> Mietzahlung | None:
    """Liefert eine einzelne Mietzahlung, falls sie dem Vermieter gehört."""
    result = await db.execute(
        select(Mietzahlung).options(
            joinedload(Mietzahlung.mieter),
            joinedload(Mietzahlung.vertrag).joinedload(Mietvertrag.einheit).joinedload(Einheit.objekt),
        ).where(
            Mietzahlung.id == zahlung_id,
            Mietzahlung.vermieter_id == vermieter_id,
            Mietzahlung.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def get_mietzahlung_for_user(
    db: AsyncSession,
    user: User,
    zahlung_id: int,
) -> Mietzahlung | None:
    """Gibt eine Mietzahlung eines Mieters zurück."""
    mieter = await _resolve_mieter_for_user(db, user)
    if mieter is None:
        return None

    result = await db.execute(
        select(Mietzahlung).options(
            joinedload(Mietzahlung.mieter),
            joinedload(Mietzahlung.vertrag).joinedload(Mietvertrag.einheit).joinedload(Einheit.objekt),
        ).where(
            Mietzahlung.id == zahlung_id,
            Mietzahlung.mieter_id == mieter.id,
            Mietzahlung.deleted_at.is_(None),
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

    if "mahnstufe" in update_fields and update_fields["mahnstufe"] is not None:
        if update_fields["mahnstufe"] < zahlung.mahnstufe:
            raise ValueError("Mahnstufe kann nicht zurueckgesetzt werden")

    for field, value in update_fields.items():
        setattr(zahlung, field, value)

    zahlung.updated_at = datetime.now(UTC)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="mietzahlung_update",
        entity="mietzahlungen",
        entity_id=zahlung.id,
        details={"updated_fields": list(update_fields.keys())},
        ip=ip,
        risk_level="mittel",
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
    """Soft-Delete einer Mietzahlung."""
    zahlung.deleted_at = datetime.now(UTC)
    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="mietzahlung_delete",
        entity="mietzahlungen",
        entity_id=zahlung.id,
        details={"vertrag_id": zahlung.vertrag_id, "betrag_soll": str(zahlung.betrag_soll)},
        ip=ip,
        risk_level="mittel",
    )
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
    zahlung.zahlungsdatum = zahlungsdatum.date() if isinstance(zahlungsdatum, datetime) else zahlungsdatum
    zahlung.updated_at = datetime.now(UTC)

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
    if zahlung.mahnstufe >= 3:
        raise ValueError("Maximale Mahnstufe erreicht")

    ist = zahlung.betrag_ist or Decimal("0.00")
    if Decimal(zahlung.betrag_soll) - ist <= 0:
        raise ValueError("Zahlung ist bereits vollstaendig beglichen")

    zahlung.mahnstufe = (zahlung.mahnstufe or 0) + 1
    zahlung.updated_at = datetime.now(UTC)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="mietzahlung_mahnstufe",
        entity="mietzahlungen",
        entity_id=zahlung.id,
        details={"mahnstufe": zahlung.mahnstufe},
        ip=ip,
        risk_level="hoch",
    )
    await db.flush()
    await db.refresh(zahlung)
    return zahlung


async def generate_mietzahlungen(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    monat: date,
    ip: str | None = None,
) -> list[Mietzahlung]:
    """Generiert Mietzahlungs-Posten für alle aktiven Verträge eines Monats."""
    result = await db.execute(
        select(Mietvertrag).where(
            Mietvertrag.vermieter_id == vermieter_id,
            Mietvertrag.status == "aktiv",
            Mietvertrag.deleted_at.is_(None),
            Mietvertrag.mietbeginn <= monat,
            (Mietvertrag.mietende.is_(None)) | (Mietvertrag.mietende >= monat),
        )
    )
    vertraege = list(result.scalars().all())
    angelegt: list[Mietzahlung] = []

    for vertrag in vertraege:
        existing = await db.execute(
            select(Mietzahlung).where(
                Mietzahlung.vertrag_id == vertrag.id,
                Mietzahlung.zahlungsdatum == monat,
                Mietzahlung.deleted_at.is_(None),
            )
        )
        if existing.scalar_one_or_none() is not None:
            continue

        gesamtsoll = Decimal(vertrag.miete_cold) + Decimal(vertrag.nebenkosten_voraus)
        zahlung = Mietzahlung(
            vermieter_id=vermieter_id,
            mieter_id=vertrag.mieter_id,
            vertrag_id=vertrag.id,
            betrag_soll=gesamtsoll,
            zahlungsdatum=monat,
        )
        db.add(zahlung)
        angelegt.append(zahlung)

    if angelegt:
        await db.flush()
        for z in angelegt:
            await db.refresh(z)
        await audit_log(
            db,
            user_id=user_id,
            vermieter_id=vermieter_id,
            action="mietzahlungen_generate",
            entity="mietzahlungen",
            entity_id=None,
            details={"monat": str(monat), "count": len(angelegt)},
            ip=ip,
            risk_level="niedrig",
        )
    return angelegt
