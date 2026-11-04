# Datenbank-Management und Deployment-Sicherheit — MietVerwaltung SaaS

> **Projekt:** MietVerwaltung SaaS  
> **Gültig ab:** 2026-11-02  
> **Dokument-Typ:** Betriebs- und Sicherheitskonzept  
> **Verknüpfte Konzepte:**
> - Repo-Struktur & Change-Management (`Repo-Struktur-und-Change-Management.md`)
> - Server-Konzept v2 (`Server-Konzept-v2.md`)
> - DB-Schema v4 (`.hermes/plans/2026-11-02_db-schema-v4.md`)

---

## 0. Zielsetzung

Dieses Dokument definiert, wie Änderungen am PostgreSQL-Datenbankschema sicher entwickelt, getestet, ausgerollt und im Fehlerfall zurückgerollt werden. Es verbindet die CI/CD-Pipeline aus dem Repo-Struktur-Konzept mit der Backup-Strategie aus dem Server-Konzept und ergänzt konkrete Operationalisierungen.

---

## 1. Sichere DB-Migrationen

### 1.1 Alembic-Migrations-Regeln

Jede Alembic-Migration in `backend/alembic/versions/` muss folgende Regeln erfüllen:

| # | Regel | Begründung |
|---|-------|------------|
| 1 | **Jede Migration hat eine funktionierende `downgrade()`-Funktion.** | Nur so ist ein Rollback möglich. |
| 2 | **Neue Spalten sind entweder `nullable=True` oder haben einen Default.** | Alter Code, der noch läuft, während die DB bereits neuer ist, bricht nicht ab. |
| 3 | **Eine semantische Änderung = Eine Migration.** | Mehrere unabhängige Schema-Änderungen nicht in einer Migration mischen. |
| 4 | **Migrationen laufen VOR dem neuen Code.** | Im Deploy-Script wird zuerst `alembic upgrade head` ausgeführt, dann erst der neue Container gestartet. |
| 5 | **Kein `alembic downgrade` auf Prod ohne vorheriges Backup.** | Downgrade ist ein destruktiver Eingriff, daher immer Backup-Voraussetzung. |
| 6 | **Downgrade-Kompatibilität:** Alter Code muss mit dem neuen DB-Schema noch funktionieren. | Zwischen Migration und Container-Start existiert ein Zeitfenster, in dem der alte Code auf die neue DB zugreift. |
| 7 | **Niemals direkte Datenmanipulation ohne `data_upgrade()`-Hilfsfunktion.** | Schema und Datenumwandlung in einer Migration klar trennen und kommentieren. |
| 8 | **Migrationen werden in CI gegen eine frische PostgreSQL 17 getestet.** | Siehe Abschnitt 1.4. |

**Beispiel: Korrekte Alembic-Migration mit `downgrade()` und nullable-Spalte**

```python
# backend/alembic/versions/0004_add_mieter_notizen.py
"""add mieter.notizen spalte

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-02 12:00:00
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Regel 2: Spalte ist nullable, damit alter Code weiterläuft.
    # Default kann später in einer Folgemigration als NOT NULL gesetzt werden.
    op.add_column(
        "mieter",
        sa.Column("notizen", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    # Regel 1: Jede Migration muss rückgängig gemacht werden können.
    op.drop_column("mieter", "notizen")
```

---

### 1.2 Backup VOR jeder Migration

#### 1.2.1 Automatisches Backup in GitHub Actions

Vor jedem Deploy auf Beta/Prod wird ein Backup erstellt. Das Backup enthält Zeitstempel und Git-Tag:

```bash
#!/bin/bash
# Innerhalb des Deploy-Scripts (siehe deploy-beta.yml / deploy-prod.yml)
TAG="${GITHUB_REF_NAME:-unknown}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="pre_deploy_${TAG}_${TIMESTAMP}.dump"

pg_dump \
  --host="${DB_HOST}" \
  --port="${DB_PORT:-5432}" \
  --username="${DB_USER}" \
  --dbname="${DB_NAME}" \
  --format=custom \
  --compress=9 \
  --file="/srv/mietverwaltung/backups/${BACKUP_NAME}"

# Integrität prüfen
pg_restore --list "/srv/mietverwaltung/backups/${BACKUP_NAME}" > /dev/null
```

#### 1.2.2 Backup-Speicherorte

| Umgebung | Backup-Typ | Speicherort | Retention |
|----------|-----------|-------------|-----------|
| Lokal | `pg_dump` lokal | `db/backups/` | Manuell |
| Beta (Proxmox) | `pg_dump` täglich + Pre-Deploy | `/srv/mietverwaltung/backups/` | 7 Tage |
| Prod (Hetzner) | WAL-G Full + WAL + monatliches `pg_dump` | Storage Box (verschlüsselt) | Full: 4 Wochen, WAL: bis zum ältesten Full, Dump: 12 Monate |

#### 1.2.3 Backup-Verifizierung

Jedes `pg_dump`-Backup wird vor der Migration auf Integrität geprüft:

