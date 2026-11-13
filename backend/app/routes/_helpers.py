"""Response-Mapper für Objekt-, Einheit-, Mieter- und Mietvertrag-Routen."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.einheit import Einheit
from app.models.mieter import Mieter
from app.models.mietvertraege import Mietvertrag
from app.models.objekt import Objekt
from app.schemas.einheit import (
    EinheitNestedMieter,
    EinheitResponse,
)
from app.schemas.mieter import (
    MieterNestedEinheit,
    MieterResponse,
)
from app.schemas.mietvertrag import (
    MietvertragNestedEinheit,
    MietvertragNestedMieter,
    MietvertragResponse,
)
from app.schemas.objekt import ObjektNestedEinheit, ObjektResponse
from app.services.crypto import decrypt_value
from app.services.einheiten import get_aktueller_mieter


def _to_decimal(value: Decimal | float | int | str | None) -> Decimal | None:
    """Konvertiert DB-Decimal/Wert in Pydantic-Decimal."""
    if value is None:
        return None
    return Decimal(str(value))


async def map_objekt_response(db: AsyncSession, objekt: Objekt) -> ObjektResponse:
    """Mappt ein Objekt-ORM inklusive Einheiten auf das Response-Schema."""
    # Beziehungen explizit laden (async Session erlaubt kein Lazy-Loading).
    await db.refresh(objekt, attribute_names=["einheiten"])

    einheiten = [
        ObjektNestedEinheit(
            id=e.id,
            name=e.name,
            size_qm=_to_decimal(e.size_qm) or Decimal("0"),
            rooms=e.rooms,
            rent_cold=_to_decimal(e.rent_cold) or Decimal("0"),
            status=None,
        )
        for e in objekt.einheiten
        if e.deleted_at is None
    ]

    return ObjektResponse(
        id=objekt.id,
        vermieter_id=objekt.vermieter_id,
        name=objekt.name,
        address=objekt.address,
        typ=objekt.typ,
        baujahr=objekt.baujahr,
        foto_url=objekt.foto_url,
        kaufpreis=_to_decimal(objekt.kaufpreis),
        kaufdatum=objekt.kaufdatum,
        eigenkapital=_to_decimal(objekt.eigenkapital),
        darlehen_betrag=_to_decimal(objekt.darlehen_betrag),
        zinssatz=_to_decimal(objekt.zinssatz),
        tilgung=_to_decimal(objekt.tilgung),
        monatliche_rate=_to_decimal(objekt.monatliche_rate),
        created_at=objekt.created_at,
        updated_at=objekt.updated_at,
        deleted_at=objekt.deleted_at,
        einheiten=einheiten,
    )


async def map_einheit_response(db: AsyncSession, einheit: Einheit) -> EinheitResponse:
    """Mappt eine Einheit-ORM inklusive aktuellem Mieter auf das Response-Schema."""
    vertrag = await get_aktueller_mieter(db, einheit.id)
    aktueller_mieter = None
    vermietungsstatus = "frei"
    if vertrag and vertrag.mieter:
        aktueller_mieter = EinheitNestedMieter(
            id=vertrag.mieter.id,
            full_name=vertrag.mieter.full_name,
            status=vertrag.mieter.status,
        )
        vermietungsstatus = "vermietet"

    return EinheitResponse(
        id=einheit.id,
        vermieter_id=einheit.vermieter_id,
        objekt_id=einheit.objekt_id,
        name=einheit.name,
        size_qm=_to_decimal(einheit.size_qm) or Decimal("0"),
        rooms=einheit.rooms,
        rent_cold=_to_decimal(einheit.rent_cold) or Decimal("0"),
        floor=einheit.floor,
        energy_class=einheit.energy_class,
        last_renovation=einheit.last_renovation,
        available_from=einheit.available_from,
        created_at=einheit.created_at,
        updated_at=einheit.updated_at,
        deleted_at=einheit.deleted_at,
        aktueller_mieter=aktueller_mieter,
        vermietungsstatus=vermietungsstatus,
    )


async def map_mieter_response(
    db: AsyncSession,
    mieter: Mieter,
    aktuelle_einheit: Einheit | None = None,
) -> MieterResponse:
    """Mappt einen Mieter-ORM inklusive aktueller Einheit auf das Response-Schema."""
    birth_date_str = decrypt_value(mieter.birth_date_enc)
    birth_date = date.fromisoformat(birth_date_str) if birth_date_str else None

    aktuelle_einheit_resp = None
    if aktuelle_einheit:
        await db.refresh(aktuelle_einheit, attribute_names=["objekt"])
        aktuelle_einheit_resp = MieterNestedEinheit(
            id=aktuelle_einheit.id,
            name=aktuelle_einheit.name,
            objekt_name=aktuelle_einheit.objekt.name if aktuelle_einheit.objekt else "",
        )

    return MieterResponse(
        id=mieter.id,
        vermieter_id=mieter.vermieter_id,
        first_name=mieter.first_name,
        last_name=mieter.last_name,
        full_name=mieter.full_name,
        email=mieter.email,
        phone=mieter.phone,
        birth_date=birth_date,
        status=mieter.status,
        since=mieter.since,
        created_at=mieter.created_at,
        updated_at=mieter.updated_at,
        deleted_at=mieter.deleted_at,
        aktuelle_einheit=aktuelle_einheit_resp,
    )


async def map_mietvertrag_response(db: AsyncSession, vertrag: Mietvertrag) -> MietvertragResponse:
    """Mappt einen Mietvertrag-ORM inklusive Mieter- und Einheit-Info auf das Response-Schema."""
    await db.refresh(vertrag, attribute_names=["mieter", "einheit"])
    await db.refresh(vertrag.einheit, attribute_names=["objekt"])

    mieter_info = None
    if vertrag.mieter:
        mieter_info = MietvertragNestedMieter(
            id=vertrag.mieter.id,
            full_name=vertrag.mieter.full_name,
        )

    einheit_info = None
    if vertrag.einheit:
        einheit_info = MietvertragNestedEinheit(
            id=vertrag.einheit.id,
            name=vertrag.einheit.name,
            objekt_name=vertrag.einheit.objekt.name if vertrag.einheit.objekt else "",
        )

    return MietvertragResponse(
        id=vertrag.id,
        vermieter_id=vertrag.vermieter_id,
        mieter_id=vertrag.mieter_id,
        einheit_id=vertrag.einheit_id,
        mietbeginn=vertrag.mietbeginn,
        mietende=vertrag.mietende,
        miete_cold=_to_decimal(vertrag.miete_cold) or Decimal("0"),
        nebenkosten_voraus=_to_decimal(vertrag.nebenkosten_voraus) or Decimal("0"),
        kaution=_to_decimal(vertrag.kaution),
        kaution_hinterlegt=vertrag.kaution_hinterlegt,
        status=vertrag.status,
        created_at=vertrag.created_at,
        updated_at=vertrag.updated_at,
        deleted_at=vertrag.deleted_at,
        mieter=mieter_info,
        einheit=einheit_info,
    )
