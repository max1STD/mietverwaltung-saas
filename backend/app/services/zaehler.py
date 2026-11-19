"""Service für Zähler und Ablesungen."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Sequence

from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.einheit import Einheit
from app.models.mieter import Mieter
from app.models.mietvertraege import Mietvertrag
from app.models.objekt import Objekt
from app.models.user import User
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


# Typische Maximalverbräuche pro Tag für Plausibilitätsprüfungen (Einheiten je Zähler-Typ).
# Werte sind konservativ gewählt für Wohngebäude; dienen als Warn-Schwelle.
_MAX_VERBRAUCH_PRO_TAG: dict[str, Decimal] = {
    "strom": Decimal("200"),      # kWh/Tag (großer Haushalt + Wärmepumpe)
    "gas": Decimal("500"),        # kWh/Tag (altes Haus, kalter Winter)
    "wasser": Decimal("5"),         # m³/Tag (extrem hoch, aber möglich bei Leck)
    "waerme": Decimal("500"),       # kWh/Tag
    "kaltwasser": Decimal("5"),     # m³/Tag
    "sonstiges": Decimal("1_000_000"),  # unbekannt, keine sinnvolle Prüfung
}


class AblesePlausibilitaetError(ValueError):
    """Harte Plausibilitätsverletzung, die nur per Zählerwechsel überschrieben werden kann."""

    pass


def zaehler_response_data(zaehler: Zaehler) -> dict[str, Any]:
    """Erzeugt ein serialisierbares Dict aus einem Zaehler inkl. Einheit/Objekt-Namen.

    Greift nur auf bereits eager-geladene Relationships zu, um Lazy-Loading-Fehler
    im Async-Kontext zu vermeiden.
    """
    einheit_name: str | None = None
    objekt_name: str | None = None
    zaehler_state = inspect(zaehler)
    if zaehler.einheit_id and "einheit_obj" not in zaehler_state.unloaded:
        einheit_obj = zaehler.einheit_obj
        einheit_name = einheit_obj.name if einheit_obj else None
        if einheit_obj and "objekt" not in inspect(einheit_obj).unloaded:
            objekt_name = einheit_obj.objekt.name if einheit_obj.objekt else None

    return {
        "id": zaehler.id,
        "public_id": zaehler.public_id,
        "vermieter_id": zaehler.vermieter_id,
        "einheit_id": zaehler.einheit_id,
        "bezeichnung": zaehler.bezeichnung,
        "zaehlernummer": zaehler.zaehlernummer,
        "typ": zaehler.typ,
        "einheit": zaehler.einheit,
        "ist_hauptzaehler": zaehler.ist_hauptzaehler,
        "ablesedatum": zaehler.ablesedatum,
        "created_at": zaehler.created_at,
        "updated_at": zaehler.updated_at,
        "deleted_at": zaehler.deleted_at,
        "einheit_name": einheit_name,
        "objekt_name": objekt_name,
    }


def ablesung_response_data(ablesung: Zaehlerablesung) -> dict[str, Any]:
    """Erzeugt ein serialisierbares Dict aus einer Ablesung inkl. Warnungen."""
    return {
        "id": ablesung.id,
        "vermieter_id": ablesung.vermieter_id,
        "zaehler_id": ablesung.zaehler_id,
        "ablesedatum": ablesung.ablesedatum,
        "zaehlerstand": ablesung.zaehlerstand,
        "verbrauch": ablesung.verbrauch,
        "ableser": ablesung.ableser,
        "notizen": ablesung.notizen,
        "ist_schaetzung": ablesung.ist_schaetzung,
        "zaehlerwechsel": ablesung.zaehlerwechsel,
        "warnings": getattr(ablesung, "warnings", []),
        "created_at": ablesung.created_at,
        "updated_at": ablesung.updated_at,
        "deleted_at": ablesung.deleted_at,
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


async def _can_access_zaehler(
    db: AsyncSession,
    user_id: int,
    user_role: str,
    zaehler_id: int,
) -> Zaehler | None:
    """Gibt den Zähler zurück, wenn der User berechtigt ist (Vermieter oder aktueller Mieter der Einheit)."""
    result = await db.execute(
        select(Zaehler)
        .options(
            selectinload(Zaehler.einheit_obj).selectinload(Einheit.objekt),
        )
        .where(
            Zaehler.id == zaehler_id,
            Zaehler.deleted_at.is_(None),
        )
    )
    zaehler = result.scalar_one_or_none()
    if zaehler is None:
        return None
    if user_role == "vermieter":
        return zaehler if zaehler.vermieter_id == user_id else None
    # Mieter: Mieter-Datensatz per E-Mail ermitteln (etabliertes Pattern aus Tickets).
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if user is None or user.email is None:
        return None
    mieter_result = await db.execute(
        select(Mieter).where(
            Mieter.email == user.email,
            Mieter.vermieter_id == zaehler.vermieter_id,
            Mieter.deleted_at.is_(None),
        )
    )
    mieter = mieter_result.scalar_one_or_none()
    if mieter is None:
        return None
    mv_result = await db.execute(
        select(Mietvertrag).where(
            Mietvertrag.mieter_id == mieter.id,
            Mietvertrag.einheit_id == zaehler.einheit_id,
            Mietvertrag.status == "aktiv",
            Mietvertrag.deleted_at.is_(None),
        )
    )
    return zaehler if mv_result.scalar_one_or_none() is not None else None


async def _berechne_verbrauch(
    db: AsyncSession,
    zaehler_id: int,
    aktueller_stand: Decimal,
    aktuelles_datum: date,
    zaehlerwechsel: bool = False,
    typ: str | None = None,
    ablesung_id: int | None = None,
) -> tuple[Decimal | None, list[str]]:
    """Berechnet den Verbrauch gegenüber der vorherigen Ablesung und prüft spätere.

    Returns:
        Tuple aus (verbrauch, warnings). verbrauch ist None, wenn keine
        vorherige Ablesung existiert oder ein Zählerwechsel vorliegt.
        warnings enthält Hinweise auf Auffälligkeiten, aber keine harten Fehler.
    """
    warnings: list[str] = []

    # Harte Regel: eine Ablesung in der Vergangenheit darf nicht größer sein
    # als eine bereits existierende spätere Ablesung (außer Zählerwechsel).
    spaetere_query = select(Zaehlerablesung).where(
        Zaehlerablesung.zaehler_id == zaehler_id,
        Zaehlerablesung.deleted_at.is_(None),
        Zaehlerablesung.ablesedatum > aktuelles_datum,
    )
    if ablesung_id:
        spaetere_query = spaetere_query.where(Zaehlerablesung.id != ablesung_id)
    spaetere_query = spaetere_query.order_by(Zaehlerablesung.ablesedatum.asc()).limit(1)
    spaetere_result = await db.execute(spaetere_query)
    spaetere = spaetere_result.scalar_one_or_none()
    if spaetere is not None and aktueller_stand > spaetere.zaehlerstand:
        if not zaehlerwechsel:
            raise AblesePlausibilitaetError(
                "Der eingegebene Zählerstand ist größer als eine spätere Ablesung. "
                "Bitte prüfen Sie das Datum und den Stand, oder hinterlegen Sie einen Zählerwechsel."
            )
        return None, warnings

    result = await db.execute(
        select(Zaehlerablesung)
        .where(
            Zaehlerablesung.zaehler_id == zaehler_id,
            Zaehlerablesung.deleted_at.is_(None),
            Zaehlerablesung.ablesedatum < aktuelles_datum,
        )
        .where(Zaehlerablesung.id != ablesung_id if ablesung_id else True)
        .order_by(Zaehlerablesung.ablesedatum.desc(), Zaehlerablesung.created_at.desc())
        .limit(1)
    )
    vorherige = result.scalar_one_or_none()
    if vorherige is None:
        return None, warnings

    if aktueller_stand < vorherige.zaehlerstand:
        if not zaehlerwechsel:
            raise AblesePlausibilitaetError(
                "Der eingegebene Zählerstand ist kleiner als die vorherige Ablesung. "
                "Bitte hinterlegen Sie einen Zählerwechsel, falls ein neuer Zähler eingebaut wurde."
            )
        # Bei Zählerwechsel kein Verbrauch aus dieser Differenz berechnen.
        return None, warnings

    verbrauch: Decimal = aktueller_stand - vorherige.zaehlerstand
    tage = (aktuelles_datum - vorherige.ablesedatum).days or 1
    verbrauch_pro_tag = verbrauch / Decimal(tage)

    # Zählerüberlauf-Heuristik: abrupte sehr kleine Werte nach großen Ständen.
    if vorherige.zaehlerstand > Decimal("900000") and aktueller_stand < Decimal("10000"):
        warnings.append(
            "Möglicher Zählerüberlauf erkannt: Der vorherige Stand war sehr hoch und der neue Stand "
            "fällt stark ab. Bitte prüfen Sie die Ablesung."
        )

    # Auffällig hoher Verbrauch pro Tag (Zahlendreher / Leck / Heizungsausfall etc.)
    max_pro_tag = _MAX_VERBRAUCH_PRO_TAG.get(typ or "sonstiges", _MAX_VERBRAUCH_PRO_TAG["sonstiges"])
    if verbrauch_pro_tag > max_pro_tag:
        warnings.append(
            f"Auffällig hoher Verbrauch ({verbrauch_pro_tag.quantize(Decimal('0.001'))} Einheiten/Tag) "
            "im Vergleich zum Erwartungswert. Bitte prüfen Sie die Ablesung auf Zahlendreher."
        )

    # Nullverbrauch über längeren Zeitraum
    if verbrauch == Decimal("0") and tage >= 30:
        warnings.append(
            "Kein Verbrauch über einen längeren Zeitraum erfasst. "
            "Bitte prüfen Sie, ob der Zähler in Betrieb ist."
        )

    return verbrauch, warnings


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
    stmt = (
        select(Zaehler)
        .options(
            selectinload(Zaehler.einheit_obj).selectinload(Einheit.objekt),
        )
        .where(
            Zaehler.vermieter_id == vermieter_id,
            Zaehler.deleted_at.is_(None),
        )
    )
    if einheit_id is not None:
        stmt = stmt.where(Zaehler.einheit_id == einheit_id)
    stmt = stmt.order_by(Zaehler.bezeichnung)
    result = await db.execute(stmt)
    return result.scalars().all()


async def list_zaehler_for_user(
    db: AsyncSession,
    user_id: int,
    user_role: str,
    einheit_id: int | None = None,
) -> Sequence[Zaehler]:
    """Listet Zähler fuer Vermieter oder berechtigte Mieter."""
    if user_role == "vermieter":
        return await list_zaehler(db, vermieter_id=user_id, einheit_id=einheit_id)

    # Mieter: nur Zaehler der eigenen aktuellen Wohneinheit(en).
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if user is None or user.email is None:
        return []
    mieter_result = await db.execute(
        select(Mieter).where(
            Mieter.email == user.email,
            Mieter.vermieter_id == user.vermieter_id,
            Mieter.deleted_at.is_(None),
        )
    )
    mieter = mieter_result.scalar_one_or_none()
    if mieter is None:
        return []

    einheit_ids_result = await db.execute(
        select(Mietvertrag.einheit_id).where(
            Mietvertrag.mieter_id == mieter.id,
            Mietvertrag.status == "aktiv",
            Mietvertrag.deleted_at.is_(None),
        )
    )
    einheit_ids = [row[0] for row in einheit_ids_result.all()]
    if not einheit_ids:
        return []

    stmt = (
        select(Zaehler)
        .options(
            selectinload(Zaehler.einheit_obj).selectinload(Einheit.objekt),
        )
        .where(
            Zaehler.einheit_id.in_(einheit_ids),
            Zaehler.deleted_at.is_(None),
        )
    )
    if einheit_id is not None and einheit_id in einheit_ids:
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
    result = await db.execute(
        select(Zaehler)
        .options(
            selectinload(Zaehler.einheit_obj).selectinload(Einheit.objekt),
        )
        .where(
            Zaehler.id == zaehler_id,
            Zaehler.vermieter_id == vermieter_id,
            Zaehler.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def get_zaehler_for_user(
    db: AsyncSession,
    user_id: int,
    user_role: str,
    zaehler_id: int,
) -> Zaehler | None:
    """Gibt einen einzelnen Zähler für berechtigte User zurück."""
    return await _can_access_zaehler(db, user_id, user_role, zaehler_id)


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
    zaehler = await get_zaehler(db, vermieter_id, zaehler_id)
    if zaehler is None:
        raise PermissionError("Zähler nicht gefunden oder nicht berechtigt.")

    verbrauch, warnings = await _berechne_verbrauch(
        db,
        zaehler_id,
        data.zaehlerstand,
        data.ablesedatum,
        zaehlerwechsel=data.zaehlerwechsel,
        typ=zaehler.typ,
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
        zaehlerwechsel=data.zaehlerwechsel,
    )
    db.add(ablesung)
    await db.flush()
    await db.refresh(ablesung)
    ablesung.warnings = warnings

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
            "zaehlerwechsel": data.zaehlerwechsel,
        },
        ip=ip,
        risk_level="niedrig",
    )
    return ablesung


async def create_ablesung_for_user(
    db: AsyncSession,
    user_id: int,
    user_role: str,
    zaehler_id: int,
    data: ZaehlerablesungCreate,
    ip: str | None = None,
) -> Zaehlerablesung:
    """Erstellt eine neue Ablesung für Vermieter oder berechtigten Mieter."""
    zaehler = await _can_access_zaehler(db, user_id, user_role, zaehler_id)
    if zaehler is None:
        raise PermissionError("Zähler nicht gefunden oder nicht berechtigt.")

    vermieter_id = zaehler.vermieter_id
    verbrauch, warnings = await _berechne_verbrauch(
        db,
        zaehler_id,
        data.zaehlerstand,
        data.ablesedatum,
        zaehlerwechsel=data.zaehlerwechsel,
        typ=zaehler.typ,
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
        zaehlerwechsel=data.zaehlerwechsel,
    )
    db.add(ablesung)
    await db.flush()
    await db.refresh(ablesung)
    ablesung.warnings = warnings

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
            "zaehlerwechsel": data.zaehlerwechsel,
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
    result = await db.execute(
        select(Zaehlerablesung).where(
            Zaehlerablesung.id == ablesung_id,
            Zaehlerablesung.vermieter_id == vermieter_id,
            Zaehlerablesung.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


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
        # Bei Updates nur Neuberechnung; Zählerwechsel-Flag wird nicht nachträglich verändert.
        verbrauch, _ = await _berechne_verbrauch(
            db,
            ablesung.zaehler_id,
            ablesung.zaehlerstand,
            ablesung.ablesedatum,
            zaehlerwechsel=ablesung.zaehlerwechsel,
            ablesung_id=ablesung.id,
        )
        ablesung.verbrauch = verbrauch

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
