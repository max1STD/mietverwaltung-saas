# REA-Analyse der 5 GitHub-Repos — MietVerwaltung SaaS

Ziel: Architektur, Module, Datenmodell, Geschäftslogik, KI-Integration, MCP-Server, API-Endpunkte und DACH-spezifische Logik der fünf geklonten Open-Source-Hausverwaltungen extrahieren und mit dem geplanten Stack **FastAPI / Vue.js / PostgreSQL** vergleichen.

Durchgeführt mit:
- `rea import-reference-source --path .` für alle Repos
- `rea analyze-javascript-application` für die JS-basierten Repos
- Code-Lecture (README, package/composer/pyproject, Schemas, Routen, Geschäftslogik) als Ergänzung, weil REA bei Quell-Repos primär Inventar- und Graph-Daten liefert

---

## 1. Mietfuchs — `speedone/mietfuchs`

### Stack
| Schicht | Technik |
|---------|---------|
| Frontend | React 19 + Vite + Tailwind 4 |
| Backend  | Express 5 + TypeScript (Node ≥ 24.15) |
| ORM/DB   | Drizzle ORM + SQLite (`mietfuchs.sqlite`) |
| Storage  | Lokaler Dateisystem-Ordner (`uploads/`, `briefpapier/`) |
| AI       | Ollama (lokal) oder OpenAI/IONOS/Mistral (optional, extern) |
| Build    | npm-workspace (root + `server/` + `client/`); Binaries via Bun |

### REA-Ergebnis
- `analyze-javascript-application` lieferte eine riesige Application-Graph-Evidence (ca. 128 MB JSON, 889 geparste JS-Dateien, 3.802 Knoten, 4.623 Kanten).
- Die automatische Zusammenfassung war für Electron-Apps optimiert und daher wenig aussagekräftig (0 BrowserWindows, 0 IPC etc. — Mietfuchs ist keine Electron-App).
- Wertvoll: vollständige Inventarisierung aller Module, statische Import-Beziehungen und Nachweis, dass es sich um eine **monolithische Express+React-Anwendung** handelt.
- REA lieferte keine semantische Architektur-Übersicht; diese musste aus README, `package.json`, `server/src/index.ts` und `server/src/db/schema.ts` manuell rekonstruiert werden.

### Architektur & Module
- **Monorepo** mit zwei Workspaces: `client/` (React SPA) und `server/` (Express API).
- Zentrale Geschäftslogik liegt im `shared/` Ordner (`shared/law/`, `shared/period.ts`, `shared/letter.ts` etc.) — wird von Server und Client geteilt.
- Server-Hauptdatei `server/src/index.ts` definiert ca. 100+ REST-Routen unter `/api/*`.
- Zentrale Domänen:
  - `db/repository.ts` — Stammdaten-CRUD (Objekte, Wohnungen, Mietverhältnisse, Zähler, Kosten)
  - `calc.ts` — Betriebskostenabrechnung
  - `snapshot.ts` / `heatingSnapshotFor.ts` — Bestands-Snapshots für Abrechnung
  - `letter.ts` / `letterDesign.ts` — PDF-Briefe/Briefpapier
  - `extract.ts` / `extractHeating.ts` — KI-gestützte Belegauswertung
  - `ai/*` — Ollama/OpenAI-Integration, Modellempfehlungen, Consent-Management
  - `bank/*` — CAMT-/MT940-Bankimport (nur lokale Dateien, kein Open Banking)

### Datenmodell (SQLite, 59 Tabellen)
Wichtige Entitäten:
- `properties`, `units`, `tenancies`
- `person_history`, `prepayments`, `flat_rates`, `base_rents`, `prepayment_overrides`
- `cost_items`, `cost_item_shares`, `cost_item_participants`, `cost_item_amounts`, `cost_item_self_amounts`
- `meters`, `readings`, `payments`
- `heating_plants`, `heating_periods`, `heating_service_values`, `heating_estimates`, `fuel_deliveries`
- `co2_statements`, `co2_refunds`
- `closed_settlements`, `closed_heating_settlements` — eingefrorene Abrechnungen
- `uploads`, `assessments`, `assessment_lines` — KI-Belegauswertung
- `settings`, `ai_slots`, `letter_texts`, `letter_design`

