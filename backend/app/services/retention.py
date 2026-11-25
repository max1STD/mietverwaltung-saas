"""DSGVO-konforme Aufbewahrung: Sperren, Vorwarnung, Löschen, Protokoll."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import and_, func, select
from sqlalchemy.orm import joinedload

from app.models.loeschregel import Loeschprotokoll, Loeschregel

if TYPE_CHECKING:
    
    from sqlalchemy.orm import DeclarativeMeta


class LoeschStatus(str, Enum):
    AKTIV = "aktiv"
    GESPERRT = "gesperrt"
    VORWARNUNG = "vorwarnung"
    GELOESCHT = "geloescht"
    LEGAL_HOLD = "legal_hold"

DEFAULT_REGELN: list[dict] = [
    {
        "klasse": "K1",
        "datenart": "Mietinteressenten und Bewerber, kein Vertrag",
        "frist_monate": 3,
        "startpunkt": "Absage oder Vergabe der Wohnung",
        "rechtsgrundlage": "DSGVO Art. 5 und 6",
        "mindestfrist_monate": 3,
    },
    {
        "klasse": "K2",
        "datenart": "Selbstauskunft und Bonitätsdaten des Mieters",
        "frist_monate": 24,
        "startpunkt": "Mietvertragsschluss",
        "rechtsgrundlage": "Datenminimierung",
        "mindestfrist_monate": 24,
    },
    {
        "klasse": "K3",
        "datenart": "Mietvertrag und Mieterstammdaten",
        "frist_monate": 36,
        "startpunkt": "Ende des Jahres, in dem die Forderungen faellig wurden",
        "rechtsgrundlage": "§§ 195, 199 BGB",
        "mindestfrist_monate": 36,
    },
    {
        "klasse": "K4",
        "datenart": "Nebenkostenabrechnung und Belege gegenueber dem Mieter",
        "frist_monate": 36,
        "startpunkt": "Ende des Jahres, in dem die Abrechnung zuging",
        "rechtsgrundlage": "§ 556 Abs. 3 BGB, §§ 195, 199 BGB",
        "mindestfrist_monate": 36,
    },
    {
        "klasse": "K5",
        "datenart": "Kaution und Kautionsabrechnung",
        "frist_monate": 36,
        "startpunkt": "Ende des Jahres der Kautionsabrechnung",
        "rechtsgrundlage": "§§ 195, 199 BGB",
        "mindestfrist_monate": 36,
    },
    {
        "klasse": "K6",
        "datenart": "Buchungsbelege, Rechnungen, Zahlungsnachweise",
        "frist_monate": 96,
        "startpunkt": "Ende des Kalenderjahres der Entstehung",
        "rechtsgrundlage": "§ 147 Abs. 3 AO, § 257 Abs. 4 HGB, § 14b UStG",
        "mindestfrist_monate": 96,
    },
    {
        "klasse": "K7",
        "datenart": "Handels- und Geschaeftsbriefe",
        "frist_monate": 72,
        "startpunkt": "Ende des Kalenderjahres",
        "rechtsgrundlage": "§ 147 AO, § 257 HGB",
        "mindestfrist_monate": 72,
    },
    {
        "klasse": "K8",
        "datenart": "Anschaffungs- und Herstellungskosten der Immobilie",
        "frist_monate": 0,
        "startpunkt": "Verkauf bzw. Ende der Nutzung",
        "rechtsgrundlage": "steuerliche Nachweise",
        "mindestfrist_monate": 0,
    },
    {
        "klasse": "K9",
        "datenart": "Tickets, Handwerkerauftraege, Kommunikation",
        "frist_monate": 36,
        "startpunkt": "Ticket geschlossen",
        "rechtsgrundlage": "§§ 195, 199 BGB",
        "mindestfrist_monate": 36,
    },
    {
        "klasse": "K10",
        "datenart": "Zugriffs- und Audit-Protokolle",
        "frist_monate": 12,
        "startpunkt": "Erzeugung",
        "rechtsgrundlage": "Art. 5 Abs. 2 DSGVO, Art. 32",
        "mindestfrist_monate": 12,
    },
    {
        "klasse": "K11",
        "datenart": "Eigene Nutzerkonten und Abrechnung",
        "frist_monate": 96,
        "startpunkt": "Vertragsende",
        "rechtsgrundlage": "§ 147 AO",
        "mindestfrist_monate": 96,
    },
    {
        "klasse": "K12",
        "datenart": "Datenraum-Pakete und Freigaben",
        "frist_monate": 1,
        "startpunkt": "Freigabe",
        "rechtsgrundlage": "Zweckbindung",
        "mindestfrist_monate": 1,
    },
]


class RetentionService:
    """Verwaltet Sperren, Vorwarnung und Löschung nach Löschklassen."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def seed_default_rules(self) -> None:
        """Legt die Standard-Löschregeln an, falls noch nicht vorhanden."""
        for regel in DEFAULT_REGELN:
            exists = await self.session.execute(
                select(Loeschregel).where(
                    and_(
                        Loeschregel.org_id.is_(None),
                        Loeschregel.klasse == regel["klasse"],
                        Loeschregel.version == 1,
                    )
                )
            )
            if exists.scalar_one_or_none() is None:
                self.session.add(Loeschregel(**regel))
        await self.session.flush()

    async def get_rule(
        self,
        klasse: str,
        org_id: int | None = None,
    ) -> Loeschregel:
        """Liest die gültige Regel: Organisationsregel oder System-Default."""
        # Prefer org-specific override, fall back to system default
        stmt = (
            select(Loeschregel)
            .where(Loeschregel.klasse == klasse)
            .where((Loeschregel.org_id == org_id) | (Loeschregel.org_id.is_(None)))
            .order_by(Loeschregel.org_id.nulls_last(), Loeschregel.version.desc())
        )
        result = await self.session.execute(stmt)
        regel = result.scalars().first()
        if regel is None:
            raise ValueError(f"Keine Löschregel für Klasse {klasse}")
        return regel

    async def sperren(
        self,
        model: DeclarativeMeta,
        obj_id: int,
        klasse: str,
        org_id: int | None = None,
        startpunkt: datetime | None = None,
        grund: str | None = None,
    ) -> None:
        """Sperrt einen Datensatz und setzt die früheste Löschfrist."""
        regel = await self.get_rule(klasse, org_id)
        start = startpunkt or datetime.now(UTC)
        loesch_frist = start + timedelta(days=30 * regel.frist_monate)

        obj = await self.session.get(model, obj_id)
        if obj is None:
            return
        obj.lifecycle_status = LoeschStatus.GESPERRT.value
        obj.gesperrt_am = datetime.now(UTC)
        obj.loeschklasse = klasse
        obj.loeschen_fruehestens_am = loesch_frist

        self.session.add(Loeschprotokoll(
            org_id=org_id,
            tabelle=model.__tablename__,
            datensatz_id=obj_id,
            public_id=getattr(obj, "public_id", None),
            klasse=klasse,
            aktion="gesperrt",
                ausloeser="system",
                grund=grund or f"Lebenszyklus-Ereignis, Klasse {klasse}",
            )
        )
        await self.session.flush()

    async def vorwarnung_senden(
        self,
        model: DeclarativeMeta,
        obj_id: int,
        klasse: str,
        org_id: int | None = None,
    ) -> None:
        """Protokolliert die 30-Tage-Vorwarnung vor Löschung."""
        self.session.add(Loeschprotokoll(
            org_id=org_id,
            tabelle=model.__tablename__,
            datensatz_id=obj_id,
            klasse=klasse,
            aktion="vorwarnung",
                ausloeser="system",
                grund="30 Tage vor geplanter Loeschung",
            )
        )

    async def loeschlauf(
        self,
        model: DeclarativeMeta,
        klasse: str,
        org_id: int | None = None,
        jetzt: datetime | None = None,
    ) -> int:
        """Löscht gesperrte Datensätze, deren Frist abgelaufen ist.

        Löschung bedeutet hier Soft-Delete + Status geloescht + Protokoll.
        Hard-Delete passiert erst nach weiterer Sicherheitsprüfung.
        """
        jetzt = jetzt or datetime.now(UTC)
        warn_zeitpunkt = jetzt + timedelta(days=30)

        # 30-Tage-Vorwarnung
        warn_candidates = await self.session.execute(
            select(model).where(
                and_(
                    model.lifecycle_status == LoeschStatus.GESPERRT.value,
                    model.loeschklasse == klasse,
                    model.loeschen_fruehestens_am <= warn_zeitpunkt,
                    model.loeschen_fruehestens_am > jetzt,
                    model.legal_hold.is_(False) if hasattr(model, "legal_hold") else True,
                )
            )
        )
        for obj in warn_candidates.scalars().all():
            await self.vorwarnung_senden(model, obj.id, klasse, org_id)

        # Eigentliche Löschung
        delete_candidates = await self.session.execute(
            select(model).where(
                and_(
                    model.lifecycle_status == LoeschStatus.GESPERRT.value,
                    model.loeschklasse == klasse,
                    model.loeschen_fruehestens_am <= jetzt,
                    model.legal_hold.is_(False) if hasattr(model, "legal_hold") else True,
                )
            )
        )
        geloescht = 0
        for obj in delete_candidates.scalars().all():
            obj.lifecycle_status = LoeschStatus.GELOESCHT.value
            if hasattr(obj, "deleted_at"):
                obj.deleted_at = jetzt
            self.session.add(
                Loeschprotokoll(
                    org_id=org_id,
                    tabelle=model.__tablename__,
                    datensatz_id=obj.id,
                    public_id=getattr(obj, "public_id", None),
                    klasse=klasse,
                    aktion="geloescht",
                    ausloeser="system",
                    grund="Aufbewahrungsfrist abgelaufen",
                )
            )
            geloescht += 1

        await self.session.flush()
        return geloescht

    async def run_dry(self, lawyer_hold: bool = False) -> list[Loeschprotokoll]:
        """Prüft anstehende Sperr-/Löschaktionen und protokolliert Warnungen (Dry-Run)."""
        jetzt = datetime.now(UTC)
        warn_zeitpunkt = jetzt + timedelta(days=30)
        protocol: list[Loeschprotokoll] = []
        from app.models import (
            abrechnungen,
            bankverbindung,
            bewerbungen,
            dokument,
            kosten,
            mieter,
            mietvertraege,
            user,
            zaehler,
        )
        models = [
            mieter.Mieter,
            bewerbungen.Bewerbung,
            mietvertraege.Mietvertrag,
            dokument.Dokument,
            abrechnungen.Abrechnung,
            kosten.Kosten,
            bankverbindung.Bankverbindung,
            zaehler.Zaehler,
            zaehler.Zaehlerablesung,
            user.User,
        ]
        for model in models:
            if not hasattr(model, "lifecycle_status"):
                continue
            result = await self.session.execute(
                select(model).where(
                    and_(
                        model.lifecycle_status == LoeschStatus.GESPERRT.value,
                        model.loeschen_fruehestens_am <= warn_zeitpunkt,
                        model.loeschen_fruehestens_am > jetzt,
                        (
                            model.legal_hold.is_(False)
                            if hasattr(model, "legal_hold")
                            else True
                        ),
                    )
                )
            )
            warn_candidates = result.scalars().all()
            for obj in warn_candidates:
                protocol.append(
                    Loeschprotokoll(
                        tabelle=model.__tablename__,
                        datensatz_id=obj.id,
                        public_id=getattr(obj, "public_id", None),
                        klasse=obj.loeschklasse or "K1",
                        aktion="WARNUNG_30_TAGE",
                        ausloeser="system",
                        grund="30 Tage vor geplanter Loeschung (Dry-Run)",
                    )
                )
        return protocol
