# Repo-Struktur & Change-Management — MietVerwaltung SaaS

> **Projekt:** MietVerwaltung SaaS für private Kleinvermieter in DACH  
> **Tech-Stack:** Python FastAPI + Vue.js 3 + PostgreSQL 17 + Redis + Ollama Cloud KI  
> **MVP:** Closed Beta für 10 Tester auf Proxmox (0€, nicht kommerziell)  
> **Späteres Go-Live:** Hetzner 2-Server-Split (CX22 Frontend + CX32 Backend)  
> **Entwickler:** Max Karthoff + Hermes Agent (KI-Builder)  
> **Dokumentstatus:** v1.0 — Fundament für Build-Plan Phase 0  

---

## 1. Repo-Strategie: Monorepo vs Multi-Repo

### 1.1 Entscheidung: Monorepo

Wir entscheiden uns für ein **Monorepo**: Frontend, Backend, Datenbank-Migrationen, Shared-Typen, Docker-Setup, CI/CD und Dokumentation leben in einem einzigen privaten GitHub-Repository.

### 1.2 Begründung

| Kriterium | Monorepo | Multi-Repo |
|-----------|----------|------------|
| **1 Entwickler + KI-Builder** | Eine Sache von Interesse, ein `git status`, ein PR. Weniger Kontextwechsel. | Mehrere Repos synchronisieren → Mehr Aufwand, höhere Fehlerwahrscheinlichkeit. |
| **MVP-Phase** | Schnelles Iterieren, gemeinsame Milestones, alles auf einen Blick. | Overhead für Release-Koordination über mehrere Repos. |
| **Gemeinsame Abhängigkeiten** | DB-Schema, API-Pydantic-Schemas und TypeScript-Typen können zentral gepflegt werden. | API-Vertrag muss manuell zwischen Repos synchron gehalten werden. |
| **API-Verträge synchron halten** | **Kernargument:** Backend definiert Pydantic-Schemas, aus denen automatisiert OpenAPI und TypeScript-Typen generiert werden. | Risiko, dass Frontend- und Backend-Types auseinanderdriften. |
| **Deployment** | Ein Tag / ein Release enthält immer kompatible Versionen von Frontend und Backend. | Versions-Mismatch bei getrennten Deployments möglich. |
| **CI/CD** | Eine GitHub Actions-Suite kann alle Services linten, testen und bauen. | Mehrere Pipelines, Duplikate, komplexere Orchestrierung. |
| **Dokumentation** | README, CHANGELOG, Architekturdoku zentral. | Aufgesplittert, schnell veraltet. |
| **Nachteile** | Größeres Repo, längere CI-Laufzeiten, subtilere Berechtigungen. | Bei unserer Größe (<100 Dateien im MVP) irrelevant. |

### 1.3 Multi-Repo wäre sinnvoll, wenn...

- Das Frontend-Team und das Backend-Team unabhängig deployen wollen (hier: 1 Mensch + KI).
- Unterschiedliche Lizenzmodelle oder öffentliche Repos geplant sind (hier: alles private, einheitlich).
- Ein Service in einer anderen Sprache/Runtime existiert, die getrennt versioniert werden muss (hier: alles Docker-basiert).

**Fazit:** Für den MVP und die erste Wachstumsphase ist Monorepo die effizientere Wahl. Eine Aufspaltung in Multi-Repo wird erst bei einem dedizierten Frontend-Team oder eigenständigen Microservices (z.B. separates KI-Service) neu evaluiert.

### 1.4 API-Vertrag-Synchronisation

Die größte Gefahr eines Monorepos mit Frontend + Backend ist ein inkonsistenter API-Vertrag. Das verhindern wir durch:

1. **Single Source of Truth im Backend:** Alle Request/Response-Schemas werden in `backend/app/schemas/` als Pydantic-Modelle definiert.
2. **OpenAPI-Export:** FastAPI erzeugt `/openapi.json`. Das ist Teil jedes Builds und wird unter `shared/openapi.json` committet.
3. **Automatische TypeScript-Generierung:** Ein CI-Job (`generate-api-types`) wandelt `shared/openapi.json` mit `openapi-typescript` in `shared/types/api.d.ts` um.
4. **Frontend-Import:** Das Vue-Frontend importiert ausschließlich aus `shared/types/api.d.ts`. Manuelle TypeScript-Duplikate sind verboten.
5. **Build-Blockade:** Wenn `openapi.json` und `api.d.ts` nicht übereinstimmen, schlägt der CI-Build fehl.
6. **API-Versioning:** Ab dem ersten öffentlichen Release wird die API-Version im Pfad geführt (`/api/v1/...`). Breaking Changes erfordern `/api/v2/...`.

---

## 2. Vollständige Verzeichnis-Struktur

