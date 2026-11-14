"""Abrechnungen-Service — CRUD, Positionsberechnung und Finalisierung."""
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.abrechnung_positionen import AbrechnungPosition
from app.models.abrechnungen import Abrechnung
from app.models.einheit import Einheit
from app.models.kosten import Kosten
from app.models.objekt import Objekt
from app.schemas.abrechnung import AbrechnungCreate, AbrechnungUpdate
from app.services.audit_log import audit_log


async def create_abrechnung(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    data: AbrechnungCreate,
    ip: str | None = None,
) -> Abrechnung:
    """Legt eine neue Nebenkostenabrechnung an."""
    objekt_id = data.objekt_id
    if objekt_id is None:
        einheit = await db.get(Einheit, data.einheit_id)
        if einheit:
            objekt_id = einheit.objekt_id

    abrechnung = Abrechnung(
        vermieter_id=vermieter_id,
        objekt_id=objekt_id,
        **data.model_dump(exclude={"objekt_id"}),
    )
    db.add(abrechnung)
    await db.flush()
    await db.refresh(abrechnung)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="abrechnung_create",
        entity="abrechnungen",
        entity_id=abrechnung.id,
        details={
            "jahr": abrechnung.jahr,
            "einheit_id": abrechnung.einheit_id,
            "zeitraum": f"{abrechnung.zeitraum_von} bis {abrechnung.zeitraum_bis}",
        },
        ip=ip,
        risk_level="niedrig",
    )
    return abrechnung


async def list_abrechnungen(
    db: AsyncSession,
    vermieter_id: int,
    einheit_id: int | None = None,
) -> list[Abrechnung]:
    """Liste aller nicht gelöschten Abrechnungen eines Vermieters."""
    query = select(Abrechnung).where(
        Abrechnung.vermieter_id == vermieter_id,
        Abrechnung.deleted_at.is_(None),
    )
    if einheit_id is not None:
        query = query.where(Abrechnung.einheit_id == einheit_id)
    query = query.order_by(Abrechnung.jahr.desc(), Abrechnung.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_abrechnung(
    db: AsyncSession,
    vermieter_id: int,
    abrechnung_id: int,
) -> Abrechnung | None:
    """Liefert eine einzelne Abrechnung, falls sie dem Vermieter gehört."""
    result = await db.execute(
        select(Abrechnung).where(
            Abrechnung.id == abrechnung_id,
            Abrechnung.vermieter_id == vermieter_id,
            Abrechnung.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def update_abrechnung(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    abrechnung: Abrechnung,
    data: AbrechnungUpdate,
    ip: str | None = None,
) -> Abrechnung:
    """Aktualisiert eine Abrechnung mit den übergebenen Feldern."""
    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(abrechnung, field, value)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="abrechnung_update",
        entity="abrechnungen",
        entity_id=abrechnung.id,
        details={"updated_fields": list(update_fields.keys())},
        ip=ip,
        risk_level="niedrig",
    )
    await db.flush()
    await db.refresh(abrechnung)
    return abrechnung


async def delete_abrechnung(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    abrechnung: Abrechnung,
    ip: str | None = None,
) -> None:
    """Markiert eine Abrechnung als gelöscht (Soft-Delete)."""
    abrechnung.deleted_at = datetime.now(UTC)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="abrechnung_delete",
        entity="abrechnungen",
        entity_id=abrechnung.id,
        details={"jahr": abrechnung.jahr, "einheit_id": abrechnung.einheit_id},
        ip=ip,
        risk_level="mittel",
    )
    await db.flush()


async def calculate_positions(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    abrechnung: Abrechnung,
    ip: str | None = None,
) -> Abrechnung:
    """Berechnet die Abrechnungspositionen für eine Abrechnung.

    Ermittelt alle umlagefähigen Kosten des Objekts im Abrechnungszeitraum,
    die noch keiner Abrechnung zugeordnet sind oder explizit dieser Abrechnung
    zugeordnet wurden, und verteilt sie nach dem in der Kategorie hinterlegten
    Verteilungsschlüssel (Standard: Quadratmeter).
    """
    einheit = await db.get(Einheit, abrechnung.einheit_id)
    if einheit is None:
        raise ValueError("Abrechnungseinheit nicht gefunden")

    objekt_id = abrechnung.objekt_id or einheit.objekt_id
    if objekt_id is None:
        raise ValueError("Abrechnung benötigt eine Einheit mit Objekt-Zuordnung")

    objekt = await db.get(Objekt, objekt_id)
    if objekt is None:
        raise ValueError("Objekt der Abrechnung nicht gefunden")

    # Gesamt-Quadratmeter des Objekts ermitteln (nur aktive Einheiten).
    einheiten_result = await db.execute(
        select(Einheit).where(
            Einheit.objekt_id == objekt_id,
            Einheit.deleted_at.is_(None),
        )
    )
    objekt_einheiten = list(einheiten_result.scalars().all())
    total_qm = sum(float(e.size_qm) for e in objekt_einheiten)
    einheit_qm = float(einheit.size_qm)

    if total_qm == 0:
        raise ValueError("Objekt hat keine gültige Gesamt-Quadratmeter-Zahl")

    # Kosten laden: umlagefähig, im Zeitraum, Objekt-Zuordnung, frei oder dieser Abrechnung.
    kosten_result = await db.execute(
        select(Kosten)
        .where(
            Kosten.vermieter_id == vermieter_id,
            Kosten.objekt_id == objekt_id,
            Kosten.umlagefaehig.is_(True),
            Kosten.datum >= abrechnung.zeitraum_von,
            Kosten.datum <= abrechnung.zeitraum_bis,
            Kosten.deleted_at.is_(None),
        )
        .where(
            (Kosten.abrechnung_id.is_(None)) | (Kosten.abrechnung_id == abrechnung.id)
        )
    )
    kosten_list = list(kosten_result.scalars().all())

    # Bestehende Positionen dieser Abrechnung als gelöscht markieren.
    pos_result = await db.execute(
        select(AbrechnungPosition).where(
            AbrechnungPosition.abrechnung_id == abrechnung.id,
            AbrechnungPosition.deleted_at.is_(None),
        )
    )
    for pos in pos_result.scalars().all():
        pos.deleted_at = datetime.now(UTC)

    for kosten in kosten_list:
        schluessel = "qm"
        if kosten.kategorie and kosten.kategorie.verteilungsschluessel:
            schluessel = kosten.kategorie.verteilungsschluessel

        betrag_total = Decimal(str(kosten.betrag))
        umlageanteil = _berechne_umlageanteil(
            betrag_total,
            schluessel,
            einheit_qm,
            total_qm,
        )

        position = AbrechnungPosition(
            vermieter_id=vermieter_id,
            abrechnung_id=abrechnung.id,
            kategorie_id=kosten.kategorie_id,
            kosten_id=kosten.id,
            betrag_total=betrag_total,
            umlageanteil=umlageanteil,
            verteilungsschluessel=schluessel,
            datev_betrag=umlageanteil,
        )
        db.add(position)

        # Kosten explizit dieser Abrechnung zuordnen, falls noch nicht geschehen.
        if kosten.abrechnung_id is None:
            kosten.abrechnung_id = abrechnung.id

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="abrechnung_calculate",
        entity="abrechnungen",
        entity_id=abrechnung.id,
        details={"kosten_count": len(kosten_list), "objekt_qm": total_qm},
        ip=ip,
        risk_level="niedrig",
    )
    await db.flush()
    await db.refresh(abrechnung)
    return abrechnung


