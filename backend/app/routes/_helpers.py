"""Response-Mapper für Objekt-, Einheit-, Mieter- und Mietvertrag-Routen."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.abrechnung_positionen import AbrechnungPosition
from app.models.abrechnungen import Abrechnung
from app.models.bewerbungen import Bewerbung
from app.models.einheit import Einheit
from app.models.kosten import Kosten
from app.models.mieter import Mieter
from app.models.mietvertraege import Mietvertrag
from app.models.mietzahlungen import Mietzahlung
from app.models.objekt import Objekt
from app.schemas.abrechnung import (
    AbrechnungNestedEinheit,
    AbrechnungPositionResponse,
    AbrechnungResponse,
)
from app.schemas.bewerbungen import (
    BewerbungNestedEinheit,
    BewerbungResponse,
)
from app.schemas.einheit import (
    EinheitNestedMieter,
    EinheitResponse,
)
from app.schemas.kosten import KostenNestedKategorie, KostenResponse
from app.schemas.mieter import (
    MieterNestedEinheit,
    MieterResponse,
)
from app.schemas.mietvertrag import (
    MietvertragNestedEinheit,
    MietvertragNestedMieter,
    MietvertragResponse,
)
from app.schemas.mietzahlung import (
    MietzahlungNestedMieter,
    MietzahlungNestedVertrag,
    MietzahlungResponse,
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


async def map_kosten_response(db: AsyncSession, kosten: Kosten) -> KostenResponse:
    """Mappt eine Kosten-ORM inklusive Kategorie auf das Response-Schema."""
    await db.refresh(kosten, attribute_names=["kategorie"])

    kategorie_info = None
    if kosten.kategorie:
        kategorie_info = KostenNestedKategorie(
            id=kosten.kategorie.id,
            name=kosten.kategorie.name,
            verteilungsschluessel=kosten.kategorie.verteilungsschluessel,
        )

    return KostenResponse(
        id=kosten.id,
        vermieter_id=kosten.vermieter_id,
        objekt_id=kosten.objekt_id,
        einheit_id=kosten.einheit_id,
        kategorie_id=kosten.kategorie_id,
        betrag=_to_decimal(kosten.betrag) or Decimal("0"),
        datum=kosten.datum,
        umlagefaehig=kosten.umlagefaehig,
        abrechnung_id=kosten.abrechnung_id,
        abgerechnet_am=kosten.abgerechnet_am,
        ki_kategorisiert=kosten.ki_kategorisiert,
        datev_konto=kosten.datev_konto,
        datev_buchungstext=kosten.datev_buchungstext,
        created_at=kosten.created_at,
        deleted_at=kosten.deleted_at,
        kategorie=kategorie_info,
    )


async def map_abrechnung_position_response(
    position: AbrechnungPosition,
) -> AbrechnungPositionResponse:
    """Mappt eine Abrechnungsposition-ORM auf das Response-Schema."""
    return AbrechnungPositionResponse(
        id=position.id,
        vermieter_id=position.vermieter_id,
        abrechnung_id=position.abrechnung_id,
        kategorie_id=position.kategorie_id,
        kosten_id=position.kosten_id,
        betrag_total=_to_decimal(position.betrag_total) or Decimal("0"),
        umlageanteil=_to_decimal(position.umlageanteil) or Decimal("0"),
        verteilungsschluessel=position.verteilungsschluessel,
        datev_betrag=_to_decimal(position.datev_betrag),
        created_at=position.created_at,
        deleted_at=position.deleted_at,
    )


async def map_abrechnung_response(
    db: AsyncSession,
    abrechnung: Abrechnung,
) -> AbrechnungResponse:
    """Mappt eine Abrechnung-ORM inklusive Positionen und Einheit auf Response."""
    await db.refresh(abrechnung, attribute_names=["einheit", "positionen"])

    einheit_info = None
    if abrechnung.einheit:
        einheit_info = AbrechnungNestedEinheit(
            id=abrechnung.einheit.id,
            name=abrechnung.einheit.name,
            size_qm=_to_decimal(abrechnung.einheit.size_qm) or Decimal("0"),
        )

    positionen = [
        await map_abrechnung_position_response(pos)
        for pos in abrechnung.positionen
        if pos.deleted_at is None
    ]

    return AbrechnungResponse(
        id=abrechnung.id,
        vermieter_id=abrechnung.vermieter_id,
        einheit_id=abrechnung.einheit_id,
        objekt_id=abrechnung.objekt_id,
        jahr=abrechnung.jahr,
        zeitraum_von=abrechnung.zeitraum_von,
        zeitraum_bis=abrechnung.zeitraum_bis,
        einwendungsfrist_bis=abrechnung.einwendungsfrist_bis,
        rechtskraeftig_seit=abrechnung.rechtskraeftig_seit,
        status=abrechnung.status,
        created_at=abrechnung.created_at,
        updated_at=abrechnung.updated_at,
        deleted_at=abrechnung.deleted_at,
        positionen=positionen,
        einheit=einheit_info,
    )


async def map_mietzahlung_response(
    db: AsyncSession,
    zahlung: Mietzahlung,
) -> MietzahlungResponse:
    """Mappt eine Mietzahlung-ORM inklusive Mieter und Vertrag auf Response."""
    await db.refresh(zahlung, attribute_names=["mieter", "vertrag"])

    mieter_info = None
    if zahlung.mieter:
        mieter_info = MietzahlungNestedMieter(
            id=zahlung.mieter.id,
            full_name=zahlung.mieter.full_name,
        )

    vertrag_info = None
    if zahlung.vertrag:
        vertrag_info = MietzahlungNestedVertrag(
            id=zahlung.vertrag.id,
            miete_cold=_to_decimal(zahlung.vertrag.miete_cold) or Decimal("0"),
        )

    return MietzahlungResponse(
        id=zahlung.id,
        vermieter_id=zahlung.vermieter_id,
        mieter_id=zahlung.mieter_id,
        vertrag_id=zahlung.vertrag_id,
        betrag_soll=_to_decimal(zahlung.betrag_soll) or Decimal("0"),
        betrag_ist=_to_decimal(zahlung.betrag_ist),
        zahlungsdatum=zahlung.zahlungsdatum,
        mahnstufe=zahlung.mahnstufe,
        zahlungsreferenz=zahlung.zahlungsreferenz,
        created_at=zahlung.created_at,
        mieter=mieter_info,
        vertrag=vertrag_info,
    )


async def map_bewerbung_response(
    db: AsyncSession,
    bewerbung: Bewerbung,
) -> BewerbungResponse:
    """Mappt eine Bewerbung-ORM inklusive Einheit-Info auf Response."""
    await db.refresh(bewerbung, attribute_names=["einheit"])
    if bewerbung.einheit:
        await db.refresh(bewerbung.einheit, attribute_names=["objekt"])

    einheit_info = None
    if bewerbung.einheit:
        einheit_info = BewerbungNestedEinheit(
            id=bewerbung.einheit.id,
            name=bewerbung.einheit.name,
            objekt_name=bewerbung.einheit.objekt.name if bewerbung.einheit.objekt else "",
        )

    return BewerbungResponse(
        id=bewerbung.id,
        vermieter_id=bewerbung.vermieter_id,
        einheit_id=bewerbung.einheit_id,
        first_name=bewerbung.first_name,
        last_name=bewerbung.last_name,
        email=bewerbung.email,
        phone=bewerbung.phone,
        income_monthly=_to_decimal(bewerbung.income_monthly),
        schufa_score=bewerbung.schufa_score,
        documents=bewerbung.documents,
        status=bewerbung.status,
        applied_at=bewerbung.applied_at,
        decided_at=bewerbung.decided_at,
        created_at=bewerbung.created_at,
        updated_at=bewerbung.updated_at,
        deleted_at=bewerbung.deleted_at,
        einheit=einheit_info,
    )