```
mietverwaltung/                              # Repository-Root
│
├── .github/
│   ├── workflows/
│   │   ├── lint.yml                         # Backend + Frontend Linting (Push/PR)
│   │   ├── test.yml                         # pytest + vitest (Push/PR)
│   │   ├── build.yml                        # Docker-Builds (Push/PR)
│   │   ├── security.yml                     # bandit, trivy, npm audit (Push/PR)
│   │   ├── generate-api-types.yml           # OpenAPI → TypeScript (bei Schema-Änderungen)
│   │   ├── deploy-beta.yml                  # Deploy auf Proxmox (nur Tags)
│   │   └── deploy-prod.yml                  # Deploy auf Hetzner (nur Release-Tags)
│   ├── pull_request_template.md             # PR-Checkliste
│   ├── issue_templates/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── dependabot.yml                       # npm + pip Updates
│
├── .husky/                                  # Git hooks (optional, s.u.)
│   └── pre-commit
│
├── .env.example                             # Nur Beispielwerte, committed
├── .env.dev                                 # Dev-Secrets, NICHT committed
├── .env.prod                                # Prod-Secrets, NICHT committed
├── .gitignore                               # Global + sprachspezifisch
├── .dockerignore                            # Für schnellere Builds
├── docker-compose.yml                       # Produktion / Standard
├── docker-compose.dev.yml                   # Dev mit Hot-Reload, Volumes, MailHog
├── docker-compose.test.yml                  # CI-Test-Stack (ephemeral DB)
├── docker-compose.override.yml              # Lokale Dev-Overrides (ignored)
├── Makefile                                 # make dev, make test, make migrate, make deploy-beta
├── README.md                                # Projekt-Übersicht
├── ARCHITECTURE.md                          # System-Architektur
├── CHANGELOG.md                             # Automatisch aus Conventional Commits
├── CONTRIBUTING.md                          # Regeln für Mensch + KI
├── LICENSE.md                               # Proprietär / Closed Beta
├── package.json                             # Root-Dev-Tools (husky, lint-staged, openapi-typescript)
└── pnpm-workspace.yaml                      # Falls pnpm workspaces genutzt werden
│
├── backend/                                 # FastAPI-Anwendung
│   ├── Dockerfile
│   ├── Dockerfile.dev                       # Dev-Image mit watchfiles
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pyproject.toml                       # ruff, mypy, pytest, bandit Konfiguration
│   ├── alembic.ini
│   ├── entrypoint.sh                        # Migration + Start
│   ├── healthcheck.py                       # Docker HEALTHCHECK
│   │
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako                   # Template für neue Migrationen
│   │   └── versions/
│   │       ├── 0001_initial_schema.py       # Initial-Migration DB-Schema v4
│   │       ├── 0002_add_user_sessions.py
│   │       └── ...                          # Weitere Migrationen
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                          # FastAPI App-Factory
│   │   ├── config.py                        # Pydantic-Settings (env-basiert)
│   │   ├── database.py                      # SQLAlchemy Engine + Session
│   │   ├── dependencies.py                  # Gemeinsame FastAPI-Dependencies
│   │   ├── lifespan.py                      # Startup/Shutdown-Events
│   │   │
│   │   ├── models/                          # SQLAlchemy-Modelle
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── user_session.py
│   │   │   ├── einwilligung.py
│   │   │   ├── objekt.py
│   │   │   ├── einheit.py
│   │   │   ├── einheit_ausstattung.py
│   │   │   ├── mieter.py
│   │   │   ├── mieter_historie.py
│   │   │   ├── bewerbung.py
│   │   │   ├── mietvertrag.py
│   │   │   ├── mietvertrag_aenderung.py
│   │   │   ├── kostenkategorie.py
│   │   │   ├── kosten.py
│   │   │   ├── mietzahlung.py
│   │   │   ├── abrechnung.py
│   │   │   ├── abrechnung_position.py
│   │   │   ├── dokument.py
│   │   │   ├── dokument_freigabe.py
│   │   │   ├── ticket.py
│   │   │   ├── ticket_kommentar.py
│   │   │   ├── ticket_sla.py
│   │   │   ├── ticket_trigger.py
│   │   │   ├── event.py
│   │   │   ├── notification.py
│   │   │   ├── frist.py
│   │   │   ├── audit_log.py
│   │   │   ├── onboarding_progress.py
│   │   │   ├── ai_stored_result.py
│   │   │   ├── referral.py
│   │   │   ├── handwerker.py
│   │   │   ├── subscription.py              # Abo-Modell
│   │   │   └── plan_usage.py
│   │   │
│   │   ├── schemas/                         # Pydantic-Request/Response-Modelle
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── objekt.py
│   │   │   ├── einheit.py
│   │   │   ├── mieter.py
│   │   │   ├── mietvertrag.py
│   │   │   ├── kosten.py
│   │   │   ├── abrechnung.py
│   │   │   ├── dokument.py
│   │   │   ├── ticket.py
│   │   │   ├── dashboard.py
│   │   │   └── subscription.py
│   │   │
│   │   ├── routes/                          # API-Endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── objekte.py
│   │   │   ├── einheiten.py
│   │   │   ├── mieter.py
│   │   │   ├── mietvertraege.py
│   │   │   ├── kosten.py
│   │   │   ├── abrechnungen.py
│   │   │   ├── dokumente.py
│   │   │   ├── tickets.py
│   │   │   ├── dashboard.py
│   │   │   ├── notifications.py
│   │   │   ├── subscriptions.py
│   │   │   ├── dsgvo.py
│   │   │   └── health.py
│   │   │
│   │   ├── services/                        # Business-Logik
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── objekt_service.py
│   │   │   ├── einheit_service.py
│   │   │   ├── mieter_service.py
│   │   │   ├── mietvertrag_service.py
│   │   │   ├── kosten_service.py
│   │   │   ├── abrechnung_service.py
│   │   │   ├── dokument_service.py
│   │   │   ├── ticket_service.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── subscription_service.py
│   │   │   ├── email_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── mahnung_service.py
│   │   │   ├── frist_service.py
│   │   │   ├── export_service.py
│   │   │   ├── pdf_service.py
│   │   │   ├── template_service.py
│   │   │   ├── ki/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ollama_client.py
│   │   │   │   ├── anonymizer.py            # Presidio-basiert
│   │   │   │   ├── deanonymizer.py
│   │   │   │   ├── keyword_classifier.py
│   │   │   │   ├── ocr_engine.py            # Tesseract + PyMuPDF
│   │   │   │   ├── prompts.py               # Prompt-Templates
│   │   │   │   ├── cache.py                 # Redis-Caching für KI
│   │   │   │   └── fallback.py
│   │   │   └── crypto_service.py
│   │   │
│   │   ├── middleware/                      # FastAPI-Middleware
│   │   │   ├── __init__.py
│   │   │   ├── auth_middleware.py
│   │   │   ├── role_middleware.py
│   │   │   ├── csrf_middleware.py
│   │   │   ├── rate_limit_middleware.py
│   │   │   ├── geoip_middleware.py
│   │   │   ├── audit_middleware.py
│   │   │   ├── security_headers.py
│   │   │   └── error_handler.py
│   │   │
│   │   ├── templates/                       # Jinja2-PDF-Templates
│   │   │   ├── briefkopf.html
│   │   │   ├── wohnungsgeberbestaetigung.html
│   │   │   ├── meldebescheinigung.html
│   │   │   ├── uebergabeprotokoll.html
│   │   │   ├── kaution_abrechnung.html
│   │   │   ├── standard_mietvertrag.html
│   │   │   ├── mahnung_stufe_1.html
│   │   │   ├── mahnung_stufe_2.html
│   │   │   ├── mahnung_stufe_3.html
│   │   │   ├── mieterhoehung_558.html
│   │   │   ├── abmahnung.html
│   │   │   ├── kuendigung.html
│   │   │   ├── abrechnung.html
│   │   │   └── email/
│   │   │       ├── welcome_vermieter.html
│   │   │       ├── welcome_mieter.html
│   │   │       ├── neues_ticket.html
│   │   │       ├── ticket_antwort.html
│   │   │       ├── mahnung.html
│   │   │       └── passwort_reset.html
│   │   │
│   │   ├── static/                          # Statische Backend-Assets
│   │   │   └── .gitkeep
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── crypto.py                    # AES-256-GCM
│   │       ├── validators.py
│   │       ├── pagination.py
│   │       ├── audit.py                     # Audit-Log-Helper
│   │       ├── exceptions.py
│   │       └── logger.py                    # JSON-Logging
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py                      # pytest-Fixtures
│   │   ├── factories.py                     # Model-Factory (factory_boy)
│   │   ├── unit/
│   │   │   ├── test_auth_service.py
│   │   │   ├── test_kosten_service.py
│   │   │   ├── test_abrechnung_service.py
│   │   │   └── test_ki_anonymizer.py
│   │   ├── integration/
│   │   │   ├── test_auth_api.py
│   │   │   ├── test_objekte_api.py
│   │   │   ├── test_tickets_api.py
│   │   │   └── test_abrechnung_api.py
│   │   └── fixtures/
│   │       ├── sample_rechnung.pdf
│   │       └── sample_ausweis.png
│   │
│   └── scripts/
│       ├── seed_data.py                     # Testdaten für Dev/Beta
│       ├── create_admin.py
│       └── rotate_keys.py
│
├── frontend/                                # Vue.js 3-Anwendung
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   ├── nginx.conf                           # Produktions-nginx im Container
│   ├── package.json
│   ├── pnpm-lock.yaml                       # Oder package-lock.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   ├── index.html
│   ├── env.d.ts
│   │
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── env.ts                           # Environment-Helper
│   │   │
│   │   ├── api/                             # API-Client + auto-generierte Typen
│   │   │   ├── client.ts                    # zentrale Axios-Instance
│   │   │   ├── interceptors.ts              # Token-Refresh, Fehlerbehandlung
│   │   │   └── types/
│   │   │       └── api.d.ts                 # Symlink zu shared/types/api.d.ts
│   │   │
│   │   ├── router/
│   │   │   ├── index.ts
│   │   │   ├── guards.ts                    # Auth + Rollen-Guards
│   │   │   ├── routes/
│   │   │   │   ├── auth.ts
│   │   │   │   ├── vermieter.ts
│   │   │   │   ├── mieter.ts
│   │   │   │   └── public.ts
│   │   │   └── route-meta.ts
│   │   │
│   │   ├── stores/                          # Pinia
│   │   │   ├── auth.ts
│   │   │   ├── user.ts
│   │   │   ├── objekte.ts
│   │   │   ├── einheiten.ts
│   │   │   ├── mieter.ts
│   │   │   ├── tickets.ts
│   │   │   ├── kosten.ts
│   │   │   ├── dashboard.ts
│   │   │   ├── notifications.ts
│   │   │   └── ui.ts                        # Theme, Darkmode, Modals
│   │   │
│   │   ├── views/
│   │   │   ├── auth/
│   │   │   │   ├── LoginView.vue
│   │   │   │   ├── RegisterView.vue
│   │   │   │   ├── TwoFactorView.vue
│   │   │   │   ├── SetupTOTPView.vue
│   │   │   │   └── PasswordResetView.vue
│   │   │   ├── vermieter/
│   │   │   │   ├── DashboardView.vue
│   │   │   │   ├── ObjekteView.vue
│   │   │   │   ├── ObjektDetailView.vue
│   │   │   │   ├── EinheitDetailView.vue
│   │   │   │   ├── MieterView.vue
│   │   │   │   ├── MieterDetailView.vue
│   │   │   │   ├── MietvertraegeView.vue
│   │   │   │   ├── KostenView.vue
│   │   │   │   ├── AbrechnungenView.vue
│   │   │   │   ├── AbrechnungDetailView.vue
│   │   │   │   ├── TicketsView.vue
│   │   │   │   ├── TicketDetailView.vue
│   │   │   │   ├── DokumenteView.vue
│   │   │   │   ├── EinstellungenView.vue
│   │   │   │   ├── PlanView.vue
│   │   │   │   └── DSGVOView.vue
│   │   │   ├── mieter/
│   │   │   │   ├── MieterDashboardView.vue
│   │   │   │   ├── MieterTicketsView.vue
│   │   │   │   ├── MieterDokumenteView.vue
│   │   │   │   └── MieterProfilView.vue
│   │   │   └── public/
│   │   │       ├── LandingView.vue
│   │   │       ├── ImpressumView.vue
│   │   │       ├── DatenschutzView.vue
│   │   │       └── CookieView.vue
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                          # Basis-UI-Komponenten
│   │   │   │   ├── AppButton.vue
│   │   │   │   ├── AppInput.vue
│   │   │   │   ├── AppSelect.vue
│   │   │   │   ├── AppModal.vue
│   │   │   │   ├── AppCard.vue
│   │   │   │   ├── AppTable.vue
│   │   │   │   ├── AppBadge.vue
│   │   │   │   ├── AppToast.vue
│   │   │   │   ├── AppSkeleton.vue
│   │   │   │   └── AppProgressBar.vue
│   │   │   ├── layout/
│   │   │   │   ├── AppLayout.vue
│   │   │   │   ├── Sidebar.vue
│   │   │   │   ├── TopBar.vue
│   │   │   │   ├── MobileNav.vue
│   │   │   │   └── Footer.vue
│   │   │   ├── dashboard/
│   │   │   │   ├── KPICard.vue
│   │   │   │   ├── ObjektCard.vue
│   │   │   │   ├── TicketPreview.vue
│   │   │   │   ├── FinanzPreview.vue
│   │   │   │   ├── SmartInsights.vue
│   │   │   │   └── QuickActions.vue
│   │   │   ├── objekte/
│   │   │   │   ├── ObjektForm.vue
│   │   │   │   ├── EinheitForm.vue
│   │   │   │   ├── AusstattungForm.vue
│   │   │   │   ├── EinheitCard.vue
│   │   │   │   └── MieterHistorie.vue
│   │   │   ├── mieter/
│   │   │   │   ├── MieterForm.vue
│   │   │   │   ├── MieterCard.vue
│   │   │   │   └── BewerbungForm.vue
│   │   │   ├── tickets/
│   │   │   │   ├── TicketForm.vue
│   │   │   │   ├── TicketList.vue
│   │   │   │   ├── TicketDetail.vue
│   │   │   │   ├── KIAntwortVorschlag.vue
│   │   │   │   └── StatusBadge.vue
│   │   │   ├── kosten/
│   │   │   │   ├── KostenForm.vue
│   │   │   │   ├── BelegScan.vue
│   │   │   │   ├── AbrechnungPreview.vue
│   │   │   │   └── UmlageSlider.vue
│   │   │   ├── dokumente/
│   │   │   │   ├── UploadDropzone.vue
│   │   │   │   ├── DokumentListe.vue
│   │   │   │   └── DokumentPreview.vue
│   │   │   ├── auth/
│   │   │   │   ├── TOTPSetup.vue
│   │   │   │   └── EmailCodeInput.vue
│   │   │   └── ki/
│   │   │       ├── KIAssistant.vue          # Schwimmende Bubble
│   │   │       ├── KIChatPanel.vue
│   │   │       └── KISparkleBadge.vue
│   │   │
│   │   ├── composables/                     # Vue-Composables
│   │   │   ├── useAuth.ts
│   │   │   ├── useApi.ts
│   │   │   ├── useToast.ts
│   │   │   ├── useDarkMode.ts
│   │   │   ├── usePlanLimits.ts
│   │   │   └── useUpload.ts
│   │   │
│   │   ├── assets/
│   │   │   ├── logo.svg
│   │   │   ├── logo-white.svg
│   │   │   └── icons/
│   │   │       └── ...
│   │   │
│   │   └── styles/
│   │       ├── tailwind.css
│   │       ├── theme.css                     # CSS-Variablen für Navy-Theme
│   │       └── animations.css
│   │
│   ├── public/
│   │   ├── favicon.ico
│   │   ├── manifest.json                     # PWA
│   │   ├── robots.txt
│   │   └── apple-touch-icon.png
│   │
│   └── tests/
│       ├── unit/
│       │   ├── components/
│       │   │   └── KPICard.spec.ts
│       │   └── composables/
│       │       └── useAuth.spec.ts
│       ├── integration/
│       │   └── router.spec.ts
│       └── e2e/
│           └── auth.spec.ts
│
├── shared/                                  # API-Vertrag zwischen Backend & Frontend
│   ├── openapi.json                         # Auto-generiert aus FastAPI
│   ├── types/
│   │   └── api.d.ts                         # Auto-generiert aus openapi.json
│   ├── constants/
│   │   ├── roles.ts
│   │   ├── ticket_status.ts
│   │   ├── kostenkategorien.ts
│   │   └── plan_limits.ts
│   └── schemas/
│       └── shared_schemas.json              # Optional: JSON-Schema für Validierung
│
├── db/                                      # Datenbank-Skripte (Migrationen primär in backend/alembic)
│   ├── init/
│   │   ├── 00-create-extensions.sql         # pgcrypto, uuid-ossp
│   │   ├── 01-rls-policies.sql             # Row-Level Security
│   │   └── 02-seed-reference-data.sql        # BetrKV-Katalog, Ticket-SLA-Defaults
│   ├── seeds/
│   │   ├── demo_vermieter.sql
│   │   └── beta_testers.sql
│   ├── backups/
│   │   └── .gitkeep                          # Backup-Skripte landen hier lokal
│   └── scripts/
│       ├── backup.sh
│       ├── restore.sh
│       └── verify-backup.sh
│
├── docker/                                  # Zusätzliche Docker-Images
│   ├── backend/
│   │   └── Dockerfile
│   ├── frontend/
│   │   └── Dockerfile
│   ├── postgres/
│   │   ├── Dockerfile
│   │   └── init-scripts/
│   ├── redis/
│   │   └── redis.conf
│   └── mailhog/
│       └── Dockerfile                        # Dev-E-Mail-Catcher
│
├── nginx/                                   # Reverse-Proxy-Konfigurationen
│   ├── dev/
│   │   └── default.conf
│   ├── beta/
│   │   └── mietverwaltung-beta.conf          # Proxmox Beta
│   └── prod/
│       └── mietverwaltung.conf               # Hetzner Produktion
│
├── scripts/                                 # Betriebs-Skripte
│   ├── dev/
│   │   ├── start-dev.sh                      # Docker Compose Dev hochfahren
│   │   ├── stop-dev.sh
│   │   ├── reset-dev-db.sh
│   │   └── seed-dev.sh
│   ├── deploy/
│   │   ├── deploy-beta.sh                    # GitHub Actions ruft dies auf Proxmox
│   │   ├── deploy-prod.sh                    # GitHub Actions ruft dies auf Hetzner
│   │   ├── rollback-beta.sh
│   │   └── rollback-prod.sh
│   ├── ops/
│   │   ├── health-check.sh                   # Server-Healthcheck
│   │   ├── backup.sh                         # pg_dump + Upload Storage Box
│   │   ├── restore.sh
│   │   ├── cleanup-uploads.sh                # Temp-Dateien löschen
│   │   ├── rotate-secrets.sh                 # JWT/DB-Keys rotieren
│   │   └── update-geoip.sh                   # MaxMind GeoLite2 aktualisieren
│   └── ci/
│       ├── generate-api-types.sh
│       ├── bump-version.sh
│       └── validate-migrations.sh
│
├── docs/                                    # Ergänzende Dokumentation
│   ├── api/
│   │   └── auth-flow.md
│   ├── security/
│   │   ├── csp-nonce-strategy.md
│   │   ├── rate-limiting.md
│   │   └── geoip-blocking.md
│   ├── ki/
│   │   ├── prompt-registry.md
│   │   └── anonymization-protocol.md
│   ├── operations/
│   │   ├── runbooks/
│   │   │   ├── incident-response.md
│   │   │   └── database-restore.md
│   │   └── onboarding-new-developer.md
│   └── decisions/
│       └── adr-001-monorepo.md               # Architecture Decision Record
│
└── monitoring/                              # Observability-Konfiguration
    ├── prometheus/
    │   └── prometheus.yml
    ├── grafana/
    │   └── dashboards/
    │       └── mietverwaltung.json
    └── loki/
        └── loki-config.yml
```