def _berechne_umlageanteil(
    betrag_total: Decimal,
    schluessel: str,
    einheit_qm: float,
    total_qm: float,
) -> Decimal:
    """Berechnet den Umlageanteil einer Einheit für eine Kostenposition.

    In Phase 8 wird 'qm' vollständig unterstützt. 'personen' und 'verbrauch'
    erfordern zusätzliche Stammdaten und werden aktuell ebenfalls nach qm
    verteilt, damit die Abrechnung nicht blockiert (mit Hinweis im Verteiler).
    """
    if total_qm == 0:
        return Decimal("0.00")

    anteil = Decimal(str(einheit_qm / total_qm))
    if schluessel == "qm":
        return (betrag_total * anteil).quantize(Decimal("0.01"))

    # Für personen/verbrauch fehlen uns noch Verbrauchsdaten; in Phase 8
    # erfolgt eine gleichmäßige Flächenverteilung als Platzhalter.
    return (betrag_total * anteil).quantize(Decimal("0.01"))


async def finalize_abrechnung(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    abrechnung: Abrechnung,
    ip: str | None = None,
) -> Abrechnung:
    """Finalisiert die Abrechnung: status 'versendet', Kosten als abgerechnet markieren."""
    heute = datetime.now(UTC).date()
    abrechnung.status = "versendet"

    # Zugehörige Kosten als abgerechnet markieren.
    kosten_result = await db.execute(
        select(Kosten).where(
            Kosten.vermieter_id == vermieter_id,
            Kosten.abrechnung_id == abrechnung.id,
            Kosten.deleted_at.is_(None),
        )
    )
    for kosten in kosten_result.scalars().all():
        kosten.abgerechnet_am = heute

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="abrechnung_finalize",
        entity="abrechnungen",
        entity_id=abrechnung.id,
        details={"status": "versendet", "abgerechnet_am": heute.isoformat()},
        ip=ip,
        risk_level="mittel",
    )
    await db.flush()
    await db.refresh(abrechnung)
    return abrechnung