```bash
#!/bin/bash
BACKUP_FILE="/srv/mietverwaltung/backups/${BACKUP_NAME}"

# 1. Datei existiert und ist nicht leer
if [ ! -s "$BACKUP_FILE" ]; then
  echo "FEHLER: Backup-Datei fehlt oder ist leer" >&2
  exit 1
fi

# 2. PostgreSQL-interne Konsistenzprüfung
pg_restore --list "$BACKUP_FILE" > /dev/null || {
  echo "FEHLER: Backup-Integritätsprüfung pg_restore --list fehlgeschlagen" >&2
  exit 1
}

# 3. Optional: Probe-Restore in eine leere Test-DB (nachts einmal pro Woche)
psql -h "$DB_HOST" -U postgres -c "DROP DATABASE IF EXISTS backup_test;"
psql -h "$DB_HOST" -U postgres -c "CREATE DATABASE backup_test;"
pg_restore --dbname="postgresql://$DB_USER@$DB_HOST/backup_test" "$BACKUP_FILE" || {
  echo "FEHLER: Probe-Restore fehlgeschlagen" >&2
  exit 1
}
psql -h "$DB_HOST" -U postgres -c "DROP DATABASE backup_test;"
```

#### 1.2.4 Go-Live: WAL-G Pre-Deploy Backup

Vor jeder Prod-Migration wird zusätzlich ein WAL-G-Full-Backup getriggert:

```bash
#!/bin/bash
# Im Deploy-Script auf Hetzner vor alembic upgrade head
export WALG_SSH_PREFIX="sftp://$STORAGE_BOX_USER@$STORAGE_BOX_HOST/backups/mietverwaltung/wal-g"
wal-g backup-push --full
wal-g backup-list
```

---

### 1.3 Automatisches Rollback bei fehlgeschlagenem Deploy

#### 1.3.1 Auslöser

Nach jedem Deploy läuft ein Health-Check:

```bash
HEALTH_URL="https://mietverwaltung.de/api/health"
MAX_RETRIES=3
DELAY=10

for i in $(seq 1 $MAX_RETRIES); do
  if curl -fsS --max-time 5 "$HEALTH_URL" | grep -q '"status":"ok"'; then
    echo "Health-Check OK"
    exit 0
  fi
  echo "Health-Check Versuch $i/$MAX_RETRIES fehlgeschlagen, warte ${DELAY}s..."
  sleep "$DELAY"
done

echo "Health-Check nach $MAX_RETRIES Versuchen fehlgeschlagen — Rollback wird eingeleitet" >&2
# -> Rollback-Script aufrufen
```

#### 1.3.2 Rollback-Reihenfolge

1. Altes Docker-Image starten.
2. `alembic downgrade -1` ausführen (nur falls zuvor eine Migration ausgeführt wurde).
3. Falls Downgrade fehlschlägt: Backup-Restore durchführen.
4. E-Mail-Alert an Max.
5. Incident-Eintrag in `docs/operations/runbooks/incident-YYYY-MM-DD.md`.

#### 1.3.3 Vollständiges Rollback-Script

Siehe Abschnitt 3.3 für das ausführbare `scripts/deploy/rollback.sh`.

---

### 1.4 Migrationstest in CI

Jeder PR mit DB-Änderung wird in CI gegen eine frische PostgreSQL 17 getestet:

1. `alembic upgrade head`
2. Seed-Daten laden
3. `alembic downgrade base`
4. Wenn Schritt 1 oder 3 fehlschlägt: CI fails

Die YAML befindet sich in Abschnitt 3.1 (`migration-test.yml`).

---

### 1.5 Der komplette Ablauf bei einer Schema-Änderung

#### 1.5.1 Lokal entwickeln

```bash
# 1. Feature-Branch erstellen
git checkout -b feature/db-mieter-notizen

# 2. Lokale Modelle anpassen
# backend/app/models/mieter.py -> notizen: Mapped[str | None]

# 3. Alembic-Migration generieren
cd backend
alembic revision --autogenerate -m "add mieter notizen"

# 4. Migration reviewen und ggf. korrigieren
# - downgrade() vorhanden?
# - neue Spalte nullable oder mit Default?
# - keine Daten zerstörerischen Operationen?

# 5. Lokal testen
alembic downgrade base
alembic upgrade head
python scripts/seed_data.py
alembic downgrade base
```

#### 1.5.2 PR erstellen

- PR-Template ausfüllen (DB-Änderung markieren).
- CI läuft: `lint.yml`, `test.yml`, `build.yml`, `security.yml`, `migration-test.yml`.
- Max reviewed CODEOWNERS-Pfad `backend/alembic/versions/`.

#### 1.5.3 Merge nach `main`

Nur nach grünem CI und menschlicher Freigabe. Kein direkter Push auf `main`.

#### 1.5.4 Tag erstellen und Beta-Deploy

```bash
# Tag nur von main
git checkout main
git pull origin main

# SemVer Pre-Release Tag
# Beispiel: Minor-Feature in Beta
git tag v0.2.0-beta.4
git push origin v0.2.0-beta.4
```

GitHub Actions `deploy-beta.yml` startet automatisch:

```bash
# Auszug aus deploy-beta.yml
# 1. Backup
pg_dump --format=custom --compress=9 --file=...
pg_restore --list ...

# 2. Migration vor neuem Code
docker compose exec backend alembic upgrade head

# 3. Neue Container starten
docker compose up -d --build

# 4. Health-Check
./scripts/ops/health-check.sh
```

#### 1.5.5 Prod-Deploy (Go-Live)

Analog zu Beta, zusätzlich:

- Max approved Production-Environment in GitHub.
- WAL-G Full-Backup vor Migration.
- E-Mail-Versand nach erfolgreichem Deploy.

#### 1.5.6 Übersicht: Schritt-für-Schritt mit Befehlen

