# Detaillierte Analyse: Top 5 GitHub-Repos für MietVerwaltung SaaS

**Analysezeit:** 2026-10-28  
**Analyst:** Hermes Code-Analyst  
**Quellen:** Lokale Klons unter `/root/mietverwaltung/repos/` + Quellcode-Lektüre  
**Ziel:** Architektur, Datenmodell, Geschäftslogik, KI/OCR/MCP, DACH-Recht, Übernahme-Potenzial für unseren FastAPI+Vue.js+PostgreSQL+Ollama-Stack bewerten.

---

## 1. fgilde/hausverwaltung (HaVeWa) — Score 89%

### Architektur
- **Full-Stack-Monolith** mit klarer Mandanten-Trennung.
- **Frontend/Backend:** Next.js 16 App Router (server components + route handlers), TypeScript.
- **Datenbank:** PostgreSQL 16 + Prisma ORM.
- **UI:** shadcn/ui + Tailwind CSS, next-intl für DE/EN.
- **Auth:** Auth.js (NextAuth), rollenbasiert: ADMIN, VERWALTER, BUCHHALTUNG, BEIRAT, EIGENTUEMER, MIETER, HANDWERKER.
- **API:** REST `/api/v1/*` + OpenAPI 3.1 + Scalar Referenz + **MCP-Server** `/api/mcp`.
- **Deployment:** Docker Compose mit Caddy (automatisches HTTPS), zusätzlich Unraid/Umbrel/CasaOS/Cosmos/Proxmox-Helm.
- **Tests:** Vitest für Engine, Abrechnung, Validierung.
- **Lizenz:** AGPL-3.0 oder kommerzielle Dual-Lizenz.

### Datenmodell (Prisma-Schema — 1.247 Zeilen, sehr ausgereift)
Zentrale Entitäten:

| Entität | Kernfelder | Beziehungen |
|---------|------------|--------------|
| `Tenant` | Mandant mit KI-Config, SMTP, IMAP, Branding, `heatingConsumptionPct` | 1:n zu allem |
| `Property` | name, street, zip, city, type (WOHNEN/GEWERBE/GEMISCHT), management (MIET/WEG), `meaTotal`, `feeType`/`feeValue`, `areaModel`, `totalArea` | n `Building`, n `CostEntry`, n `EconomicPlan`, n `Reserve`, n `Meeting` |
| `Building` | name | n `Unit` |
| `Unit` | label, type, area (Decimal 10,2), rooms, `mea` (Tausendstel), buildingId, subcommunityId | n `Lease`, n `Meter`, n `Owner`, n `Ticket` |
| `Person` | firstName, lastName, email, phone, type (MIETER/EIGENTUEMER/…), iban, accountHolder, address | n `Owner`, n `Renter`, n `User`, n `SepaMandate` |
| `Lease` | startDate, endDate, rentCold, personCount, noticePeriodM | n `Renter`, n `RentComponent`, n `RentAdjustment`, 1:1 `Deposit`, n `Charge` |
| `Renter` | personId + leaseId (Zwischentabelle) | — |
| `CostEntry` | propertyId, year, type (CostType-Enum: GRUNDSTEUER, WASSER, HEIZUNG, AUFZUG, …), amount (Decimal 12,2), method (AREA/UNITS/PERSONS/CONSUMPTION/MEA), `umlagefaehig`, subcommunityId, `consumptionSharePct` | → `Property`, → `Subcommunity` |
| `Charge` | leaseId?, areaAllocationId?, type (MIETE/NEBENKOSTEN/HAUSGELD/KAUTION/SONSTIGES), period, dueDate, amount | n `Payment`, n `DunningNotice` |
| `Payment` | accountId?, chargeId?, date, amount, direction, reference, counterparty, externalId | n `Document` |
| `Account` | name, type (BANK/KAUTION/RUECKLAGE/SACHKONTO), iban, balance | n `Payment`, n `Deposit` |
| `Meter` / `MeterReading` | type (STROM/GAS/WASSER_KALT/WASSER_WARM/WAERME), serialNo, value | — |
| `Subcommunity` | propertyId, name | n `Unit`, n `CostEntry`, n `Reserve`, n `Resolution`, n `SubcommunityPlan` |
| `EconomicPlan` | propertyId, year, totalAmount | WEG-Hausgeld-Planung |
| `Reserve` / `ReserveTransaction` | propertyId, subcommunityId?, name, date, amount | WEG-Erhaltungsrücklage |
| `Meeting` / `AgendaItem` / `Resolution` | propertyId, meetingId, subcommunityId, number (fortlaufend), title, text, date, result, votes | §24 WEG-Beschlusssammlung |
| `Ticket` | propertyId, unitId, contractorId, assigneeId, reporterId, title, category, status, priority, dueDate, timeSpentMin | — |
| `Document` | propertyId, unitId, personId, name, category, mime, size, storageKey, eInvoice, invoiceNo, invoiceTotal | GoBD-konform |
| `Letter` / `EmailMessage` | DIN-5008-Briefe, Postausgang, IMAP-Eingang, Anhänge | — |
| `ApiToken` | tokenHash, prefix, lastUsedAt, revokedAt | je User, für REST + MCP |
| `AuditLog` | action (CREATE/UPDATE/DELETE), entity, entityId, summary | GoBD-Nachvollziehbarkeit |

### Geschäftslogik: NK-Abrechnung, Umlage, Heizkosten
- **Verteilerschlüssel-Engine** in `src/lib/allocation/index.ts` — reine Funktion, cent-genau mit **Largest-Remainder**.
- Unterstützte Methoden: `AREA`, `UNITS`, `MEA`, `PERSONS`, `CONSUMPTION`, `CUSTOM`.
- Zeitanteilige Kürzung über `timeFactor` (z. B. Mieterwechsel).
- **Miet-NK-Abrechnung** in `src/lib/allocation/statement.ts`:
  - Trennung in Zeit-Topf (Fläche/Einheit/Person/MEA) und Verbrauchs-Topf (Zähler).
  - Nur der Zeit-Topf wird bei unterjährigem Mietverhältnis gekürzt.
  - **HeizkostenV §7/§8:** Heiz-/Warmwasserpositionen splitten in Grundkosten (Fläche) und Verbrauchskosten (Zähler). Default 70 % Verbrauch / 30 % Fläche (`HEATING_CONSUMPTION_SHARE = 0.7`), pro Kostenposition überschreibbar via `consumptionSharePct`.
  - Verbrauch fehlend → fällt auf Fläche zurück (§9a-Näherung).