### Geschäftslogik (DACH)
- **BetrKV-konforme Nebenkostenabrechnung** mit Umlageschlüsseln: Wohnfläche, Personentage, Wohneinheiten, Verbrauch, Direktzuordnung, vereinbarte Anteile, Hausgeldabrechnung.
- **Heizkostenverordnung**: eigene Heizkostenabrechnung, Grund-/Verbrauchskosten, Warmwasseranteil, Mieterwechsel nach Gradtagen, Schätzung nach § 9a, mehrere Heizanlagen, Kesseltausch.
- **CO₂-Kostenaufteilungsgesetz (CO2KostAufG)**: Stufenmodell, Erstattung an selbstheizende Mieter.
- **§ 556 / § 560 BGB**: Fristen-Hinweise, Vorauszahlungsanpassung.
- **§ 35a EStG**: Lohnanteil in Abrechnung und Steuer-Übersicht.
- **Anlage V**: Steuer-Übersicht mit Eigennutzung, abziehbaren/privatem Anteil.
- **Hare-Verfahren** für centgenaue Verteilung.

### KI-Integration
- Optional. Lokale Auswertung via **Ollama** (Standard: `qwen3.5:4b`) oder externe OpenAI-kompatible APIs.
- Unterstützt PDF-Textebene, Scan und Handyfoto (Bilder werden an Ollama geschickt).
- Auswertungen werden gespeichert; Nutzer muss jede Position prüfen und buchen.
- Consent-Management für externe Anbieter, API-Key-Speicherung in `data/secrets.json`.

### MCP-Server
- **Nein.** Es gibt keinen MCP-Server und keine API-Key-gestützte externe Automatisierung.

### API-Endpunkte
- REST unter `/api/*`, ca. 100+ Routen.
- Beispiele: `GET /api/properties`, `POST /api/costItems`, `GET /api/settlement/:period`, `POST /api/assessments`, `PUT /api/ai/key`.
- Keine öffentliche API-Dokumentation, kein OpenAPI.

### Vergleich mit FastAPI/Vue.js/PostgreSQL
| Aspekt | Mietfuchs | Unser Stack (FastAPI/Vue/PostgreSQL) |
|--------|-----------|--------------------------------------|
| Backend | Express/TS — reif, aber viel manuelle Fehlerbehandlung | FastAPI — bessere Validierung, OpenAPI, Dependency Injection |
| Frontend | React 19/Vite | Vue 3 — passt, beide sind modern |
| DB | SQLite (lokal) | PostgreSQL (multi-tenant, skalierbar) |
| Architektur | Monolith, 1 Prozess | API + getrenntes Frontend, optional Microservices |
| KI | Ollama/OpenAI für Belege | gleiche Provider leicht übertragbar |
| MCP | fehlt | kann Vorbild von mietkartei/HaVeWa übernehmen |
| DACH-Logik | extrem ausgereift | großer Pool an übernehmbaren Regeln |
| Lizenz | AGPL-3.0 | kompatibel, wenn ebenfalls Open Source |

### Übernehmbar
- `shared/law/`-Module (BetrKV, HeizkostenV, CO2KostAufG, BGB-Fristen).
- Centgenaue Verteilung und Abrechnungs-Engine.
- KI-Belegauswertungs-Workflow mit Consent.

### Besser/Schlechter als unser Stack
- **Besser:** sehr tiefe DACH-Abrechnungslogik, lokale-first Datenschutz-Story, ausgefeilte Heizkosten/CO₂-Logik.
- **Schlechter:** SQLite limitiert Multi-User/Multi-Tenant; kein MCP; keine echte API-Doku; Frontend eng mit Server gekoppelt.

---

## 2. mietkartei.de — `OliverHennhoefer/mietkartei.de`

### Stack
| Schicht | Technik |
|---------|---------|
| Frontend | SvelteKit 3 + Svelte 5 + Vite |
| Backend  | SvelteKit server routes (+ Node-Adapter oder Cloudflare Workers) |
| ORM/DB   | Drizzle ORM + SQLite (`better-sqlite3`) oder Cloudflare D1 |
| Auth     | Eigenes OAuth + Sessions + API-Keys |
| AI       | Keine eigene KI, aber **MCP-Server** für Claude/ChatGPT |
| Deploy   | Docker oder Cloudflare Workers |

