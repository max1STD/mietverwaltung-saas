# Pre-Build Architecture Review: API & Frontend

> **Projekt:** MietVerwaltung SaaS  
> **Review-Datum:** 2026-11-13  
> **Geprüfte Dokumente:**
> - `/root/mietverwaltung/Repo-Struktur-und-Change-Management.md`
> - `/root/mietverwaltung/UX-UI-Konzept-konsolidiert.md`
> - `/root/.hermes/skills/software-development/mietverwaltung-saas/references/ki-architecture.md`
> - `/root/mietverwaltung/KI-Konzept.md`
> - Bestehender Code unter `/root/mietverwaltung-saas/`

## Executive Summary

Das Konzept ist für den MVP **weitgehend vollständig**, der bestehende Code im Repository befindet sich jedoch noch im **Skeleton-Stadium**. Fast alle architektonischen Verträge (API-Routen, OpenAPI-Typen, Pinia-Stores, Komponenten-Hierarchie, Upload-Pipeline, Fehlerbehandlung, Paginierung, Tests) sind **dokumentiert, aber nicht implementiert**. Der Build kann erst starten, nachdem diese Lücken in einem aktualisierten Build-Plan adressiert wurden.

---

## 1. API-Design

### 1.1 Konzept vs. Implementierung

| Ebene | Status |
|-------|--------|
| API-Versionierung (`/api/v1/…`) | ✅ Konzept definiert, im Code teilweise umgesetzt (`/api/v1/auth`) |
| Route-Module für Domänen | ✅ 15 Module in `Repo-Struktur-und-Change-Management.md` definiert |
| Tatsächlich implementierte Routen | ❌ Nur `auth.py` und `health.py` existieren; alle anderen sind leere TODOs |

### 1.2 Abdeckung der 33 DB-Tabellen durch Routen

Das DB-Schema v4 umfasst 33 Tabellen. Die geplanten Route-Module decken nicht alle tabellennahen Ressourcen ab:

| Tabelle | Geplante Route | Lücke |
|---------|----------------|-------|
| `users` | `users.py` | ✅ abgedeckt |
| `user_sessions` | `auth.py` / `users.py` | ⚠️ implicit, aber keine eigenen Endpunkte dokumentiert |
| `einwilligungen` | `auth.py` / `dsgvo.py` | ⚠️ implicit |
| `audit_logs` | keine eigene Route | ❌ Admin-Center fehlt komplett |
| `subscriptions`, `plan_usage` | `subscriptions.py` | ✅ abgedeckt |
| `bankverbindungen` | nicht explizit | ❌ fehlendes Modul; gehört zu Vermieter-Profil |
| `objekte` | `objekte.py` | ✅ abgedeckt |
| `einheiten` | `einheiten.py` | ✅ abgedeckt |
| `einheit_ausstattung` | `einheiten.py` | ⚠️ sub-Ressource, aber keine Detaildoku |
| `mieter_historie` | `mieter.py` / `einheiten.py` | ⚠️ implicit |
| `bewerbungen` | `mieter.py` | ⚠️ implicit, braucht eigene Endpunkte |
| `mieter` | `mieter.py` | ✅ abgedeckt |
| `mietvertraege` | `mietvertraege.py` | ✅ abgedeckt |
| `mietvertrag_aenderungen` | `mietvertraege.py` | ⚠️ implicit |
| `kostenkategorien` | `kosten.py` | ⚠️ Referenzdaten, kaum dokumentiert |
| `kosten` | `kosten.py` | ✅ abgedeckt |
| `abrechnungen`, `abrechnung_positionen` | `abrechnungen.py` | ✅ abgedeckt (Positionen als Sub-Ressource) |
| `dokumente`, `dokument_freigaben` | `dokumente.py` | ⚠️ Freigaben implicit |
| `tickets`, `ticket_kommentare` | `tickets.py` | ⚠️ Kommentare implicit |
| `ticket_sla`, `ticket_trigger` | `tickets.py` | ❌ SLA/Trigger-Endpunkte nicht definiert |
| `mietzahlungen` | keine eigene Route | ❌ fehlendes Modul |
| `events` | keine eigene Route | ⚠️ interne Queue, akzeptabel |
| `notifications` | `notifications.py` | ✅ abgedeckt |
| `fristen` | keine eigene Route | ❌ fehlendes Modul; nötig für Dashboard/Calendar |
| `onboarding_progress` | `users.py` / `auth.py` | ⚠️ implicit |
| `ai_stored_results` | keine öffentliche Route | ✅ intern, akzeptabel |
| `referrals` | keine Route | ❌ fehlt komplett |
| `handwerker` | keine Route | ⚠️ Roadmap, MVP-relevant? Nein |

