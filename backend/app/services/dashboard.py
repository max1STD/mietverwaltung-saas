"""Dashboard-Service — Kennzahlen, Finanzen und Smart Insights."""
from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.einheit import Einheit
from app.models.fristen import Frist
from app.models.kosten import Kosten
from app.models.mieter import Mieter
from app.models.mietvertraege import Mietvertrag
from app.models.mietzahlungen import Mietzahlung
from app.models.objekt import Objekt
from app.models.subscription import Subscription  # noqa: TCH001
from app.models.tickets import Ticket
from app.schemas.dashboard import (
    DashboardFinancials,
    DashboardInsight,
    DashboardInsights,
    DashboardObjectSummary,
    DashboardSubscriptionInfo,
    DashboardSummary,
    MonthlyFinance,
)


def _today() -> date:
    """Heutiges Datum (Wrapper für Testbarkeit)."""
    return date.today()


def _round2(value: Decimal | float | None) -> Decimal:
    """Rundet auf 2 Dezimalstellen (kaufmännisch)."""
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _price_per_we(wohnungen_count: int) -> Decimal:
    """Staffelpreis pro WE nach aktuellem Pro-WE-Modell."""
    if wohnungen_count <= 0:
        return Decimal("0.00")
    if wohnungen_count <= 5:
        return Decimal("9.75")
    if wohnungen_count <= 25:
        return Decimal("7.50")
    if wohnungen_count <= 49:
        return Decimal("5.90")
    # Ab 50 WE: Custom Pricing — hier als Signalwert 4,90 anzeigen.
    return Decimal("4.90")


async def _get_wohnungen_count(db: AsyncSession, vermieter_id: int) -> int:
    """Aktuelle Anzahl der Wohneinheiten eines Vermieters."""
    result = await db.execute(
        select(func.count(Einheit.id)).where(
            Einheit.vermieter_id == vermieter_id,
            Einheit.deleted_at.is_(None),
        )
    )
    return int(result.scalar_one() or 0)


async def _get_subscription_info(
    db: AsyncSession,
    vermieter_id: int,
    wohnungen_count: int,
) -> DashboardSubscriptionInfo:
    """Ermittelt den aktuellen Abo-Status aus subscriptions/plan_usage."""
    sub_result = await db.execute(
        select(Subscription).where(Subscription.user_id == vermieter_id)
    )
    subscription = sub_result.scalar_one_or_none()

    if subscription:
        price = _round2(subscription.price_per_we)
        return DashboardSubscriptionInfo(
            status=subscription.status,
            billing_cycle=subscription.billing_cycle,
            wohnungen_count=wohnungen_count,
            price_per_we=price,
            total_monthly=_round2(
                price * Decimal(wohnungen_count)
                if subscription.billing_cycle == "monthly"
                else (price * Decimal(wohnungen_count)) / Decimal("12")
            ),
            trial_ends_at=subscription.trial_ends_at.date() if subscription.trial_ends_at else None,
            is_trial=subscription.status == "trial",
        )

    # Fallback: Trial-Status mit dynamisch ermittelter WE-Anzahl.
    price = _price_per_we(wohnungen_count)
    return DashboardSubscriptionInfo(
        status="trial",
        billing_cycle="monthly",
        wohnungen_count=wohnungen_count,
        price_per_we=price,
        total_monthly=_round2(price * Decimal(wohnungen_count)),
        trial_ends_at=None,
        is_trial=True,
    )