### REA-Ergebnis
- `analyze-javascript-application` lieferte Application-Graph-Evidence (ca. 123 MB JSON, 889 JS-Dateien).
- Wiederum Electron-fokussierte Summary wenig aussagekräftig.
- Wertvoll: Nachweis der SvelteKit-Struktur, vollständiges API- und MCP-Routen-Inventar.

### Architektur & Module
- Monorepo: `app/` (Anwendung), `website/`, `docs/`.
- SvelteKit-App-Router: jede Route kann Server-Logik enthalten (`+page.server.ts`, `+server.ts`).
- Zentrale Domänen unter `src/lib/server/`: leases, tenants, properties, operating-costs, statements, ledger, deposits, bank-imports, tasks, deadlines, tax.
- `src/lib/server/api/operations.ts` definiert **einen gemeinsamen Operationskatalog** für REST und MCP.

### Datenmodell (SQLite/D1, 55 Tabellen)
Wichtige Entitäten:
- `accounts`, `users`, `sessions`, `oauth_clients`, `api_keys`
- `properties`, `units`, `tenants`, `leases`, `lease_persons`, `lease_units`, `rent_changes`
- `payments`, `rent_charges`, `deposit_transactions`
- `expenses`, `cost_categories`, `allocation_keys`, `allocation_key_shares`, `cost_items`, `cost_item_unit_amounts`, `billing_circles`
- `meters`, `meter_readings`, `operating_cost_statements`, `statement_results`
- `bank_accounts`, `bank_connections`, `bank_imports`, `bank_transactions`, `matching_rules`
- `documents`, `association_statements`, `tax_years`, `insurance_policies`
- `tasks`, `outbox`, `audit_log`

### Geschäftslogik (DACH)
- Betriebskostenabrechnung mit nachvollziehbarem Rechenweg pro Mieter.
- Mietkonto (Soll/Ist), Bankabgleich, Rückstands-Erkennung.
- Index- und Staffelmiete, Kaution.
- Hausgeldabrechnung für Eigentumswohnungen (WEG).
- Steuerübersicht / Anlage V.
- CSV-Import, vollständiger Export.

### KI-Integration
- Kein eigener KI-Beleg-Parser.
- Stattdessen: **MCP-Server** unter `/mcp`, der Claude/ChatGPT erlaubt, direkt auf die Daten zuzugreifen und zu schreiben.

### MCP-Server
- **Ja**, zentraler Bestandteil.
- `POST /mcp` mit JSON-RPC, Bearer-Auth (API-Key oder OAuth-Token).
- Tools umfassen: `list_properties`, `get_property`, `list_leases`, `get_rent_ledger`, `list_balances`, `record_payment`, `create_task`, `create_cost_item`, etc.
- Schreibende Tools sind auf wenige sichere Aktionen beschränkt (Zahlung buchen, Aufgabe anlegen, Beleg erfassen).

### API-Endpunkte
- REST API v1 unter `/api/v1/[...path]`.
- Jede Operation aus `operations.ts` ist gleichzeitig REST-Route und MCP-Tool.
- Beispiele: `GET /api/v1/properties`, `GET /api/v1/leases/{id}/ledger`, `POST /api/v1/leases/{id}/payments`, `POST /api/v1/tasks`.
- API-Keys mit Scopes `read`/`write`.

### Vergleich mit FastAPI/Vue.js/PostgreSQL
| Aspekt | mietkartei.de | Unser Stack |
|--------|---------------|-------------|
| Backend | SvelteKit (server routes) | FastAPI — beides modern, FastAPI hat Vorteil bei API-Design |
| Frontend | Svelte 5 | Vue 3 — ähnlich reaktiv |
| DB | SQLite/D1 | PostgreSQL — besser für Mandantenfähigkeit |
| API/MCP | Hervorragend: gemeinsamer Operationskatalog | starkes Vorbild für unseren API- und MCP-Layer |
| Auth | OAuth + API-Keys | kann übernommen werden |
| DACH-Logik | solide, aber weniger Heizkosten-Tiefe als Mietfuchs | Heizkosten-Regeln von Mietfuchs ergänzen |

### Übernehmbar
- Architekturmuster: **ein Operation-Katalog für REST + MCP**.
- MCP-Authentifizierung und Tool-Beschreibungen.
- API-Key-Scope-Konzept (`read`/`write`).
- Bankimport-Zuordnungslogik und Mietkonto.