### 1.3 Fehlende Endpunkte (kritisch)

Für den MVP fehlen dedizierte Endpunkte für:

1. **Mietzahlungen** (`/api/v1/mietzahlungen`) — essenziell für Cashflow-Tracking und Mahnwesen.
2. **Fristen** (`/api/v1/fristen`) — Kalender-Widget im Dashboard und Fristen-Monitoring.
3. **Bankverbindungen** (`/api/v1/bankverbindungen`) — IBAN-Verschlüsselung für SEPA/Überweisungen.
4. **Einwilligungen** (`/api/v1/einwilligungen`) — DSGVO-konforme Consent-Verwaltung.
5. **Bewerbungen** (`/api/v1/bewerbungen`) — Mieter-Bewerbung mit Ausweis/Lohnabrechnung/Schufa.
6. **Ticket-SLA & Trigger** — Konzept aus Zammad-Analyse, aber keine API-Endpunkte.
7. **Admin-Center-Endpunkte** — Sperren/Entsperren, Impersonate, Feature-Flags, KI-Kosten, E-Mail-Logs.
8. **KI-Post-Processing-Endpunkte** — `POST /ki/ticket-kategorie`, `POST /ki/beleg-scan`, `POST /ki/mahnung`, `POST /ki/smart-insights`, `POST /ki/antwort-entwurf`.
9. **Export-Endpunkte** — DATEV, CSV, XRechnung/ZUGFeRD (Admin-Center).

**Empfehlung:** Im Build-Plan für Phase 1 (Auth + Objektverwaltung) nur die notwendigen Endpunkte definieren; Fristen, Mietzahlungen und KI-Endpunkte in Phase 2/3 ergänzen.

---

## 2. OpenAPI-Typen-Synchronisation

| Aspekt | Status |
|--------|--------|
| `shared/openapi.json` | ❌ Nicht vorhanden; `shared/`-Ordner existiert nicht |
| `shared/types/api.d.ts` | ❌ Nicht vorhanden |
| `frontend/src/api/types/api.d.ts` | ❌ Nicht vorhanden; Frontend hat nur `main.ts` |
| Export-Skript `backend/scripts/export_openapi.py` | ❌ Nicht vorhanden |
| CI-Workflow `generate-api-types.yml` | ⚠️ Konzept beschrieben, aber nicht im Repo |
| Symlink/Kopie-Mechanismus Frontend ↔ shared | ⚠️ Konzept beschrieben, aber nicht umgesetzt |

### 2.1 Beobachtung

FastAPI erzeugt zwar automatisch `/openapi.json`, solange Pydantic-Schemas und Router registriert sind. Aktuell sind jedoch fast alle Router noch TODO-Stubs; das generierte OpenAPI wäre daher praktisch leer. Eine Build-Blockade "wenn `openapi.json` und `api.d.ts` nicht übereinstimmen" ist konzeptionell richtig, kann aber erst greifen, wenn die CI-Pipeline und das Generationsskript existieren.

### 2.2 Empfohlene Pipeline (konkret)

1. Alle Schemas in `backend/app/schemas/` anlegen.
2. `backend/scripts/export_openapi.py` erstellen (lädt `app.main:app`, exportiert `app.openapi()`).
3. `shared/openapi.json` und `shared/types/api.d.ts` generieren lassen.
4. Frontend importiert nur aus `shared/types/api.d.ts` (Symlink oder Copy-Schritt in `frontend/src/api/types`).
5. CI-Workflow `generate-api-types.yml` bei Änderungen in `backend/app/schemas/` oder `backend/app/routes/` auslösen.
6. Frontend-Build bricht bei Type-Mismatch — erst dann sinnvoll, wenn genügend Typen existieren.

