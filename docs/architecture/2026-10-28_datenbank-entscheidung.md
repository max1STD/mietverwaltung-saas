# MietVerwaltung — Datenbank-Entscheidung

> **Erstellt:** 28. Oktober 2026
> **Frage:** Welche Datenbank? Selbst bauen (MySQL/PostgreSQL) oder Anbieter einbinden?

---

## Unsere Anforderung an die Datenbank

| Anforderung | Warum | Priorität |
|-------------|-------|-----------|
| **Multi-Tenant (RLS)** | Jeder Vermieter sieht nur seine Daten — Isolation auf DB-Ebene | ⭐⭐⭐⭐⭐⭐ |
| **DSGVO / EU-Hosting** | Daten dürfen DACH nicht verlassen — Art. 44 DSGVO | ⭐⭐⭐⭐⭐⭐ |
| **AES-256 Feld-Verschlüsselung** | IBAN, Geburtstag, Steuernr. verschlüsselt in DB | ⭐⭐⭐⭐⭐⭐ |
| **Audit-Log (revisionssicher)** | Wer hat was wann geändert — für Banken/GoBD | ⭐⭐⭐⭐⭐ |
| **JSONB-Spalten** | trigger.condition, trigger.perform, events.payload, ai_stored_results.result | ⭐⭐⭐⭐ |
| **Async / Connection Pooling** | FastAPI ist async — DB muss async können | ⭐⭐⭐⭐ |
| **Volltextsuche** | Tickets durchsuchen (inkl. Anhänge) | ⭐⭐⭐ |
| **Migrationen** | DB-Schema v3 (30 Tabellen) muss migrierbar sein | ⭐⭐⭐⭐ |
| **Backup / Restore** | Tägliche Backups, Point-in-Time-Recovery | ⭐⭐⭐⭐ |
| **Skalierung** | Start: 100 User → Ziel: 10.000+ User | ⭐⭐⭐ |
| **Preis** | Start klein, wächst mit | ⭐⭐⭐ |
| **Docker-kompatibel** | Läuft in Docker-Compose auf Hetzner | ⭐⭐⭐⭐⭐ |
| **Python-kompatibel** | FastAPI + SQLAlchemy + Alembic | ⭐⭐⭐⭐⭐⭐ |

---

## Option 1: PostgreSQL selbst gehostet (EMPFOHLEN) ✅

### Was
PostgreSQL 17 auf unserem Hetzner-Server (Docker-Container), verwaltet von uns.

### Warum perfekt für uns

| Vorteil | Erklärung |
|----------|-----------|
| **RLS (Row-Level Security)** | PostgreSQL hat RLS BUILT-IN — `CREATE POLICY ... USING (vermieter_id = current_setting('app.user_id'))`. Kein anderer Anbieter hat das so gut. |
| **JSONB** | PostgreSQL hat den besten JSONB-Support aller Datenbanken — perfekt für unsere `trigger.condition`, `events.payload`, `ai_stored_results.result` |
| **DSGVO** | Selbst gehostet auf Hetzner (DE) → Daten verlassen nie die EU |
| **Verschlüsselung** | `pgcrypto` Extension für AES-256 direkt in der DB |
| **Volltextsuche** | Built-in `tsvector` + `tsquery` — braucht keine Extra-Software |
| **Migrationen** | Alembic (Python) — perfekt für FastAPI |
| **Async** | `asyncpg` — fastest Python PostgreSQL driver, async nativ |
| **Docker** | Offizielles PostgreSQL Docker Image — `docker compose up db` |
| **Preis** | **0€** — läuft auf unserem Hetzner-Server, kein extra Anbieter |
| **Skalierung** | Start: 1 Container auf CX32 → später: Read-Replicas + Connection Pooling |
| **Audit-Log** | PostgreSQL Triggers für Audit-Logs — automatisches Logging auf DB-Ebene |
| **Backup** | `pg_dump` + `pgBackRest` — inkrementelle Backups, Point-in-Time |
| **Reif** | PostgreSQL 17 ist die am häufigsten genutzte DB für SaaS weltweit |

### Nachteile
- Wir müssen Backups/Updates selbst machen
- Kein automatisches Failover (bis wir Replikas aufbauen)
- Bei Server-Ausfall: DB down (bis HA-Setup)

### Stack
```
docker-compose.yml:
  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_DB: mietverwaltung
      POSTGRES_USER: mv_admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./init:/docker-entrypoint-initdb.d  # RLS, Extensions, etc.
    healthcheck:
      test: pg_isready -U mv_admin
```