- **WEG-Jahresabrechnung** in `src/lib/allocation/weg.ts`:
  - Kosten je Position nach Verteilerschlüssel, bei Untergemeinschaft nur deren Einheiten.
  - Hausgeld = Wirtschaftsplan je Kreis (Gesamt-WEG oder UG) nach MEA.
  - Eigentümeranteil in Tausendstel, cent-genau auf Eigentümer verteilt.
- **Mahnwesen:** `DunningNotice` mit Stufen, Gebühren, objektübergreifendes Mahn-Dashboard.
- **Sollstellung (`Charge`):** monatliche Forderungen, Verrechnung mit `Payment`, offene Posten.

### KI-Integration
- `src/lib/ai.ts` — **KI-Adapter** für Mandanten-Config.
- Unterstützt **Anthropic Claude** und beliebige **OpenAI-kompatible** Endpunkte (OpenAI, OpenRouter, Groq, Ollama, LM Studio).
- Config kommt aus `Tenant.aiProvider / aiBaseUrl / aiApiKey / aiModel`, Fallback auf ENV.
- Standardmodell: Claude `claude-opus-4-8` oder OpenAI `gpt-4o-mini`.
- Ohne API-Key läuft die App vollständig mit regelbasierter Zusammenfassung.
- **Prompt-System:** „Du bist der Assistent einer deutschen Hausverwaltungssoftware… Stütze dich auf im Kontext gelieferte Daten; erfinde keine Zahlen."
- Anreicherung mit Bestands-Kontext (JSON). **Keine eingebaute Anonymisierung** — das müssten wir ergänzen.

### OCR / Belegscanning
- **Nicht implementiert.** Dokumente werden hochgeladen, kategorisiert, als Beleg verknüpft, aber keine OCR-/KI-Extraktion.
- E-Rechnung (XML) wird extrahiert (`invoiceNo`, `invoiceTotal`).

### MCP-Server
- `src/app/api/mcp/route.ts` — **eigener MCP-Server** über Streamable HTTP / JSON-RPC.
- Auth per Bearer-Token (API-Token, gehasht), Mandanten-Scoped.
- **27+ Tools**, u. a.:
  - `portfolio_summary`, `list_properties`, `get_property`, `list_units`, `list_persons`, `list_leases`, `list_tickets`, `list_open_items`, `list_meters`, `list_accounts`, `list_charges`, `list_payments`, `list_documents`, `list_meetings`, `list_resolutions`, `list_economic_plans`, `list_reserves`, `list_tasks`, `list_contractors`.
  - CRUD: `create_record`, `update_record`, `delete_record` (mit `list_entities` Discovery).
  - Operationen: `run_operation` (Sollstellungslauf, Mahnlauf, Mietanpassung, Bank-Import, E-Mail senden, Dokument-Upload).
- Beschreibungen auf Deutsch, ideal für deutsche KI-Assistenten.

### DACH: BetrKV / Mietrecht / WEG
- **BetrKV-Enum `CostType`** mit 17 Positionen (Grundsteuer, Wasser, Entwässerung, Heizung, Warmwasser, Aufzug, Straßenreinigung, Müll, Gebäudereinigung, Gartenpflege, Beleuchung, Schornstein, Versicherung, Hauswart, Kabel, Instandhaltung, Verwaltung, Sonstige).
- **HeizkostenV-Logik** mit Verbrauchsanteil 50–100 % (Default 70 %).
- **WEG:** Wirtschaftsplan (§28 WEG), Erhaltungsrücklage (WEG-Reform 2020), Beschlusssammlung §24 WEG mit fortlaufender Nummer, Eigentümerversammlung mit Abstimmung.
- **Mahnwesen & Fristen:** §556 BGB (12-Monats-Abrechnungsfrist) wird in Templates erwähnt.
- **DIN 5008-Briefe** und GoBD-konforme Dokumentenverwaltung.
- Bank-Sync via **Enable-Banking** (Open Banking) + camt.053-Import.

### Tech-Stack
- Next.js 16, TypeScript, Prisma, PostgreSQL, Tailwind/shadcn, Auth.js, Vitest, Docker, Caddy.

### Was können WIR übernehmen?
1. **Verteilerschlüssel-Engine** (`allocate()` in `src/lib/allocation/index.ts`) — saubere, getestete, cent-genaue Funktion. Könnte 1:1 in Python portiert werden.
2. **HeizkostenV-Logik** mit Grund-/Verbrauchskosten-Split und Zeitanteil-Kürzung.
3. **WEG-Abrechnungslogik** (Untergemeinschaften, MEA, Hausgeld, Rücklagen, Beschlüsse) — hochrelevant für spätere WEG-Erweiterung.
4. **MCP-Server-Architektur** als Vorlage für unseren eigenen MCP-Server: JSON-RPC, Bearer-Auth, Tool-Discovery, CRUD + Operations.
5. **REST-API-Design** mit OpenAPI + persönlichen API-Tokens.
6. **DIN-5008-Brief & GoBD-Audit-Log** als Inspiration.
7. **Mandantenfähigkeit** mit `tenantId`-Scoping in jedem Modell.