---

## 3. Frontend-State-Management (Pinia)

| Aspekt | Status |
|--------|--------|
| Pinia als State-Management | ✅ In `main.ts` aktiviert (`app.use(createPinia())`) |
| Store-Dateien unter `frontend/src/stores/` | ❌ Ordner existiert nicht |
| Stores gemäß Konzept | ❌ Keine implementiert |

### 3.1 Konzeptuell geplante Stores

`Repo-Struktur-und-Change-Management.md` sieht folgende Stores vor:

- `auth.ts` — Login/Register/2FA, Tokens, Session-Status.
- `user.ts` — Profil, Einstellungen, Onboarding-Fortschritt.
- `objekte.ts` — Objekt-Liste, Detail, CRUD.
- `einheiten.ts` — Einheiten, Ausstattung, Mieter-Historie.
- `mieter.ts` — Mieter, Bewerbungen.
- `tickets.ts` — Tickets, Kommentare, SLA-Status.
- `kosten.ts` — Kosten, Belege, Umlage.
- `dashboard.ts` — KPIs, Smart Insights, Fristen.
- `notifications.ts` — Benachrichtigungen, Badges.
- `ui.ts` — Theme, Dark Mode, Modals, Toast-Queue.

### 3.2 Lücken

- Keine Store-Implementierungen vorhanden.
- Keine API-Client-Integration (`api/client.ts`, `api/interceptors.ts`) vorhanden.
- Keine Composables (`useAuth`, `useApi`, `useToast`) vorhanden.
- `HomeView.vue` ist ein statischer Platzhalter.

---

## 4. Komponenten-Architektur

| Aspekt | Status |
|--------|--------|
| Komponenten-Hierarchie im Konzept | ✅ Detailliert in `Repo-Struktur-und-Change-Management.md` |
| Tatsächliche Komponenten | ❌ Keine Komponenten vorhanden |
| Layout-Komponenten (Sidebar, TopBar, MobileNav) | ❌ Nicht vorhanden |
| Feature-Komponenten (Dashboard, Objekte, Tickets, Kosten, Dokumente, KI) | ❌ Nicht vorhanden |
| UI-Basis-Komponenten (Button, Input, Modal, Table, Badge, Toast) | ❌ Nicht vorhanden |

### 4.1 Konzeptueller Komponenten-Baum

```
App.vue
├── RouterView
│   ├── views/public/*      → Landing, Impressum, Datenschutz
│   ├── views/auth/*        → Login, Register, 2FA, Passwort-Reset
│   ├── views/vermieter/*   → Dashboard, Objekte, Mieter, Kosten, Tickets, Dokumente, Einstellungen, Plan, DSGVO
│   └── views/mieter/*      → Mieter-Dashboard, Tickets, Dokumente, Profil
└── (globale Komponenten)
    ├── KIAssistant.vue
    └── AppToast.vue
```

Empfohlene Umsetzung: In Phase 0 zuerst das Design-System (Basis-UI + Layout) bauen, dann pro Feature die View-Komponenten.

---

## 5. KI-Integration

### 5.1 3-Schicht-Modell

| Schicht | Konzept | Code |
|---------|---------|------|
| Schicht 1 (lokal) | ✅ OCR, Anonymisierung, Keyword-Classifier, Berechnungen, Cache | ❌ Kein Code vorhanden; `backend/app/ai/` existiert, ist aber leer |
| Schicht 2 (Ollama Cloud) | ✅ GLM 5.2 + Kimi K2.6 definiert | ❌ Kein Client vorhanden |
| Schicht 3 (lokal) | ✅ Platzhalter-Auflösung, PDF, E-Mail, DB, Audit | ❌ Keine Implementierung |

### 5.2 Vorhandene Prompt-Templates