### Besser/Schlechter als unser Stack
- **Besser:** exzellente API/MCP-Integration, klare Architektur, Cloudflare-Deploy-Option.
- **Schlechter:** SQLite/D1 limitiert komplexe Queries; Heizkosten/CO₂ weniger tief; Frontend-Frameworkwechsel nötig.

---

## 3. ImmoBase — `s3gv/immobase`

### Stack
| Schicht | Technik |
|---------|---------|
| Backend  | PHP 8.4 + Symfony 8.1 |
| DB       | PostgreSQL 16 |
| Webserver| FrankenPHP (Caddy) |
| Frontend | Twig + Tailwind CSS + wenig JS (kein Node-Build) |
| Plugins  | HTTP-Plugin-API, isolierte Prozesse |
| Auth     | Symfony Security, RBAC, 2FA |

### REA-Ergebnis
- `import-reference-source` lieferte Inventar: 64 Migrationsdateien, 13 Module (`Api`, `Auth`, `Billing`, `Dashboard`, `Dunning`, `Finance`, `Party`, `Plugin`, `Portal`, `Property`, `Settings`, `Tenancy`), Sprachen PHP/JS/CSS/YAML.
- Kein vollständiger `analyze` verfügbar für PHP; daher manuelle Code-Lecture der Migrations und Module.

### Architektur & Module
- Stark modularisiert nach **Domain-Driven Design** (Module mit `Application/`, `Domain/`, `Infrastructure/`, `UserInterface/`).
- 13 Module decken alle Hausverwaltungs-Bereiche ab.
- Plugin-System: Plugins laufen als eigene Prozesse hinter Netzsperre.
- Tenant-/Verwaltungsfokus: eine Installation = eine Verwaltung.

### Datenmodell (PostgreSQL, 65 Tabellen)
Wichtige Entitäten:
- `auth_user`, `auth_role`, `auth_role_permission`, `auth_user_role`
- `property`, `property_unit`, `property_unit_owner`, `tenancy`, `tenancy_tenant`, `tenancy_rent`, `tenancy_household`
- `finance_cost_kind`, `finance_distribution_key`, `finance_distribution_key_share`, `finance_cost_item`, `finance_cost_item_year`, `finance_house_money`, `finance_reserve_movement`, `finance_loan`
- `billing_statement`, `billing_document`, `billing_line`, `billing_plan`, `billing_asset_report`, `billing_budget`, `billing_rent_invoice`
- `dunning_base_rate`, `dunning_claim`, `dunning_notice`
- `portal_enquiry`, `portal_message`, `audit_entry`, `plugin_installation`, `plugin_delivery`

### Geschäftslogik (DACH)
- Betriebskostenabrechnung, Hausgeldabrechnung, Wirtschaftsplan, Vermögensbericht nach § 28 WEG.
- Dauermietrechnung für Gewerbe inkl. USt.
- **E-Rechnung XRechnung (CII)** — validiert gegen amtliche Schemata.
- Mahnwesen mit Verzugszinsen, Mahnstufen, gerichtlichem Mahnverfahren.
- Tagesgenaue Mieter-/Eigentümerwechsel.
- Zweisprachig (DE/EN).

### KI-Integration
- **Keine** KI-Integration im Quellcode sichtbar.

### MCP-Server
- **Nein.** Weder MCP noch eine öffentliche REST-API für externe Agenten.

### API-Endpunkte
- Eigenes `Module/Api` existiert, aber scheinbar intern/intern für Plugins und UI.
- Keine dokumentierte externe API gefunden.

### Vergleich mit FastAPI/Vue.js/PostgreSQL
| Aspekt | ImmoBase | Unser Stack |
|--------|----------|-------------|
| Backend | Symfony/PHP | FastAPI/Python |
| DB | PostgreSQL 16 | PostgreSQL — direkt vergleichbar |
| Frontend | server-rendered Twig | Vue.js SPA — mehr Interaktivität |
| Architektur | sehr saubere Modulgrenzen | DDD-Modularisierung übernehmbar |
| E-Rechnung | XRechnung (CII) | wertvolle Referenz |
| Plugins | isolierte Plugin-Prozesse | interessant, aber Overhead |
| KI/MCP | fehlt | Chancen für Differenzierung |