async def summary(db: AsyncSession, vermieter_id: int) -> DashboardSummary:
    """Aggregierte Übersicht für das Dashboard."""
    today = _today()
    first_of_month = today.replace(day=1)

    # Objekte
    objekte_result = await db.execute(
        select(func.count(Objekt.id)).where(
            Objekt.vermieter_id == vermieter_id,
            Objekt.deleted_at.is_(None),
        )
    )
    objekte_count = int(objekte_result.scalar_one() or 0)

    # Einheiten
    einheiten_count = await _get_wohnungen_count(db, vermieter_id)

    # Mieter
    mieter_result = await db.execute(
        select(func.count(Mieter.id)).where(
            Mieter.vermieter_id == vermieter_id,
            Mieter.deleted_at.is_(None),
        )
    )
    mieter_count = int(mieter_result.scalar_one() or 0)

    # Offene Tickets (nicht final)
    ticket_final_states = {"erledigt", "geschlossen", "abgelehnt"}
    tickets_result = await db.execute(
        select(func.count(Ticket.id)).where(
            Ticket.vermieter_id == vermieter_id,
            Ticket.status.notin_(ticket_final_states),
        )
    )
    offene_tickets = int(tickets_result.scalar_one() or 0)

    # Umsatz diesen Monat: Summe Soll-Mietzahlungen im aktuellen Monat,
    # Fallback auf aktive Verträge wenn keine Zahlungen erfasst.
    zahlungen_result = await db.execute(
        select(func.coalesce(func.sum(Mietzahlung.betrag_soll), Decimal("0.00"))).where(
            Mietzahlung.vermieter_id == vermieter_id,
            Mietzahlung.zahlungsdatum >= first_of_month,
            Mietzahlung.zahlungsdatum <= today,
        )
    )
    umsatz = _round2(zahlungen_result.scalar_one())

    if umsatz == Decimal("0.00"):
        vertraege_result = await db.execute(
            select(Mietvertrag).where(
                Mietvertrag.vermieter_id == vermieter_id,
                Mietvertrag.status == "aktiv",
                Mietvertrag.deleted_at.is_(None),
            )
        )
        vertraege = list(vertraege_result.scalars().all())
        umsatz = _round2(
            sum(
                float(v.miete_cold or 0) + float(v.nebenkosten_voraus or 0)
                for v in vertraege
            )
        )

    # Kosten diesen Monat
    kosten_result = await db.execute(
        select(func.coalesce(func.sum(Kosten.betrag), Decimal("0.00"))).where(
            Kosten.vermieter_id == vermieter_id,
            Kosten.datum >= first_of_month,
            Kosten.datum <= today,
            Kosten.deleted_at.is_(None),
        )
    )
    kosten_monat = _round2(kosten_result.scalar_one())

    subscription = await _get_subscription_info(db, vermieter_id, einheiten_count)

    return DashboardSummary(
        objekte_count=objekte_count,
        einheiten_count=einheiten_count,
        mieter_count=mieter_count,
        offene_tickets_count=offene_tickets,
        subscription=subscription,
        umsatz_diesen_monat=umsatz,
        kosten_diesen_monat=kosten_monat,
    )


async def object_summary(
    db: AsyncSession,
    vermieter_id: int,
    objekt_id: int,
) -> DashboardObjectSummary:
    """Kennzahlen für ein einzelnes Objekt."""
    objekt = await db.get(Objekt, objekt_id)
    if objekt is None or objekt.vermieter_id != vermieter_id:
        raise ValueError("Objekt nicht gefunden")

    einheiten_result = await db.execute(
        select(Einheit).where(
            Einheit.objekt_id == objekt_id,
            Einheit.deleted_at.is_(None),
        )
    )
    einheiten = list(einheiten_result.scalars().all())
    einheiten_total = len(einheiten)

    vermietet = 0
    jahreskaltmiete = Decimal("0.00")
    einheit_ids = [e.id for e in einheiten]

    if einheit_ids:
        vertraege_result = await db.execute(
            select(Mietvertrag).where(
                Mietvertrag.einheit_id.in_(einheit_ids),
                Mietvertrag.status == "aktiv",
                Mietvertrag.deleted_at.is_(None),
            )
        )
        vertraege = list(vertraege_result.scalars().all())
        vermietet = len({v.einheit_id for v in vertraege})
        jahreskaltmiete = _round2(
            sum(float(v.miete_cold or 0) for v in vertraege) * 12
        )

    quote = Decimal("0.00")
    if einheiten_total > 0:
        quote = _round2(Decimal(vermietet) / Decimal(einheiten_total) * Decimal("100"))

    # Jahreskosten des Objekts (alle nicht gelöschten Kostenpositionen).
    kosten_result = await db.execute(
        select(func.coalesce(func.sum(Kosten.betrag), Decimal("0.00"))).where(
            Kosten.vermieter_id == vermieter_id,
            Kosten.objekt_id == objekt_id,
            Kosten.deleted_at.is_(None),
        )
    )
    jahreskosten = _round2(kosten_result.scalar_one())

    kaufpreis = _round2(objekt.kaufpreis) if objekt.kaufpreis else None
    bruttomietrendite: Decimal | None = None
    nettomietrendite: Decimal | None = None
    if kaufpreis and kaufpreis > 0:
        bruttomietrendite = _round2(jahreskaltmiete / kaufpreis * Decimal("100"))
        nettomietrendite = _round2(
            (jahreskaltmiete - jahreskosten) / kaufpreis * Decimal("100")
        )

    return DashboardObjectSummary(
        objekt_id=objekt.id,
        name=objekt.name,
        einheiten_total=einheiten_total,
        einheiten_vermietet=vermietet,
        vermietungsquote=quote,
        jahreskaltmiete=jahreskaltmiete,
        jahreskosten=jahreskosten,
        kaufpreis=kaufpreis,
        bruttomietrendite=bruttomietrendite,
        nettomietrendite=nettomietrendite,
    )