### 2.1 Wichtige Design-Entscheidungen zur Struktur

- **`shared/`** ist die Brücke zwischen Backend und Frontend. Es enthält ausschließlich generierte Dateien plus sprachübergreifende Konstanten. Niemand editiert `api.d.ts` manuell.
- **`backend/app/models/`** folgt 1:1 dem DB-Schema v4 (30+ Tabellen). Dateinamen sind Deutsch, Klassennamen gemäß Python-Konvention.
- **`backend/app/schemas/`** definiert den öffentlichen API-Vertrag. Hier entscheidet sich, welche Felder das Frontend sieht.
- **`backend/app/services/`** trennt Business-Logik von HTTP-Layer. Services sind unabhängig von FastAPI testbar.
- **`frontend/src/api/types/api.d.ts`** ist ein Symlink oder Post-Build-Kopie aus `shared/types/api.d.ts`, damit IDE-Autocompletion funktioniert.
- **`docs/decisions/`** fasst wichtige Architekturentscheidungen als ADRs zusammen (z.B. Monorepo, Presidio, Ollama Cloud).

---

## 3. Branching-Strategie

### 3.1 Entscheidung: Trunk-Based Development (TBD) mit geschütztem `main`

Wir nutzen **Trunk-Based Development** — eine Abwandlung des GitHub Flow, die für 1 Entwickler + KI im MVP optimal ist.

