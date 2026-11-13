# MietVerwaltung SaaS — Build-Plan v3

> **Erstellt:** 13. November 2026  
> **Grundlage:** Pre-Build Architektur-Review (GitHub Issue #24), DB-Schema v4.1, WE-basiertes Pricing v3, Native Dev  
> **Ziel:** Vollständiger Bauplan für das MVP — 16 Phasen, **ca. 137–175 PT**

---

## 0. Executive Summary

Build-Plan v3 ersetzt v2. Er beruht auf **DB-Schema v4.1 (33 Tabellen)** und dem beschlossenen **WE-basierten Preismodell** (kein Free-Plan, 14-Tage-Trial mit Kreditkarte). Die Entwicklung läuft **nativ** (kein Docker) auf dem Proxmox-MVP: `uvicorn` für das Backend, `vite dev` für das Frontend, PostgreSQL 17 ist vorhanden, Redis wird installiert.

**Neue, eigene Phasen gegenüber v2:**

1. **Phase 2 — Stripe-Abos & WE-basiertes Billing** (Checkout, Webhook, Trial, Proration, Reconciliation)
2. **Phase 3 — Onboarding & Setup-Checkliste**
3. **Phase 5 — Mieter-Bewerbung** (Ausweis/Lohnabrechnung/Schufa, KEIN KI-Scoring)
4. **Phase 14 — Admin-Center** (internes Verwaltungsportal)

Jede Phase listet konkret die betroffenen **Tabellen, Routen, Frontend-Komponenten, Tests** und einen **Meilenstein**. Der Abhängigkeitsgraph ist ein DAG — keine Zirkelschlüsse.

---

## 1. Annahmen & Tech-Stack

| Komponente | Entscheidung |
|------------|--------------|
| Backend | Python 3.12 + FastAPI + SQLAlchemy 2.0 (async) + Pydantic v2 |
| Frontend | Vue.js 3 + Vite + Vue Router + Pinia + Tailwind CSS + TypeScript |
| Datenbank | PostgreSQL 17, nativ auf Server, Row-Level Security (RLS) |
| Cache/Queue | Redis (muss installiert werden) |
| KI | Ollama Cloud (GLM 5.2 + Kimi K2.6) |
| OCR/PDF | Tesseract + PyMuPDF + WeasyPrint + Jinja2 |
| Zahlungen | Stripe (Checkout, Subscription, Webhooks, Trial mit KK) |
| E-Mail | Resend (Transactional E-Mail, kein eigener Postfix) |
| GeoIP | MaxMind GeoLite2 |
| Anonymisierung | Presidio + spaCy `de_core_news_lg` + Custom-Regeln |
| Hosting MVP | Proxmox LXC + Cloudflared Tunnel (0 €) |
| Deploy | GitHub Actions via SSH, native systemd-Services, keine Docker-Compose im Produktivpfad |

---

## 2. Preismodell v3 (WE-basiert)

| WE-Bereich | Preis/WE/Monat | Beispiel |
|------------|----------------|----------|
| 1–5 WE | 9,75 € | 3 WE = 29,25 €/Mo |
| 6–25 WE | 7,50 € | 10 WE = 75,00 €/Mo |
| 26–49 WE | 5,90 € | 30 WE = 177,00 €/Mo |
| 50+ WE | **Anfrage** | Custom Pricing / Manual Approval |

- **Kein Free-Plan.** Nach Kündigung/Trial-Ablauf: Account gesperrt, Daten 30 Tage aufbewahrt, dann Export + Löschung.
- **14-Tage-Trial mit Kreditkarte** (Netflix-Style). Automatische Abbuchung danach.
- Standard: jährliche Zahlung (20 % Rabatt = 2 Monate geschenkt), monatlich optional.
- Zahlungsmethoden: Kreditkarte (Stripe, Apple Pay/Google Pay), SEPA-Lastschrift, PayPal.
- Live-Abo-Widget im Dashboard: "Dein Abo: 7 Wohnungen · 51,75 €/Monat".

---

## 3. Phasen-Abhängigkeitsgraph

```
Phase 0 ──► Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5
(Fundament) (Auth)     (Stripe)   (Onboard)  (Domain)   (Bewerbung)
                              │                   │
                              │                   ├──► Phase 6 (Dokumente)
                              │                   ├──► Phase 7 (Tickets)
                              │                   └──► Phase 8 (Kosten/Abrechnung)
                              │                        │
                              │                        ▼
                              │                     Phase 9 (Dashboard)
                              │                        │
                              ▼                        ▼
                           Phase 10 (KI-Schicht)
                              │
                              ├──► Phase 11 (E-Mail/Mahnung/Fristen)
                              │         │
                              │         ▼
                              │      Phase 12 (PDF/Templates)
                              │         │
                              ▼         ▼
                           Phase 13 (DSGVO/Hardening)
                              │
                              ▼
                           Phase 14 (Admin-Center) ──► Phase 15 (Production Deploy)

Parallel (ab Phase 1):
  Admin-Center ─────────────────────────────────────────────► Phase 15
```

**Parallelisierbar:**
- Phase 6 (Dokumente) und Phase 7 (Tickets) parallel nach Phase 4.
- Phase 9 (Dashboard) parallel zu Phase 10 (KI) ab Phase 8.
- Phase 12 (PDF) parallel zu Phase 11 (E-Mail) ab Phase 10.
- Admin-Center als paralleler Stream ab Phase 1.

---

## 4. Phasen im Detail

### Phase 0: Native Dev-Fundament & DB v4.1 (8–10 PT)

**Ziel:** Lokale Native-Dev-Umgebung, die ohne Docker läuft. Alembic-Initial-Migration für alle 33 Tabellen plus v4.1-Fixes.

**Voraussetzungen:** Server hat kein Docker; PostgreSQL 17 läuft bereits; Redis fehlt noch.

**Native-Setup-Artefakte:**

```bash
# 1. Python-Venv im Backend
python3.12 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt

# 2. Node / pnpm im Frontend
fnm install 22
fnm use 22
cd frontend && pnpm install

# 3. Redis installieren (Server)
sudo apt-get update
sudo apt-get install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
redis-cli ping   # → PONG

# 4. PostgreSQL DB + User anlegen
sudo -u postgres psql <<'EOF'
CREATE USER mv WITH PASSWORD 'change-me' CREATEDB;
CREATE DATABASE mietverwaltung OWNER mv;
GRANT ALL PRIVILEGES ON DATABASE mietverwaltung TO mv;
EOF

# 5. Alembic initialisieren (nur einmalig)
cd backend
alembic init alembic
# Danach: env.py anpassen (asyncpg, .env), erste Revision schreiben
alembic revision --autogenerate -m "initial_schema_v4_1"
alembic upgrade head
```

**Makefile (native):**

```makefile
.PHONY: dev dev-backend dev-frontend dev-worker setup test lint migrate migrate-create health clean

setup:          ## Einmalige Native-Dev-Einrichtung
	./scripts/setup-dev.sh

dev:            ## Backend + Frontend + Worker parallel starten
	make dev-backend & make dev-frontend & make dev-worker

dev-backend:    ## Uvicorn mit Hot-Reload
	cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:   ## Vite Dev-Server
	cd frontend && pnpm dev --host 0.0.0.0 --port 5173

dev-worker:     ## Hintergrund-Worker (Events, E-Mails, Cron)
	cd backend && source .venv/bin/activate && python -m app.worker

test:           ## Alle Tests
	cd backend && source .venv/bin/activate && pytest
	cd frontend && pnpm test

lint:           ## Ruff + mypy + bandit + eslint
	cd backend && source .venv/bin/activate && ruff check app/ && mypy app/ && bandit -r app/ -ll
	cd frontend && pnpm lint

migrate:        ## Alembic auf HEAD
	cd backend && source .venv/bin/activate && alembic upgrade head

migrate-create: ## Neue Migration: make migrate-create m="beschreibung"
	cd backend && source .venv/bin/activate && alembic revision --autogenerate -m "$(m)"

health:         ## Health-Check aufrufen
	curl -s http://localhost:8000/health | jq .

clean:          ## Build-Artefakte löschen
	cd backend && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
	cd frontend && rm -rf dist node_modules/.cache
```

**DB-Schema v4.1 — in die Initial-Migration aufgenommene Fixes:**
- `users`: RLS-Policy für Vermieter/Mieter/Admin korrigiert; `email_verified`, `is_active`, Vermieter-Stammdaten (`company`, `address`, `plz`, `city`, `phone`, `tax_number_enc`, `logo_path`) ergänzt.
- `users.email` partial-unique `WHERE deleted_at IS NULL`.
- `subscriptions` / `plan_usage`: WE-basiert (`price_per_unit`, `unit_count`, `billing_interval`, `payment_provider_id`), jeweils UNIQUE pro `user_id`.
- `kosten`, `abrechnung_positionen`, `bankverbindungen`: `deleted_at` hinzugefügt.
- `dokumente`: `sichtbarkeit` enum ergänzt.
- `dokument_freigaben`: `user_id` statt `role`.
- `abrechnungen`: partial-unique `UNIQUE(einheit_id, jahr) WHERE deleted_at IS NULL`.
- CHECK-Constraints für `tickets.status/priority/category`, `objekte.typ`, `einheiten.energy_class`, `dokumente.type`, `fristen.warn_level`, `notifications.status`, `mietzahlungen.mahnstufe`.
- Composite-Indizes `(vermieter_id, id)` auf großen Tenant-Tabellen.

**Tabellen:** alle 33 Tabellen aus v4.1.

**Backend-Routen:**
- `GET /health` (DB + Redis + Stripe-Testmodus-Check)
- `GET /api/v1/openapi.json` (später via `export_openapi.py`)

**Frontend-Komponenten:**
- `App.vue`, `main.ts`, Router-Setup, Pinia-Setup
- `components/ui/AppButton.vue`, `AppInput.vue`, `AppToast.vue`
- `views/public/LandingView.vue` (Skelett)

**Tests:**
- Backend: `/health` liefert 200; Alembic-Migration erzeugt alle 33 Tabellen + 34 RLS-Policies.
- Frontend: vitest-Suite läuft, Routing/Layout renderbar.
- DB-Test: jede Tabelle hat `vermieter_id` oder entsprechende RLS-Policy.

**Meilenstein:**
> `make setup` + `make dev` startet Backend, Frontend und Redis; `/health` ist grün; Alembic hat alle 33 v4.1-Tabellen angelegt.

---

### Phase 1: Auth, 2FA, Sicherheit, Audit & DSGVO-Einwilligungen (12–14 PT)

**Ziel:** Sicheres Login-System für Vermieter, Mieter und Admins; Audit-Logging und Consent-Management von Tag 1.

**Tabellen:** `users`, `user_sessions`, `einwilligungen`, `audit_logs`.

**Backend-Routen:**
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/2fa/setup`
- `POST /api/v1/auth/2fa/verify`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/password-reset`
- `GET/POST /api/v1/einwilligungen`
- `GET /api/v1/sessions` + `DELETE /api/v1/sessions/{id}`
- `GET /api/v1/users/me`, `PATCH /api/v1/users/me`
- `POST /api/v1/bankverbindungen` (Vermieter-Standardkonto, IBAN verschlüsselt)

**Frontend-Komponenten / Views:**
- `LoginView.vue`, `RegisterView.vue`, `TwoFactorSetupView.vue`, `PasswordResetView.vue`
- `ConsentModal.vue`
- `stores/auth.ts`, `stores/user.ts`
- `composables/useApi.ts`, `useToast.ts`

**Tests:**
- Backend Integration: Registrierung → Login → 2FA → Logout → Session-Revocation.
- Unit: Argon2id, JWT-Refresh, Rate-Limit (5 Versuche/15 Min), CSRF-Token, CSP-Nonce.
- RLS-Tests: Mieter sieht nur eigene Daten; Vermieter sieht seine Mieter.
- Audit-Log: Jeder Login, jede Passwortänderung, jede Einwilligungsänderung geloggt.

**Meilenstein:**
> Registrierung mit DSGVO-Einwilligung → Login → 2FA → geschütztes Dashboard; Audit-Log enthält alle sicherheitsrelevanten Aktionen.

---

### Phase 2: Stripe-Abos & WE-basiertes Billing (10–13 PT)

**Ziel:** Zahlungsfluss, 14-Tage-Trial mit Kreditkarte, WE-basierte Abrechnung, Webhooks, Account-Sperre bei Nichtzahlung.

**Tabellen:** `subscriptions`, `plan_usage`, `users`, `events`, `notifications`, `audit_logs`.

**Preisstaffel-Logik (Backend-Service):**

```python
def calculate_we_price(unit_count: int, interval: str) -> Decimal:
    if unit_count >= 50:
        raise PlanLimitExceeded("Ab 50 WE bitte Anfrage stellen.")
    if 1 <= unit_count <= 5:   price = Decimal("9.75")
    elif 6 <= unit_count <= 25: price = Decimal("7.50")
    elif 26 <= unit_count <= 49: price = Decimal("5.90")
    else: price = Decimal("0.00")
    total = price * unit_count
    if interval == "yearly":
        total = total * 12 * Decimal("0.80")
    return price, total
```

**Backend-Routen:**
- `POST /api/v1/stripe/checkout-session` (Trial + Kreditkarte)
- `GET /api/v1/subscriptions/me`
- `PATCH /api/v1/subscriptions/me` (WE-Anzahl ändern, jährlich/monatlich)
- `POST /api/v1/subscriptions/me/cancel`
- `POST /api/v1/stripe/webhook` (signaturverifiziert)
  - `checkout.session.completed`
  - `invoice.paid`
  - `invoice.payment_failed`
  - `customer.subscription.deleted`
- `POST /api/v1/stripe/portal` (Stripe Customer Portal)
- `GET /api/v1/plan/price-preview?we=7&interval=yearly`
- Hintergrund-Cron: `reconcile_subscriptions` (täglich)

**Frontend-Komponenten / Views:**
- `PricingView.vue` mit WE-Slider (1–49), Live-Berechnung, Staffelvisualisierung
- `CheckoutView.vue` (Stripe-Embedded-Checkout / Stripe Elements)
- `SubscriptionWidget.vue` (Dashboard-Widget)
- `views/settings/SubscriptionSettings.vue`

**Tests:**
- Stripe-Webhook-Tests mit Test-Secret + Mock-Events.
- Trial-Ablauf → Account-Sperre → Login blockiert mit CTA.
- WE-Upgrade/Downgrade: Proration und `plan_usage.unit_count` synchron.
- Keine 50+ WE im Checkout → Anfrage-Modal.

**Meilenstein:**
> Test-Vermieter schließt 14-Tage-Trial mit Kreditkarte ab; Stripe-Webhook aktiviert das Abo; Dashboard-Widget zeigt korrekten WE-Preis.

---

### Phase 3: Onboarding & Setup-Checkliste (4–6 PT)

**Ziel:** Neuer Vermieter durch Setup führen, Conversion in den Trial maximieren.

**Tabelle:** `onboarding_progress`.

**Backend-Routen:**
- `GET /api/v1/onboarding`
- `POST /api/v1/onboarding/{step}`
- `GET /api/v1/onboarding/next-action`

**Onboarding-Schritte:**
1. Profil vervollständigen (Adresse, Bankverbindung)
2. Erstes Objekt anlegen
3. Erste Einheit anlegen
4. Optional: Ersten Mieter anlegen
5. KI-Assistent-Einwilligung

**Frontend-Komponenten / Views:**
- `OnboardingView.vue` (Welcome + Progress 40 % Endowed-Progress)
- `OnboardingChecklist.vue`
- `views/onboarding/ProfileStep.vue`, `ObjectStep.vue`, `UnitStep.vue`
- `components/ki/KIWelcomeBubble.vue`

**Tests:**
- Frontend: Onboarding-Flow bis 100 %.
- Backend: Schritt-Status korrekt persistiert; bei Trial-Ablauf bleibt Onboarding-Status erhalten, aber Account blockiert.

**Meilenstein:**
> Neuer Nutzer sieht nach Registrierung das Onboarding; nach 3 abgehakten Schritten erreicht er das „Aha-Erlebnis“ (erstes Objekt + Einheit sichtbar).

---

### Phase 4: Domain-Core — Objekte, Einheiten, Mieter, Verträge (13–16 PT)

**Ziel:** Stammdaten-Modell; WE-Limit-Prüfung gegen `plan_usage`; erste Finanzierungsfelder.

**Tabellen:** `objekte`, `einheiten`, `einheit_ausstattung`, `mieter_historie`, `mieter`, `mietvertraege`, `mietvertrag_aenderungen`, `kostenkategorien`, `bankverbindungen`, `users` (Vermieter-Stammdaten).

**Backend-Routen:**
- `/api/v1/objekte` (CRUD)
- `/api/v1/objekte/{id}/foto` (Upload, Dateisystem)
- `/api/v1/einheiten` (CRUD, WE-Limit-Check)
- `/api/v1/einheiten/{id}/ausstattung`
- `/api/v1/einheiten/{id}/mieter-historie`
- `/api/v1/mieter` (CRUD + Login erstellen)
- `/api/v1/mieter/{id}/bankverbindungen`
- `/api/v1/mietvertraege` (CRUD, Vertragsänderungen als Sub-Ressource)
- `/api/v1/kostenkategorien` (BetrKV-Katalog-Defaults + Custom)

**Frontend-Komponenten / Views:**
- `views/vermieter/ObjekteView.vue`, `ObjektDetailView.vue`
- `views/vermieter/EinheitenView.vue`, `EinheitDetailView.vue`
- `views/vermieter/MieterView.vue`, `MieterDetailView.vue`
- `views/vermieter/MietvertraegeView.vue`
- `components/objekte/ObjektCard.vue`, `ObjektFotoUpload.vue`
- `components/einheiten/AusstattungBadges.vue`, `MieterHistorieList.vue`
- `components/mieter/CreateMieterModal.vue`

**Tests:**
- Integration: Objekt → Einheit → Mieter → Mietvertrag; WE-Limit blockiert weitere Einheit.
- RLS: Mieter sieht nur eigene Stammdaten; Vermieter sieht alles.
- Validierung: Mietbeginn < Mietende, Kaltmiete > 0, PLZ-Format.

**Meilenstein:**
> Vermieter legt Objekt, Einheit, Mieter und Mietvertrag an; System blockiert das Anlegen über das WE-Limit hinaus.

---

### Phase 5: Mieter-Bewerbung (5–8 PT)

**Ziel:** Externe Mieter können sich auf freie Wohnungen bewerben; Vermieter entscheidet menschlich (kein KI-Score).

**Tabellen:** `bewerbungen`, `dokumente`, `einheiten`, `mieter`, `users`, `audit_logs`.

**Backend-Routen:**
- `GET /api/v1/einheiten/{id}/bewerbungen` (öffentliche Bewerbungsseite Link)
- `POST /api/v1/public/bewerbungen` (ungeschützt, Captcha/Rate-Limit)
- `POST /api/v1/bewerbungen/{id}/upload` (Ausweis/Lohn/Schufa)
- `PATCH /api/v1/bewerbungen/{id}/annehmen` → erzeugt `mieter` + `mietvertrag`
- `PATCH /api/v1/bewerbungen/{id}/ablehnen`
- `GET /api/v1/bewerbungen/{id}/summary` (KI-Zusammenfassung der Unterlagen, KEIN Score)

**DSGVO-Hinweis:**
- Ausweis-Upload nur mit „KOPIE“-Wasserzeichen; OCR extrahiert Text → Bild sofort sicher löschen (3× überschreiben).
- Lohnabrechnung: KI extrahiert Netto-Einkommen + berechnet Mietbelastungsquote; Mensch entscheidet.

**Frontend-Komponenten / Views:**
- `views/public/BewerbungView.vue` (öffentlich, pro Einheit)
- `views/vermieter/BewerbungenView.vue`
- `components/bewerbung/BewerbungDetailModal.vue`
- `components/bewerbung/BewerbungUpload.vue`
- `components/bewerbung/MietbelastungsQuote.vue`

**Tests:**
- End-to-End: Bewerber füllt Formular → Vermieter sieht Zusammenfassung → Annehmen erzeugt Mieter + Vertrag.
- Sicherheit: Öffentliche Bewerbung ohne Auth funktioniert, aber Admin-Endpunkte blockiert.
- DSGVO: Ausweisbild wird nach OCR gelöscht; kein KI-Score in der UI.

**Meilenstein:**
> Eine Bewerbung wird eingereicht, der Vermieter nimmt sie an und ein neuer Mietvertrag entsteht automatisch.

---

### Phase 6: Dokumenten-Management & Upload (5–8 PT)

**Ziel:** Verschlüsselte Dateiablage, Sichtbarkeit, Freigaben, Beleg-Scan-Vorstufe.

**Tabellen:** `dokumente`, `dokument_freigaben`.

**Backend-Routen:**
- `POST /api/v1/dokumente/upload` (multipart, max 10 MB, MIME + Magic-Bytes)
- `GET /api/v1/dokumente`
- `GET /api/v1/dokumente/{id}/download`
- `DELETE /api/v1/dokumente/{id}`
- `POST /api/v1/dokumente/{id}/freigaben`
- `POST /api/v1/dokumente/{id}/scan-preview` (OCR-Extraktion ohne Speicherung)

**Speicherpfad:** `uploads/{vermieter_id}/{jahr}/{monat}/{uuid}.{ext}`

**Frontend-Komponenten / Views:**
- `components/dokumente/DocumentUploader.vue`
- `components/dokumente/DocumentGallery.vue`
- `views/vermieter/DokumenteView.vue`
- `components/dokumente/DocumentShareModal.vue`

**Tests:**
- Upload/Download/Löschen mit Rollenprüfung.
- Mieter sieht nur Dokumente mit `sichtbarkeit IN ('mieter','beide')` oder gezielte Freigabe.
- Magic-Bytes-Check blockiert gefälschte Dateien.

**Meilenstein:**
> Vermieter und Mieter können Dokumente hochladen; Mieter sieht nur freigegebene Dateien.

---

### Phase 7: Ticket-System (7–10 PT)

**Ziel:** Störungsmeldungen mit Kategorie, Priorität, Status-Workflow, Kommentaren, SLA & Trigger.

**Tabellen:** `tickets`, `ticket_kommentare`, `ticket_sla`, `ticket_trigger`, `handwerker`, `einheiten`, `mieter`, `users`.

**Backend-Routen:**
- `/api/v1/tickets` (CRUD)
- `POST /api/v1/tickets/{id}/status`
- `/api/v1/tickets/{id}/kommentare`
- `POST /api/v1/tickets/{id}/assign`
- `/api/v1/ticket-sla`
- `/api/v1/ticket-trigger`
- `/api/v1/handwerker` (Roadmap-Vorbereitung)

**Status-Workflow:** `offen → in_bearbeitung → wartend_auf_mieter / wartend_auf_handwerker → erledigt → geschlossen` (+ `abgelehnt`)

**Frontend-Komponenten / Views:**
- `views/mieter/TicketCreateView.vue`
- `views/mieter/TicketsView.vue`
- `views/vermieter/TicketsView.vue`, `TicketDetailView.vue`
- `components/tickets/TicketStatusBadge.vue`
- `components/tickets/TicketCommentThread.vue`
- `components/tickets/TicketFilterBar.vue`

**Tests:**
- Integration: Mieter erstellt Ticket → Keyword-Classifier setzt Kategorie/Priorität → Vermieter kommentiert → Status ändert sich.
- SLA-Cron: unbeantwortetes dringendes Ticket eskaliert nach Geschäftszeiten.
- Trigger: neues Ticket → Notification an Vermieter.

**Meilenstein:**
> Mieter erstellt Ticket → System kategorisiert automatisch → Vermieter bearbeitet im UI.

---

### Phase 8: Kosten & Nebenkostenabrechnung (13–16 PT)

**Ziel:** Betriebskosten erfassen, automatische NK-Abrechnung pro Einheit/Jahr, Verteilung nach qm/Personen/Verbrauch, Mietzahlungen tracken.

**Tabellen:** `kosten`, `kostenkategorien`, `abrechnungen`, `abrechnung_positionen`, `mietzahlungen`, `mietvertraege`, `einheiten`, `objekte`.

**Backend-Routen:**
- `/api/v1/kosten` (CRUD)
- `POST /api/v1/kosten/{id}/scan` (OCR + KI-Extraktion Betrag/Kategorie/Umlagefähigkeit)
- `/api/v1/abrechnungen` (CRUD)
- `POST /api/v1/abrechnungen/{id}/calculate` (Positionen berechnen)
- `POST /api/v1/abrechnungen/{id}/finalize`
- `/api/v1/mietzahlungen` (Soll/Ist, Mahnstufe)
- `POST /api/v1/mietzahlungen/{id}/mark-paid`

**Frontend-Komponenten / Views:**
- `views/vermieter/KostenView.vue`, `KostenCreateModal.vue`
- `components/kosten/ReceiptScanPanel.vue`
- `views/vermieter/AbrechnungenView.vue`, `AbrechnungDetailView.vue`
- `components/abrechnung/AbrechnungPositionTable.vue`
- `views/vermieter/MietzahlungenView.vue`

**Tests:**
- NK-Abrechnung: Heizkosten 1.200 € / 100 qm × 50 qm = 600 € für WE.
- `UNIQUE(einheit_id, jahr)` partial-unique greift.
- Mietzahlung: Mahnstufe steigt bei Fehlbetrag.

**Meilenstein:**
> Vermieter erfasst Kosten mit Beleg-Scan; System erstellt NK-Abrechnung mit Positionen und Mietzahlungs-Tracking.

---

### Phase 9: Dashboard & Kennzahlen (7–9 PT)

**Ziel:** Alles auf einen Blick: KPIs, Objekt-Übersicht, offene Tickets, Fristen, Finanzen, Abo-Widget.

**Tabellen:** nutzt `objekte`, `einheiten`, `mieter`, `mietvertraege`, `kosten`, `mietzahlungen`, `tickets`, `abrechnungen`, `fristen`, `subscriptions`, `plan_usage`, `ai_stored_results`.

**Backend-Routen:**
- `GET /api/v1/dashboard/summary`
- `GET /api/v1/dashboard/object/{id}`
- `GET /api/v1/dashboard/insights`
- `GET /api/v1/dashboard/financials`

**Kennzahlen:**
- Bruttomietrendite, Nettomietrendite, Eigenkapitalrendite, Cash-on-Cash, DSCR, LTV, Gesamtrendite, Vermietungsquote.

**Frontend-Komponenten / Views:**
- `views/vermieter/DashboardView.vue`
- `components/dashboard/KPICard.vue`, `KPIGrid.vue`
- `components/dashboard/ObjectOverview.vue` (Vermietungs-Progressbar)
- `components/dashboard/OpenTicketsWidget.vue`
- `components/dashboard/DeadlinesWidget.vue`
- `components/dashboard/FinanceWidget.vue`
- `components/dashboard/SubscriptionWidget.vue`

**Tests:**
- Unit: Berechnungs-Engine mit/ohne Finanzierung.
- Integration: Dashboard-Daten isoliert pro Vermieter.

**Meilenstein:**
> Dashboard zeigt korrekte Rendite-KPIs, Vermietungsquote, offene Tickets und das aktuelle Abo-Widget.

---

### Phase 10: KI-Schicht — Presidio, OCR, Ollama (14–17 PT)

**Ziel:** 3-Schicht-Modell: lokal anonymisieren → Ollama Cloud → lokal verarbeiten.

**Tabellen:** `ai_stored_results`, `audit_logs`, `einwilligungen`, `events`.

**Backend-Komponenten:**
- `services/ai/presidio.py` (Anonymisierung + Deanonymisierung)
- `services/ai/ollama_client.py` (GLM 5.2 + Kimi K2.6)
- `services/ai/keyword_classifier.py` (heiz/wasser/elektrik/schimmel)
- `services/ai/prompts.py` (Prompt-Registry)
- `services/ocr/tesseract.py`

**Backend-Routen:**
- `POST /api/v1/ki/ticket-kategorie`
- `POST /api/v1/ki/ticket-prioritaet`
- `POST /api/v1/ki/antwort-entwurf`
- `POST /api/v1/ki/beleg-scan`
- `POST /api/v1/ki/mahnung`
- `POST /api/v1/ki/mieterhoehung`
- `POST /api/v1/ki/smart-insights` (täglich, gecacht)
- `POST /api/v1/ki/bewerbungs-summary`

**Frontend-Komponenten:**
- `components/ki/KIAssistantBubble.vue`
- `components/ki/KISuggestionButton.vue`
- `components/ki/ReceiptScanResult.vue`
- `components/ki/SmartInsightsPanel.vue`
- `components/ki/TicketDraftEditor.vue`

**Tests:**
- Presidio erkennt deutsche Namen, Adressen, IBAN, Geburtsdatum.
- Anonymisierter Prompt enthält keine PII; Deanonymisierung liefert Originalwerte zurück.
- KI-Cache (`ai_stored_results`) vermeidet doppelte Aufrufe.
- Keyword-Classifier erledigt 60 % ohne KI.

**Meilenstein:**
> Beleg-Upload → OCR + Presidio + GLM extrahiert Betrag/Kategorie/Umlagefähigkeit → Vorschlag im Kosten-Formular.

---

### Phase 11: E-Mail, Mahnungen & Fristen-Warner (9–12 PT)

**Ziel:** Transactional E-Mails via Resend, automatisiertes Mahnwesen, Fristen-Kalender.

**Tabellen:** `events`, `notifications`, `fristen`, `mietzahlungen`, `mietvertraege`, `subscriptions`, `dokumente`.

**Backend-Routen:**
- `POST /api/v1/notifications/{id}/resend`
- `GET /api/v1/notifications`
- `GET /api/v1/fristen`
- `POST /api/v1/fristen`
- `PATCH /api/v1/fristen/{id}/done`
- `POST /api/v1/mahnungen/{mietzahlung_id}/send` (erzeugt PDF + E-Mail)
- `POST /api/v1/webhooks/resend` (Bounce/Status)

**Hintergrund-Jobs:**
- Täglicher Mahn-Cron (Tag 3/7/14/21)
- Fristen-Warner (6/3/1 Monate vor Mietende, 12-Monats-Abrechnungsfrist)
- Trial-Ablauf-Erinnerung (Tag 7/12/13)

**Frontend-Komponenten / Views:**
- `views/vermieter/MahnungenView.vue`
- `views/vermieter/FristenView.vue` (Kalender + Liste)
- `components/fristen/DeadlineCalendar.vue`
- `components/notifications/NotificationList.vue`

**Tests:**
- E-Mail-Versand stubbed; Status wird in `notifications` korrekt gesetzt.
- Mahnstufe steigt mit Cron; gesperrter Account sendet keine Mahnungen.
- Fristen wechseln Warnstufen green → yellow → red.

**Meilenstein:**
> Fällige Miete löst nach 3 Tagen Mahnung Stufe 1 aus; E-Mail wird via Resend versendet und im UI protokolliert.

---

### Phase 12: PDF-Export & Vorlagen (6–8 PT)

**Ziel:** Dokumente mit Briefkopf generieren, statische Vorlagen + KI-generierte Texte.

**Tabellen:** `dokumente`, `objekte`, `einheiten`, `mieter`, `mietvertraege`, `bankverbindungen`, `kosten`, `abrechnungen`.

**Backend-Routen:**
- `POST /api/v1/dokumente/generate`
- `GET /api/v1/dokumente/{id}/pdf`
- `POST /api/v1/abrechnungen/{id}/pdf`
- `POST /api/v1/mahnungen/{id}/pdf`

**Vorlagen:**
- Statisch (10): Wohnungsgeberbestätigung, Meldebescheinigung, Übergabeprotokolle, Kaution-Abrechnung, Standard-Mietvertrag, Einzugs-/Auszugsbestätigung, Schufa-Einverständnis, Nebenkostenabrechnung (Zahlen).
- KI-generiert (8): Mahnungen Stufe 1–3, Mieterhöhung § 558 BGB, Abmahnung, Kündigung, Abrechnungserklärungstext, individuelles Anschreiben.

**Frontend-Komponenten:**
- `components/dokumente/DocumentGeneratorModal.vue`
- `components/dokumente/PDFPreview.vue`
- `components/dokumente/TemplateSelector.vue`

**Tests:**
- Wohnungsgeberbestätigung enthält Briefkopf (Vermieter-Adresse, Bankdaten).
- KI-generierte Mahnung lässt sich editieren, bevor PDF erzeugt wird.
- PDF-Download nur für berechtigte Rollen.

**Meilenstein:**
> Vermieter generiert Wohnungsgeberbestätigung mit Briefkopf als PDF im Browser.

---

### Phase 13: DSGVO, Compliance & Hardening (10–12 PT)

**Ziel:** Datenschutz-Export, Löschung, IP-Blocking, Security-Headers, Logging, VVT/AVV, Go-Live-Härtung.

**Tabellen:** `users`, `mieter`, `einheiten`, `objekte`, `bewerbungen`, `mietvertraege`, `kosten`, `abrechnungen`, `abrechnung_positionen`, `bankverbindungen`, `dokumente`, `einwilligungen`, `audit_logs`.

**Backend-Routen:**
- `GET /api/v1/dsgvo/export` (ZIP: JSON-Daten + Dokumente)
- `POST /api/v1/dsgvo/delete-request` (Soft-Delete + 30-Tage-Countdown)
- `POST /api/v1/dsgvo/widerspruch`
- `GET /api/v1/dsgvo/vvt` (Verzeichnis Verarbeitungstätigkeiten, nur Admin)

**DSGVO-Features:**
- PII-Filter-Middleware + structlog (JSON-Logs).
- IP-Blocking via MaxMind GeoLite2 (nur DE/AT/CH + Whitelist).
- Security-Headers: HSTS, CSP-Nonce, X-Frame-Options, Permissions-Policy.
- Soft-Delete-Cron: Daten nach Fristen endgültig löschen (außer `einwilligungen`, `audit_logs`).

**Frontend-Komponenten / Views:**
- `views/settings/DatenschutzView.vue`
- `views/public/ImpressumView.vue`, `DatenschutzView.vue`

**Tests:**
- DSGVO-Export enthält alle personenbezogenen Daten.
- Nicht-DACH-IP wird mit 403 blockiert.
- Logs enthalten keine Passwörter, IBANs, Geburtsdaten.

**Meilenstein:**
> DSGVO-Export liefert vollständige ZIP; nicht-deutsche IP wird abgewiesen; alle Security-Headers aktiv.

---

### Phase 14: Admin-Center (paralleler Stream, 8–9 PT)

**Ziel:** Internes Verwaltungsportal für uns als SaaS-Betreiber.

**Tabellen:** `users`, `subscriptions`, `plan_usage`, `audit_logs`, `events`, `notifications`, `ai_stored_results`, `bankverbindungen`, `referrals`.

**Backend-Routen (Admin-Scope, 2FA + IP-Whitelist):**
- `GET /api/v1/admin/users`
- `POST /api/v1/admin/users/{id}/suspend`
- `POST /api/v1/admin/users/{id}/impersonate` (30-Min-Limit)
- `GET /api/v1/admin/subscriptions`
- `POST /api/v1/admin/subscriptions/{id}/refund`
- `GET /api/v1/admin/payments` (Stripe-Zahlungen)
- `GET /api/v1/admin/audit-logs`
- `GET /api/v1/admin/ki-costs`
- `GET /api/v1/admin/leads`
- `GET/POST /api/v1/admin/feature-flags`
- `POST /api/v1/admin/maintenance-mode`
- `GET /api/v1/admin/system/health`

**Frontend-Komponenten / Views:**
- `views/admin/AdminDashboard.vue`
- `views/admin/UserManagement.vue`
- `views/admin/SubscriptionManagement.vue`
- `views/admin/AuditLogView.vue`
- `views/admin/KICostsView.vue`
- `views/admin/FeatureFlagsView.vue`
- `components/admin/ImpersonateBanner.vue`

**Tests:**
- Admin-Route nur für `role=admin`.
- Impersonate-Audit-Log enthält Start/Ende/Zeitstempel.
- Stripe-Refund wird über Admin-Center ausgelöst und im Abo-Status reflektiert.

**Meilenstein:**
> Admin kann Vermieter sperren/entsperren, als Vermieter einloggen, Stripe-Refund auslösen und Feature-Flags toggeln.

---

### Phase 15: Production Deploy & Go-Live (6–7 PT)

**Ziel:** MVP auf Proxmox produktiv verfügbar, deploybar über GitHub-Tag.

**Artefakte:**
- GitHub Actions: `.github/workflows/deploy-beta.yml` (SSH auf Proxmox bei `v0.x-beta.y`)
- systemd-Units: `backend.service`, `frontend-build.service`, `worker.service`, `cloudflared.service`
- nginx-Config (Reverse Proxy, SSL via Cloudflare/Origin-Cert oder Let’s Encrypt)
- `deploy/scripts/deploy-native.sh` (git pull → venv update → pnpm install → alembic upgrade → build → service restart → health-check)
- Rollback-Skript
- Monitoring: Prometheus + Grafana (optional) oder einfacher Health-Check-Endpoint.

**Tests:**
- Smoke-Test: 5 Beispiel-Vermieter anlegen, Trial abonnieren, Objekt/Mieter/Ticket/Abrechnung durchspielen.
- Deploy-Rollback: alte Version startet innerhalb von 5 Minuten.

**Meilenstein:**
> `https://mietverwaltung.de` erreichbar; erste reale Registrierung + Trial-Abschluss funktioniert.

---

## 5. Aufwandsübersicht
| Phase | Backend | Frontend | DevOps | QA | Gesamt |
|-------|---------|----------|--------|-----|--------|
| 0 — Native Fundament & DB v4.1 | 3 | 2 | 2 | 1 | **8–10** |
| 1 — Auth, 2FA, Security, Audit | 6 | 2.5 | 1.5 | 2 | **12–14** |
| 2 — Stripe & WE-Billing | 7 | 2 | 2 | 2 | **10–13** |
| 3 — Onboarding | 2 | 2 | 0.5 | 1 | **4–6** |
| 4 — Domain-Core | 8 | 4 | 1 | 2 | **13–16** |
| 5 — Mieter-Bewerbung | 4 | 2 | 0.5 | 1.5 | **5–8** |
| 6 — Dokumenten-Management | 3.5 | 2.5 | 1 | 1.5 | **5–8** |
| 7 — Ticket-System | 5 | 3 | 1 | 2 | **7–10** |
| 8 — Kosten & NK-Abrechnung | 9 | 3.5 | 1 | 2.5 | **13–16** |
| 9 — Dashboard & Kennzahlen | 3 | 3 | 0.5 | 1.5 | **7–9** |
| 10 — KI-Schicht | 10 | 3.5 | 1.5 | 3 | **14–17** |
| 11 — E-Mail, Mahnungen, Fristen | 6 | 2 | 1.5 | 2 | **9–12** |
| 12 — PDF & Vorlagen | 4 | 3 | 0.5 | 1.5 | **6–8** |
| 13 — DSGVO & Hardening | 6 | 2 | 2.5 | 2 | **10–12** |
| 14 — Admin-Center (parallel) | 5 | 3 | 1.5 | 1.5 | **8–9** |
| 15 — Production Deploy | 2 | 1 | 2 | 1.5 | **6–7** |
| **Summe** | **83.5** | **41.0** | **20.5** | **28.5** | **137–175** |

*Gesamtsoll: ca. 137–175 PT. Puffer in Phase 0/15.*
---

## 6. Risiken & Gegenmaßnahmen

| Risiko | Wahrscheinlichkeit | Auswirkung | Gegenmaßnahme |
|--------|-------------------|------------|---------------|
| Stripe-Webhook-Signatur/Proration komplex | Mittel | Hoch | Webhook-Tests mit `stripe-cli`, Idempotenz-Keys, Reconciliation-Cron |
| WE-basiertes Pricing-UX überfordert Nutzer | Mittel | Mittel | Pricing-Slider + Live-Kalkulation + Tooltips, A/B-Test später |
| Presidio erkennt deutsche PII nicht 100 % | Mittel | Hoch | Custom-Regeln, Quality-Feedback-Loop, manuelle Review-Flag |
| Native Dev ohne Docker = mehr Setup-Arbeit | Mittel | Mittel | `setup-dev.sh`, `Makefile`, systemd-Units, dokumentierte Schritte |
| Redis auf 4 GB RAM optional belastend | Niedrig | Mittel | Für MVP Redis optional; Cache-Fallback In-Memory mit TTL |
| Resend-Bounce/Spam-Reputation | Mittel | Mittel | DKIM/SPF/DMARC, eigene Subdomain, Bounce-Webhook |
| Ollama Cloud API-Ausfall | Mittel | Hoch | Keyword-Fallback, Redis-Cache, Health-Check, Nutzer informieren |
| Trial-Missbrauch (mehrfache KK-Testaccounts) | Mittel | Hoch | Fingerprinting, E-Mail-Verifizierung, Stripe-Radar |

---

## 7. Nächste Schritte

1. Build-Plan v3 im Team/User finalisieren (Issue #24).
2. DB-Schema v4.1 als Alembic-Initial-Migration erstellen (Issues #17–#21).
3. Stripe-Testkonto + Webhook-Endpoint vorbereiten.
4. Resend-Konto + Absender-Domain konfigurieren.
5. Native-Dev-Skripte (`setup-dev.sh`, `run-backend.sh`, `run-frontend.sh`) im Repo anlegen.
6. Redis installieren und in Health-Check integrieren.
7. Phase 0 starten: Venv, pnpm, DB, Alembic, erster `/health`-Commit.

---

**Plan erstellt:** 13. November 2026  
**Status:** Bereit zur Freigabe — danach Phase 0 starten