Folgende Prompts sind in `KI-Konzept.md` und `ki-architecture.md` definiert:

- ✅ Ticket-Kategorisierung
- ✅ Ticket-Priorität (implizit)
- ✅ Antwort-Entwurf für Vermieter
- ✅ Mahnung (Stufe 1–3)
- ✅ Smart Insights
- ✅ System-Prompt (allgemein)

### 5.3 Fehlende oder unvollständige Prompt-Definitionen

| Feature | Status | Bemerkung |
|---------|--------|-----------|
| Beleg-Scan / Kosten-Extraktion | ⚠️ Konzept vorhanden, aber kein ausformuliertes Prompt-Template | Braucht Ausgabe-Schema (Betrag, Kategorie, Umlagefähigkeit, Datum) |
| Dokument-Klassifikation | ❌ Kein Prompt-Template | Nötig für `dokumente.py` |
| Lösungs-Vorschlag FAQ | ⚠️ Erwähnt, aber kein Template | Für automatische Mieter-Antworten |
| Ticket-Zusammenfassung | ❌ Kein Template | Vermieter-Übersicht bei langen Tickets |
| Sprachübersetzung | ❌ Kein Template | Niedrig priorisiert |
| Mieterhöhung § 558 BGB | ⚠️ Modell zugewiesen (Kimi K2.6), aber kein Prompt | Rechtlich sensibel, muss exakt sein |
| Jahresbericht | ⚠️ Modell zugewiesen, aber kein Prompt | Format/Zielgruppe definieren |
| Kostenvergleich regional | ❌ Kein Prompt | Datenquelle/Benchmark unklar |
| Energie-Empfehlung | ❌ Kein Prompt | Datenquelle unklar |
| Abrechnungstext | ⚠️ Modell zugewiesen, aber kein Prompt | Muss Vorlagen-Syntax beachten |
| Tone-Anpassung | ❌ Kein Prompt | Nice-to-have |
| Mieter-Bewerbungs-Zusammenfassung | ⚠️ Konzept vorhanden, aber kein Prompt | DSGVO-kritisch, kein Scoring |

### 5.4 Anonymisierungs-Protokoll

| Aspekt | Status |
|--------|--------|
| Anonymisierungsregeln in `ki-architecture.md` | ⚠️ Nur Regex-basiert dargestellt |
| Forderung nach Presidio (NER-basiert) | ✅ In `mietverwaltung-saas`-Skill und `KI-Konzept.md` erwähnt |
| Konsistenz | ❌ Widerspruch: Skill sagt "NICHT reine Regex", `ki-architecture.md` zeigt Regex-Lösung |

**Empfehlung:** Presidio (`presidio-analyzer`, `presidio-anonymizer`) mit `de_core_news_lg` + Custom-Regeln als Standard implementieren; Regex nur als Fallback.

---

## 6. Fehlerbehandlung

| Aspekt | Status |
|--------|--------|
| Einheitliches API-Fehlerformat | ❌ Nicht definiert |
| `backend/app/utils/exceptions.py` | ❌ Existiert nicht |
| `backend/app/middleware/error_handler.py` | ❌ Existiert nicht |
| Frontend-Error-State-Konzept | ✅ In `UX-UI-Konzept-konsolidiert.md` beschrieben |
| API-Fehlercodes & Recovery-Pfade | ❌ Nicht dokumentiert |

