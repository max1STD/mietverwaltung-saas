"""Mieter-Service — CRUD-Logik für Mieter-Stammdaten."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.einheit import Einheit
from app.models.mieter import Mieter
from app.schemas.mieter import MieterCreate, MieterUpdate
from app.services.audit_log import audit_log
from app.services.crypto import encrypt_value


def _split_name(name: str | None) -> tuple[str, str]:
    """Teilt einen vollen Namen in Vor- und Nachname auf."""
    if not name:
        return ("", "")
    name = name.strip()
    parts = name.rsplit(" ", 1)
    return (parts[0], parts[1] if len(parts) > 1 else "")


async def create_mieter(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    data: MieterCreate,
    ip: str | None = None,
) -> Mieter:
    """Legt einen neuen Mieter für einen Vermieter an."""
    payload = data.model_dump()

    first_name = payload.get("first_name", "")
    last_name = payload.get("last_name", "")
    birth_date = payload.get("geburtsdatum")
    phone = payload.get("telefon")
    notes = payload.get("notizen")
    adressen = payload.get("adressen", [])
    buergschaften = payload.get("buergschaften", [])

    mieter = Mieter(
        vermieter_id=vermieter_id,
        first_name=first_name,
        last_name=last_name,
        email=payload.get("email"),
        phone=phone,
        notes=notes,
        birth_date_enc=encrypt_value(birth_date.isoformat() if birth_date else None),
        status=payload.get("status", "aktiv"),
        since=payload.get("since"),
    )
    db.add(mieter)
    await db.flush()

    # Adressen anlegen
    from app.models.adresse import Adresse

    for i, a in enumerate(adressen):
        adresse = Adresse(
            mieter_id=mieter.id,
            typ=a["typ"],
            strasse=a["strasse"],
            hausnummer=a.get("hausnummer"),
            plz=a["plz"],
            ort=a["ort"],
            land=a.get("land", "DE"),
            is_primary=a.get("is_primary", i == 0),
        )
        db.add(adresse)

    # Bürgschaften anlegen
    from app.models.buergschaft import Buergschaft

    for b in buergschaften:
        buerger_adresse = None
        if b.get("buerge_adresse"):
            ba = b["buerge_adresse"]
            buerger_adresse = Adresse(
                mieter_id=mieter.id,
                typ="guarantor",
                strasse=ba["strasse"],
                hausnummer=ba.get("hausnummer"),
                plz=ba["plz"],
                ort=ba["ort"],
                land=ba.get("land", "DE"),
                is_primary=False,
            )
            db.add(buerger_adresse)
            await db.flush()

        buergschaft = Buergschaft(
            mieter_id=mieter.id,
            vermieter_id=vermieter_id,
            buerge_first_name=b["buerge_first_name"],
            buerge_last_name=b["buerge_last_name"],
            buerge_geburtsdatum=b.get("buerge_geburtsdatum"),
            buerge_adresse_id=buerger_adresse.id if buerger_adresse else None,
            buerge_phone=b.get("buerge_phone"),
            buerge_email=b.get("buerge_email"),
            hoechstbetrag=b.get("hoechstbetrag"),
            gueltig_bis=b.get("gueltig_bis"),
            status=b.get("status", "aktiv"),
            notizen=b.get("notizen"),
        )
        db.add(buergschaft)

    await db.flush()
    await db.refresh(mieter)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="mieter_create",
        entity="mieter",
        entity_id=mieter.id,
        details={"name": mieter.full_name, "adressen": len(adressen), "buergschaften": len(buergschaften)},
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

    # Frontend-kompatible Namen auf interne Felder mappen
    if "geburtsdatum" in update_fields:
        birth_date = update_fields.pop("geburtsdatum")
        mieter.birth_date_enc = encrypt_value(
            birth_date.isoformat() if birth_date else None
        )

    if "first_name" in update_fields:
        mieter.first_name = update_fields.pop("first_name")
    if "last_name" in update_fields:
        mieter.last_name = update_fields.pop("last_name")

    field_map = {
        "telefon": "phone",
        "notizen": "notes",
    }
    for frontend_field, db_field in field_map.items():
        if frontend_field in update_fields:
            setattr(mieter, db_field, update_fields[frontend_field])

    # email / status / since sind identisch benannt
    for field in ("email", "status", "since"):
        if field in update_fields:
            setattr(mieter, field, update_fields[field])

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