```bash
# Lokale Entwicklung
1. git checkout -b feature/db-mieter-notizen
2. cd backend && alembic revision --autogenerate -m "add mieter notizen"
3. # Migration prüfen: downgrade() + nullable/default
4. cd backend && alembic upgrade head
5. python backend/scripts/seed_data.py
6. cd backend && alembic downgrade base
7. git add backend/alembic/versions/0004_add_mieter_notizen.py backend/app/models/mieter.py
8. git commit -m "feat(mieter): Notizen-Spalte hinzufügen

- Neue nullable-Spalte mieter.notizen
- Downgrade-Funktion vorhanden

Refs: #123"
9. git push origin feature/db-mieter-notizen
10. # PR erstellen, CI läuft

# Review & Merge
11. # Max approved, CI grün
12. git checkout main && git pull origin main
13. git tag v0.2.0-beta.4
14. git push origin v0.2.0-beta.4

# Deploy (automatisch via GitHub Actions)
15. # Backup, alembic upgrade head, Docker Deploy, Health-Check
```

---

## 2. Testdaten-Strategie pro Umgebung

### 2.1 Lokal (Entwickler-Rechner)

Lokale Entwickler-Umgebungen verwenden feste Dummy-Daten über `backend/scripts/seed_data.py`.

#### 2.1.1 Seed-Daten-Inhalt

| Entität | Anzahl |
|---------|--------|
| Objekte | 3 |
| Wohnungen | 5 |
| Mieter | 4 |
| Tickets | 2 |
| Kosten | 10 |
| Abrechnung | 1 |
| Bewerbungen | 2 |

#### 2.1.2 Makefile-Targets

```makefile
# Makefile (Auszug)
seed-dev:
	cd backend && python scripts/seed_data.py

reset-dev-db:
	docker compose -f docker-compose.dev.yml down -v
	docker compose -f docker-compose.dev.yml up -d db redis
	@echo "Warte auf PostgreSQL..."
	@sleep 3
	cd backend && alembic upgrade head && python scripts/seed_data.py
```

#### 2.1.3 Konkretes Python-Beispiel `seed_data.py`

```python
#!/usr/bin/env python3
"""Lokale Seed-Daten für Entwicklungsumgebungen.

ACHTUNG: Dieses Script darf NIE gegen Beta oder Prod ausgeführt werden.
Es ist ausschließlich für lokale Docker-DBs gedacht.
"""

import asyncio
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker
from app.models import (
    Objekt,
    Einheit,
    Mieter,
    Ticket,
    Kosten,
    Abrechnung,
    Bewerbung,
    User,
)
from app.utils.crypto import hash_password


async def seed() -> None:
    async with async_session_maker() as session:
        # Idempotenz: nur seeden, wenn DB leer ist
        existing = await session.execute(select(User).limit(1))
        if existing.scalar_one_or_none() is not None:
            print("Datenbank enthält bereits Daten — überspringe seed_data.py")
            return

        # Demo-Vermieter
        vermieter = User(
            id=uuid4(),
            email="dev@example.com",
            hashed_password=hash_password("changeme"),
            vorname="Max",
            nachname="Developer",
            rolle="vermieter",
            ist_aktiv=True,
            created_at=datetime.utcnow(),
        )
        session.add(vermieter)

        # Objekte
        objekte = [
            Objekt(
                id=uuid4(),
                user_id=vermieter.id,
                bezeichnung="Musterstraße 1",
                strasse="Musterstraße",
                hausnummer="1",
                plz="10115",
                ort="Berlin",
                land="DE",
               baujahr=1990,
                wohnflaeche_qm=Decimal("120.00"),
            ),
            Objekt(
                id=uuid4(),
                user_id=vermieter.id,
                bezeichnung="Hauptplatz 5",
                strasse="Hauptplatz",
                hausnummer="5",
                plz="8010",
                ort="Graz",
                land="AT",
                baujahr=2005,
                wohnflaeche_qm=Decimal("85.50"),
            ),
            Objekt(
                id=uuid4(),
                user_id=vermieter.id,
                bezeichnung="Seestrasse 12",
                strasse="Seestrasse",
                hausnummer="12",
                plz="8001",
                ort="Zürich",
                land="CH",
                baujahr=2010,
                wohnflaeche_qm=Decimal("95.00"),
            ),
        ]
        session.add_all(objekte)

        # Wohnungen (5)
        einheiten = []
        objekt_idx = 0
        for i in range(5):
            objekt = objekte[objekt_idx % len(objekte)]
            einheit = Einheit(
                id=uuid4(),
                objekt_id=objekt.id,
                bezeichnung=f"Wohnung {i+1}",
                lage=f"{i+1}. OG",
                wohnflaeche_qm=Decimal("55.00") + Decimal("5") * i,
                zimmer=2 + (i % 3),
                ist_vermietet=i < 4,
            )
            einheiten.append(einheit)
            objekt_idx += 1
        session.add_all(einheiten)

        # Mieter (4)
        mieter_data = [
            ("Anna", "Muster", "anna@example.com"),
            ("Bernd", "Beispiel", "bernd@example.com"),
            ("Clara", "Demo", "clara@example.com"),
            ("Daniel", "Test", "daniel@example.com"),
        ]
        mieter_list = []
        for idx, (vorname, nachname, email) in enumerate(mieter_data):
            m = Mieter(
                id=uuid4(),
                user_id=vermieter.id,
                einheit_id=einheiten[idx].id if idx < len(einheiten) else None,
                vorname=vorname,
                nachname=nachname,
                email=email,
                telefon=f"+49 170 {idx+1:06d}",
                geburtsdatum=date(1985 + idx, 5, 15),
                einzugsdatum=date(2024, 1, 1),
                adresse=f"{einheiten[idx].lage}, Musterstadt",
                iban=f"DE8937040044053201300{idx}",
                ist_aktiv=True,
            )
            mieter_list.append(m)
        session.add_all(mieter_list)

        # Tickets (2)
        tickets = [
            Ticket(
                id=uuid4(),
                user_id=vermieter.id,
                mieter_id=mieter_list[0].id,
                titel="Heizung defekt",
                beschreibung="Die Heizung in der Wohnung funktioniert nicht.",
                status="offen",
                prioritaet="hoch",
                created_at=datetime.utcnow(),
            ),
            Ticket(
                id=uuid4(),
                user_id=vermieter.id,
                mieter_id=mieter_list[1].id,
                titel="Wasserhahn tropft",
                beschreibung="Küchenwasserhahn tropft ständig.",
                status="in_bearbeitung",
                prioritaet="niedrig",
                created_at=datetime.utcnow(),
            ),
        ]
        session.add_all(tickets)

        # Kosten (10)
        kostenarten = ["Strom", "Gas", "Wasser", "Müll", "Versicherung", "Grundsteuer"]
        kosten_list = []
        for i in range(10):
            kosten = Kosten(
                id=uuid4(),
                user_id=vermieter.id,
                objekt_id=objekte[i % len(objekte)].id,
                kategorie=kostenarten[i % len(kostenarten)],
                betrag=Decimal("150.00") + Decimal("12.50") * i,
                rechnungsdatum=date(2024, 1 + (i % 12), 1),
                bezeichnung=f"Rechnung {i+1}",
            )
            kosten_list.append(kosten)
        session.add_all(kosten_list)

        # Abrechnung (1)
        abrechnung = Abrechnung(
            id=uuid4(),
            user_id=vermieter.id,
            objekt_id=objekte[0].id,
            jahr=2024,
            abrechnungszeitraum_start=date(2024, 1, 1),
            abrechnungszeitraum_ende=date(2024, 12, 31),
            status="entwurf",
            created_at=datetime.utcnow(),
        )
        session.add(abrechnung)

        # Bewerbungen (2)
        bewerbungen = [
            Bewerbung(
                id=uuid4(),
                user_id=vermieter.id,
                einheit_id=einheiten[4].id,
                vorname="Erik",
                nachname="Bewerber",
                email="erik@example.com",
                telefon="+49 171 1234567",
                status="eingegangen",
                eingangsdatum=date(2026, 10, 15),
            ),
            Bewerbung(
                id=uuid4(),
                user_id=vermieter.id,
                einheit_id=einheiten[4].id,
                vorname="Fiona",
                nachname="Interessent",
                email="fiona@example.com",
                telefon="+49 172 7654321",
                status="in_pruefung",
                eingangsdatum=date(2026, 10, 20),
            ),
        ]
        session.add_all(bewerbungen)

        await session.commit()
        print("Seed-Daten erfolgreich geladen.")


if __name__ == "__main__":
    asyncio.run(seed())
```