### Übernehmbar
- Datenbank-Schema-Struktur (Kostenarten, Verteilerschlüssel, Abrechnungen, Mahnwesen).
- DDD-Modulaufteilung (`Module/*/Domain`).
- XRechnung-Validierung.
- RBAC-/Rechtematrix-Konzept.

### Besser/Schlechter als unser Stack
- **Besser:** Produktionsreife, sehr saubere Architektur, PostgreSQL, E-Rechnung, 1.400+ Tests.
- **Schlechter:** Keine API/MCP für KI-Agenten, PHP-Stack schwer direkt wiederverwendbar, serverseitiges UI weniger modern.

---

## 4. NebenkostenFix — `Nerbry72/NebenkostenFix`

### Stack
| Schicht | Technik |
|---------|---------|
| Backend  | Python 3.11 + Flask |
| ORM/DB   | SQLAlchemy + SQLite (`nebenkosten.db`) |
| Frontend | Vanilla JS/HTML/CSS (kein Framework) |
| PDF      | reportlab |
| Build    | Windows-App (PyInstaller/Inno Setup/MSIX) + Docker |
| Test     | pytest, 55 % Coverage-Schwelle |

### REA-Ergebnis
- `import-reference-source` lieferte Inventar: Python-Flask-App, Alembic-Migrationen, Vanilla-Frontend, 106 Flask-Routen.
- Kein JavaScript-Application-Analyze möglich (kein JS-Framework); stattdessen manuelle Analyse von `app.py`, `models.py`, `rechenkern.py` etc.

### Architektur & Module
- Einfache monolithische Flask-Anwendung.
- Geschäftslogik in `nebenkostenfix/`: `rechenkern.py`, `heizung.py`, `co2.py`, `betrkv.py`, `jahresabrechnung.py`, `pdf_generator.py`.
- 4 UI-Arbeitsbereiche: Heute, Haus, Kosten, Abrechnung.
- CLI-Kommandos für Backup, User-Verwaltung.

### Datenmodell (SQLite, 21 Tabellen)
Wichtige Entitäten:
- `properties`, `apartments`, `tenants`, `haushaltsgroessen`, `vorauszahlung_soll`, `kaltmiete_soll`
- `cost_categories`, `heizungsanlagen`, `cost_invoices`, `invoice_documents`
- `meters`, `meter_readings`
- `tenant_billing_reports`, `billing_report_versions`, `billing_report_categories`
- `payments`, `users`, `vermieterdaten`, `providers`

### Geschäftslogik (DACH)
- Nebenkostenabrechnung nach BetrKV.
- Heizkosten nach HeizkostenV.
- CO₂-Kostenaufteilung nach CO2KostAufG (Stufenmodell).
- Allgemeinverbrauch, Zählerwechsel, Eichfrist.
- § 35a EStG Lohnanteile.
- Fristenkalender, Mehrjahresblick.
- Abrechnung als PDF mit GiroCode.

### KI-Integration
- **Keine** KI-Integration.

### MCP-Server
- **Nein.**

### API-Endpunkte
- REST-API unter `/api/*`, 106 Flask-Routen.
- Beispiele: `/api/properties`, `/api/tenants`, `/api/categories`, `/api/meters`, `/api/readings`, `/api/belege/export`.
- Eher intern für die SPA; keine öffentliche API-Doku.

### Vergleich mit FastAPI/Vue.js/PostgreSQL
| Aspekt | NebenkostenFix | Unser Stack |
|--------|----------------|-------------|
| Backend | Flask/Python | FastAPI/Python — sehr ähnlich |
| Frontend | Vanilla JS | Vue.js — deutlich mehr Struktur |
| DB | SQLite | PostgreSQL |
| Scope | kleiner, 1-15 Wohnungen | unserer Stack kann mehr Mandanten |
| Tests | pytest, 55 % | mit FastAPI/Pydantic leichter testbar |
| KI/MCP | fehlt | Differenzierungspotenzial |

### Übernehmbar
- Python-Rechenkern (`rechenkern.py`, `heizung.py`, `co2.py`) als Algorithmen-Referenz.
- Flask-Routen als API-Design-Inspiration.
- Testabdeckungs-Disziplin.

### Besser/Schlechter als unser Stack
- **Besser:** sehr einfache, lokale Lösung; gute Heizkosten/CO₂-Implementierung; Python-Code leicht lesbar.
- **Schlechter:** SQLite, Vanilla-Frontend, keine API-Doku, keine Mandantenfähigkeit, keine KI/MCP.