### Was ist besser / schlechter als unsere Lösung?
- **Besser:** Viel vollständiger (WEG, Mahnwesen, Bank-Sync, Portal, Audit-Log), sehr saubere Architektur, MCP-Server bereits implementiert, DIN-5008/GoBD.
- **Schlechter:** Next.js/TypeScript statt unserem Python/FastAPI/Vue.js-Stack; OCR/KI-Belegauswertung fehlt; keine Mieter-Bewerbung mit KI; keine Ticket-KI-Kategorisierung; keine Anonymisierungsschicht für KI.
- **Lizenz:** AGPL-3.0 — direkte Code-Übernahme nur in Open-Source-Projekt oder kommerzielle Lizenz erforderlich. Ideen und Algorithmen können wir frei studieren.

---

## 2. speedone/mietfuchs — Score 83%

### Architektur
- **Lokale Desktop-/Server-App**, 100 % offline, keine Cloud.
- **Backend:** TypeScript/Node (ausführbar ohne Build ab Node 24.15), SQLite.
- **ORM:** Drizzle ORM.
- **Frontend:** React + Vite.
- **Packaging:** Bun für Binaries (Windows, macOS, Linux, ARM), Docker-Image, Linux-Pakete (deb/rpm/pacman).
- **Tests:** `npm test` für Berechnungs-Engine.
- **Lizenz:** AGPL-3.0.

### Datenmodell (Drizzle-SQLite — 2.132 Zeilen `schema.ts`)
Kern-Tabellen:

| Tabelle | Kernfelder |
|---------|------------|
| `properties` | id, name, kind (mfh/etw/efh/zfh/sonstiges), address, landlordName, iban, paymentDeadlineDays, periodStartMonth, cableBuiltBeforeDec2021, tightMarket, state (Bundesland) |
| `periodChanges` | propertyId, fromMonth — Wechsel des Abrechnungsrhythmus |
| `units` | propertyId, name, areaM2, participates, selfUsed, selfPersons, mea, rooms, floor |
| `tenancies` | unitId, tenantName, persons, start, end, email, phone, costModel, heatingModel, selfSupplyKind, depositCents, depositStatus |
| `personHistory` | tenancyId, from, persons — **Personentage**-Staffel |
| `prepayments` | tenancyId, from, monthlyCents — NK-Vorauszahlung-Staffel |
| `flatRates` | tenancyId, from, monthlyCents — Pauschale |
| `baseRents` | tenancyId, from, monthlyCents — Kaltmiete-Staffel |
| `costCategories` | propertyId, name, allocationKey, costKindId, notes |
| `costInvoices` | propertyId, vendor, invoiceDate, periodStart/End, totalCents, notes |
| `costInvoicePositions` | invoiceId, costCategoryId, description, grossCents, allocationKey, isHeating, … |
| `meters` | propertyId, unitId, kind (kaltwasser/warmwasser/strom/waerme/hkv/sonstig), number, heatingInfoId |
| `meterReadings` | meterId, date, valueHt, valueNt, kind (regular/zwischen/wechsel) |
| `heatingInfo` / `heatingDeliveries` / `heatingPeriods` | Heizanlagen, Brennstofflieferungen, Heizperioden |
| `bankAccounts` | accountId, name, iban, bankCode |
| `bankTransactions` | accountId, date, amountCents, reference, counterpart, matchedLeaseId |
| `uploads` | id, propertyId, fileName, kind (receipt/heating/meter), ocrText, extractedAt |
| `settings` | App-Einstellungen inkl. `ai` (JSON) |

**Besonderheit:** Alle Geldbeträge als Integer-Cent, nie Float.

### Geschäftslogik: NK-Abrechnung, Umlage, Heizkosten
- **Umlageschlüssel:** Wohnfläche, Personenzahl (personentagesgenau), Wohneinheiten, Verbrauch (Zähler), Direktzuordnung, vereinbarte Anteile, „laut Gemeinschaftsabrechnung“ (Hausgeld), Einzelbeträge, `heatingSystem`.
- **Centgenaue Verteilung** nach Hare-Verfahren.
- **Heizkosten:** eigene Heizkostenabrechnung nach §§ 7–9 HeizkostenV; Grund-/Verbrauchskosten; Warmwasseranteil gemessen oder nach Formel; Mieterwechsel nach Gradtagen; Schätzung nach § 9a; Kesseltausch; mehrere Heizanlagen; Brennstoffvorrat.
- **CO₂-Kostenaufteilung** nach CO2KostAufG-Stufenmodell.
- **Mietkonto:** Soll/Ist je Monat, fällige Rückstände.
- **Steuer-Übersicht (Anlage V):** Einnahmen nach Zufluss, Werbungskosten, Überschuss; Eigennutzung abziehbar/privat aufgeteilt.
- **Belegordner:** Posteingang, Belegabdeckung, Belegmappe für Mieter, Steuer-ZIP.

### KI-Integration
- **Optionale KI-Belegauswertung** — sehr ausgereift.
- **Anbieter:** Ollama (lokal) oder OpenAI-kompatible Dienste (OpenAI, IONOS AI Model Hub, Mistral, LM Studio, Groq …).
- Architektur: `server/src/ai/index.ts` → `ollama.ts` / `openai.ts`.
- **Zwei Slots:** `text` und `images` — unterschiedliche Modelle für Text- und Bildauswertung.
- **Consent-Logik:** Vor jeder Anfrage prüft `consentProblem`, ob Daten das Haus verlassen; Nutzer muss bestätigen.
- **JSON-Schema-Extraktion:** Mit striktem Schema, Fallback-Stufen (`json_schema` → `json_object` → Prompt-only), Stream-Handling, Fortschritts-Events.
- **Prompt-Engineering in `extract.ts`:** Schemas für Rechnungssteller, Datum, Leistungszeitraum, Positionen (description, category, amountEur, allocationKey, vatRate), Hinweise, Belegtyp.
- **Modell-Empfehlungen** (`recommendations.ts`, `ki-modelle.json`): qwen3.5:4b, gemma4:12b, gpt-5.4-nano etc. mit Scores für text/scan/photo.