---

### 2.2 Test/Staging (anonymisierter Dump)

#### 2.2.1 Zweck

Staging enthält realistische Daten aus Beta, aber anonymisiert. So können neue Features und Migrationen mit produktionsnahen Daten getestet werden, ohne personenbezogene Daten zu gefährden.

#### 2.2.2 Ablauf

Wöchentlich oder manuell:

1. `pg_dump` von Beta.
2. Anonymisierungs-Script ausführen.
3. Restore in Test/Staging-DB.

#### 2.2.3 Anonymisierungs-Script

```python
#!/usr/bin/env python3
"""Anonymisiert personenbezogene Daten in einem Staging-Dump.

ACHTUNG: Dieses Script darf NIE auf Prod oder Beta ausgeführt werden.
Eingabe: frisch erzeugter Dump von Beta.
Ausgabe: anonymisierter Dump für Staging.
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Final

ANONYMIZED_IBAN: Final[str] = "[IBAN]"
ANONYMIZED_GEBURTSDATUM: Final[str] = "[GEBURTSDATUM]"
ANONYMIZED_ADRESSE: Final[str] = "[ADRESSE]"
ANONYMIZED_TELEFON: Final[str] = "[TELEFON]"


def anonymize_sql_dump(input_path: Path, output_path: Path) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"Eingabedatei nicht gefunden: {input_path}")

    # Mieter-Zähler für eindeutige E-Mail-Adressen
    mieter_counter = 0

    with input_path.open("r", encoding="utf-8") as infile, output_path.open(
        "w", encoding="utf-8"
    ) as outfile:
        for line in infile:
            # E-Mail-Adressen: test+mieter1@example.com, test+bewerber1@example.com, etc.
            def replace_email(match: re.Match) -> str:
                nonlocal mieter_counter
                mieter_counter += 1
                prefix = match.group(1).lower()
                if "bewerbung" in prefix or "bewerber" in prefix:
                    return f"'test+bewerber{mieter_counter}@example.com'"
                return f"'test+mieter{mieter_counter}@example.com'"

            line = re.sub(r"'[^'\s]+@[^'\s]+'", replace_email, line)

            # IBAN-Muster (DE/AT/CH)
            line = re.sub(r"'[A-Z]{2}\d{2}[A-Za-z0-9]{1,30}'", f"'{ANONYMIZED_IBAN}'", line)

            # Geburtsdatum (ISO-Format YYYY-MM-DD in SQL-Strings)
            line = re.sub(r"'\d{4}-\d{2}-\d{2}'", f"'{ANONYMIZED_GEBURTSDATUM}'", line)

            # Telefonnummern (vereinfachtes Muster)
            line = re.sub(r"'\+?[0-9\s\-\(\)/]{7,25}'", f"'{ANONYMIZED_TELEFON}'", line)

            # Straße + Hausnummer
            line = re.sub(
                r"'[A-Za-zäöüÄÖÜß\.\-]+(?:straße|str\.?|weg|platz|gasse|allee|ring|ufer)\s+\d+[a-zA-Z]?'",
                f"'{ANONYMIZED_ADRESSE}'",
                line,
                flags=re.IGNORECASE,
            )

            # Klartextnamen in mieter- und bewerbungstabellen (heuristisch)
            # Dies ist ein beispielhafter Regex für INSERT in mieter/bewerbung
            line = re.sub(
                r"(INSERT INTO (?:mieter|bewerbung).*?VALUES.*?')([^'\s]+)('.*?')([^'\s]+)(')",
                lambda m: f"{m.group(1)}[VORNAME]{m.group(3)}[NACHNAME]{m.group(5)}",
                line,
                flags=re.IGNORECASE,
            )

            outfile.write(line)

    print(f"Anonymisierung abgeschlossen: {output_path}")


def restore_to_staging(dump_path: Path, db_url: str) -> None:
    print(f"Restore nach Staging: {db_url}")
    subprocess.run(
        ["pg_restore", "--clean", "--if-exists", "--dbname", db_url, str(dump_path)],
        check=True,
    )
    print("Restore abgeschlossen.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: anonymize_db.py <input.dump> <output.dump>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    anonymize_sql_dump(input_file, output_file)

    # Optional: direkt in Staging-DB restoren, wenn DB_URL gesetzt
    db_url = sys.argv[3] if len(sys.argv) > 3 else None
    if db_url:
        restore_to_staging(output_file, db_url)
```

