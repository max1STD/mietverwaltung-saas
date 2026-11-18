"""Service für Zähler und Ablesungen."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.einheit import Einheit
from app.models.zaehler import Zaehler, Zaehlerablesung
from app.schemas.zaehler import (
    ZaehlerCreate,
    ZaehlerUpdate,
    ZaehlerablesungCreate,
    ZaehlerablesungUpdate,
)
from app.services.audit_log import audit_log


_ZAEHLER_TYP_EINHEIT = {
    "strom": "kwh",
    "gas": "kwh_m3",
    "wasser": "m3",
    "waerme": "kwh",
    "kaltwasser": "m3",
    "sonstiges": "sonstiges",
}


async def _owns_einheit(
    db: AsyncSession,
    vermieter_id: int,
    einheit_id: int,
) -> bool:
    """Prüft, ob die Einheit dem Vermieter gehört."""
    result = await db.execute(
        select(Einheit).where(
            Einheit.id == einheit_id,
            Einheit.vermieter_id == vermieter_id,
            Einheit.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none() is not None


async def _get_zaehler(
    db: AsyncSession,
    vermieter_id: int,
    zaehler_id: int,
) -> Zaehler | None:
    """Gibt einen Zähler zurück, wenn er dem Vermieter gehört und aktiv ist."""
    result = await db.execute(
        select(Zaehler).where(
            Zaehler.id == zaehler_id,
            Zaehler.vermieter_id == vermieter_id,
            Zaehler.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def _get_ablesung(
    db: AsyncSession,
    vermieter_id: int,
    ablesung_id: int,
) -> Zaehlerablesung | None:
    """Gibt eine Ablesung zurück, wenn sie dem Vermieter gehört und aktiv ist."""
    result = await db.execute(
        select(Zaehlerablesung).where(
            Zaehlerablesung.id == ablesung_id,
            Zaehlerablesung.vermieter_id == vermieter_id,
            Zaehlerablesung.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def _berechne_verbrauch(
    db: AsyncSession,
    zaehler_id: int,
    aktueller_stand: Decimal,
    aktuelles_datum: date,
) -> Decimal | None:
    """Berechnet den Verbrauch gegenüber der vorherigen Ablesung."""
    result = await db.execute(
        select(Zaehlerablesung)
        .where(
            Zaehlerablesung.zaehler_id == zaehler_id,
            Zaehlerablesung.deleted_at.is_(None),
            Zaehlerablesung.ablesedatum < aktuelles_datum,
        )
        .order_by(Zaehlerablesung.ablesedatum.desc(), Zaehlerablesung.created_at.desc())
        .limit(1)
    )
    vorherige = result.scalar_one_or_none()
    if vorherige is None:
        return None
    return aktueller_stand - vorherige.zaehlerstand


async def create_zaehler(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    data: ZaehlerCreate,
    ip: str | None = None,
) -> Zaehler:
    """Erstellt einen neuen Zähler für eine Einheit."""
    if not await _owns_einheit(db, vermieter_id, data.einheit_id):
        raise PermissionError("Einheit nicht gefunden oder nicht berechtigt.")

    zaehler = Zaehler(
        vermieter_id=vermieter_id,
        einheit_id=data.einheit_id,
        bezeichnung=data.bezeichnung,
        zaehlernummer=data.zaehlernummer,
        typ=data.typ,
        einheit=_ZAEHLER_TYP_EINHEIT.get(data.typ, data.einheit or "sonstiges"),
        ist_hauptzaehler=data.ist_hauptzaehler,
    )
    db.add(zaehler)
    await db.flush()
    await db.refresh(zaehler)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="zaehler_create",
        entity="zaehler",
        entity_id=zaehler.id,
        details={
            "bezeichnung": zaehler.bezeichnung,
            "typ": zaehler.typ,
            "einheit_id": zaehler.einheit_id,
        },
        ip=ip,
        risk_level="niedrig",
    )
    return zaehler


async def list_zaehler(
    db: AsyncSession,
    vermieter_id: int,
    einheit_id: int | None = None,
) -> Sequence[Zaehler]:
    """Listet alle aktiven Zähler eines Vermieters, optional gefiltert nach Einheit."""
    stmt = select(Zaehler).where(
        Zaehler.vermieter_id == vermieter_id,
        Zaehler.deleted_at.is_(None),
    )
    if einheit_id is not None:
        stmt = stmt.where(Zaehler.einheit_id == einheit_id)
    stmt = stmt.order_by(Zaehler.bezeichnung)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_zaehler(
    db: AsyncSession,
    vermieter_id: int,
    zaehler_id: int,
) -> Zaehler | None:
    """Gibt einen einzelnen Zähler zurück."""
    return await _get_zaehler(db, vermieter_id, zaehler_id)


async def update_zaehler(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    zaehler: Zaehler,
    data: ZaehlerUpdate,
    ip: str | None = None,
) -> Zaehler:
    """Aktualisiert einen Zähler."""
    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(zaehler, field, value)

    await db.flush()
    await db.refresh(zaehler)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="zaehler_update",
        entity="zaehler",
        entity_id=zaehler.id,
        details={"updated_fields": list(update_fields.keys())},
        ip=ip,
        risk_level="niedrig",
    )
    return zaehler


async def delete_zaehler(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    zaehler: Zaehler,
    ip: str | None = None,
) -> None:
    """Soft-Delete eines Zählers inklusive aller Ablesungen."""
    from datetime import UTC, datetime

    zaehler.deleted_at = datetime.now(UTC)
    for ablesung in zaehler.ablesungen:
        ablesung.deleted_at = datetime.now(UTC)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="zaehler_delete",
        entity="zaehler",
        entity_id=zaehler.id,
        details={"bezeichnung": zaehler.bezeichnung},
        ip=ip,
        risk_level="niedrig",
    )
    await db.flush()


async def create_ablesung(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    zaehler_id: int,
    data: ZaehlerablesungCreate,
    ip: str | None = None,
) -> Zaehlerablesung:
    """Erstellt eine neue Ablesung und berechnet den Verbrauch."""
    zaehler = await _get_zaehler(db, vermieter_id, zaehler_id)
    if zaehler is None:
        raise PermissionError("Zähler nicht gefunden oder nicht berechtigt.")

    verbrauch = await _berechne_verbrauch(
        db,
        zaehler_id,
        data.zaehlerstand,
        data.ablesedatum,
    )

    ablesung = Zaehlerablesung(
        vermieter_id=vermieter_id,
        zaehler_id=zaehler_id,
        ablesedatum=data.ablesedatum,
        zaehlerstand=data.zaehlerstand,
        verbrauch=verbrauch,
        ableser=data.ableser,
        notizen=data.notizen,
        ist_schaetzung=data.ist_schaetzung,
    )
    db.add(ablesung)
    await db.flush()
    await db.refresh(ablesung)

    zaehler.ablesedatum = data.ablesedatum

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="zaehlerablesung_create",
        entity="zaehlerablesungen",
        entity_id=ablesung.id,
        details={
            "zaehler_id": zaehler_id,
            "zaehlerstand": str(data.zaehlerstand),
            "verbrauch": str(verbrauch) if verbrauch is not None else None,
        },
        ip=ip,
        risk_level="niedrig",
    )
    return ablesung


async def list_ablesungen(
    db: AsyncSession,
    vermieter_id: int,
    zaehler_id: int,
) -> Sequence[Zaehlerablesung]:
    """Listet alle aktiven Ablesungen eines Zählers."""
    result = await db.execute(
        select(Zaehlerablesung).where(
            Zaehlerablesung.zaehler_id == zaehler_id,
            Zaehlerablesung.vermieter_id == vermieter_id,
            Zaehlerablesung.deleted_at.is_(None),
        ).order_by(
            Zaehlerablesung.ablesedatum.desc(),
            Zaehlerablesung.created_at.desc(),
        )
    )
    return result.scalars().all()


async def get_ablesung(
    db: AsyncSession,
    vermieter_id: int,
    ablesung_id: int,
) -> Zaehlerablesung | None:
    """Gibt eine einzelne Ablesung zurück."""
    return await _get_ablesung(db, vermieter_id, ablesung_id)


async def update_ablesung(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    ablesung: Zaehlerablesung,
    data: ZaehlerablesungUpdate,
    ip: str | None = None,
) -> Zaehlerablesung:
    """Aktualisiert eine Ablesung und berechnet den Verbrauch neu."""
    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(ablesung, field, value)

    if "zaehlerstand" in update_fields or "ablesedatum" in update_fields:
        ablesung.verbrauch = await _berechne_verbrauch(
            db,
            ablesung.zaehler_id,
            ablesung.zaehlerstand,
            ablesung.ablesedatum,
        )

    await db.flush()
    await db.refresh(ablesung)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="zaehlerablesung_update",
        entity="zaehlerablesungen",
        entity_id=ablesung.id,
        details={"updated_fields": list(update_fields.keys())},
        ip=ip,
        risk_level="niedrig",
    )
    return ablesung


async def delete_ablesung(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    ablesung: Zaehlerablesung,
    ip: str | None = None,
) -> None:
    """Soft-Delete einer Ablesung."""
    from datetime import UTC, datetime

    ablesung.deleted_at = datetime.now(UTC)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="zaehlerablesung_delete",
        entity="zaehlerablesungen",
        entity_id=ablesung.id,
        details={"zaehler_id": ablesung.zaehler_id},
        ip=ip,
        risk_level="niedrig",
    )
    await db.flush()