### OCR / Belegscanning
- **Browser-seitige PDF-Vorverarbeitung:** `pdf.js` im Client liest Textebene; bei Scan ohne Textebene werden gerenderte Seitenbilder hochgeladen.
- **Bilder/Scans** gehen an Vision-Modell (Ollama/OpenAI).
- Server braucht **kein natives OCR-Modul** — elegant für Docker/Binary.
- **Extraktions-Kategorien** (`EXTRACT_CATEGORIES`): Grundsteuer, Wasser/Abwasser, Müll, Straßenreinigung, Gebäudereinigung, Garten, Beleuchtung, Schornsteinfeger, Versicherung, Hauswart, Aufzug, Kabel, Niederschlagswasser, Heizung und Warmwasser, Sonstige, Nicht umlagefähig, Zuführung Erhaltungsrücklage.
- **Zahlen-Normalisierung** (`numberFromModel`): deutsche/us-Schreibweise, Währungen/Einheiten, Mehrdeutigkeiten werden verworfen statt geraten.

### MCP
- **Nicht implementiert.** Kein MCP-Server; nur lokale App + REST intern.

### DACH: BetrKV / Mietrecht
- **BetrKV-konform:** 17 Kostenarten aus § 2 BetrKV in `shared/types.ts` / `calc.ts`.
- **HeizkostenV** sehr detailliert: Grund-/Verbrauchskosten, Warmwasser, Gradtage, Schätzung, Kesseltausch.
- **CO2KostAufG** Stufenmodell implementiert.
- **§ 35a EStG** Lohnanteil-Bescheinigung.
- **§ 556 / § 560 BGB** Fristen-Hinweis und Vorauszahlungsanpassung.
- **Personentage** für Personenumlage (nicht Momentaufnahme).
- **Leerstand & Eigennutzung** fließen korrekt in die Verteilung.

### Tech-Stack
- TypeScript, Node 24.15+, React, Vite, Drizzle ORM, SQLite, Docker, Bun.

### Was können WIR übernehmen?
1. **KI-Belegauswertungs-Architektur** — das ist das Beste an mietfuchs. Prompts, JSON-Schema-Fallback, Zwei-Slot-Modell, Consent, clientseitige PDF-Vorbereitung.
2. **Kostenarten-Katalog** und Umlageschlüssel-Logik.
3. **HeizkostenV-Implementierung** mit Gradtagen, Warmwasser, CO2-Aufteilung.
4. **Anlage-V-Steuer-Logik** mit Eigennutzungssplit.
5. **Personentage-Engine** für genaue Personenumlage.
6. **Modell-Empfehlungsmechanismus** mit nachladbarer `ki-modelle.json`.
7. **Zahlen-Normalisierung** für KI-Antworten.

### Was ist besser / schlechter als unsere Lösung?
- **Besser:** DACH-NK-Logik extrem tief (BetrKV, HeizkostenV, CO2KostAufG, §35a, Personentage); KI-Belegauswertung sehr ausgereift; 100 % offline/lokal möglich; Steuer-Übersicht.
- **Schlechter:** Kein MCP-Server; kein Mieter-Portal/Ticket-System; SQLite statt PostgreSQL; TypeScript statt Python; keine Benutzer-/Rollen-Trennung für SaaS-Multi-Tenant; kein Bank-Sync.
- **Lizenz:** AGPL-3.0 — Algorithmen/Ideen übernehmbar, Code direkt nur bedingt.

---

## 3. OliverHennhoefer/mietkartei.de — Score 81%

### Architektur
- **SvelteKit-App**, lauffähig als Node.js, Docker oder **Cloudflare Workers**.
- **Backend/ORM:** Drizzle ORM mit SQLite (D1 bei Cloudflare, lokal SQLite).
- **Frontend:** SvelteKit + Tailwind.
- **Auth:** Eigene Account-basierte Authentifizierung, Stripe-Abos für gehostete Version.
- **API:** REST + **MCP-Server** (`/mcp`).
- **Tests:** GitHub Actions, Codecov, viele `.spec.ts`.
- **Lizenz:** AGPL-3.0.

### Datenmodell (Drizzle-SQLite — 1.588 Zeilen `schema.ts`)
Kern-Tabellen:

| Tabelle | Kernfelder |
|---------|------------|
| `accounts` | id, name, landlordName, street, postalCode, city, iban, bankName, stripe-IDs, subscriptionStatus, trialEndsAt |
| `properties` | accountId, name, street, postalCode, city, kind (building/condominium), associationManager (WEG-Verwalter), ownershipShare, ownershipShareTotal, buildingUse, state (Bundesland), vacancyPersons, acquisitionDate/Cost, buildingShare, depreciationRate, loanAmount, lat/long |
| `units` | accountId, propertyId, name, kind, floorArea, floor, rooms |
| `tenants` | accountId, salutation, firstName, lastName, email, phone, address |
| `leases` | accountId, unitId, startDate, endDate, baseRent, operatingCostPrepayment, heatingCostPrepayment, securityDeposit, kind, rentModel (fixed/graduated/indexed), operatingCostModel, heatingCostModel, persons, rentDueDay, ledgerStart |
| `leaseTenants` | leaseId, tenantId (n:m) |
| `leaseUnits` | leaseId, unitId (Zusatzeinheiten) |
| `leasePersons` | leaseId, validFrom, persons — Personen-Staffel |
| `rentChanges` | leaseId, validFrom, baseRent, operatingCostPrepayment, heatingCostPrepayment, reason, status, indexMonth/Value, letterText, letterTable |
| `operatingCostDefaults` / `operatingCostItems` | Vorgabe-Kostenarten je Account, angepasste Kostenart je Property |
| `costEntries` | propertyId, costKindId, fiscalYear, grossCents, distributionKeyId, vatRate, note |
| `distributionKeys` | accountId, name, kind (area/persons/units/metered/fixed), shares |
| `meterReadings` | meterId, date, value |
| `statements` / `statementItems` | Abrechnungsläufe, Positionen je Lease |
| `bankAccounts` / `bankConnections` / `bankTransactions` | IBAN, Enable-Banking-Session, Umsätze, Zuordnung |
| `dunnings` / `dunningNotices` | Mahnwesen |
| `documents` | E-Rechnung, Belege |
| `tasks` | Aufgaben/Fristen |
| `auditLog` | Änderungsprotokoll |
| `apiKeys` | Für REST + MCP, read/write/get |