### 3.2 Warum nicht Git Flow?

Git Flow mit `main`, `develop`, `release/*` und langen Feature-Branches ist für schnelle MVP-Iteration zu schwerfällig. Wir brauchen keine Release-Branches, weil wir Continuous Deployment auf Tags/Release-Releases betreiben. Git Flow würde unnötige Merge-Konflikte und veraltete Branches produzieren.

### 3.3 Warum nicht reiner GitHub Flow?

GitHub Flow (`main` + feature-Branches, nach PR sofort mergen) ist prinzipiell nah dran. Wir ergänzen ihn um:

- Einen stabilen `main`, der jederzeit deploybar ist.
- Kurzlebige Feature-Branches (max. 1-3 Tage Lebensdauer).
- Einen Beta-Deploy nur über Tags, nicht jeden Merge.
- Manuelle Freigabe für Production-Releases.

### 3.4 Branches, die wir wirklich brauchen

| Branch | Zweck | Lebensdauer | Schutz |
|--------|-------|-------------|--------|
| `main` | Produktions-Code. Jeder Commit ist deploybar. | Dauerhaft | ✅ Geschützt |
| `feature/<kurzbeschreibung>` | Neue Features, Refactorings, Bugfixes. | 1-3 Tage, danach PR → `main` | ❌ Kein Schutz |
| `hotfix/<kurzbeschreibung>` | Kritische Fixes, die sofort in Produktion müssen. | Wenige Stunden | ❌ Kein Schutz |

**Wir brauchen KEINEN `dev` oder `develop` Branch.** Die Closed Beta wird aus `main` getaggt und auf Proxmox deployed. Für 1 Entwickler + KI wäre ein extra Branch reiner Verwaltungsaufwand ohne Mehrwert.

### 3.5 Branch-Namen Konvention

```
feature/auth-2fa-setup
feature/ticket-auto-kategorie
feature/db-subscription-tabelle
fix/api-types-generation
hotfix/login-csrf-token
refactor/kosten-service-tests
docs/architecture-adrs
```

- Kleinschreibung
- Wörter durch Bindestrich getrennt
- Präfix: `feature/`, `fix/`, `hotfix/`, `refactor/`, `docs/`, `ci/`, `test/`

### 3.6 Branch-Protection-Regeln für `main`

Im privaten Repository mit 1 Menschen und 1 KI-Builder:

| Regel | Einstellung | Begründung |
|-------|-------------|------------|
| **Restrict pushes that create files larger than 100 MiB** | ✅ Aktiv | Verhindert versehentliche Commits von großen Dateien. |
| **Require a pull request before merging** | ✅ Aktiv | Selbst bei 1 Person: PR-Template zwingt zur Reflexion. |
| **Require approvals** | ⚠️ 1 Approval | Max Karthoff als menschlicher Approval-Pflicht. |
| **Require review from Code Owners** | ✅ Aktiv | `CODEOWNERS` verpflichtet Max für kritische Pfade. |
| **Dismiss stale PR approvals** | ✅ Aktiv | Nach neuem Commit muss Review erneuert werden. |
| **Require status checks to pass** | ✅ Aktiv | `lint`, `test`, `build`, `security` müssen grün sein. |
| **Require branches to be up to date before merging** | ✅ Aktiv | Verhindert, dass veraltete Feature-Branches gemergt werden. |
| **Require conversation resolution** | ✅ Aktiv | Alle Review-Kommentare müssen geklärt sein. |
| **Restrict who can push to matching branches** | ✅ Max + KI-Bot | Kein direkter Push auf `main`. |
| **Allow force pushes** | ❌ Deaktiviert | Force-Push auf `main` ist verboten. |
| **Allow deletions** | ❌ Deaktiviert | `main` darf nicht gelöscht werden. |

**Ausnahme Hotfix:** In echten Notfällen kann Max als Admin-Berechtigung temporär umgehen, muss aber danach einen Post-Mortem-Eintrag in `docs/decisions/` oder CHANGELOG setzen.

### 3.7 Umgang mit KI-generierten Commits

Da Hermes Agent (KI) Code generiert und committet, brauchen wir klare Regeln:

1. **KI committet niemals direkt in `main`.** Alle KI-Änderungen laufen über einen Feature-Branch.
2. **KI-Commits identifizieren sich durch `chore(bot):` oder `feat(bot):` mit `[skip ci]` nur für rein technische Meta-Änderungen.** Bei normalen Commits läuft CI.
3. **Jeder KI-generierte PR benötigt menschliche Freigabe durch Max**, außer er fällt unter die unten definierte "Auto-Merge-Light"-Kategorie.
4. **Im PR-Body muss stehen:**
   - Welche User-Story / Aufgabe wurde umgesetzt?
   - Welche Dateien wurden geändert?
   - Welche Tests wurden ausgeführt?
   - Gibt es DB-Migrationen?
   - Gibt es Breaking Changes?
   - Ist eine manuelle Nacharbeit nötig?
5. **Max behält das Recht, jeden KI-PR zu requesten oder abzulehnen**, auch wenn CI grün ist.

### 3.8 Auto-Merge-Light (KI darf direkt mergen)

Folgende Änderungen dürfen nach grünem CI von der KI ohne menschliche Freigabe in `main` gemergt werden:

- `docs(*):` reine Dokumentations-Updates
- `chore(deps):` Dependabot-artige Patch-Updates von Sicherheits-fixes
- `chore(ci):` Rein technische CI-Optimierungen, die keine Produktions-Änderung enthalten
- `refactor(test):` Nur Test-Dateien, keine Produktionslogik

**Voraussetzung:** CI läuft grün, keine Migrationen, keine Breaking Changes, keine `CODEOWNERS`-Pfade betroffen.

---

## 4. Commit-Konventionen

### 4.1 Conventional Commits