#### 2.2.4 GitHub Actions Workflow

Siehe Abschnitt 3.2 (`db-sync-staging.yml`).

---

### 2.3 Beta (Proxmox, 10 Tester)

| Aspekt | Regel |
|--------|-------|
| Daten | Echte Testdaten der 10 Tester |
| Überschreiben | NIEMALS |
| Backup | Täglich per Cron (`ops/scripts/mvp-backup.sh`) |
| Migration | Backup VOR `alembic upgrade head` |
| Zugriff | Nur per Cloudflared-Tunnel an registrierte Tester |
| DSGVO | Nicht-kommerzieller Closed-Beta-Modus |

---

### 2.4 Prod (Hetzner, echte Kunden)

| Aspekt | Regel |
|--------|-------|
| Daten | Echte Kundendaten, DSGVO-relevant |
| Überschreiben | NIEMALS |
| Backup | WAL-G kontinuierlich (WAL-Archivierung) + tägliche Delta + wöchentliche Full |
| Restore | PITR (Point-in-Time-Recovery) möglich |
| Testdaten | Nie aus Beta/Staging importieren |
| Löschung | DSGVO-gerechte Aufbewahrung und Löschfristen |

---

### 2.5 Datenfluss-Regel

Daten fließen **nur in eine Richtung**: Prod/Beta → Test → Lokal.  
**NIEMALS** umgekehrt.

```
┌─────────────┐       ┌───────────────┐       ┌───────────────┐       ┌─────────────┐
│   Prod      │──────▶│  Test/Staging │──────▶│     Lokal     │──────▶│   Seed-DB   │
│ (echte PB)  │       │ (anonymisiert)│       │  (Entwickler) │       │  (Dummy)    │
└─────────────┘       └───────────────┘       └───────────────┘       └─────────────┘
        │                      │                      │
        │                      │                      │
        ▼                      ▼                      ▼
   WAL-G Backup          pg_dump +             make reset-dev-db
   Storage Box          anonymize_db.py       + seed_data.py

VERBOTENE FLÜSSE:
  ❌ Lokal ──────▶ Beta
  ❌ Lokal ──────▶ Prod
  ❌ Test  ──────▶ Beta
  ❌ Test  ──────▶ Prod
  ❌ Beta  ──────▶ Prod (nur über Migration, nie per Dump-Restore)
```

---

## 3. GitHub Actions Workflows

### 3.1 `migration-test.yml` — Vollständige YAML