### Geschäftslogik: NK-Abrechnung, Umlage
- **Umlageschlüssel:** `area`, `persons`, `units`, `metered`, `fixed` — plus Zeitanteil bei Mieter-/Eigentümerwechsel.
- **Abrechnungskreise** je Property.
- **Betriebskostenabrechnung** mit nachvollziehbarem Rechenweg je Mieter, PDF.
- **Mietkonto:** Soll/Ist, Rückstände, Bankabgleich mit Zuordnungsvorschlägen.
- **Index-/Staffelmiete** eingebaut.
- **Kaution:** movements getrennt vom Mietkonto.
- **WEG:** Eigentumswohnung mit Hausgeldabrechnung, Miteigentumsanteil.

### KI-Integration
- **Keine eigene KI-Belegauswertung** im Code, aber:
- **MCP-Server** ermöglicht Claude/ChatGPT-Zugriff auf die Datenbank.
- KI kann Belege erfassen, Zahlungen buchen, Fragen beantworten — über MCP-Tools.
- Keine OCR, keine lokale LLM-Anbindung.

### OCR / Belegscanning
- **Nicht implementiert.**

### MCP-Server
- `app/src/lib/server/api/mcp.ts` — **Streamable HTTP**, JSON-RPC.
- Unterstützt Protokoll-Versionen `2025-06-18`, `2025-03-26`, `2024-11-05`.
- Auth per API-Key mit Rollen: read/write/get.
- `listTools` filtert nach Berechtigung (`permits(caller, operation)`).
- Tools basieren auf zentralen `operations` (`app/src/lib/server/api/operations.ts`).
- `INSTRUCTIONS` auf Englisch, sagt dem Modell: „Answer the landlord in German unless asked otherwise."
- Ergebnis als `content` (text) + `structuredContent`.

### DACH: BetrKV / Mietrecht
- **BetrKV-konforme Kostenarten** als System-Vorgaben.
- **§ 556b BGB:** Miete fällig am dritten Werktag (`rentDueDay` default 3).
- **§ 557b / § 558 BGB:** Index-/Staffelmiete mit Fristenkalender.
- **§ 28 WEG:** Vermögensbericht (asset report) WEG-Reform.
- **Enable-Banking** für Bankabgleich (DACH-konform).

### Tech-Stack
- SvelteKit, TypeScript, Drizzle ORM, SQLite/D1, Tailwind, Cloudflare Workers, Docker, Stripe.

### Was können WIR übernehmen?
1. **MCP-Server-Implementierung** mit Protokoll-Versionen, Berechtigungsfilter, structuredContent.
2. **Bankabgleich-Architektur** (`enable-banking.ts`, `sync.ts`) — Enable-Banking-Session, Consent-Handling, Überlappung bei erneutem Abruf.
3. **API-Key-System** mit read/write/get-Berechtigungen.
4. **Drizzle-Schema-Muster** für SQLite/PostgreSQL (gut portierbar).
5. **Mietkonto + Bankabgleich + Zuordnungsregeln** als Komplett-Modul.
6. **Cloudflare-Deployment-Pattern** (optional).

### Was ist besser / schlechter als unsere Lösung?
- **Besser:** MCP-Server sehr sauber; Bankabgleich (Enable Banking) implementiert; Abrechnung mit Rechenweg; Stripe-Abrechnung für SaaS.
- **Schlechter:** SvelteKit statt Vue.js; SQLite/D1 statt PostgreSQL; keine KI-Belegauswertung; keine OCR; keine Ticket-System-KI; keine Anonymisierungsschicht.
- **Lizenz:** AGPL-3.0.

---

## 4. Nerbry72/NebenkostenFix — Score 74%

### Architektur
- **Python-Flask-Desktop-/Server-App**, 100 % lokal.
- **ORM:** Flask-SQLAlchemy.
- **DB:** SQLite (lokal) oder MySQL (Docker).
- **UI:** WebView2 (Windows) / Browser (Docker), Jinja2-Templates + Vue.js-artige Komponenten (vermutlich).
- **Packaging:** Windows-App (Microsoft Store/Installer), Docker.
- **Tests:** Viele `test_*.py` (z. B. Heizkosten, Zähler, Abrechnung, PDF, Determinismus).
- **Lizenz:** GPL-3.0.

### Datenmodell (SQLAlchemy — `models.py` 765 Zeilen)
Kern-Entitäten:

| Entität | Kernfelder |
|---------|------------|
| `Provider` | Rechnungssteller |
| `Property` | name, is_standalone, abrechnungsjahr_beginn (MM-TT) |
| `Apartment` | property_id, name, sqm, nutzungsart, selbstversorger, eigennutzung |
| `Tenant` | apartment_id, name, move_in_date, move_out_date, last_billed_until, anrede, anschrift, zustellanschrift |
| `Haushaltsgroesse` | tenant_id, gueltig_ab, personenanzahl — **Personentage** |
| `VorauszahlungSoll` | tenant_id, gueltig_ab, betrag |
| `KaltmieteSoll` | tenant_id, gueltig_ab, betrag, indexmiete |
| `TenantCostProfile` | tenant_id, category_id, billing_type (qm/personen/direkt/nur_allgemein/ignoriert) |
| `CostCategory` | name (unique!), allocation_method, requires_meter, **betrkv_nr** |
| `CostInvoice` | property_id, provider_id, date, total, period |
| `CostInvoicePosition` | invoice_id, category_id, description, gross_amount, billing_type, lohnanteil_35a |
| `Meter` / `MeterReading` | apartment_id/property_id, kind, number, readings (HT/NT), art (regular/zwischen/wechsel), eichfrist |
| `Heizungsanlage` | property_id, name, versorgt (heizung/warmwasser/verbunden), verbrauchsanteil, warmwasserweg |
| `Payment` | tenant_id, date, amount, kind (rent/settlement) |
| `User` | lokale Auth, bis zu 2 Konten |