### 6.1 Empfohlenes Fehlerformat

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Die IBAN ist ungültig.",
    "field": "iban",
    "details": null,
    "request_id": "req-uuid",
    "docs_url": "https://docs.mietverwaltung.de/errors/VALIDATION_ERROR"
  }
}
```

Zusätzlich sollten HTTP-Status-Codes standardisiert werden:

| Situation | HTTP-Status |
|-----------|-------------|
| Validierungsfehler | 422 |
| Authentifizierungsfehler | 401 |
| Berechtigungsfehler | 403 |
| Ressource nicht gefunden | 404 |
| Plan-Limit erreicht | 402 / 403 mit Code `PLAN_LIMIT_EXCEEDED` |
| Rate-Limit | 429 |
| Interner Fehler | 500 |

---

## 7. Paginierung

| Aspekt | Status |
|--------|--------|
| `backend/app/utils/pagination.py` | ❌ Existiert nicht |
| Paginierung für List-Endpunkte | ❌ Nicht definiert |
| Frontend-Tabellen-Paginierung | ❌ Keine Komponente vorhanden |

### 7.1 Empfohlene Paginierungsstrategie

Für alle Listen-Endpunkte (Objekte, Einheiten, Mieter, Tickets, Kosten, Dokumente, Abrechnungen, Benachrichtigungen):

**Query-Parameter:**

```
GET /api/v1/tickets?page=1&page_size=20&sort=-created_at&status=offen
```

**Response-Format:**

```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 157,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

Frontend: `AppTable.vue` mit Pagination-Controls; Default `page_size = 20`, Max `page_size = 100`.

---

## 8. Datei-Upload-Pipeline

| Aspekt | Status |
|--------|--------|
| Upload-Endpunkt | ⚠️ `dokumente.py` geplant, aber nicht implementiert |
| Speicherpfad | ❌ Nicht definiert |
| Viren-Check | ❌ Nicht definiert |
| Dateigrößen-Limit | ⚠️ In UX-UI-Konzept als Beispiel "max. 10 MB" erwähnt, aber nicht verbindlich |
| Dateityp-Whitelist | ❌ Nicht definiert |
| Dokument-Sichtbarkeit (`vermieter/mieter/beide/handwerker`) | ✅ Konzept definiert |
| Verschlüsselung / Schutz am Speicherort | ❌ Nicht definiert |

### 8.1 Empfohlene Upload-Pipeline

1. **Client** → `POST /api/v1/dokumente/upload` mit `multipart/form-data`.
2. **Middleware** → Dateigröße-Check (max. 10 MB pro Datei, 50 MB pro Request).
3. **Dateityp-Whitelist** → PDF, JPG, JPEG, PNG, HEIC, DOCX, TXT.
4. **Virenscan** → Optional via `clamav` oder SaaS (z. B. Cloudmersive) im Hintergrund; bei MVP ausreichend: MIME-Type + Magic-Byte-Check.
5. **Speicherung** → `uploads/{vermieter_id}/{jahr}/{monat}/{uuid}.{ext}` (nicht im Docker-Volume auf Proxmox verlieren; später S3/Storage Box).
6. **Metadaten** → `dokumente`-Tabelle mit `sichtbarkeit`, `kategorie`, `mime_type`, `size_bytes`, `storage_path`, `virus_scan_status`.
7. **OCR/KI** → Asynchrones Post-Processing für Belege/Dokumente.
8. **Audit-Log** → Upload, Download, Löschung loggen.

**Empfehlung:** Upload-Pipeline im Build-Plan als eigene Phase definieren, da sie DSGVO- und Sicherheitsrelevanz hat.

---

## 9. Teststrategie

| Aspekt | Status |
|--------|--------|
| Test-Verzeichnisstruktur Backend | ⚠️ Konzept definiert, aber Ordner leer |
| Test-Verzeichnisstruktur Frontend | ⚠️ Konzept definiert, aber Ordner leer |
| `conftest.py`, `factories.py` | ❌ Nicht vorhanden |
| CI-Workflows (`test.yml`, `lint.yml`, `security.yml`) | ⚠️ Konzept beschrieben, aber nicht im Repo |
| Coverage-Ziele | ❌ Nicht definiert |

### 9.1 Empfohlene Test-Pyramide

```
        /
       / \   e2e (Playwright)        → ~5% der Tests, kritische Flows
      /   \
     /-----\  Integration (FastAPI TestClient, DB-Setup) → ~25%
    /       \
   /---------\ Unit (Services, KI-Anonymisierung, Berechnungen) → ~70%
```

### 9.2 Coverage-Ziele

