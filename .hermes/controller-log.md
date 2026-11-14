# Controller-Log — MietVerwaltung SaaS

> Letzte Aktualisierung: 2026-11-13 15:31:44 UTC  
> Controller-Agent: Qualitaetskontrolle + Koordination Phase 8/9/3/2  
> Repo: `max1STD/mietverwaltung-saas`  
> Branch: `main`  
> HEAD: `9bacf245ae9407313accce07424b8baacbc6feb5`  

---

## Gesamtstatus

| Bereich | Status | Hinweis |
|---------|--------|---------|
| Backend-Tests (Phase 0+1+4+7) | ✅ gruen | 96/96 passieren bei `PYTHONPATH` bereinigt |
| Frontend-Build | 🔴 rot | `vue-tsc` + `pnpm build` blockiert durch 4 TypeScript-Fehler |
| Phase 8 (Kosten/Abrechnungen/Mietzahlungen) | 🟡 teilweise | Modelle/Schemas/Services/Frontend-Stores+Views existieren, **Backend-Routen fehlen** |
| Phase 9 (Dashboard) | 🟡 teilweise | Backend-Dashboard-Schema vorhanden, **kein Service/Route**, Frontend-View existiert |
| Phase 2 (Stripe/Billing) | 🔴 nicht gestartet | `Subscription`/`PlanUsage`-Modelle existieren, aber **keine Routes/Services/Schemas**, `models/__init__.py` exportiert sie nicht |
| Phase 3 (Onboarding) | 🔴 nicht gestartet | Keine Dateien, keine Routen, keine Komponenten |

---

## Git-Status

```text
9bacf24 test: Phase 0+1 test automation suite (61 tests) + bugfixes
5231202 feat: Phase 4+7 — Objekte, Einheiten, Mieter, Mietverträge, Tickets (Backend + Frontend)
b33298d feat: Phase 1 — Auth, 2FA, Security, Audit, DSGVO (Backend + Frontend)
f71fd7d feat: Phase 0 — native dev environment + DB schema v4.1 migration
b274128 docs: DB-Schema v4.1 (5 CRITICAL fixes) + Build-Plan v3 (16 phases, native dev)

```

```text
 M backend/app/main.py
 M backend/app/models/__init__.py
 M backend/app/models/abrechnungen.py
 M backend/app/models/user.py
 M backend/app/routes/_helpers.py
 M backend/app/schemas/__init__.py
 M backend/app/services/auth.py
 M frontend/src/components/AppSidebarContent.vue
 M frontend/src/components/ui/AppTable.vue
 M frontend/src/router/index.ts
?? backend/app/models/abrechnung_positionen.py
?? backend/app/models/fristen.py
?? backend/app/models/kosten.py
?? backend/app/models/kostenkategorien.py
?? backend/app/models/mietzahlungen.py
?? backend/app/models/plan_usage.py
?? backend/app/models/subscription.py
?? backend/app/routes/abrechnungen.py
?? backend/app/routes/kosten.py
?? backend/app/routes/mietzahlungen.py
?? backend/app/schemas/abrechnung.py
?? backend/app/schemas/billing.py
?? backend/app/schemas/dashboard.py
?? backend/app/schemas/kosten.py
?? backend/app/schemas/mietzahlung.py
?? backend/app/services/abrechnungen.py
?? backend/app/services/dashboard.py
?? backend/app/services/kosten.py
?? backend/app/services/mietzahlungen.py
?? backend/tests/phase8/
?? frontend/src/components/abrechnung/
?? frontend/src/components/kosten/
?? frontend/src/stores/abrechnungen.ts
?? frontend/src/stores/kosten.ts
?? frontend/src/stores/mietzahlungen.ts
?? frontend/src/views/abrechnungen/
?? frontend/src/views/kosten/
?? frontend/src/views/mietzahlungen/

```

### Uncommitted / Untracked (Phase 8 Agent)
- Staged: `backend/app/models/__init__.py`, `backend/app/models/abrechnungen.py`, `backend/app/schemas/__init__.py`
- Untracked: `backend/app/models/abrechnung_positionen.py`, `kosten.py`, `kostenkategorien.py`, `mietzahlungen.py`, `schemas/abrechnung.py`, `schemas/kosten.py`, `schemas/mietzahlung.py`, `frontend/src/components/abrechnung/AbrechnungPositionTable.vue`, `frontend/src/components/kosten/ReceiptScanPanel.vue`, `frontend/src/stores/abrechnungen.ts`, `kosten.ts`, `mietzahlungen.ts`

