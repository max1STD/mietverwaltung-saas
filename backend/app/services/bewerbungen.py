"""Bewerbungen-Service — CRUD, Annahme und Ablehnung."""
from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bewerbungen import Bewerbung
from app.models.einheit import Einheit
from app.schemas.bewerbungen import BewerbungCreate, BewerbungDecisionRequest, BewerbungUpdate
from app.services.audit_log import audit_log
from app.services.mieter import create_mieter
from app.services.mietvertraege import create_mietvertrag


async def create_bewerbung(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    data: BewerbungCreate,
    ip: str | None = None,
) -> Bewerbung:
    """Legt eine neue Mieter-Bewerbung an."""
    einheit = await db.get(Einheit, data.einheit_id)
    if einheit is None or einheit.vermieter_id != vermieter_id:
        raise ValueError("Einheit nicht gefunden oder nicht berechtigt")

    payload = data.model_dump()
    bewerbung = Bewerbung(
        vermieter_id=vermieter_id,
        **payload,
    )
    db.add(bewerbung)
    await db.flush()
    await db.refresh(bewerbung)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="bewerbung_create",
        entity="bewerbungen",
        entity_id=bewerbung.id,
        details={"einheit_id": bewerbung.einheit_id, "name": bewerbung.full_name},
        ip=ip,
        risk_level="niedrig",
    )
    return bewerbung


async def list_bewerbungen(
    db: AsyncSession,
    vermieter_id: int,
    status: str | None = None,
) -> list[Bewerbung]:
    """Listet alle nicht gelöschten Bewerbungen eines Vermieters."""
    query = select(Bewerbung).where(
        Bewerbung.vermieter_id == vermieter_id,
        Bewerbung.deleted_at.is_(None),
    )
    if status is not None:
        query = query.where(Bewerbung.status == status)
    query = query.order_by(Bewerbung.applied_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_bewerbung(
    db: AsyncSession,
    vermieter_id: int,
    bewerbung_id: int,
) -> Bewerbung | None:
    """Liefert eine einzelne Bewerbung, falls sie dem Vermieter gehört."""
    result = await db.execute(
        select(Bewerbung).where(
            Bewerbung.id == bewerbung_id,
            Bewerbung.vermieter_id == vermieter_id,
            Bewerbung.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def update_bewerbung(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    bewerbung: Bewerbung,
    data: BewerbungUpdate,
    ip: str | None = None,
) -> Bewerbung:
    """Aktualisiert Stammdaten einer Bewerbung (ohne Status)."""
    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(bewerbung, field, value)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="bewerbung_update",
        entity="bewerbungen",
        entity_id=bewerbung.id,
        details={"updated_fields": list(update_fields.keys())},
        ip=ip,
        risk_level="niedrig",
    )
    await db.flush()
    await db.refresh(bewerbung)
    return bewerbung


async def delete_bewerbung(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    bewerbung: Bewerbung,
    ip: str | None = None,
) -> None:
    """Markiert eine Bewerbung als gelöscht (Soft-Delete)."""
    bewerbung.deleted_at = datetime.now(UTC)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="bewerbung_delete",
        entity="bewerbungen",
        entity_id=bewerbung.id,
        details={"name": bewerbung.full_name},
        ip=ip,
        risk_level="mittel",
    )
    await db.flush()


async def annehmen(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    bewerbung: Bewerbung,
    decision: BewerbungDecisionRequest,
    ip: str | None = None,
) -> dict[str, any]:
    """Nimmt eine Bewerbung an und erzeugt optional Mieter + Mietvertrag."""
    if bewerbung.status != "offen":
        raise ValueError("Bewerbung wurde bereits entschieden")

    bewerbung.status = decision.status or "angenommen"
    bewerbung.decided_at = datetime.now(UTC)

    result: dict[str, any] = {
        "bewerbung_id": bewerbung.id,
        "status": bewerbung.status,
        "mieter_id": None,
        "vertrag_id": None,
    }

    if decision.create_mieter_and_vertrag:
        mieter = await create_mieter(
            db,
            vermieter_id=vermieter_id,
            user_id=user_id,
            data=__bewerbung_to_mieter_data(bewerbung),
            ip=ip,
        )
        result["mieter_id"] = mieter.id

        einheit = await db.get(Einheit, bewerbung.einheit_id)
        mietbeginn = decision.mietbeginn or date.today()
        miete_cold = decision.miete_cold or (
            Decimal(einheit.kaltmiete) if einheit else Decimal("0")
        )
        nebenkosten_voraus = decision.nebenkosten_voraus or Decimal("0")
        kaution = decision.kaution

        vertrag = await create_mietvertrag(
            db,
            vermieter_id=vermieter_id,
            user_id=user_id,
            data=__vertrag_data(
                mieter_id=mieter.id,
                einheit_id=bewerbung.einheit_id,
                mietbeginn=mietbeginn,
                miete_cold=miete_cold,
                nebenkosten_voraus=nebenkosten_voraus,
                kaution=kaution,
            ),
            ip=ip,
        )
        result["vertrag_id"] = vertrag.id

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="bewerbung_annehmen",
        entity="bewerbungen",
        entity_id=bewerbung.id,
        details={
            "create_mieter_and_vertrag": decision.create_mieter_and_vertrag,
            "mieter_id": result["mieter_id"],
            "vertrag_id": result["vertrag_id"],
        },
        ip=ip,
        risk_level="mittel",
    )
    await db.flush()
    await db.refresh(bewerbung)
    return result


async def ablehnen(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    bewerbung: Bewerbung,
    ip: str | None = None,
) -> Bewerbung:
    """Lehnt eine Bewerbung ab."""
    if bewerbung.status != "offen":
        raise ValueError("Bewerbung wurde bereits entschieden")

    bewerbung.status = "abgelehnt"
    bewerbung.decided_at = datetime.now(UTC)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="bewerbung_ablehnen",
        entity="bewerbungen",
        entity_id=bewerbung.id,
        details={"name": bewerbung.full_name},
        ip=ip,
        risk_level="niedrig",
    )
    await db.flush()
    await db.refresh(bewerbung)
    return bewerbung


# ── Hilfsfunktionen ──


def __bewerbung_to_mieter_data(bewerbung: Bewerbung):
    """Wandelt Bewerbungs-Stammdaten in MieterCreate-kompatibles Dict um."""
    from app.schemas.mieter import MieterCreate

    name = f"{bewerbung.first_name or ''} {bewerbung.last_name or ''}".strip()
    return MieterCreate(
        name=name or "Unbekannt",
        email=bewerbung.email,
        telefon=bewerbung.phone,
        status="aktiv",
        since=date.today(),
        adresse=None,
        notizen=None,
    )


def __vertrag_data(
    mieter_id: int,
    einheit_id: int,
    mietbeginn: date,
    miete_cold: Decimal,
    nebenkosten_voraus: Decimal,
    kaution: Decimal | None,
):
    """Baut MietvertragCreate aus Bewerbungs-Entscheidung."""
    from app.schemas.mietvertrag import MietvertragCreate

    return MietvertragCreate(
        mieter_id=mieter_id,
        einheit_id=einheit_id,
        mietbeginn=mietbeginn,
        miete_cold=miete_cold,
        nebenkosten_voraus=nebenkosten_voraus,
        kaution=kaution,
        kaution_hinterlegt=False,
        status="aktiv",
    )