| Ebene | Ziel |
|-------|------|
| Backend Unit | ≥ 80% für Services und Utils |
| Backend Integration | ≥ 60% für API-Endpunkte |
| Frontend Unit (Vitest) | ≥ 70% für Composables und Utilities |
| Frontend Komponenten | ≥ 50% für komplexe Komponenten |
| e2e | Kritische Flows abgedeckt (Login, Objekt anlegen, Ticket erstellen) |

### 9.3 Empfohlene Test-Kategorien

**Backend Unit:**
- Auth-Service (Passwort-Hash, JWT, 2FA)
- Kosten-Service (Umlageberechnung, Verteilung nach qm)
- Abrechnung-Service (Positionen, Verteilung, PDF)
- KI-Anonymisierung (Presidio + Deanonymisierung)
- Fristen-Service (Berechnung, Eskalation)

**Backend Integration:**
- Auth-API (Register, Login, 2FA, Refresh, Logout)
- Objekte-API (CRUD, RLS, Soft-Delete)
- Tickets-API (Erstellen, Kategorisierung, Kommentare)
- Abrechnung-API (Erstellen, PDF, Senden)
- Dokumente-API (Upload, Download, Sichtbarkeit)

**Frontend Unit:**
- `useAuth`-Composable
- `useApi`-Composable (Interceptor, Token-Refresh)
- `useToast`-Composable
- `KPICard.vue` (Berechnungen)
- `usePlanLimits`-Composable

**Frontend Integration:**
- Router-Guards (Auth, Rollen)
- Store-Interaktionen

**e2e (Playwright):**
- Vermieter registriert sich und legt Objekt an.
- Mieter erstellt Ticket.
- Beleg hochladen + OCR-Extraktion.
- Mahnung erstellen und per PDF senden.

---

## 10. Kritische Blocker vor Build-Start

| # | Blocker | Priorität |
|---|---------|-----------|
| 1 | `shared/`-Ordner und OpenAPI-Typen-Pipeline fehlt komplett | Hoch |
| 2 | FastAPI-Routen sind nur TODO-Stubs; MVP-Endpunkte (Mietzahlungen, Fristen, Bankverbindungen, Bewerbungen) fehlen | Hoch |
| 3 | Pinia-Stores und API-Client fehlen | Hoch |
| 4 | Keine Komponenten außer `HomeView.vue` | Hoch |
| 5 | KI-Client, Anonymisierungs-Engine, Keyword-Classifier fehlen | Hoch |
| 6 | Fehlerbehandlungs-Middleware und einheitliches Fehlerformat fehlen | Mittel |
| 7 | Paginierungs-Utility fehlt | Mittel |
| 8 | Upload-Pipeline (Speicherpfad, Viren-Check, Limits) nicht spezifiziert | Hoch |
| 9 | CI-Workflows und Test-Infrastruktur fehlen | Mittel |
| 10 | Admin-Center-Endpunkte nicht definiert | Niedrig-Mittel (nicht MVP-kritisch) |

---

## 11. Empfohlene Nächste Schritte

1. **Build-Plan v3 aktualisieren** auf Basis dieses Reviews; jede Phase mit expliziten API-, Frontend- und Test-Lieferungen versehen.
2. **API-Vertrag zuerst** bauen: Pydantic-Schemas für alle MVP-Tabellen, dann Routen, dann `export_openapi.py` + `shared/`.
3. **KI-Prompt-Registry** in `docs/ki/prompt-registry.md` ergänzen (fehlende Prompts aus Kapitel 5.3).
4. **Fehlerformat & Paginierung** in `backend/app/utils/` und `backend/app/middleware/` implementieren, bevor weitere Routen entstehen.
5. **Upload-Pipeline** in eigenem Tech-Spec dokumentieren (Pfad, Limits, Viren-Check, Audit).
6. **Design-System** (Basis-UI + Layout) als erstes Frontend-Ziel definieren, bevor Feature-Views gebaut werden.
7. **Tests von Anfang an** mitführen: `conftest.py` + `factories.py` im ersten Backend-Commit.

---

*Review erstellt von Hermes Agent*  
*Ausgabedatei: `/root/mietverwaltung-saas/docs/architecture/review-api-frontend.md`*