### Geschäftslogik: NK-Abrechnung, Umlage, Heizkosten
- **Rechenkern getrennt von DB** (`rechenkern.py` ~4.000 Zeilen) — sehr sauber: reine Funktionen, frozen Dataclasses, deterministisch.
- **Abrechnungsarten:** `qm`, `personen`, `direkt`, `nur_allgemein`, `ignoriert`.
- **Personentage** über `Haushaltsgroesse` mit `personentage()`.
- **Zählerweg:** Hauptzähler → Allgemeinverbrauch = max(0, Haupt - Σ Wohnungszähler); Verbrauch nach Personentagen; Direktzähler = Eigenverbrauch × Preis + Allgemeinanteil.
- **HeizkostenV-Logik** in `heizung.py`:
  - Verbrauchsanteil 50–70 % (Default 70 %).
  - Grund-/Verbrauchskosten.
  - Warmwasseranteil gemessen oder nach Formel.
  - Zwischenablesung, Zählerwechsel, Eichfrist.
- **CO2KostAufG** Stufenmodell in `co2.py`.
- **§ 35a EStG** Lohnanteil (`lohnausweis.py`).
- **Vorauszahlungs-Soll/Ist** mit Zahlungserinnerung.
- **Abrechnung als PDF** mit Brief, Übersichtsblatt, Rechenweg je Position, QR-Code (GiroCode) bei Nachzahlung, Belegeinsicht.

### KI-Integration
- **Nicht implementiert.** Keine LLM-Anbindung.

### OCR / Belegscanning
- **Nicht implementiert.** Belege werden als PDF/Foto hochgeladen und manuell zugeordnet.

### MCP
- **Nicht implementiert.**

### DACH: BetrKV / Mietrecht
- **BetrKV-Katalog** (`betrkv.py`) — der herausragende Teil:
  - Alle 17 § 2 BetrKV-Nummern mit Bezeichnungen.
  - Seed legt je Nummer eine Kostenart an (inkl. doppelter Nr. 3 für Entwässerung + Niederschlagswasser).
  - `betrkv_nr` als Pflichtfeld in `CostCategory` mit DB-Check.
  - Zuordnung fremder Namen zu Katalognummern.
- **HeizkostenV, CO2KostAufG, § 35a EStG** detailliert implementiert.
- **Personentage** korrekt nach Recht.
- **Leerstand & Eigennutzung** in Verteilung.

### Tech-Stack
- Python 3, Flask, Flask-SQLAlchemy, SQLite/MySQL, Jinja2, WeasyPrint o. ä. für PDF, Docker.

### Was können WIR übernehmen?
1. **BetrKV-Katalog (`betrkv.py`)** — 1:1 portierbar als Python-Modul für unsere Kostenarten.
2. **Rechenkern-Architektur** (`rechenkern.py`): Trennung von DB und Berechnung, frozen Vorgang, deterministisch, gut testbar.
3. **Zähler-/Verbrauchslogik** (Hauptzähler, Allgemeinverbrauch, Personentage).
4. **HeizkostenV-Logik** (inkl. Warmwasser, Zwischenablesung, Eichfrist).
5. **CO2KostAufG-Logik**.
6. **§ 35a EStG Lohnanteil-Logik**.
7. **PDF-Abrechnungsstruktur** mit Rechenweg je Position.

### Was ist besser / schlechter als unsere Lösung?
- **Besser:** BetrKV-Katalog sehr sauber; Rechenkern extrem gut dokumentiert und getestet; DACH-Logik tief (Heizung, CO2, §35a, Personentage); PDF mit Rechenweg und GiroCode.
- **Schlechter:** Kein KI, kein MCP, kein OCR, kein modernes Frontend (Flask/Jinja2), SQLite, lokale Single-User-App, kein SaaS-Multi-Tenant.
- **Lizenz:** GPL-3.0 — stärker als AGPL, aber weiterhin Open Source. Ideen/Algorithmen frei.

---

## 5. s3gv/immobase — Score 73%

### Architektur
- **PHP 8.4 + Symfony 8.1**, modular nach Domänen aufgeteilt (Module je Bounded Context).
- **Datenbank:** PostgreSQL 16.
- **Webserver:** FrankenPHP (Caddy).
- **ORM:** Doctrine mit PHP 8 Attributes.
- **UI:** Twig + Tailwind CSS, kaum JS, **kein Node-Build**.
- **Deployment:** Docker Compose, 3 Befehle.
- **Sicherheit:** RBAC, 2FA (TOTP/E-Mail-Code), Recovery-Codes, CSP, rate-limited Login, container non-root.
- **Plugin-System:** HTTP-Schnittstelle, Plugins als eigene Prozesse mit eigener UID hinter Netzsperre.
- **Tests:** 1.400+ automatisierte Tests, PHPStan level max, Deptrac.
- **Lizenz:** AGPL-3.0-or-later.

### Datenmodell (Doctrine-Entities + 64 Migrationen)
Kern-Entitäten:

| Entität | Kernfelder |
|---------|------------|
| `auth_user` | id UUID, email, display_name, password, extra_roles, number, status, 2FA-Daten |
| `party` | Kontakte (Mieter, Eigentümer, Firmen), Adressen als JSON-Array, status |
| `property` | id UUID, number, name, management modes, address, building, heating, landRegister, shares, accounting |
| `property_unit` | property_id, number, label, usage, measures, meaNumerator, households, owners |
| `property_unit_owner` / `property_unit_household` | Eigentümeranteile, Personenzahl je Zeitraum |
| `finance_cost_kind` | name, apportionable, ordering, is_system — 17 BetrKV-Positionen |
| `finance_distribution_key` | propertyId?, name, kind (area/mea/persons/units/metered/fixed), system, shares |
| `finance_distribution_key_share` | key_id, unit_id?, share |
| `finance_cost_item` | number, propertyId, cost_kind_id, distribution_key_id, due, apportionment, metering, measure, years |
| `finance_cost_item_year` | item_id, fiscalYear, grossCents |
| `finance_advance_payment` | Vorauszahlungen |
| `billing_statement` | property_id, fiscal_year, period, label, kinds, release, reserve, documents |
| `billing_statement_document` | Abrechnungs-PDF je Empfänger |
| `dunning_claim` / `dunning_notice` | Forderungen, Mahnstufen, Verzugszinsen |
| `portal_enquiry` / `portal_attachment` | Mieter-/Eigentümerportal mit verschlüsselten Anhängen |
| `audit_*` | Änderungsprotokoll |

**Besonderheiten:**
- Geldbeträge durchgehend als ganze Cent (kein Float).
- **Weight-Klasse** (`Weight.php`): Dezimalzahlen mit 3 Nachkommastellen × 1000 für exakte Verteilung.
- Verteilung über `App\Shared\Money\Money::allocate()` (wahrscheinlich Largest-Remainder/Hare).

### Geschäftslogik: NK-Abrechnung, Umlage, Heizkosten
- **Kostenarten** zentral gepflegt, umlagefähig/nicht umlagefähig, mit BetrKV-Reihenfolge.
- **Verteilerschlüssel-Arten:**
  - `area` — berechnet aus Unit-Fläche.
  - `mea` — Miteigentumsanteile.
  - `persons` — Personenzahl am Mietverhältnis.
  - `units` — gleich je Einheit.
  - `metered` — erfasster Verbrauch.
  - `fixed` — feste Anteile am Schlüssel.
- **Kostenposition** (`CostItem`) hat:
  - `Apportionment` (umlagefähig ja/nein, tagesgenau aufteilen ja/nein).
  - `Metering` (Mengeneinheit).
  - `ChosenMeasure`.
  - `CostItemYear` — Jahreswerte, damit alte Abrechnungen nicht überschrieben werden.
- **Abrechnungslauf** (`Statement`):
  - Ein Objekt, ein Wirtschaftsjahr, viele Empfänger.
  - Kann gleichzeitig **Hausgeldabrechnung (WEG)** und **Nebenkostenabrechnung (Miete)** erzeugen.
  - Korrekturen erhöhen `iteration` (Versionierung).
  - Freigabe-Status (`draft` → released), eingefrorene Daten.
  - Vermögensbericht / Erhaltungsrücklage-Entwicklung im Abrechnungsjahr (§ 28 Abs. 4 WEG).
- **Tagesgenaue Aufteilung** bei Mieter-/Eigentümerwechsel.

### KI-Integration
- **Nicht implementiert.** Keine LLM/OCR-Features.
- **Plugin-Schnittstelle** könnte KI-Plugins aufnehmen.

### OCR / Belegscanning
- **Nicht implementiert.**

### MCP
- **Nicht implementiert.**

### DACH: BetrKV / Mietrecht / WEG
- **BetrKV:** 17 Kostenarten aus § 2 als `finance_cost_kind` mit `ordering`.
- **WEG:**
  - Miteigentumsanteile (MEA) an Einheit, Eigentümer teilen Anteil.
  - Wirtschaftsplan, Hausgeldabrechnung.
  - Vermögensbericht § 28 Abs. 4 WEG (WEMoG).
  - Erhaltungsrücklage.
- **Mahnwesen:** Mahnstufen, Verzugszinsen, Mahnschreiben PDF, gerichtliches Mahnverfahren-Übersicht.
- **E-Rechnung:** XRechnung (CII) für Gewerbe-Dauermietrechnung und Betriebskostenabrechnung.
- **DIN 5008** Briefkopf für alle Schreiben.

### Tech-Stack
- PHP 8.4, Symfony 8.1, PostgreSQL 16, Doctrine, Twig, Tailwind, FrankenPHP, Docker.

### Was können WIR übernehmen?
1. **Domain-Driven-Modularisierung** nach Symfony-Modulen — Architektur-Inspiration.
2. **Kostenposition mit Jahreswerten** (`CostItemYear`) — wichtig für Korrekturhistorie.
3. **Verteilerschlüssel-Modell** mit `area/mea/persons/units/metered/fixed`.
4. **WEG-Abrechnungslauf** inkl. Hausgeld + Miet-NK in einem Durchgang.
5. **Vermögensbericht § 28 WEG** / Erhaltungsrücklage-Entwicklung.
6. **E-Rechnung XRechnung (CII)** Implementierung als Referenz.
7. **RBAC + 2FA + Audit-Log** Sicherheitsarchitektur.
8. **Ganze-Cent-Beträge + Weight-Klasse** für exakte Verteilung.

### Was ist besser / schlechter als unsere Lösung?
- **Besser:** Sehr saubere Architektur (DDD, Module, PHPStan max, 1.400 Tests); WEG + Vermögensbericht; E-Rechnung; RBAC/2FA; Plugin-Sandbox; DIN 5008; PostgreSQL (passt zu uns).
- **Schlechter:** PHP/Symfony statt Python/FastAPI; kein KI, kein OCR, kein MCP; kein Vue.js; kein Bank-Sync; sehr umfangreich und schwer portierbar.
- **Lizenz:** AGPL-3.0-or-later.

---

## Vergleichs-Matrix der Top 5