async def financials(db: AsyncSession, vermieter_id: int) -> DashboardFinancials:
    """Mieteinnahmen vs. Kosten der letzten 12 Monate."""
    today = _today()
    monate: list[MonthlyFinance] = []
    einnahmen_map: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    kosten_map: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))

    # Aktive Verträge als monatliche Soll-Einnahmen für jeden Monat.
    vertraege_result = await db.execute(
        select(Mietvertrag).where(
            Mietvertrag.vermieter_id == vermieter_id,
            Mietvertrag.status == "aktiv",
            Mietvertrag.deleted_at.is_(None),
        )
    )
    vertraege = list(vertraege_result.scalars().all())

    for i in range(11, -1, -1):
        monats_datum = today.replace(day=1) - timedelta(days=i * 30)
        # Genauer: Monatserster
        monats_datum = monats_datum.replace(day=1)
        monat_key = monats_datum.strftime("%Y-%m")
        for v in vertraege:
            if v.mietbeginn and v.mietbeginn <= monats_datum:
                if v.mietende is None or v.mietende >= monats_datum:
                    einnahmen_map[monat_key] += _round2(
                        Decimal(str(v.miete_cold or 0))
                        + Decimal(str(v.nebenkosten_voraus or 0))
                    )

    # Kosten nach Monat
    startdatum = today.replace(day=1) - timedelta(days=11 * 30)
    startdatum = startdatum.replace(day=1)
    kosten_result = await db.execute(
        select(Kosten).where(
            Kosten.vermieter_id == vermieter_id,
            Kosten.datum >= startdatum,
            Kosten.datum <= today,
            Kosten.deleted_at.is_(None),
        )
    )
    for k in kosten_result.scalars().all():
        monat_key = k.datum.strftime("%Y-%m")
        kosten_map[monat_key] += _round2(k.betrag)

    # Mietzahlungen (Ist) überschreiben die Soll-Einnahmen, falls vorhanden.
    zahlungen_result = await db.execute(
        select(Mietzahlung).where(
            Mietzahlung.vermieter_id == vermieter_id,
            Mietzahlung.zahlungsdatum >= startdatum,
            Mietzahlung.zahlungsdatum <= today,
        )
    )
    for z in zahlungen_result.scalars().all():
        if z.zahlungsdatum:
            monat_key = z.zahlungsdatum.strftime("%Y-%m")
            einnahmen_map[monat_key] = _round2(z.betrag_soll or 0)

    summe_einnahmen = Decimal("0.00")
    summe_kosten = Decimal("0.00")

    for i in range(11, -1, -1):
        monats_datum = today.replace(day=1) - timedelta(days=i * 30)
        monats_datum = monats_datum.replace(day=1)
        monat_key = monats_datum.strftime("%Y-%m")
        einnahmen = _round2(einnahmen_map[monat_key])
        kosten = _round2(kosten_map[monat_key])
        netto = _round2(einnahmen - kosten)
        monate.append(
            MonthlyFinance(
                monat=monat_key,
                label=monats_datum.strftime("%b %y"),
                einnahmen=einnahmen,
                kosten=kosten,
                netto=netto,
            )
        )
        summe_einnahmen += einnahmen
        summe_kosten += kosten

    return DashboardFinancials(
        monate=monate,
        summe_einnahmen=_round2(summe_einnahmen),
        summe_kosten=_round2(summe_kosten),
        summe_netto=_round2(summe_einnahmen - summe_kosten),
    )