Wir verwenden [Conventional Commits](https://www.conventionalcommits.org/) in deutscher Sprache für den menschlichen Teil, technische IDs können Englisch sein.

### 4.2 Typen (Types)

| Type | Bedeutung | Beispiel |
|------|-----------|----------|
| `feat` | Neues Feature | `feat(auth): TOTP-Setup für Vermieter hinzufügen` |
| `fix` | Bugfix | `fix(tickets): Status-Übergang von erledigt zu geschlossen korrigiert` |
| `docs` | Dokumentation | `docs: ADR für Monorepo-Entscheidung hinzufügen` |
| `style` | Formatierung (keine Logikänderung) | `style(frontend): Tailwind-Klassen sortieren` |
| `refactor` | Refactoring ohne externes Verhalten | `refactor(kosten): Umlageberechnung in Service auslagern` |
| `perf` | Performance-Verbesserung | `perf(db): Index auf tickets.status hinzufügen` |
| `test` | Tests hinzufügen/ändern | `test(auth): 2FA-Fallback-Tests ergänzen` |
| `chore` | Wartung/Build/Deps | `chore(deps): FastAPI auf 0.115 aktualisieren` |
| `ci` | CI/CD-Änderungen | `ci: Security-Scan mit Trivy hinzufügen` |
| `build` | Build-System | `build(docker): Multi-Stage-Build für Frontend optimieren` |
| `revert` | Revert eines vorherigen Commits | `revert: feat(db): SERIAL zu IDENTITY wechseln` |

### 4.3 Scopes

Scopes sind klein, fachlich und nach Domain-Bereichen gruppiert:

| Scope | Bereich |
|-------|---------|
| `auth` | Login, Register, 2FA, JWT, Sessions |
| `users` | Benutzer, Rollen, Profile |
| `objekte` | Objektverwaltung |
| `einheiten` | Einheiten, Ausstattung, Historie |
| `mieter` | Mieter, Bewerbungen |
| `mietvertraege` | Mietverträge, Änderungen |
| `kosten` | Betriebskosten, Kategorien, Belege |
| `abrechnung` | NK-Abrechnung, Positionen |
| `tickets` | Ticket-System, Kommentare, SLA |
| `dokumente` | Upload, Download, Verschlüsselung |
| `dashboard` | KPIs, Insights |
| `db` | Migrationen, Schema, RLS |
| `api` | API-Vertrag, OpenAPI, Typen |
| `shared` | Generierte Typen/Schemas |
| `ci` | GitHub Actions |
| `deps` | Abhängigkeiten |
| `security` | CSP, Rate-Limiting, GeoIP |
| `ops` | Deploy, Backup, Monitoring |

### 4.4 Commit-Message-Format

```
<type>(<scope>): <kurze Zusammenfassung im Imperativ>

<längere Beschreibung, optional>

Refs: <Issue/PR-Nummer oder Task-ID>
BREAKING CHANGE: <Beschreibung, falls vorhanden>
```

### 4.5 Beispiele

```
feat(auth): TOTP-Setup für Vermieter und Mieter implementieren

- Hinzufügen von pyotp zur requirements.txt
- Endpunkte /auth/totp/setup und /auth/totp/verify
- Frontend: TOTPSetup.vue mit QR-Code-Anzeige
- Feld-Verschlüsselung für totp_secret mit AES-256-GCM

Refs: #42
```

```
fix(abrechnung): Verteilung nach qm berücksichtigt unvermietete Zeiträume

Vorher wurde die Gesamt-qm des Objekts genutzt, unabhängig vom
Abrechnungszeitraum. Jetzt wird nur die bewohnte qm pro Monat summiert.

Refs: #67
```

```
feat(db): Subscription- und Plan-Usage-Tabellen hinzufügen

- Neue Tabellen subscriptions, plan_usage
- RLS-Policies für beide Tabellen
- Seed-Daten für Free/Basis/Pro/Business Pläne

BREAKING CHANGE: Benötigt Migration 0003_add_subscriptions
Refs: #88
```

### 4.6 Changelog-Generierung

Wir nutzen die Node.js-Toolchain im Root-`package.json`:

- **`standard-version`** oder **`release-please`** (empfohlen) generiert `CHANGELOG.md` aus Conventional Commits.
- **Konfiguration** in `.release-please-config.json`.
- **Manueller Ablauf:**
  1. Alle offenen Feature-Branches in `main` mergen.
  2. Lokal: `pnpm release` (ruft `release-please release-pr` auf).
  3. Release-PR wird erstellt.
  4. Max approved und merged.
  5. GitHub Actions deployed automatisch auf Proxmox/Hetzner.

**CHANGELOG-Sections:**

```markdown
## [0.3.0-beta.2](https://github.com/.../compare/v0.3.0-beta.1...v0.3.0-beta.2) (2026-11-15)

### Features
* feat(tickets): SLA-basierte Eskalation implementieren (#112)

### Bug Fixes
* fix(auth): Refresh-Token-Cookie auf Safari korrekt setzen (#115)

### BREAKING CHANGES
* API-Pfad für Abrechnungen von /api/abrechnung auf /api/v1/abrechnungen geändert.
```

---

## 5. Versionierung

### 5.1 Semantic Versioning

Wir folgen strikt [SemVer 2.0.0](https://semver.org/lang/de/):

```
MAJOR.MINOR.PATCH
```

| Komponente | Wann bumpen? | Beispiel |
|------------|--------------|----------|
| **MAJOR** | Breaking Change in API oder Datenbank, das manuell migriert werden muss. | `v0.x → v1.0.0` erst beim öffentlichen Launch mit stabiler API. |
| **MINOR** | Neues Feature, rückwärtskompatibel. | `v0.1.0 → v0.2.0` bei NK-Abrechnung. |
| **PATCH** | Bugfix, rückwärtskompatibel. | `v0.1.1` bei Hotfix. |

### 5.2 Pre-Release Tags für MVP

Bis zum öffentlichen Launch (v1.0.0) bleiben wir bei Major-Version 0 und Pre-Release-Tags:

| Phase | Version | Bedeutung |
|-------|---------|-----------|
| Closed Beta Proxmox | `v0.1.0-beta.1` | Erster interner Build |
| Closed Beta mit 10 Testern | `v0.2.0-beta.3` | Stabilere Beta |
| Hetzner-Preview / Staging | `v0.8.0-rc.1` | Release Candidate |
| Öffentlicher Launch | `v1.0.0` | Produktionsreif |

### 5.3 Version-Tags

- Tags werden nur von `main` erstellt.
- Format: `v{MAJOR}.{MINOR}.{PATCH}[-{pre-release}.{n}]`
- Beispiele:
  - `v0.1.0-beta.1`
  - `v0.2.0-beta.3`
  - `v0.5.0`
  - `v1.0.0`

### 5.4 API-Versionierung

- Interne API-Version wird im URL-Pfad geführt: `/api/v1/...`
- Solange wir unter `v1.0.0` sind, ist die API-Version noch `v0` (oder bereits `v1` Preview). Bei öffentlichem Launch wird API `v1` offiziell.
- Breaking API-Changes erfordern neues Major-Release und ggf. `/api/v2/...`.

### 5.5 Docker-Image-Versionierung

- Images werden mit Git-Tag versioniert: `ghcr.io/.../backend:v0.2.0-beta.3`
- Zusätzlich: `latest` nur auf explizite Releases, niemals auf Beta-Tags.
- Für Beta: `beta` Tag zusätzlich zum konkreten Versionstag.

---

## 6. CI/CD Pipeline (GitHub Actions)

### 6.1 Überblick Workflows

| Workflow | Auslöser | Zweck |
|----------|----------|-------|
| `lint.yml` | Push/PR auf `main`, `feature/*` | ruff, mypy, eslint, vue-tsc |
| `test.yml` | Push/PR | pytest (Backend), vitest (Frontend) |
| `build.yml` | Push/PR | Docker-Images bauen, Layer-Caching prüfen |
| `security.yml` | Push/PR + wöchentlich | bandit, trivy, npm audit |
| `generate-api-types.yml` | Änderung in `backend/app/schemas/` | OpenAPI → TypeScript prüfen/regenerieren |
| `deploy-beta.yml` | Push von `v0.*-beta.*` Tags | Deploy auf Proxmox |
| `deploy-prod.yml` | Push von `v*.*.*` Release-Tags (ohne -beta/-rc) | Deploy auf Hetzner |

### 6.2 `lint.yml`

```yaml
name: Lint

on:
  push:
    branches: [main, feature/*, hotfix/*]
  pull_request:
    branches: [main]

jobs:
  backend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - run: pip install ruff mypy
      - run: ruff check backend/
      - run: ruff format --check backend/
      - run: mypy backend/app

  frontend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
      - run: pnpm install
      - run: pnpm -C frontend lint
      - run: pnpm -C frontend type-check  # vue-tsc --noEmit
```

### 6.3 `test.yml`

```yaml
name: Test

on:
  push:
    branches: [main, feature/*, hotfix/*]
  pull_request:
    branches: [main]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:17-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
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
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - run: pip install -r backend/requirements-dev.txt
      - run: cd backend && alembic upgrade head
      - run: cd backend && pytest -q --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v4

  frontend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
      - run: pnpm install
      - run: pnpm -C frontend test:unit
```

### 6.4 `security.yml`

```yaml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 3 * * 1'  # Montag 03:00 UTC

jobs:
  bandit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install bandit[toml]
      - run: bandit -r backend/app -f json -o bandit-report.json || true
      - run: bandit -r backend/app -ll  # fail on MEDIUM+

  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'HIGH,CRITICAL'

  npm-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
      - run: pnpm audit --audit-level high
```

### 6.5 `generate-api-types.yml`

```yaml
name: Generate API Types

on:
  push:
    paths:
      - 'backend/app/schemas/**'
      - 'backend/app/routes/**'
      - 'backend/app/main.py'
    branches: [main]

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r backend/requirements.txt
      - run: python backend/scripts/export_openapi.py > shared/openapi.json
      - uses: pnpm/action-setup@v3
      - run: pnpm install
      - run: pnpm exec openapi-typescript shared/openapi.json -o shared/types/api.d.ts
      - name: Commit changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add shared/openapi.json shared/types/api.d.ts
          git diff --cached --quiet || git commit -m "chore(shared): regenerate OpenAPI types"
          git push
```

### 6.6 `deploy-beta.yml` (Proxmox)

```yaml
name: Deploy Beta

on:
  push:
    tags:
      - 'v0.*-beta.*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: beta
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Proxmox via SSH
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.PROXMOX_BETA_HOST }}
          username: ${{ secrets.PROXMOX_BETA_USER }}
          key: ${{ secrets.PROXMOX_BETA_SSH_KEY }}
          script: |
            cd /opt/mietverwaltung
            git fetch --tags
            git checkout ${{ github.ref_name }}
            docker compose -f docker-compose.yml down
            docker compose -f docker-compose.yml pull
            docker compose -f docker-compose.yml up -d --build
            docker compose exec backend alembic upgrade head
            ./scripts/ops/health-check.sh
```

### 6.7 `deploy-prod.yml` (Hetzner)

Analog zu Beta, aber:

- Auslöser: Tags `v[0-9]+.[0-9]+.[0-9]+` ohne `-beta`/`-rc`.
- Ziel: Hetzner CX22 + CX32.
- Vor Deploy: Production-Freigabe durch Max über GitHub Environment.
- Nach Deploy: Smoke-Tests gegen `https://mietverwaltung.de/api/health`.

### 6.8 Pre-commit Hooks

Wir nutzen Husky + lint-staged:

```json
// package.json (Root)
{
  "lint-staged": {
    "backend/**/*.py": [
      "ruff check --fix",
      "ruff format",
      "mypy --ignore-missing-imports"
    ],
    "frontend/**/*.{ts,vue}": [
      "eslint --fix",
      "vue-tsc --noEmit"
    ],
    "*.md": [
      "markdownlint --fix"
    ]
  },
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged"
    }
  }
}
```

**Wichtig:** Pre-commit Hooks sind lokal optional, aber empfohlen. CI ist die verbindliche Prüfung, damit KI-Commits in Cloud-Umgebungen auch geprüft werden.

### 6.9 Secrets in GitHub Actions

| Secret | Zweck | Woher |
|--------|-------|-------|
| `PROXMOX_BETA_HOST` | IP/Hostname Proxmox Beta | Max |
| `PROXMOX_BETA_USER` | SSH-User | Max |
| `PROXMOX_BETA_SSH_KEY` | SSH-Private-Key | Max generiert |
| `HETZNER_PROD_FRONTEND_HOST` | CX22 IP | Hetzner |
| `HETZNER_PROD_BACKEND_HOST` | CX32 IP | Hetzner |
| `HETZNER_PROD_SSH_KEY` | SSH-Private-Key | Max generiert |
| `GHCR_TOKEN` | Push/Pull Docker Images | GitHub PAT mit `write:packages` |
| `CODECOV_TOKEN` | Coverage-Upload | Codecov |
| `OLLAMA_API_KEY` | Optional: KI-Tests in CI | Ollama Cloud |

**Kein Secret wird je im Repository-Code oder in Logs ausgegeben.** Alle Secrets werden per `${{ secrets.XXX }}` referenziert. Docker Images enthalten keine `.env`-Dateien.

---

## 7. Change-Management

### 7.1 CHANGELOG.md

- `CHANGELOG.md` wird automatisch aus Conventional Commits generiert.
- Zusätzlich wird für jede Version ein **Release Notes-Dokument** in `docs/releases/v0.x.x.md` erstellt, das fachliche Zusammenhänge erklärt.
- Manuelle Einträge für Security-Fixes oder DSGVO-relevante Änderungen sind erlaubt und erwünscht.

### 7.2 Datenbank-Migrationen mit Alembic

| Aspekt | Regel |
|--------|-------|
| **Tool** | Alembic mit SQLAlchemy 2.x |
| **Initial-Migration** | `0001_initial_schema.py` erzeugt alle Tabellen des DB-Schema v4 |
| **Namen** | `XXXX_<beschreibung>.py`, z.B. `0002_add_user_sessions.py` |
| **Eine Änderung = Eine Migration** | Keine mehrfachen Schema-Änderungen in einer einzigen Migration, außer sie gehören semantisch zusammen. |
| **Downgrade muss möglich sein** | Jede Migration braucht eine funktionierende `downgrade()`-Funktion. |
| **Migrationen vor Deploy** | Immer `alembic upgrade head` **bevor** der neue Code live geht. |
| **Datenmigrationen** | Bei Bedarf eigene `data_upgrade()`-Funktion in der Migration, getrennt vom Schema. |
| **Test** | Jede PR mit DB-Änderung führt Migrationen in CI gegen eine frische PostgreSQL durch. |

### 7.3 Breaking Change-Prozess

1. **Erkennung:** Entwickler/KI markiert Commit mit `BREAKING CHANGE:`.
2. **Dokumentation:** Im PR-Body und im ADR-Ordner (`docs/decisions/adr-XXX-breaking-...`) wird der Grund dokumentiert.
3. **Kommunikation:** Beta-Tester werden per E-Mail über Breaking Changes informiert.
4. **Migrationspfad:** Wenn nötig, wird ein `scripts/migrations/` Hilfsskript bereitgestellt.
5. **Version:** Breaking Change erhöht MAJOR oder MINOR (bei Pre-Release).

### 7.4 Frontend-Backend-Kompatibilität

- **API-Version im Pfad:** `/api/v1/...`
- **OpenAPI-Datei committed:** `shared/openapi.json` ist Teil jedes Builds.
- **Typen-Generierung in CI:** Wenn Backend-Schemas sich ändern, wird `api.d.ts` neu generiert. Frontend-Build bricht, wenn Typen nicht passen.
- **Contract-Tests:** Für kritische Endpunkte gibt es JSON-Schema-Validierung in `backend/tests/integration/`.
- **Deprecation-Header:** Ältere API-Versionen erhalten `Deprecation`-Header mit Datum, ab dem sie entfernt werden.

### 7.5 Rollback-Strategie

| Ebene | Rollback-Methode | Zeitaufwand |
|-------|------------------|-------------|
| **Code** | `git checkout <previous-tag>` + Docker-Image mit vorherigem Tag ausrollen | 2-5 Min |
| **Datenbank** | Alembic `downgrade` auf vorherige Revision, dann altes Image starten | 5-15 Min |
| **Daten/Uploads** | Aus Backup (`db/backups/` bzw. Hetzner Storage Box) wiederherstellen | 15-60 Min |
| **DNS/Traffic** | Cloudflare / CloudPanel auf vorherige Instanz umleiten (nur Prod) | 1-5 Min |

**Automatisches Rollback bei fehlgeschlagenem Deploy:**

- Nach jedem Deploy läuft `health-check.sh`.
- Wenn Health-Check nach 3 Versuchen fehlschlägt:
  1. Docker-Container auf vorheriges Image zurücksetzen.
  2. Datenbank auf vorherige Alembic-Revision downgraden (falls Migration fehlgeschlagen).
  3. E-Mail-Alert an Max.
  4. Incident-Eintrag in `docs/operations/runbooks/`.

### 7.6 Environment-Promotion

Da wir im MVP nur Proxmox haben, ist die Promotion vereinfacht:

```
LOKAL (Entwickler-Notebook)
   │
   ▼
PROXMOX BETA (Closed Beta für 10 Tester)
   │
   ▼
HETZNER PROD (späterer Go-Live)
```

| Umgebung | Zweck | Deploy-Auslöser |
|----------|-------|-----------------|
| **Lokal** | Entwicklung, Hot-Reload, Tests | Manuell (`make dev`) |
| **Beta** | 10 Closed-Beta-Tester | Tag `v0.x.y-beta.z` |
| **Prod** | Öffentliche Nutzer | Release-Tag `v1.x.y` |

Später, wenn Budget vorhanden ist, kann eine **Staging-Umgebung** zwischen Beta und Prod eingefügt werden (`v0.x.y-rc.z`).

---

## 8. Code-Review-Prozess

### 8.1 Grundsatz bei 1 Entwickler + KI

Max Karthoff ist der einzige menschliche Entwickler und Change-Manager. Hermes Agent (KI) erzeugt Code, Tests, Dokumentation und Deployment-Skripte. Der Review-Prozess muss diesen hybriden Workflow abbilden.

### 8.2 Review-Level

| Level | Wer reviewed? | Wann? | Beispiele |
|-------|---------------|-------|-----------|
| **L1 — Automatisiert** | CI + Tools (ruff, mypy, pytest, eslint, trivy, bandit) | Jeder Commit / PR | Syntax, Format, Tests, Sicherheit |
| **L2 — KI-Review** | Hermes Agent prüft eigenen/einen anderen PR auf Vollständigkeit | Vor menschlicher Freigabe | Passt die Änderung zum Konzept? Gibt es offene Kanten? |
| **L3 — Menschlich** | Max Karthoff | Vor Merge in `main` | Architektur, DSGVO, Sicherheit, Business-Logik |

### 8.3 Wann braucht Max Freigabe?

Max muss freigeben bei Änderungen an:

- `backend/app/models/` (DB-Schema)
- `backend/alembic/versions/` (Migrationen)
- `backend/app/services/auth_service.py`
- `backend/app/middleware/security_headers.py`
- `backend/app/services/ki/anonymizer.py`
- `docker-compose.yml`, `docker-compose.prod.yml`
- `.github/workflows/deploy-*.yml`
- `shared/openapi.json`, `shared/types/api.d.ts`
- `docs/decisions/` (ADRs)
- Jeder `BREAKING CHANGE`

Max kann direkt mergen (ohne weiteren Review) bei:

- Reinen Dokumentations-Änderungen (`docs:`)
- Eigenen Hotfixes, wenn Notfall besteht (Post-Mortem nachträglich)
- Kleinere Refactorings mit 100% Testabdeckung

### 8.4 Wann kann KI direkt mergen?

Siehe Abschnitt 3.8 (Auto-Merge-Light). Zusätzlich: Nie bei Änderungen an `CODEOWNERS`-Pfaden oder bei `BREAKING CHANGE`.

### 8.5 PR-Template

`.github/pull_request_template.md`:

```markdown
## Zusammenfassung
<!-- Was ändert dieser PR? -->

## Geänderte Bereiche
- [ ] Backend
- [ ] Frontend
- [ ] Datenbank
- [ ] CI/CD
- [ ] Dokumentation
- [ ] DevOps / Scripts

## Tests
- [ ] Backend-Unit-Tests hinzugefügt/aktualisiert
- [ ] Frontend-Unit-Tests hinzugefügt/aktualisiert
- [ ] Manuell getestet (lokal)
- [ ] Integrationstests gegen Test-DB erfolgreich

## Breaking Changes
- [ ] Nein
- [ ] Ja — bitte unten beschreiben:

## DB-Migrationen
- [ ] Keine
- [ ] Neue Migration: `XXXX_name.py`

## Sicherheit / DSGVO
- [ ] Keine sensiblen Änderungen
- [ ] Neue Felder verschlüsselt
- [ ] Audit-Log ergänzt
- [ ] RLS-Policies ergänzt/aktualisiert

## Checkliste
- [ ] `make test` läuft lokal erfolgreich
- [ ] OpenAPI-Typen sind aktuell (`make generate-types`)
- [ ] CHANGELOG-Eintrag nicht vergessen (wird automatisch generiert)
- [ ] Dokumentation aktualisiert, falls nötig

## Screenshots / Deployment-Hinweise
<!-- Optional -->
```

### 8.6 CODEOWNERS

```
# Repository Root
* @maxkarthoff

# Kritische Bereiche erfordern menschliche Freigabe
backend/app/models/ @maxkarthoff
backend/alembic/versions/ @maxkarthoff
backend/app/services/auth_service.py @maxkarthoff
backend/app/services/ki/anonymizer.py @maxkarthoff
backend/app/middleware/ @maxkarthoff
docker-compose*.yml @maxkarthoff
.github/workflows/deploy-*.yml @maxkarthoff
shared/ @maxkarthoff
docs/decisions/ @maxkarthoff
```

---

## 9. Environment-Management

### 9.1 .env-Dateien

| Datei | Inhalt | Im Repo? |
|-------|--------|----------|
| `.env.example` | Beispielwerte, Dokumentation aller Variablen | ✅ Ja |
| `.env.dev` | Lokale Dev-Secrets | ❌ Nein (`.gitignore`) |
| `.env.prod` | Produktions-Secrets | ❌ Nein (`.gitignore`) |
| `.env.beta` | Beta/Proxmox-Secrets | ❌ Nein (`.gitignore`) |
| `.env.test` | Test-Konfiguration (kann committed sein, ohne echte Secrets) | ⚠️ Nur mit Dummy-Werten |

### 9.2 Secrets auf den Server bringen

| Umgebung | Methode | Details |
|----------|---------|---------|
| **Lokal** | `.env.dev` auf Entwicklungs-Maschine | Max pflegt lokal, nie committed |
| **Beta (Proxmox)** | `.env.beta` per GitHub Actions SCP/SSH auf Server | Secret wird in `PROXMOX_BETA_ENV_FILE` als GitHub Secret hinterlegt |
| **Prod (Hetzner)** | `.env.prod` per GitHub Actions auf CX22/CX32 | Secret wird in `HETZNER_PROD_ENV_FILE` hinterlegt |
| **Zukunft: SOPS** | Wenn Team wächst: Mozilla SOPS + Age/GPG für verschlüsselte `.env` im Repo | Optional, nicht MVP |

### 9.3 Dev-Umgebung auf Proxmox

- Hot-Reload für Backend (`watchfiles` oder `--reload`) und Frontend (Vite HMR).
- `docker-compose.dev.yml` mountet lokale Verzeichnisse als Volumes.
- E-Mail-Versand wird durch **MailHog** abgefangen (`http://localhost:8025`).
- Datenbank: PostgreSQL 17 im Container (nicht SQLite), damit Migrationen realistisch laufen.
- Redis: Im Container, exposed auf `localhost:6379`.

### 9.4 Beta-Umgebung auf Proxmox

- Betrieben wie Prod, aber mit Testdaten und eingeschränkter Zugriffsliste.
- Domain via Cloudflared Tunnel (`*.trycloudflare.com`).
- Keine echten Kundendaten.
- Automatisches Backup täglich um 02:00 Uhr.
- Nach Deploy: Smoke-Tests gegen `/api/health`.

### 9.5 Environment-Variablen-Checkliste

```env
# === App ===
APP_ENV=development|beta|production
APP_URL=http://localhost:3000|https://beta...|https://mietverwaltung.de
DEBUG=true|false

# === Datenbank ===
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=mietverwaltung
POSTGRES_USER=mietverwaltung
POSTGRES_PASSWORD=<strong-random>
DATABASE_URL=postgresql+asyncpg://... (optional, überschreibt obige)
DB_ENCRYPTION_KEY=<32-byte-base64>

# === Redis ===
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=<optional>

# === Auth ===
JWT_SECRET=<strong-random>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=15
JWT_REFRESH_EXPIRE_DAYS=7
CSRF_SECRET=<strong-random>

# === KI (Ollama Cloud) ===
OLLAMA_BASE_URL=https://ollama.com/v1
OLLAMA_API_KEY=<api-key>
OLLAMA_MODEL_PRIMARY=glm-5.2
OLLAMA_MODEL_COMPLEX=kimi-k2.6

# === E-Mail (Resend empfohlen) ===
EMAIL_PROVIDER=resend
EMAIL_FROM=noreply@mietverwaltung.de
RESEND_API_KEY=<api-key>

# === GeoIP / Sicherheit ===
MAXMIND_LICENSE_KEY=<key>
ALLOWED_COUNTRIES=DE,AT,CH

# === DSGVO ===
DSGVO_RETENTION_CONTRACT_YEARS=10
DSGVO_RETENTION_BILLING_YEARS=6

# === Backup ===
BACKUP_ENCRYPTION_KEY=<strong-random>
STORAGE_BOX_USER=<user>
STORAGE_BOX_HOST=<host>
```

---

## 10. .gitignore

```gitignore
# ============================================
# GLOBAL
# ============================================
.env
.env.dev
.env.beta
.env.prod
.env.local
.env.*.local
!.env.example
!.env.test

*.log
*.pid
*.seed
*.pid.lock

# OS
.DS_Store
Thumbs.db
*.swp
*.swo
*~
.idea/
.vscode/
*.sublime-project
*.sublime-workspace

# ============================================
# PYTHON / BACKEND
# ============================================
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtualenvs
venv/
ENV/
env/
.venv/

# pytest / coverage
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/
coverage.xml
*.cover
.hypothesis/

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# ruff
.ruff_cache/

# Bandit
bandit-report.json

# Alembic / DB
*.db
*.sqlite
*.sqlite3

# ============================================
# NODE / FRONTEND
# ============================================
node_modules/
.pnpm-store/
.npm
.eslintcache
.stylelintcache

# Build output
frontend/dist/
frontend/.vite/
frontend/.output/
*.tsbuildinfo

# ============================================
# DOCKER
# ============================================
.dockerignore
# Ausnahme: Wir commiten .dockerignore im Root, aber nicht lokale Override
*.override.yml
!docker-compose.override.yml.example

# Volumes / Daten
pgdata/
redisdata/
uploads/
mailhog-data/

# ============================================
# SECRETS / KEYS
# ============================================
*.pem
*.key
*.crt
*.p12
*.pfx
secrets/
.age-key*
.sops.yaml

# ============================================
# BACKUPS / TEMP
# ============================================
db/backups/*.sql
db/backups/*.dump
db/backups/*.gz
db/backups/*.gpg
!db/backups/.gitkeep
tmp/
temp/
.tmp/

# ============================================
# GENERATED / SHARED (wenn Tool nicht läuft)
# ============================================
# Hinweis: shared/openapi.json und shared/types/api.d.ts werden committed,
# da sie den Vertrag dokumentieren. Falls jemand lokal generiert, sollten
# Änderungen reviewed und committed werden, nicht ignoriert.
```

---

## 11. Erste Schritte

### 11.1 GitHub-Repository erstellen

Max führt lokal aus (GH_TOKEN ist bereits vorhanden, read:org scope fehlt aber für `gh repo create` mit Teams — hier reicht es für ein privates Repo):

```bash
# Login prüfen (read:org fehlt, aber create geht)
gh auth status

# Repository erstellen
gh repo create mietverwaltung-saas \
  --private \
  --description "MietVerwaltung SaaS für private Kleinvermieter in DACH" \
  --source=. \
  --remote=origin \
  --push
```

Falls `--source` und `--push` nicht funktionieren wegen fehlendem `read:org`:

```bash
# Alternative: Remote manuell hinzufügen
git init
git add .
git commit -m "chore(init): initiales Repository-Setup"
git branch -M main
git remote add origin https://github.com/<user>/mietverwaltung-saas.git
git push -u origin main
```

### 11.2 Initiale Struktur anlegen

```bash
cd /root/mietverwaltung
mkdir -p backend/app/{models,schemas,routes,services/ki,middleware,templates/email,utils}
mkdir -p backend/alembic/versions backend/tests/{unit,integration,fixtures}
mkdir -p frontend/src/{api/types,router/routes,stores,views/{vermieter,mieter,public},components/{ui,layout,dashboard,objekte,mieter,tickets,kosten,dokumente,auth,ki},composables,assets/icons,styles}
mkdir -p frontend/public frontend/tests/{unit,integration,e2e}
mkdir -p shared/types shared/constants shared/schemas
mkdir -p db/init db/seeds db/backups db/scripts
mkdir -p docker/{backend,frontend,postgres/redis/mailhog}
mkdir -p nginx/{dev,beta,prod}
mkdir -p scripts/{dev,deploy,ops,ci}
mkdir -p docs/{api,security,ki,operations/runbooks,decisions}
mkdir -p monitoring/{prometheus,grafana/dashboards,loki}
mkdir -p .github/workflows .github/issue_templates .husky
```

### 11.3 Erste Dateien anlegen

| Datei | Inhalt |
|-------|--------|
| `README.md` | Projekt-Übersicht, Tech-Stack, Quickstart |
| `ARCHITECTURE.md` | System-Architektur, Datenflüsse, Security |
| `CONTRIBUTING.md` | Commit-Konventionen, Branching, Review-Prozess |
| `CHANGELOG.md` | Leer, wird automatisch gefüllt |
| `LICENSE.md` | Closed Beta / proprietär |
| `Makefile` | `dev`, `test`, `migrate`, `lint`, `generate-types`, `deploy-beta` |
| `package.json` | Root-Dev-Dependencies |
| `pyproject.toml` | Python-Tool-Konfiguration |
| `.env.example` | Alle notwendigen Env-Variablen mit Dummy-Werten |
| `.gitignore` | Wie in Abschnitt 10 |
| `docker-compose.yml` | Produktions-ähnlicher Stack |
| `docker-compose.dev.yml` | Dev mit Hot-Reload |
| `backend/app/main.py` | Minimaler FastAPI-Einstieg mit `/health` |
| `backend/app/config.py` | Pydantic-Settings |
| `backend/app/database.py` | SQLAlchemy-Setup |
| `frontend/src/main.ts` | Vue-3-Entry |
| `frontend/src/App.vue` | Root-Komponente |
| `frontend/vite.config.ts` | Vite-Konfiguration |
| `frontend/package.json` | Vue-Stack |

### 11.4 Initialer Commit

```bash
git init
git add .
git commit -m "chore(init): initiales Monorepo-Setup für MietVerwaltung SaaS

- Monorepo-Struktur für FastAPI + Vue.js 3
- Docker-Compose Dev/Prod
- CI/CD-Workflows (lint, test, build, security)
- Alembic + DB-Schema v4 initiale Migration
- API-Typen-Synchronisation über shared/openapi.json
- CHANGELOG, CONTRIBUTING, ARCHITECTURE

Refs: #1"
```

### 11.5 Initiale README.md (Vorlage)

```markdown
# MietVerwaltung SaaS

KI-gestützte Mietverwaltung für private Kleinvermieter in Deutschland, Österreich und der Schweiz.

## Tech-Stack

- **Backend:** Python 3.13, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic
- **Frontend:** Vue.js 3, Vite, Pinia, Vue Router, Tailwind CSS
- **Datenbank:** PostgreSQL 17 mit Row-Level Security
- **Cache:** Redis 7
- **KI:** Ollama Cloud (GLM 5.2 + Kimi K2.6)
- **Container:** Docker + Docker Compose

## Schnellstart

```bash
# 1. Repository klonen
git clone git@github.com:<user>/mietverwaltung-saas.git
cd mietverwaltung-saas

# 2. Umgebungsvariablen kopieren
cp .env.example .env.dev

# 3. Dev-Stack starten
make dev

# 4. Tests ausführen
make test
```

## Dokumentation

- [Architektur](ARCHITECTURE.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## Lizenz

Closed Beta — proprietär. Nicht für kommerzielle Weiterverbreitung.
```

---

## Anhang A: Zusammenfassung der wichtigsten Entscheidungen

| Thema | Entscheidung |
|-------|--------------|
| Repo-Strategie | Monorepo |
| Branching | Trunk-Based Development mit geschütztem `main` |
| Branches | `main`, `feature/*`, `hotfix/*` — kein `dev` |
| Commits | Conventional Commits, deutsche Beschreibung |
| Versionierung | SemVer mit Pre-Release-Tags (`v0.x.y-beta.z`) |
| CI/CD | GitHub Actions: lint, test, build, security, deploy |
| Pre-commit | Husky + lint-staged (optional lokal, verbindlich in CI) |
| API-Typen | OpenAPI → TypeScript, generiert in CI |
| DB-Migrationen | Alembic, jede Migration mit `downgrade()` |
| Deploy Beta | Proxmox bei Tag `v0.*-beta.*` |
| Deploy Prod | Hetzner CX22+CX32 bei Release-Tag |
| Rollback | Vorheriger Tag + Alembic `downgrade` |
| Secrets | `.env.*` nicht im Repo, GitHub Secrets + Server-Datei |
| Code-Review | L1 CI, L2 KI-Review, L3 Max-Freigabe |
| KI-Auto-Merge | Nur bei docs/chore/ci/test ohne kritische Pfade |

---

## Anhang B: Verknüpfung mit Server-Konzept und Build-Plan

- Das Server-Konzept (`Server-Konzept.md`, Abschnitt 11) definiert die grobe Verzeichnisstruktur. Dieses Dokument erweitert sie auf Dateiebene und ergänzt Change-Management, CI/CD und Governance.
- Der Build-Plan (`Build-Plan-v2.md`) legt die 12 Phasen fest. Dieses Dokument ist das operative Fundament für Phase 0 (Projekt-Fundament & Dev-Umgebung).
- Sobald das DB-Schema v4 fertig ist, wird die erste Alembic-Migration `backend/alembic/versions/0001_initial_schema.py` daraus erzeugt.

---

*Dokument erstellt: 2026-11-02*  
*Autor: Hermes Agent (KI-Builder)*  
*Status: Vorschlag für Max Karthoff zur Freigabe*