### Extensions die wir aktivieren
```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;     -- AES-256 Verschlüsselung
CREATE EXTENSION IF NOT EXISTS pg_trgm;       -- Fuzzy-Suche (Namen finden)
CREATE EXTENSION IF NOT EXISTS unaccent;       -- Umlaut-Suche (Müller = Muller)
```

---

## Option 2: PostgreSQL als Managed Service (Alternative)

### Anbieter im Vergleich

| Anbieter | Preis (klein) | Region | DSGVO? | RLS? | JSONB? | Backup? | Veredict |
|-----------|----------------|--------|---------|-----|--------|---------|---------|
| **Hetzner Managed PostgreSQL** | ab 4,80€/Mo | DE (Falkenstein) | ✅ | ✅ | ✅ | ✅ Automatisch | ⭐ Beste Option |
| **Supabase** | Free 500MB → 25€/Mo | EU (Frankfurt) | ✅ | ✅ | ✅ | ✅ | ⭐ Gute Alternative |
| **Neon** | Free 0,5GB → 19€/Mo | EU (Frankfurt) | ✅ | ❌ | ✅ | ✅ | OK aber kein RLS |
| **Railway** | ab 5€/Mo | EU (Frankfurt) | ✅ | ✅ | ✅ | ✅ | OK |
| **Aiven** | ab 15€/Mo | EU ( Helsinki) | ✅ | ✅ | ✅ | ✅ | Teuer |
| **DigitalOcean Managed PG** | ab 15€/Mo | EU (Frankfurt) | ✅ | ✅ | ✅ | ✅ | OK |

### Hetzner Managed PostgreSQL (beste Managed-Option)
- **Vorteil:** Auf unserem Server + Managed = wir müssen uns um nichts kümmern
- **Preis:** ab 4,80€/Mo für 1GB RAM + 5GB Storage
- **DSGVO:** Hosting in Falkenstein (DE) ✅
- **Backup:** Automatisch tögliche + Point-in-Time
- **Problem:** Hetzner hat erst seit 2024 Managed PostgreSQL — noch nicht so reif wie AWS RDS

### Supabase (interessant aber Overhead)
- **Vorteil:** Auth + Storage + Realtime BUILT-IN — wir bräuchten kein separates Auth-System
- **Preis:** Free 500MB → Pro 25€/Mo
- **DSGVO:** Frankfurt-Region verfügbar ✅
- **Problem:** Supabase ist PostgreSQL + viel Extra-Zeug. Wir haben schon FastAPI für Auth. Das wäre Redundant.
- **Problem:** RLS geht bei Supabase über deren Policy-Editor, nicht über nativ PostgreSQL-RLS

---

## Option 3: MySQL (NICHT EMPFOHLEN) ❌

### Warum nicht MySQL

| Grund | Erklärung |
|-------|-----------|
| **Kein RLS** | MySQL hat kein nativ Row-Level Security — wir müssten alles in der App logik machen |
| **JSONB schwächer** | MySQL JSON-Support ist gut aber nicht so stark wie PostgreSQL JSONB (kein GIN-Index, schwächer Query) |
| **Kein pgcrypto** | AES-256 müssten in der App machen statt in der DB |
| **Volltextsuche schwächer** | MySQL FULLTEXT ist OK aber nicht so flexibel wie tsvector |
| **Async schwächer** | `aiomysql` ist weniger reif als `asyncpg` |
| **Migrations** | Alembic unterstützt MySQL, aber weniger gut als PostgreSQL |
| **Konsens** | MySQL ist kommerziell (Oracle), PostgreSQL ist Open-Source + Community-getrieben |

---

## Option 4: SQLite (NICHT EMPFOHLEN) ❌

### Warum nicht SQLite

| Grund | Erklärung |
|-------|-----------|
| **Kein RLS** | SQLite hat kein Row-Level Security |
| **Keine nebenläufige Schreibt** | SQLite sperrt die DB bei Schreibt — FastAPI async bringt nichts |
| **Keine Skalierung** | SQLite ist für single-Server, nicht für SaaS |
| **Trotzdem gesehen:** mietfuchs und NebenkostenFix nutzen SQLite — aber das sind single-User-Apps, keine Multi-Tenant-SaaS |

---

## Option 5: Cloud-Datenbanken wie Firebase, PlanetScale, DynamoDB (NICHT EMPFOHLEN) ❌

### Warum nicht