| Kriterium | HaVeWa | mietfuchs | mietkartei.de | NebenkostenFix | immobase |
|-----------|--------|-----------|---------------|----------------|----------|
| **Tech-Stack** | Next.js/TS/Prisma/PG | Node/TS/Drizzle/SQLite | SvelteKit/TS/Drizzle/SQLite | Python/Flask/SQLAlchemy/SQLite | PHP/Symfony/Doctrine/PG |
| **Passend zu uns (FastAPI/Vue/PG)** | ▲ (PG) | ▼ (Node/SQLite) | ▼ (Svelte/SQLite) | ▲▲ (Python) | ▲ (PG) |
| **Datenmodell-Reife** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **NK-Abrechnung** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **HeizkostenV** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **BetrKV-Katalog** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **KI-Belegauswertung** | — | ⭐⭐⭐⭐⭐ | — | — | — |
| **MCP-Server** | ⭐⭐⭐⭐⭐ | — | ⭐⭐⭐⭐⭐ | — | — |
| **OCR** | — | ⭐⭐⭐⭐ (Vision) | — | — | — |
| **Bank-Sync** | ⭐⭐⭐⭐⭐ (Enable) | — | ⭐⭐⭐⭐⭐ (Enable) | — | — |
| **WEG / Hausgeld** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | — | ⭐⭐⭐⭐⭐ |
| **Ticket-System** | ⭐⭐⭐⭐⭐ | — | — | — | ⭐⭐⭐ (Portal) |
| **2FA / RBAC / Audit** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Lizenz** | AGPL/dual | AGPL | AGPL | GPL-3.0 | AGPL |

Legende: ⭐⭐⭐⭐⭐ = sehr stark / vorbildlich; — = nicht vorhanden.

---

## Empfohlene Übernahme-Priorität für unser Projekt

### Sofort übernehmbar (Algorithmen/Ideen, kein direkter Code nötig)
1. **Verteilerschlüssel-Engine** aus HaVeWa (`allocate()` + Largest-Remainder) → Python-Port.
2. **HeizkostenV-Split** (Grund-/Verbrauchskosten, 70/30, verbrauchsanteilig) aus HaVeWa/mietfuchs/NebenkostenFix.
3. **BetrKV-Katalog** aus NebenkostenFix/mietfuchs → unsere `kosten`-Kategorien mit `betrkv_nr`.
4. **Personentage-Umlage** aus mietfuchs/NebenkostenFix.
5. **Kostenposition mit Jahreswerten** aus immobase → Korrekturhistorie.

### Als Modul bauen (inspiriert, neu implementieren)
6. **KI-Belegauswertung** nach mietfuchs-Architektur:
   - Clientseitige PDF-Textebene + gerenderte Seitenbilder.
   - Zwei-Slot-Modell (Text/Bild).
   - JSON-Schema + Fallback-Stufen.
   - Consent für Datenverlassen des Hauses.
   - Anonymisierungsschicht (DSGVO) ergänzen.
7. **MCP-Server** nach HaVeWa/mietkartei.de:
   - JSON-RPC Streamable HTTP.
   - API-Token (read/write/get).
   - Tool-Discovery + CRUD + Operations.
   - Deutsche Tool-Beschreibungen.
8. **Bankabgleich** nach mietkartei.de:
   - Enable-Banking-Integration.
   - Session/Consent-Handling.
   - Umsatz-Import + Zuordnungsregeln.
9. **WEG-Modul** nach HaVeWa/immobase:
   - MEA, Untergemeinschaften, Hausgeld, Wirtschaftsplan, Rücklagen, Beschlusssammlung.

### Architektur-Lektionen
10. **Mandanten-Scoping** (`tenantId` / `accountId` in jeder Tabelle) aus HaVeWa/mietkartei.de.
11. **Audit-Log** für GoBD/DSGVO aus HaVeWa/immobase.
12. **DIN-5008-Briefe + PDF** aus HaVeWa/immobase.
13. **RBAC + 2FA + Recovery-Codes** aus immobase.
14. **Ganze-Cent-Beträge + exakte Verteilung** aus mietfuchs/immobase (nie Float für Geld).

---

## Risiken & Einschränkungen

- **Lizenzen:** Alle Top-5 sind AGPL/GPL. Direkte Code-Kopie in unseren SaaS erfordert Offenlegung oder kommerzielle Lizenz (HaVeWa bietet dual). Wir sollten **Ideen, Algorithmen und Architekturmuster** übernehmen, nicht 1:1 Code.
- **Stack-Divergenz:** HaVeWa (Next.js), mietfuchs/mietkartei.de (Node/SvelteKit/SQLite), immobase (PHP) passen nicht direkt. Nur **NebenkostenFix** ist Python, aber Flask/SQLite/Desktop.
- **OCR-Lokalität:** mietfuchs nutzt clientseitige PDF-Verarbeitung + Cloud-Vision-Modelle. Wir müssen entscheiden: Tesseract lokal (unser Plan) oder Vision-LLM (Ollama Cloud). Beides kombinierbar.
- **Anonymisierung:** Keines der Repos anonymisiert Personendaten vor KI. Unsere geplante Anonymisierungsschicht ist ein **USP**.
- **DSGVO-Mieter-Scoring:** Keines macht automatisiertes Scoring — alle lassen den Menschen entscheiden. Passt zu uns.

---

## Fazit

Die Top-5 Repos bilden zusammen fast das komplette Feature-Set ab, das wir für den MietVerwaltung-SaaS brauchen. **HaVeWa** ist die vollständigste Architektur-Referenz (WEG, MCP, Bank, Tickets), **mietfuchs** die beste KI/OCR- und NK-Logik-Referenz, **mietkartei.de** die sauberste MCP/Bank-Integration, **NebenkostenFix** der beste Python-Rechenkern und BetrKV-Katalog, **immobase** das Vorbild für DDD-Modularisierung, WEG-Vermögensbericht und Sicherheit.

Für unser MVP empfiehlt sich:
1. **NK-Abrechnung** mit Verteilerschlüssel-Engine + BetrKV-Katalog + Personentage.
2. **HeizkostenV-Logik** (70/30-Split, Verbrauch, Warmwasser).
3. **KI-Belegauswertung** nach mietfuchs, mit unserer Anonymisierungsschicht.
4. **MCP-Server** nach HaVeWa/mietkartei.de.
5. **Bankabgleich** später nach mietkartei.de.
6. **WEG-Modul** als Roadmap-Erweiterung nach HaVeWa/immobase.