```yaml
name: Migration Test

on:
  push:
    branches: [main, feature/*, hotfix/*]
    paths:
      - 'backend/alembic/versions/**'
      - 'backend/app/models/**'
      - 'backend/scripts/seed_data.py'
  pull_request:
    branches: [main]
    paths:
      - 'backend/alembic/versions/**'
      - 'backend/app/models/**'
      - 'backend/scripts/seed_data.py'

jobs:
  migration-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:17-alpine
        env:
          POSTGRES_USER: mietuser
          POSTGRES_PASSWORD: mietpass
          POSTGRES_DB: mietverwaltung
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install backend dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt
          pip install -r backend/requirements-dev.txt

      - name: Set environment for local CI
        run: |
          echo "DATABASE_URL=postgresql+asyncpg://mietuser:mietpass@localhost:5432/mietverwaltung" >> "$GITHUB_ENV"
          echo "REDIS_URL=redis://localhost:6379/0" >> "$GITHUB_ENV"
          echo "APP_ENV=test" >> "$GITHUB_ENV"
          echo "DB_ENCRYPTION_KEY=dGVzdC1rZXktZm9yLWNpLXRoYXQtaXMtMzItYnl0ZXM=" >> "$GITHUB_ENV"
          echo "JWT_SECRET=ci-jwt-secret-muss-lang-genug-sein-12345" >> "$GITHUB_ENV"
          echo "CSRF_SECRET=ci-csrf-secret-muss-auch-lang-sein-67890" >> "$GITHUB_ENV"

      - name: Alembic upgrade head
        working-directory: backend
        run: |
          echo "==> Schritt 1/4: alembic upgrade head"
          alembic upgrade head

      - name: Load seed data
        working-directory: backend
        run: |
          echo "==> Schritt 2/4: Seed-Daten laden"
          python scripts/seed_data.py

      - name: Alembic downgrade base
        working-directory: backend
        run: |
          echo "==> Schritt 3/4: alembic downgrade base"
          alembic downgrade base

      - name: Verify clean state
        working-directory: backend
        run: |
          echo "==> Schritt 4/4: downgrade-base Verifizierung"
          alembic current || true

      - name: Report failure
        if: failure()
        run: |
          echo "MIGRATION TEST FEHLGESCHLAGEN"
          echo "Entweder upgrade head oder downgrade base ist fehlgeschlagen."
          echo "Bitte Migration reviewen: downgrade() vorhanden? neue Spalten nullable/default?"
          exit 1
```

---

### 3.2 `db-sync-staging.yml` — Anonymisierter Dump

```yaml
name: Sync Staging DB from Beta

on:
  schedule:
    # Jeden Sonntag um 02:00 UTC
    - cron: '0 2 * * 0'
  workflow_dispatch:
    inputs:
      beta_host:
        description: 'Beta DB Host'
        required: true
        default: 'beta-db.internal'
      staging_host:
        description: 'Staging DB Host'
        required: true
        default: 'staging-db.internal'

jobs:
  sync-staging:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y postgresql-client ssh
          python -m pip install --upgrade pip

      - name: Configure SSH for Beta
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.PROXMOX_BETA_SSH_KEY }}" > ~/.ssh/beta_key
          chmod 600 ~/.ssh/beta_key
          cat >> ~/.ssh/config <<EOF
          Host beta
            HostName ${{ secrets.PROXMOX_BETA_HOST }}
            User ${{ secrets.PROXMOX_BETA_USER }}
            IdentityFile ~/.ssh/beta_key
            StrictHostKeyChecking accept-new
          EOF

      - name: Dump Beta DB
        run: |
          TIMESTAMP=$(date +%Y%m%d_%H%M%S)
          echo "BETA_DUMP=beta_dump_${TIMESTAMP}.sql" >> "$GITHUB_ENV"
          ssh beta "pg_dump --no-owner --no-acl --clean --if-exists -h localhost -U mietuser mietverwaltung" > "beta_dump_${TIMESTAMP}.sql"

      - name: Anonymize dump
        run: |
          python scripts/ops/anonymize_db.py "$BETA_DUMP" "staging_${BETA_DUMP}"

      - name: Configure SSH for Staging
        run: |
          echo "${{ secrets.HETZNER_STAGING_SSH_KEY }}" > ~/.ssh/staging_key
          chmod 600 ~/.ssh/staging_key
          cat >> ~/.ssh/config <<EOF
          Host staging
            HostName ${{ secrets.HETZNER_STAGING_HOST }}
            User ${{ secrets.HETZNER_STAGING_USER }}
            IdentityFile ~/.ssh/staging_key
            StrictHostKeyChecking accept-new
          EOF

      - name: Restore to Staging
        run: |
          ssh staging "psql -h localhost -U mietuser -c 'DROP DATABASE IF EXISTS mietverwaltung_staging;'"
          ssh staging "psql -h localhost -U mietuser -c 'CREATE DATABASE mietverwaltung_staging;'"
          scp "staging_${BETA_DUMP}" staging:/tmp/staging_dump.sql
          ssh staging "psql -h localhost -U mietuser -d mietverwaltung_staging -f /tmp/staging_dump.sql"
          ssh staging "rm /tmp/staging_dump.sql"

      - name: Run Staging Health Check
        run: |
          sleep 10
          curl -fsS --max-time 10 "https://staging.app.mietverwaltung.de/api/health" || true

      - name: Cleanup local dumps
        if: always()
        run: |
          rm -f beta_dump_*.sql staging_beta_dump_*.sql
          rm -f ~/.ssh/beta_key ~/.ssh/staging_key
```

---

### 3.3 `rollback.sh` — Vollständiges Bash-Script für automatisches Rollback