---

## 5. HaVeWa — `fgilde/hausverwaltung`

### Stack
| Schicht | Technik |
|---------|---------|
| Frontend | Next.js 16 (App Router) + React 19 + TypeScript + shadcn/ui + Tailwind |
| Backend  | Next.js API routes + Server Actions |
| ORM/DB   | Prisma + PostgreSQL |
| Auth     | Auth.js (next-auth v5) + RBAC |
| AI       | Anthropic SDK / OpenAI (optional) |
| API-Doku | Scalar + OpenAPI 3.1 |
| Test     | Vitest |

### REA-Ergebnis
- `import-reference-source` lieferte Inventar: Next.js-App, 49 API-Routen, 101 lib-Dateien, Prisma-Migrations.
- Kein JavaScript-Application-Analyze sinnvoll (Next.js Server Components); stattdessen Code-Lecture.

### Architektur & Module
- Next.js App Router mit `[locale]` für i18n (de/en).
- Zwei Bereiche: Manager-App (`(admin)`) und Mieter-/Eigentümer-Portal (`portal/`).
- `src/lib/` enthält Domänen-Logik: `allocation/`, `adapters/`, `api-ops.ts`, `api-data.ts`, `api-write.ts`, `ai.ts`.
- `src/server/actions/` — server actions pro Modul (RBAC-scoped).
- Multi-tenant: `Tenant`-Modell, alle Zeilen tragen `tenantId`.

### Datenmodell (PostgreSQL, 60+ Models)
Wichtige Entitäten:
- `Tenant` (Mandant), `User`, `ApiToken`, `Notification`
- `Property`, `Building`, `Unit`, `Subcommunity`, `AreaAllocation`
- `Person`, `Owner`, `Lease`, `Renter`, `RentComponent`, `RentAdjustment`, `Deposit`
- `Account`, `BankConnector`, `BankLink`, `Charge`, `Payment`, `DunningNotice`, `SepaMandate`
- `CostEntry`, `EconomicPlan`, `Reserve`, `ReserveTransaction`
- `Document`, `InboundEmail`, `EmailMessage`, `Letter`, `LetterStatusEvent`
- `Meeting`, `AgendaItem`, `Resolution`
- `Ticket`, `Contractor`, `MaintenanceContract`
- `Insurance`, `PropertyTax`, `Task`, `Appointment`
- `Template`, `ImportPreset`, `CustomFieldDef`, `AuditLog`

### Geschäftslogik (DACH)
- Miet- und WEG-Verwaltung (`ManagementType`: MIET / WEG).
- Betriebskostenabrechnung mit Umlage-Engine (`lib/allocation/`).
- WEG: MEA, Wirtschaftsplan, Hausgeld, Rücklagen, Beschlusssammlung § 24 WEG, Eigentümerversammlungen.
- Mahnwesen, SEPA, DATEV-Export, camt.053-Import.
- E-Rechnung (Einlesen).
- Briefversand via Pingen / Deutsche Post E-POSTBUSINESS.
- IMAP-Posteingang, E-Mail-Postausgang.
- Grundsteuer-Reform 2025.

### KI-Integration
- Optional: Anthropic (Claude) oder OpenAI-kompatible Endpunkte.
- KI-Config je Mandant (`aiProvider`, `aiBaseUrl`, `aiApiKey`, `aiModel`).
- Ohne Key wird eine regelbasierte Summary zurückgegeben.

### MCP-Server
- **Ja**, unter `/api/mcp`.
- JSON-RPC, Bearer-Auth (persönliche API-Tokens).
- 30+ Tools: `portfolio_summary`, `list_properties`, `list_leases`, `list_open_items`, `create_record`, `update_record`, `run_operation`, etc.
- Generische CRUD-Tools + spezialisierte Operationen.

### API-Endpunkte
- REST API v1 unter `/api/v1/*`.
- Generischer CRUD-Layer (`api-write.ts`) + Operationen (`api-ops.ts`).
- OpenAPI 3.1 unter `/api/v1/openapi.json`, Scalar-Doku unter `/api-reference`.
- Beispiel-Operationen: `run_charge_generation`, `run_dunning`, `apply_adjustment`, `import_camt`, `send_email`, `upload_document`.