| Grund | Erklärung |
|-------|-----------|
| **Nicht relational** | Wir brauchen relatione Joins (mieter → vertraege → einheiten → objekt) |
| **Kein SQL** | Firestore/DynamoDB sind NoSQL — unsere 30 Tabellen mit Joins passen nicht |
| **Vendor Lock-in** | Migration weg von NoSQL zu relational ist extrem schwer |
| **DSGVO** | Firebase = US (Google), DynamoDB = US (AWS) — Daten verlassen EU |

---

## EMPFOHLUNG

### Phase 1 (MVP-Launch): PostgreSQL selbst gehostet

```
Server: Hetzner CX32 (Backend + DB in einem Container)
Datenbank: PostgreSQL 17 in Docker
Backup: tögliche pg_dump + Hetzner Storage Box
Preis: 0€ extra (läuft auf unserem Server)
```

**Warum:**
- 0€ extra Kosten
- Volle Kontrolle (RLS, Extensions, pgcrypto)
- DSGVO: Daten auf unserem Server in DE
- Wir lernen die DB kennen (für späteres Skalieren)
- Kein Vendor-Lock-in

### Phase 2 (Wachstum 100+ User): PostgreSQL + Read-Replika

```
Server 1 (CX32): Backend + Primary DB
Server 2 (CX22): Read-Replika + Backup
Backup: pgBackRest (inkrementell)
Monitoring: Prometheus + Grafana
```

**Warum:**
- Read-Replica entlastet die Primary DB bei Lese-Lasten (Dashboard, Listen)
- Failover: Wenn Primary ausfallt → Replika wird Primary
- Kosten: +4,50€/Mo für CX22

### Phase 3 (Skalierung 1000+ User): Hetzner Managed PostgreSQL

```
Managed PostgreSQL (Hetzner Cloud)
High-Availability: Automatisch
Backup: Automatisch
Monitoring: Inklusive
Preis: ab 4,80€/Mo
```

**Warum:**
- Ab 1000+ User: wir wollen uns nicht mehr um Backups/Updates kümmern
- Hetzner Managed = wir zahlen, aber wir haben kein Ops-Team
- Migration von selbst gehostet → Managed ist sealmlos (selbe PostgreSQL)

---

## Entschiedungs-Matrix

| Kriterium | PostgreSQL selbst | PostgreSQL Managed | Supabase | MySQL | SQLite | Cloud NoSQL |
|-----------|-------------------|--------------------|------------|---------|----------|-------------|
| RLS | ✅ BUILT-IN | ✅ | ✅ (aber Editor) | ❌ | ❌ | ❌ |
| JSONB | ✅ Beste | ✅ | ✅ | 🟡 OK | ❌ | ❌ |
| DSGVO/EU | ✅ DE-Server | ✅ DE | ✅ EU | ✅ | ✅ | ❌ US |
| Verschlüsselung | ✅ pgcrypto | ✅ | ✅ | ❌ App | ❌ App | ❌ |
| Async | ✅ asyncpg | ✅ | ✅ | 🟡 | ❌ | ❌ |
| Preis (Start) | 0€ | ab 4,80€ | 0€→25€ | 0€ | 0€ | ab 5€ |
| Docker | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Migrationen | ✅ Alembic | ✅ | ✅ | ✅ | 🟡 | ❌ |
| Volle Kontrolle | ✅ | 🟡 | ❌ | ✅ | ✅ | ❌ |
| Backup | self | ✅ auto | ✅ auto | self | self | ✅ auto |
| Skalierung | Manual | ✅ auto | ✅ auto | Manual | ❌ | ✅ auto |
| Reif | ✅ | ✅ | 🟡 new | ✅ | ✅ | ✅ |

---

## Finale Empfohlenung

**PostgreSQL 17 selbst gehostet auf Hetzner (Docker) — Phase 1.**
- 0€ extra, volle Kontrolle, DSGVO, RLS, JSONB, pgcrypto, asyncpg
- Wechsel zu Managed ab Phase 3 (1000+ User) wenn wir kein Ops-Team haben

**NICHT:** MySQL (kein RLS), SQLite (keine nebenläufige Schreibt), Cloud-NoSQL (nicht relational, US-Hosting), Supabase (Overhead — wir haben schon FastAPI-Auth).

---

**Entscheidung:** PostgreSQL 17 selbst gehostet (Docker) — Start 0€, volle Kontrolle, DSGVO-konform
**Migration-Pfad:** selbst → +Replika (100+ User) → Hetzner Managed (1000+ User)