---

## Offene GitHub-Issues (5)

- **#31** `high, pre-build, api, frontend` — [HIGH][API] Error-Format, Pagination, File-Upload und Testing fehlen
- **#30** `high, pre-build, security` — [HIGH][Security] CSP-Header und CSRF-Strategie unvollstaendig
- **#29** `high, pre-build, security, encryption` — [HIGH][Security] AES-256-GCM Schluesselmanagement nicht definiert
- **#28** `critical, pre-build, api, frontend` — [CRITICAL][API] shared/ Ordner fehlt — OpenAPI Type-Sync Pipeline nicht vorhanden
- **#27** `critical, pre-build, api` — [CRITICAL][API] Fehlende Route-Module fuer MVP

---

## Phasen-Detailstatus

### Phase 8 — Kosten, Abrechnungen, Mietzahlungen

**Backend vorhanden:**
- Modelle: `Kosten`, `Kostenkategorie`, `Abrechnung`, `AbrechnungPosition`, `Mietzahlung` ✅
- Schemas: `kosten.py`, `abrechnung.py`, `mietzahlung.py` ✅
- Services: `kosten.py`, `abrechnungen.py`, `mietzahlungen.py` ✅

**Backend fehlend:**
- Route-Module `kosten.py`, `abrechnungen.py`, `mietzahlungen.py` ❌
- Registrierung in `app/main.py` ❌
- API-Endpunkte damit **nicht erreichbar** ❌

**Frontend vorhanden:**
- Stores: `kosten.ts`, `abrechnungen.ts`, `mietzahlungen.ts` ✅
- Views: `KostenListView.vue`, `KostenFormView.vue`, `AbrechnungenListView.vue`, `AbrechnungDetailView.vue`, `MietzahlungenListView.vue` ✅
- Komponenten: `AbrechnungPositionTable.vue`, `ReceiptScanPanel.vue` ✅

**Frontend fehlend / defekt:**
- Routen in `src/router/index.ts` fuer `/kosten`, `/abrechnungen`, `/mietzahlungen` ❌
- Navigation in `AppSidebarContent.vue` ❌
- TypeScript-Fehler in `AbrechnungPositionTable.vue` (siehe Build-Status) 🔴

**Empfohlene Fix-Agent-Aufgabe:**
1. Route-Module + `main.py`-Registrierung fuer Kosten/Abrechnungen/Mietzahlungen ergaenzen.
2. Router-Eintraege + Sidebar-Navigation + Abrechnungs-/Kosten-/Mietzahlungs-Views verknuepfen.
3. TypeScript-Fehler in `AbrechnungPositionTable.vue` beheben (`AppTable`-Generic oder Datentyp anpassen).
4. Backend-Integrationstests fuer Kosten/Abrechnungen/Mietzahlungen ergaenzen.

### Phase 9 — Dashboard

**Vorhanden:**
- Backend-Schema `dashboard.py` mit `DashboardSummary`, `ObjectRendite`, `DashboardFinancials`, `DashboardInsights`, `DashboardSubscriptionInfo` ✅
- Frontend `DashboardView.vue` ✅

**Fehlend:**
- Dashboard-Service + API-Route ❌
- Datenversorgung aus realen Tabellen (`objekte`, `einheiten`, `mieter`, `kosten`, `mietzahlungen`, `tickets`) ❌
- Smart-Insights-Logik ❌
- Verknuepfung Subscription/PlanUsage mit `User`-Modell (`models/__init__.py` exportiert `Subscription`/`PlanUsage` nicht) ❌

### Phase 2 — Stripe / WE-basiertes Billing

**Vorhanden:**
- `Subscription`-Modell, `PlanUsage`-Modell ✅
- Stripe-Bibliothek in Venv ✅