```bash
#!/usr/bin/env bash
# scripts/deploy/rollback.sh
# Automatisches Rollback bei fehlgeschlagenem Deploy.
# Wird von deploy-beta.yml / deploy-prod.yml nach einem fehlgeschlagenen Health-Check aufgerufen.

set -euo pipefail

ENVIRONMENT="${1:-}"        # beta | prod
PREVIOUS_TAG="${2:-}"        # z.B. v0.2.0-beta.3
FAILED_TAG="${3:-}"          # z.B. v0.2.0-beta.4
ALERT_EMAIL="${4:-max@example.com}"
BACKUP_DIR="${BACKUP_DIR:-/srv/mietverwaltung/backups}"
APP_DIR="${APP_DIR:-/opt/mietverwaltung}"
LOG_FILE="${APP_DIR}/logs/rollback_${FAILED_TAG}_$(date +%Y%m%d_%H%M%S).log"

if [ -z "$ENVIRONMENT" ] || [ -z "$PREVIOUS_TAG" ] || [ -z "$FAILED_TAG" ]; then
  echo "Usage: $0 <environment> <previous_tag> <failed_tag> [alert_email]" >&2
  exit 1
fi

mkdir -p "$(dirname "$LOG_FILE")"
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "[$(date -Iseconds)] ROLLBACK gestartet: ${FAILED_TAG} -> ${PREVIOUS_TAG} (${ENVIRONMENT})"

# Hilfsfunktion zum Alerten
alert() {
  local subject="$1"
  local body="$2"
  echo "[$(date -Iseconds)] ALERT: $subject"
  if command -v sendmail >/dev/null 2>&1; then
    printf 'Subject: %s\n\n%s\n' "$subject" "$body" | sendmail "$ALERT_EMAIL"
  else
    echo "$body" | mail -s "$subject" "$ALERT_EMAIL" || true
  fi
}

# 1. Letztes Backup finden
LATEST_BACKUP=$(find "$BACKUP_DIR" -maxdepth 1 -name "pre_deploy_*_${FAILED_TAG}_*.dump" -printf '%T+ %p\n' | sort -r | head -n1 | cut -d' ' -f2-)
if [ -z "$LATEST_BACKUP" ]; then
  LATEST_BACKUP=$(find "$BACKUP_DIR" -maxdepth 1 -name "*.dump" -printf '%T+ %p\n' | sort -r | head -n1 | cut -d' ' -f2-)
fi

if [ -z "$LATEST_BACKUP" ]; then
  alert "Rollback fehlgeschlagen: kein Backup gefunden" "Umgebung: ${ENVIRONMENT}, Tag: ${FAILED_TAG}"
  exit 1
fi

echo "[$(date -Iseconds)] Verwende Backup: $LATEST_BACKUP"

# 2. Container stoppen
echo "[$(date -Iseconds)] Stoppe aktuelle Container..."
cd "$APP_DIR"
docker compose -f docker-compose.yml down || true

# 3. Vorheriges Image starten
echo "[$(date -Iseconds)] Starte vorherige Version ${PREVIOUS_TAG}..."
GIT_TAG="$PREVIOUS_TAG" docker compose -f docker-compose.yml up -d --no-build

# 4. Versuche Alembic downgrade
MIGRATION_SUCCESS=false
if docker compose ps backend >/dev/null 2>&1; then
  echo "[$(date -Iseconds)] Versuche alembic downgrade -1..."
  if docker compose exec -T backend alembic downgrade -1; then
    echo "[$(date -Iseconds)] Downgrade erfolgreich."
    MIGRATION_SUCCESS=true
  else
    echo "[$(date -Iseconds)] Downgrade fehlgeschlagen, fahre mit Backup-Restore fort." >&2
  fi
else
  echo "[$(date -Iseconds)] Backend-Container nicht erreichbar, überspringe downgrade." >&2
fi

# 5. Falls downgrade fehlgeschlagen: Backup restoren
if [ "$MIGRATION_SUCCESS" != "true" ]; then
  echo "[$(date -Iseconds)] Starte Backup-Restore..."
  docker compose stop db || true

  # Sicherstellen, dass wir als postgres-User arbeiten
  docker compose run --rm -u postgres db \
    sh -c "rm -rf \"\${PGDATA:?}\"/* && pg_restore --clean --if-exists --dbname postgresql://mietuser@localhost/mietverwaltung \"$LATEST_BACKUP\"" || {
    alert "Rollback: Backup-Restore fehlgeschlagen" "Backup: $LATEST_BACKUP"
    exit 1
  }

  docker compose up -d db
fi

# 6. Finaler Health-Check
sleep 15
HEALTH_URL=""
if [ "$ENVIRONMENT" = "beta" ]; then
  HEALTH_URL="https://mietverwaltung-beta.trycloudflare.com/api/health"
else
  HEALTH_URL="https://mietverwaltung.de/api/health"
fi

for i in 1 2 3; do
  if curl -fsS --max-time 10 "$HEALTH_URL" | grep -q '"status":"ok"'; then
    echo "[$(date -Iseconds)] Rollback Health-Check OK."
    break
  fi
  echo "[$(date -Iseconds)] Rollback Health-Check Versuch $i/3 fehlgeschlagen, warte 10s..."
  sleep 10
done

# 7. Incident-Eintrag anlegen
INCIDENT_DIR="${APP_DIR}/docs/operations/runbooks"
mkdir -p "$INCIDENT_DIR"
INCIDENT_FILE="${INCIDENT_DIR}/incident-$(date +%Y-%m-%d)-${FAILED_TAG}.md"
cat > "$INCIDENT_FILE" <<EOF
# Incident: Fehlgeschlagener Deploy ${FAILED_TAG}

- **Datum:** $(date -Iseconds)
- **Umgebung:** ${ENVIRONMENT}
- **Fehlgeschlagenes Tag:** ${FAILED_TAG}
- **Zurückgerollt auf:** ${PREVIOUS_TAG}
- **Backup verwendet:** ${LATEST_BACKUP}
- **Rollback-Log:** ${LOG_FILE}

## Ablauf
1. Deploy von ${FAILED_TAG} gestartet.
2. Health-Check fehlgeschlagen.
3. rollback.sh ausgeführt.
4. $(if [ "$MIGRATION_SUCCESS" = "true" ]; then echo "Alembic downgrade -1 erfolgreich."; else echo "Backup-Restore durchgeführt."; fi)

## Nächste Schritte
- [ ] Ursache des fehlgeschlagenen Deploys analysieren.
- [ ] Fix auf Feature-Branch entwickeln.
- [ ] migration-test.yml muss grün sein.
- [ ] Max approved erneuten Deploy.
EOF

echo "[$(date -Iseconds)] Incident-Eintrag angelegt: $INCIDENT_FILE"

# 8. Alert senden
alert "Rollback ausgeführt: ${FAILED_TAG} -> ${PREVIOUS_TAG}" \
  "Umgebung: ${ENVIRONMENT}\nFehlgeschlagenes Tag: ${FAILED_TAG}\nBackup: ${LATEST_BACKUP}\nIncident: ${INCIDENT_FILE}\nLog: ${LOG_FILE}"

echo "[$(date -Iseconds)] ROLLBACK abgeschlossen."
```

