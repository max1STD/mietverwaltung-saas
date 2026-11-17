"""Service fuer Kostenkategorien — CRUD und Default-Katalog."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.kostenkategorien import Kostenkategorie
from app.schemas.kosten import KostenkategorieCreate, KostenkategorieUpdate
from app.services.audit_log import audit_log


# Vorbelegte Betriebskosten-Kategorien nach BetrKV (§2) fuer neue Vermieter.
DEFAULT_KATEGORIEN = [
    {"name": "Grundsteuer", "betrkv_key": "GrSt", "umlagefaehig": True, "verteilungsschluessel": "qm"},
    {"name": "Versicherungen", "betrkv_key": "Vers", "umlagefaehig": True, "verteilungsschluessel": "qm"},
    {"name": "Wasserversorgung", "betrkv_key": "Wasser", "umlagefaehig": True, "verteilungsschluessel": "verbrauch"},
    {"name": "Entwaesserung", "betrkv_key": "Entw", "umlagefaehig": True, "verteilungsschluessel": "verbrauch"},
    {"name": "Heizung", "betrkv_key": "Heiz", "umlagefaehig": True, "verteilungsschluessel": "verbrauch"},
    {"name": "Warmwasser", "betrkv_key": "WW", "umlagefaehig": True, "verteilungsschluessel": "verbrauch"},
    {"name": "Strom allgemein", "betrkv_key": "Strom", "umlagefaehig": True, "verteilungsschluessel": "qm"},
    {"name": "Aufzug", "betrkv_key": "Aufz", "umlagefaehig": True, "verteilungsschluessel": "qm"},
    {"name": "Gartenpflege", "betrkv_key": "Gart", "umlagefaehig": True, "verteilungsschluessel": "qm"},
    {"name": "Winterdienst", "betrkv_key": "Winter", "umlagefaehig": True, "verteilungsschluessel": "qm"},
    {"name": "Reinigung", "betrkv_key": "Rein", "umlagefaehig": True, "verteilungsschluessel": "qm"},
    {"name": "Muellbeseitigung", "betrkv_key": "Muell", "umlagefaehig": True, "verteilungsschluessel": "qm"},
    {"name": "Schornsteinfeger", "betrkv_key": "Schorn", "umlagefaehig": True, "verteilungsschluessel": "qm"},
]


async def ensure_default_kategorien(db: AsyncSession, vermieter_id: int) -> None:
    """Legt fuer einen neuen Vermieter die Default-Kostenkategorien an, falls noch keine existieren."""
    result = await db.execute(
        select(Kostenkategorie).where(
            Kostenkategorie.vermieter_id == vermieter_id,
            Kostenkategorie.deleted_at.is_(None),
        )
    )
    if result.scalars().first():
        return

    for item in DEFAULT_KATEGORIEN:
        kategorie_data = {
            "vermieter_id": vermieter_id,
            "is_default": True,
            "name": item["name"],
            "umlagefaehig": item.get("umlagefaehig", True),
            "verteilungsschluessel": item["verteilungsschluessel"],
        }
        db.add(Kostenkategorie(**kategorie_data))
    await db.flush()


async def create_kostenkategorie(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    data: KostenkategorieCreate,
    ip: str | None = None,
) -> Kostenkategorie:
    """Erstellt eine neue benutzerdefinierte Kostenkategorie."""
    kategorie = Kostenkategorie(
        vermieter_id=vermieter_id,
        is_default=False,
        **data.model_dump(),
    )
    db.add(kategorie)
    await db.flush()
    await db.refresh(kategorie)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="kostenkategorie_create",
        entity="kostenkategorien",
        entity_id=kategorie.id,
        details={"name": kategorie.name},
        ip=ip,
        risk_level="niedrig",
    )
    return kategorie


async def list_kostenkategorien(
    db: AsyncSession,
    vermieter_id: int,
) -> list[Kostenkategorie]:
    """Listet alle aktiven Kostenkategorien eines Vermieters (Default + eigene)."""
    result = await db.execute(
        select(Kostenkategorie).where(
            Kostenkategorie.vermieter_id == vermieter_id,
            Kostenkategorie.deleted_at.is_(None),
        ).order_by(Kostenkategorie.name)
    )
    return list(result.scalars().all())


async def get_kostenkategorie(
    db: AsyncSession,
    vermieter_id: int,
    kategorie_id: int,
) -> Kostenkategorie | None:
    """Gibt eine einzelne Kostenkategorie zurueck."""
    result = await db.execute(
        select(Kostenkategorie).where(
            Kostenkategorie.id == kategorie_id,
            Kostenkategorie.vermieter_id == vermieter_id,
            Kostenkategorie.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def update_kostenkategorie(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    kategorie: Kostenkategorie,
    data: KostenkategorieUpdate,
    ip: str | None = None,
) -> Kostenkategorie:
    """Aktualisiert eine Kostenkategorie (Default-Kategorien duerfen nicht umbenannt werden)."""
    update_fields = data.model_dump(exclude_unset=True)
    if kategorie.is_default and "name" in update_fields:
        del update_fields["name"]

    for field, value in update_fields.items():
        setattr(kategorie, field, value)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="kostenkategorie_update",
        entity="kostenkategorien",
        entity_id=kategorie.id,
        details={"updated_fields": list(update_fields.keys())},
        ip=ip,
        risk_level="niedrig",
    )
    await db.flush()
    await db.refresh(kategorie)
    return kategorie


async def delete_kostenkategorie(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    kategorie: Kostenkategorie,
    ip: str | None = None,
) -> None:
    """Soft-Delete einer benutzerdefinierten Kategorie. Default-Kategorien werden nicht geloescht."""
    from datetime import UTC, datetime

    if kategorie.is_default:
        return

    kategorie.deleted_at = datetime.now(UTC)
    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="kostenkategorie_delete",
        entity="kostenkategorien",
        entity_id=kategorie.id,
        details={"name": kategorie.name},
        ip=ip,
        risk_level="niedrig",
    )
    await db.flush()