**Fehlend:**
- `Subscription`/`PlanUsage` nicht in `models/__init__.py` exportiert ❌
- Keine Schemas/Routes/Services fuer Checkout, Webhook, Portal, Preisvorschau ❌
- Kein Frontend-Pricing-/Checkout-/Subscription-Widget ❌

### Phase 3 — Onboarding & Setup-Checkliste

**Vorhanden:** Keine Artefakte (weder Modelle, noch Routen, noch Komponenten).
**Fehlend:** Alles.

---

## Qualitaetsverifikation

### Backend-Tests
- **Befehl:** `cd backend && source .venv/bin/activate && unset PYTHONPATH && pytest -q --tb=short`
- **Ergebnis:** 96/96 passed
- **Hinweis:** Standardmaessige Testausfuehrung schlaegt fehl, weil `PYTHONPATH` des Hermes-Runners eine inkompatible `pydantic_core`-Version aus Python 3.14 vorzieht. Bei bereinigtem `PYTHONPATH` laufen alle Tests.

### Frontend-Build
- **Befehl:** `cd frontend && eval "$(fnm env)" && pnpm build`
- **Ergebnis:** Exit 2
- **Fehler:**
  - `AbrechnungPositionTable.vue(2,14)`: `AbrechnungPosition[]` nicht zuweisbar zu `Record<string,unknown>[]`
  - `AbrechnungPositionTable.vue(5,80/6,70/7,92)`: `unknown`-Typ-Argumente in `formatCurrency` / `schluesselLabel`

### Lint
- **Backend (ruff):** Noch nicht geprueft — Route-Fehler priorisieren.
- **Frontend (eslint):** Noch nicht geprueft — Build blockiert.

---

## Naechste Schritte / Dispatch-Plan

1. **Fix-Agent Phase 8** — Backend-Routen + Router + Sidebar + TS-Fix
2. **QA-Agent Phase 8** — Nach Fix: Backend-Tests + Frontend-Build + Integrationstests
3. **Sub-Agent Phase 9** — Dashboard-Service + Route + Datenaggregation (abhaengig von Phase 8)
4. **Sub-Agent Phase 2** — Stripe-Checkout + Webhook + Subscription-Service (abhaengig von Phase 9 nur gering)
5. **Sub-Agent Phase 3** — Onboarding-Flow (kann parallel zu Phase 2 beginnen, sobald Phase 8 stabil ist)

---

## Risiken

- **Konsistenz:** Phase 8 hat Frontend-Views fuer Kosten/Abrechnungen, aber keine Backend-Routen → API-Calls werden 404 liefern.
- **Type-Sync:** `shared/` Ordner (OpenAPI-Typen) fehlt weiterhin (Issue #28); Frontend-Typen sind handgeschrieben und koennen vom Backend-Schema abweichen.
- **Abhaengigkeit:** Phase 9 Dashboard braucht Phase 8 Finanzdaten; Phase 2 Billing braucht PlanUsage.
- **Build-Blocker:** Frontend-Build ist rot; kein erfolgreicher Deploy moeglich.

---

*Controller-Log wird mit jeder Pruefrunde aktualisiert (max. alle 5 Minuten).*


## Erstellte/GitHub-Issues in dieser Runde

- **#32** Backend-Routen Kosten/Abrechnungen/Mietzahlungen fehlen
- **#33** TypeScript Build-Fehler in AbrechnungPositionTable.vue
- **#34** Dashboard-Service + Route + Datenaggregation
- **#35** Stripe-Abos + WE-basiertes Billing
- **#36** Onboarding + Setup-Checkliste

## Dispatch-Empfehlung

1. **Fix-Agent Phase 8a** → Issue #32 (Backend-Routen + main.py)
2. **Fix-Agent Phase 8b** → Issue #33 (Frontend TS-Fix + Router/Sidebar)
3. **QA-Agent** → nach 8a+8b: `pytest` + `vue-tsc && vite build` + Integrationstests
4. **Sub-Agent Phase 9** → nach QA-Grün: Issue #34
5. **Sub-Agent Phase 2** → parallel zu Phase 9 (keine starke Abhängigkeit)
6. **Sub-Agent Phase 3** → parallel zu Phase 2 (starten sobald Phase 8a/8b grün)

---

*Controller-Runde abgeschlossen.*