### Vergleich mit FastAPI/Vue.js/PostgreSQL
| Aspekt | HaVeWa | Unser Stack |
|--------|--------|-------------|
| Backend | Next.js API routes | FastAPI — beides TS/Python, FastAPI spezialisiert |
| Frontend | Next.js/React | Vue.js — beides modern, Vue weniger Server-Abhängigkeit |
| DB | PostgreSQL + Prisma | PostgreSQL + SQLAlchemy/Alembic |
| API/MCP | Hervorragend, OpenAPI, Scalar | starkes Vorbild |
| Multi-Tenant | eingebaut | übernehmbar |
| DACH | sehr breit (Miet + WEG) | breite Abdeckung anstreben |
| E-Rechnung/Bank | importiert camt.053, liest E-Rechnung | implementierbar |

### Übernehmbar
- API/MCP-Architektur mit getrenntem `api-data`, `api-write`, `api-ops`.
- OpenAPI/Scalar-Dokumentation.
- Multi-Tenant-Schema mit `tenantId` auf jeder Zeile.
- Umlage-Engine (`lib/allocation/`).
- Brief-/E-Mail-Outbox-Konzept.

### Besser/Schlechter als unser Stack
- **Besser:** modernster Stack der fünf, Multi-Tenant, MCP, OpenAPI, breiteste Feature-Abdeckung, Integrationsadapter (Bank, Post, E-Rechnung).
- **Schlechter:** Next.js-Lock-in (Server Components, App Router); stark an React/Next gebunden; keine echte Trennung von API und UI.

---

## Zusammenfassender Vergleich

| Repo | Backend | Frontend | DB | KI | MCP | API-Doku | DACH-Tiefe | Multi-Tenant |
|------|---------|----------|-----|----|-----|----------|------------|--------------|
| mietfuchs | Express/TS | React 19 | SQLite | Ollama/OpenAI | ❌ | ❌ | ⭐⭐⭐⭐⭐ | ❌ |
| mietkartei.de | SvelteKit | Svelte 5 | SQLite/D1 | ❌ | ✅ | gut | ⭐⭐⭐⭐ | teils |
| ImmoBase | Symfony/PHP | Twig | PostgreSQL | ❌ | ❌ | ❌ | ⭐⭐⭐⭐⭐ | ❌ |
| NebenkostenFix | Flask/Python | Vanilla | SQLite | ❌ | ❌ | ❌ | ⭐⭐⭐⭐ | ❌ |
| HaVeWa | Next.js/TS | Next.js/React | PostgreSQL | Anthropic/OpenAI | ✅ | OpenAPI/Scalar | ⭐⭐⭐⭐⭐ | ✅ |

---

## Empfehlungen für unseren FastAPI/Vue.js/PostgreSQL-Stack

1. **Datenmodell** am ehesten an **HaVeWa** + **ImmoBase** orientieren (PostgreSQL, Multi-Tenant mit `tenantId`, saubere Domänen-Trennung).
2. **API/MCP-Layer** nach dem Muster von **mietkartei.de** und **HaVeWa** bauen:
   - Ein gemeinsamer Operationskatalog für REST und MCP.
   - API-Keys mit Scopes (`read`/`write`).
   - OpenAPI/Scalar-Dokumentation.
3. **DACH-Abrechnungslogik** primär aus **Mietfuchs** und **NebenkostenFix** übernehmen:
   - Heizkostenverordnung, CO2KostAufG, BetrKV, § 556/560 BGB, Anlage V.
   - Centgenaue Verteilung (Hare-Verfahren).
4. **KI-Integration** als optionaler Beleg-Parser (Mietfuchs-Muster) + MCP-Zugriff für Agenten (HaVeWa/mietkartei-Muster).
5. **Frontend** als Vue.js 3 SPA, API-getrennt — das ist gegenüber Next.js/HaVeWa und SvelteKit/mietkartei.de unser größter Architekturvorteil (echte Entkopplung, Wiederverwendung, Testing).
6. **E-Rechnung / Bankimport** aus ImmoBase/HaVeWa als spätere Erweiterungen vorsehen.
7. **Lizenz:** Alle fünf stehen unter AGPLv3/GPLv3 — bei Übernahme von Code/Logik müssen eigene Quellcode-Veröffentlichung geprüft werden.