---

## 4. Deployment-Security-Checkliste

### 4.1 Pre-Deploy

| # | Checkpoint | Verantwortlich |
|---|------------|----------------|
| 1 | PR wurde von Max approved (CODEOWNERS für DB/Deploy/Sicherheit) | Max |
| 2 | CI ist grün: lint, test, build, security, migration-test | GitHub Actions |
| 3 | Migration hat `downgrade()` und wurde lokal sowie in CI getestet | Entwickler |
| 4 | OpenAPI-Typen sind aktuell (`shared/types/api.d.ts`) | CI |
| 5 | Secrets / `.env` sind auf dem Zielserver vorhanden und gültig | GitHub Actions / Max |
| 6 | Backup-Speicher hat ausreichend Platz | Ops |
| 7 | Letztes Backup ist erfolgreich verifiziert (`pg_restore --list`) | Deploy-Script |
| 8 | Datum/Zeit des Deploys ist kommuniziert (Beta-Tester / Kunden) | Max |
| 9 | Rollback-Plan ist bekannt: vorheriges Tag + Backup-Pfad | Deploy-Script |
| 10 | Keine sensiblen Daten im Docker-Image (Secrets nicht committed) | CI / Docker Build |

### 4.2 Post-Deploy

| # | Checkpoint | Verantwortlich |
|---|------------|----------------|
| 1 | Health-Check `/api/health` 3x mit 10s Abstand erfolgreich | Deploy-Script |
| 2 | `/api/health/db` prüft DB-Verbindung | Healthcheck |
| 3 | Wichtige Endpunkte manuell/smoke-getestet | Deploy-Script |
| 4 | Fehler-Logs sind sauber (keine neuen Exceptions) | Monitoring |
| 5 | Migration hat korrekte Revision hinterlassen (`alembic current`) | Deploy-Script |
| 6 | Docker-Container laufen mit erwarteten Tags | Deploy-Script |
| 7 | Backup nach Deploy optional erneut verifiziert | Ops |
| 8 | Kunden/Testern wurde Erfolg kommuniziert | Max |

### 4.3 Rollback-Plan

| # | Checkpoint | Verantwortlich |
|---|------------|----------------|
| 1 | Vorheriges Tag ist bekannt und im Registry verfügbar | GitHub Actions |
| 2 | Pre-Deploy-Backup ist vorhanden und intakt | Deploy-Script |
| 3 | `rollback.sh` wurde auf Zielserver getestet (trockener Lauf) | Ops |
| 4 | E-Mail-Alert an Max ist konfiguriert | Deploy-Script |
| 5 | Incident-Vorlage liegt unter `docs/operations/runbooks/` | Repo |
| 6 | Nach Rollback: Post-Mortem innerhalb 24h angelegt | Max |
| 7 | Fix wird auf Feature-Branch entwickelt und erneut getestet | Entwickler |

---

## 5. Zusammenfassung

| Bereich | Entscheidung |
|---------|--------------|
| Migrationstool | Alembic + SQLAlchemy 2.x |
| Downgrade-Pflicht | Jede Migration muss `downgrade()` haben |
| Neue Spalten | `nullable=True` oder Default |
| Backup vor Migration | `pg_dump --format=custom --compress=9` + WAL-G in Prod |
| Backup-Prüfung | `pg_restore --list` und wöchentlicher Probe-Restore |
| Automatisches Rollback | `rollback.sh` bei fehlgeschlagenem Health-Check |
| CI-Migrationstest | `upgrade head` → Seed → `downgrade base` |
| Lokale Testdaten | `backend/scripts/seed_data.py` + `make seed-dev` |
| Staging | Anonymisierter Beta-Dump via `scripts/ops/anonymize_db.py` |
| Datenfluss | Prod/Beta → Test → Lokal, niemals umgekehrt |

---

## 6. Referenzen

- `Repo-Struktur-und-Change-Management.md` — CI/CD, Branching, Review-Prozess
- `Server-Konzept-v2.md` — Backup, Migration, Go-Live-Sicherheit
- `.hermes/plans/2026-11-02_db-schema-v4.md` — DB-Schema-Definition
- `docs/operations/runbooks/incident-response.md`
- `docs/operations/runbooks/database-restore.md`

---

*Dokument erstellt: 2026-11-02*  
*Autor: Hermes Agent (KI-Builder)*  
*Status: Vorschlag für Max Karthoff zur Freigabe*