async def insights(db: AsyncSession, vermieter_id: int) -> DashboardInsights:
    """Smart Insights: Leerstand, Tickets, Mahnungen, Fristen."""
    today = _today()
    items: list[DashboardInsight] = []

    # Leerstände: Objekte mit mindestens einer freien Einheit.
    einheiten_result = await db.execute(
        select(Einheit).where(
            Einheit.vermieter_id == vermieter_id,
            Einheit.deleted_at.is_(None),
        )
    )
    einheiten = list(einheiten_result.scalars().all())
    einheit_ids = [e.id for e in einheiten]

    if einheit_ids:
        vertraege_result = await db.execute(
            select(Mietvertrag.einheit_id).where(
                Mietvertrag.einheit_id.in_(einheit_ids),
                Mietvertrag.status == "aktiv",
                Mietvertrag.deleted_at.is_(None),
            )
        )
        vermietete_einheit_ids = {row[0] for row in vertraege_result.all()}
        freie_einheiten = [e for e in einheiten if e.id not in vermietete_einheit_ids]

        if freie_einheiten:
            frei = freie_einheiten[0]
            items.append(
                DashboardInsight(
                    typ="leerstand",
                    titel=f"{len(freie_einheiten)} Leerstand{'' if len(freie_einheiten) == 1 else 'äume'}",
                    beschreibung=f"{frei.name} ist aktuell nicht vermietet. Miete ausgeschrieben?",
                    link=f"/objekte/{frei.objekt_id}",
                    prioritaet="normal" if len(freie_einheiten) <= 1 else "hoch",
                    entity_id=frei.id,
                )
            )

    # Offene Tickets (älteste 3)
    ticket_final_states = {"erledigt", "geschlossen", "abgelehnt"}
    tickets_result = await db.execute(
        select(Ticket).where(
            Ticket.vermieter_id == vermieter_id,
            Ticket.status.notin_(ticket_final_states),
        ).order_by(Ticket.created_at.asc()).limit(3)
    )
    for ticket in tickets_result.scalars().all():
        prio = "dringend" if ticket.priority == "dringend" else (
            "hoch" if ticket.priority == "normal" else "normal"
        )
        items.append(
            DashboardInsight(
                typ="ticket",
                titel=f"Ticket {ticket.ticket_number}: {ticket.title}",
                beschreibung=f"Status: {ticket.status} · Priorität: {ticket.priority}",
                link=f"/tickets/{ticket.id}",
                prioritaet=prio,
                entity_id=ticket.id,
            )
        )

    # Mahnungen: Mietzahlungen mit mahnstufe > 0
    mahnungen_result = await db.execute(
        select(Mietzahlung).where(
            Mietzahlung.vermieter_id == vermieter_id,
            Mietzahlung.mahnstufe > 0,
        ).order_by(Mietzahlung.mahnstufe.desc()).limit(3)
    )
    for mahnung in mahnungen_result.scalars().all():
        items.append(
            DashboardInsight(
                typ="mahnung",
                titel=f"Mahnstufe {mahnung.mahnstufe} offen",
                beschreibung=f"Offene Forderung: {_round2(mahnung.betrag_soll or 0)} €",
                link="/mietvertraege",
                prioritaet="dringend" if mahnung.mahnstufe >= 2 else "hoch",
                entity_id=mahnung.id,
            )
        )

    # Anstehende Fristen (fristen Tabelle)
    fristen_result = await db.execute(
        select(Frist).where(
            Frist.vermieter_id == vermieter_id,
            Frist.is_done.is_(False),
            Frist.deadline >= today,
        ).order_by(Frist.deadline.asc()).limit(3)
    )
    for frist in fristen_result.scalars().all():
        tage = (frist.deadline - today).days
        items.append(
            DashboardInsight(
                typ="frist",
                titel=frist.description or "Frist anstehend",
                beschreibung=f"Fällig in {tage} Tag{'en' if tage != 1 else ''} ({frist.deadline.isoformat()})",
                link="/einstellungen",
                prioritaet="dringend" if tage <= 3 else ("hoch" if tage <= 7 else "normal"),
                entity_id=frist.id,
            )
        )

    return DashboardInsights(insights=items)
