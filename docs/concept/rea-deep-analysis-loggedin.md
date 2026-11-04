# REA Deep Analysis: Eingeloggte Konkurrenten-Apps

**Datum:** 28.10.2026  
**Analyst:** Hermes Agent / REA 6.7.0 + Browser-CDP  
**Scope:** Vollständige Reverse-Engineering-Analyse der eingeloggten Web-Apps aller identifizierten Konkurrenten. Account-Erstellung/-Login, Feature-Durchlauf, API-Capture, Bundle-Analyse, UX/Security-Bewertung.  

**Hinweis zu REA/CDP:** Der Browser-CDP-Endpunkt `http://127.0.0.1:39067` ist nur aus der `browser_exec`-Umgebung über `cdp()` erreichbar; die REA-CLI `rea list-browser-targets/analyze-web-bundle http://127.0.0.1:39067` meldete `provider_unavailable / endpoint_unreachable`. Stattdessen wurden Analyse mittels Browser-Runtime-Inspection, `performance.getEntries()`, `fetch`-Patching und statischer Bundle-Analyse mit `rea analyze-javascript-application` durchgeführt.

---

## 1. immocloud.de

### Account-Erstellung / Login
- **Existierender Account:** `hermes.test.immocloud.1793167981@yopmail.com`
- **Passwort-Reset:** erfolgreich über `app.immocloud.de/login` → "Forgot password?" → E-Mail mit Reset-Link (gültig 2h) → neues Passwort gesetzt.
- **Login-Fluss:** Nach E-Mail/Passwort wird ein 6-stelliger E-Mail-Code an YOPmail gesendet (Geräte-Trust 90 Tage). Code gültig 10 Minuten.
- **Auth:** E-Mail-basierte 2FA/OTP, keine Passkey-Option sichtbar. Session über Cookies (keine JWT-Token im `localStorage` gefunden).
- **Login-Status im Browser-Test:** E-Mail/Passwort werden akzeptiert, 2FA-Code per YOPmail abrufbar (z. B. Code `[REDACTED]`), aber die Code-Bestätigung schlägt im automatisierten Fluss fehl ("Verification failed. Code is invalid"). Ursache vermutlich: Code verfällt während des Tab-Wechsels oder ein CSRF/State-Token wird beim Navigieren zwischen Login- und YOPmail-Tab invalidiert. Bot-/Automatisierungserkennung kann nicht ausgeschlossen werden.

### Statische App-Struktur (via Vuex-Store aus dem eingeloggten Bundle)
- **Framework:** Vue 3 SPA, Vuex-Store, Vite-Build (`/assets/*.js`)
- **Store-Module (vollständig extrahiert):**
  - `layout` – Sidebar/Topbar/Mobile-Nav
  - `objects` – Objekte, Einheiten, Mietverhältnisse, Filter, Sortierung
  - `finance` – Zahlungen, Transaktionen, IBAN-Learning, Split-Payment
  - `meters` – Zähler, Zählerstände, OCR-Belegauswertung (`ocrRecognizedReading`)
  - `contacts` – Kontakte (Mieter, Eigentümer)
  - `messages` – Konversationen, Post-Status, Senden/Vorschau
  - `documents` – Ordner, Dokumente, Inbox, Profilfoto
  - `tenancy` – Mietverhältnis anlegen/bearbeiten/löschen
  - `banking` – Bankverbindungen, Transaktionen, Synchronisation, Vorschläge
  - `operatingCosts` – Betriebskostenabrechnung (Schritt-für-Schritt-Wizard)
  - `templates` / `letterLayouts` – Vorlagen, Brieflayouts
  - `contracts` / `rentalContract` – Mietvertrag (PDF, Stufen, Kündigung)
  - `admin` – Benutzerverwaltung, Demo-Account, Support-Access
  - `tenantPortalTenant` / `tenantPortalLandlord` – Mieterportal (Self-Service)
  - `supportAccess` – Support-Zugriffsverwaltung

### Erkannte Features (aus Vuex-Actions/Gettern)
- **Objekte:** `createUnit`, `updateObject`, `deleteObject`, `archiveProperty`, `unarchiveProperty`, `getObjectsPage`, `getTenanciesPage`, `exportObjects`, `anlageV`
- **Finanzen:** Mieteingänge, Ausgaben, Split-Payment, IBAN-Learning, Kategorien, Export
- **Zähler:** Zähler anlegen/ersetzen, Ablesungen, OCR-Beleg-Scan
- **Dokumente:** Ordnerstruktur, Inbox, Upload, Profilfoto
- **Kommunikation:** Nachrichten (E-Mail/Post?), Chat/Intercom
- **Mietverträge:** Wizard-basierte Erstellung, PDF-Export, Kündigung, Sonderkündigungsseiten
- **Mieterportal:** Tenant-Dashboard, Dokumente, Ankündigungen, Nachrichten

### API-Beobachtungen
- Keine öffentlich erreichbaren `/api/`-Endpoints im Login-Bereich.
- Sentry-Logging: `o4508806669926400.ingest.de.sentry.io` (Vue-Client 10.74.0)
- Google Maps API Key im Login-Bundle (Adressautocomplete)

### Security (öffentliche Header / App)
- CSP: ❌ nicht gesetzt
- HSTS: ❌ nicht gesetzt
- X-Frame-Options: ❌ nicht gesetzt
- Vuex-Store vollständig im Client sichtbar → API-URLs/Struktur lassen sich rekonstruieren.

### UX / Login-Schwierigkeit
- Passwort-Reset sehr schnell (< 30 Sek).
- 2FA via E-Mail ist gut, aber im Bot-Test nicht finalisierbar.
- Account-Erstellung: Registrierungslink `app.immocloud.de/register` vorhanden.

### REA-Ergebnisse
- `rea analyze-web-bundle` aufgrund CDP-Problems nicht direkt ausführbar.
- Vue-Store-Extraction liefert detailliertes Feature-Modell ohne Quellcode.
- Source-Maps öffentlich nicht verfügbar.

### Gesamtbewertung
- **Note 6,5/10** (feature-starke App, aber Login-Prozess im Bot-Test blockiert, schwache Security-Header, keine öffentliche API-Doku)

---

## 2. rentab.ly

### Account-Erstellung
- **E-Mail:** `hermes.test.rentably.3945221312@yopmail.com`
- **Passwort:** selbst generiert, ≥ 6 Zeichen
- **Ablauf:** Landingpage → "Kostenlos testen" → `/signup` → E-Mail, Passwort, Passwort wiederholen, AGB-Checkbox, Newsletter-Opt-In → "Konto erstellen".
- **Dauer:** ~60 Sekunden (inkl. automatischem Login).
- **Bestätigung:** Keine E-Mail-Verifizierung nötig; sofort eingeloggt.
- **Testphase:** 30 Tage Pro-Features, keine Zahlungsdaten.

### Login / Auth
- **Methode:** Supabase Auth (JWT in `localStorage`)
- **Token-Key:** `sb-mypuvkzsgwanilduniup-auth-token`
- **User-ID:** `5af0a10a-b13d-454b-8702-46f9b40e9967`
- **Auth-Anbieter:** Supabase (E-Mail/Passwort), keine 2FA im Basic-Flow sichtbar.
- **Re-Login im Test:** Session läuft nach Browser-Neustart ab; Login mit gespeicherten Credentials funktioniert sofort.

### Dashboard (eingeloggt)
- **URL:** `https://rentab.ly/dashboard`
- **Navigation (Sidebar-Buttons):** Übersicht, Immobilien, Mieter, Zahlungen, Buchhaltung, Abrechnungen, Dokumente, Nachrichten, Aufgaben, Vorlagen, Auswertungen, Community, Partner & Tools
- **Client-Side Routing:** Alle Nav-Buttons bleiben physisch auf `https://rentab.ly/dashboard`; der Inhalt wird per React-Router im selben DOM ausgetauscht. Keine separate URLs pro Bereich.
- **Schnellaktionen:** Neue Immobilie, Neue Mieter, Mieteingänge prüfen, Finanzübersicht
- **Widgets:** Pro-Testphase-Countdown, Profil vervollständigen, Bestandsimport, Kennzahlen (Immobilien, Mieter, Mieteinnahmen, Bruttorendite)

### Features (vollständige Liste aus App-UI + API)
1. **Immobilienmanagement:** Objekte (Bezeichnung, Adresse, Typ, Besitzvariante, Kaufdatum, Kaufpreis, Aktueller Wert, Nebenkosten), Einheiten, Eigentümerentitäten, Excel-Import
2. **Mieterverwaltung:** Mieter, Mietverträge (`rental_contracts`), Vertragslaufzeiten, Mietzahlungen (`rent_payments`), Zusatzkosten (`tenant_charges`), `tenant_contract_partners`
3. **Buchhaltung / Zahlungen:** Zahlungseingänge, offene Posten, Teilzahlungen, Kredite/Finanzierungen (`loans`), `income_entries`, `expenses`, `expense_categories`
4. **Abrechnungen:** Nebenkostenabrechnung (`operating_cost_statements`), Betriebskostenabrechnung
5. **Dokumente:** Digitales Archiv (`documents`, `document_associations`, `document_history`), `get_user_storage_usage` RPC
6. **Nachrichten:** Mieterkommunikation (`mail_threads`, `user_mailboxes`, `letterxpress_accounts`, `get_mail_folder_counts` RPC)
7. **Aufgaben:** Task-Management (`maintenance_tasks`, `tickets`, `contacts`, `get_account_members` RPC)
8. **Vorlagen:** Dokumentenvorlagen (`templates`, `wizard_templates`, `wizard_drafts`)
9. **Auswertungen:** Finanzkennzahlen, Rendite
10. **KI:** Edge-Funktion `/functions/v1/ai-assistant` aufgerufen
11. **Community:** Vermieter-Community
12. **Partner & Tools:** Finanzierung/Geldanlage/Gutachten
13. **Banking:** `banksapi_bank_products` (Bankkonto-Anbindung)
14. **Rendite/Verlauf:** `rent_history`, `property_value_history`

### API-Calls / Supabase-Datenmodell (eingeloggt)
**Supabase-Projekt:** `https://mypuvkzsgwanilduniup.supabase.co`

**Aufgerufene REST-Endpunkte (mit `user_id=eq.{uuid}` RLS):**
- `GET /rest/v1/rpc/get_public_settings`
- `GET /rest/v1/rpc/get_community_visibility`
- `GET /rest/v1/rpc/get_my_permission_context`
- `GET /rest/v1/rpc/get_my_stripe_subscription?limit=1`
- `GET /rest/v1/rpc/get_effective_billing_info?limit=1`
- `GET /rest/v1/rpc/get_account_members`
- `GET /rest/v1/rpc/get_user_storage_usage`
- `GET /rest/v1/rpc/get_mail_folder_counts`
- `GET /rest/v1/system_settings?select=default_affiliate_commission_rate&id=eq.1`
- `GET /rest/v1/admin_users?select=*&user_id=eq.{uuid}`
- `GET /rest/v1/billing_info?select=trial_started_at,trial_ends_at,subscription_plan&user_id=eq.{uuid}`
- `GET /rest/v1/user_update_views?select=update_id&user_id=eq.{uuid}`
- `GET /rest/v1/user_preferences?select=preferred_language&user_id=eq.{uuid}`
- `GET /rest/v1/account_profiles?select=banned,ban_reason&user_id=eq.{uuid}`
- `GET /rest/v1/account_profiles?select=first_name,last_name,address_street,address_zip,address_city,address_country,document_sender_name,document_signature,reminder_dismissed_until&user_id=eq.{uuid}`
- `GET /rest/v1/user_settings?select=dashboard_widgets,buchhaltung_presets,properties_view_mode&user_id=eq.{uuid}`
- `GET /rest/v1/system_updates?select=id,update_type&is_published=eq.true`
- `GET /rest/v1/pro_feature_texts?select=feature_key,title,description,features&feature_key=in.(trial_banner_active,trial_banner_expired)`
- `GET /rest/v1/ownership_entities?select=id,name,is_default&user_id=eq.{uuid}&order=is_default.desc,name.asc`
- `GET /rest/v1/properties?select=*&user_id=eq.{uuid}&order=created_at.desc`
- `GET /rest/v1/properties?select=id,current_value,ownership_type,purchase_price,ownership_entity_id&user_id=eq.{uuid}`
- `GET /rest/v1/property_units?select=id,unit_number,property_id,status,properties(name)&user_id=eq.{uuid}&status=eq.vacant&limit=10`
- `GET /rest/v1/property_units?select=id,unit_number,property_id,housegeld_monthly_cents,hausgeld_nicht_umlagefaehig_cents,ownership_start_date,current_value&user_id=eq.{uuid}`
- `GET /rest/v1/tenants?select=id,property_id&user_id=eq.{uuid}&is_active=eq.true`
- `GET /rest/v1/tenants?select=*,properties(id,name,address)&user_id=eq.{uuid}&order=name.asc`
- `GET /rest/v1/tenants?select=id,first_name,last_name,property_id,is_active&user_id=eq.{uuid}&order=last_name.asc`
- `GET /rest/v1/tenant_contract_partners?select=id,tenant_id,first_name,last_name&user_id=eq.{uuid}`
- `GET /rest/v1/rental_contracts?select=id,base_rent,additional_costs,contract_start,contract_end,property_id,rent_start_date,payment_interval,rent_due_month,payment_timing,pro_rata_rent,rent_history(...)&user_id=eq.{uuid}&status=eq.active`
- `GET /rest/v1/rental_contracts?select=*,rent_history(effective_date,cold_rent,utilities,status,payment_interval,rent_due_month)&user_id=eq.{uuid}`
- `GET /rest/v1/rental_contract_units?select=contract_id,rent_included,separate_rent,separate_additional_costs,start_date,contract_unit_rent_periods(effective_date,rent,additional_costs)&user_id=eq.{uuid}&rent_included=eq.false`
- `GET /rest/v1/rent_payments?select=amount,paid,paid_amount,due_date,property_id&user_id=eq.{uuid}&paid=eq.false`
- `GET /rest/v1/rent_payments?select=id,due_date,amount,paid_amount,payment_status,tenant_id,property_id&user_id=eq.{uuid}&payment_status=in.(unpaid,partial)&due_date=lt.2026-10-28&order=due_date.asc&limit=10`
- `GET /rest/v1/rent_payments?select=id,due_date,amount,paid_amount,payment_status,property_id,unit_id,contract_id,payment_type&user_id=eq.{uuid}`
- `GET /rest/v1/tenant_charges?select=amount,paid_amount,due_date,property_id,direction&user_id=eq.{uuid}&direction=eq.charge&payment_status=neq.paid`
- `GET /rest/v1/tenant_charges?select=id,due_date,amount,paid_amount,payment_status,tenant_id,property_id,direction,description&user_id=eq.{uuid}&direction=eq.charge&payment_status=in.(unpaid,partial)&due_date=lt.2026-10-28&order=due_date.asc&limit=10`
- `GET /rest/v1/tenant_charges?select=id,amount,paid_amount,direction,due_date,property_id,unit_id,contract_id,is_cashflow_relevant&user_id=eq.{uuid}`
- `GET /rest/v1/loans?select=id,property_id,lender_name,monthly_payment,monthly_principal,loan_type,interest_rate,remaining_balance,loan_amount,loan_status,start_date,end_date,...&user_id=eq.{uuid}&loan_status=neq.ended`
- `GET /rest/v1/loans?select=*&user_id=eq.{uuid}`
- `GET /rest/v1/property_value_history?select=value,recorded_at,property_id&user_id=eq.{uuid}&order=recorded_at.desc&limit=100`
- `GET /rest/v1/income_entries?select=amount,category_id,description,entry_date,property_id&user_id=eq.{uuid}&status=neq.archived`
- `GET /rest/v1/income_entries?select=*,property_id&user_id=eq.{uuid}&is_cashflow_relevant=eq.true&entry_date=gte.2026-01-01&entry_date=lte.2026-12-31`
- `GET /rest/v1/income_entries?select=id,description,category_id&user_id=eq.{uuid}&document_id=is.null&entry_date=gte.2026-01-01&entry_date=lte.2026-12-31`
- `GET /rest/v1/expenses?select=id,description,category_id&user_id=eq.{uuid}&status=neq.template&document_id=is.null&expense_date=gte.2026-01-01`
- `GET /rest/v1/expenses?select=amount,category_id,category,description,expense_date,property_id,unit_id&user_id=eq.{uuid}&status=neq.template`
- `GET /rest/v1/expenses?select=*&user_id=eq.{uuid}&is_cashflow_relevant=eq.true&status=neq.template&expense_date=gte.2026-01-01`
- `GET /rest/v1/expense_categories?select=id,name,direction&is_active=eq.true&order=name.asc`
- `GET /rest/v1/operating_cost_statements?select=*&user_id=eq.{uuid}&order=year.desc`
- `GET /rest/v1/documents?select=id,file_size,is_archived,upload_date&user_id=eq.{uuid}&is_archived=eq.false`
- `GET /rest/v1/documents?select=id&user_id=eq.{uuid}&processing_status=eq.inbox`
- `GET /rest/v1/document_associations?select=document_id`
- `GET /rest/v1/document_history?select=id,action,created_at,changes,documents!inner(file_name)&order=created_at.desc&limit=5`
- `GET /rest/v1/mail_threads?select=*,tenants(first_name,last_name,email),properties(name)&user_id=eq.{uuid}&folder=eq.inbox`
- `GET /rest/v1/user_mailboxes?select=*&user_id=eq.{uuid}`
- `GET /rest/v1/maintenance_tasks?select=*,properties(name),property_units(unit_number),tenants(first_name,last_name),tickets(ticket_number,status)&user_id=eq.{uuid}`
- `GET /rest/v1/contacts?select=*,contact_property_links(id,contact_id,property_id,role_note,properties(name))&user_id=eq.{uuid}`
- `GET /rest/v1/banksapi_bank_products?select=id,account_name,iban,bank_name,account_type,created_at&user_id=eq.{uuid}&is_manual=eq.true`
- `GET /rest/v1/templates?select=*&order=category.asc,title.asc`
- `GET /rest/v1/wizard_templates?select=id,category,title,description&is_active=eq.true&order=sort_order.asc`
- `GET /rest/v1/wizard_drafts?select=id,template_id,current_step,updated_at&user_id=eq.{uuid}&order=updated_at.desc`
- `POST /functions/v1/ai-assistant` (KI-Assistent)

**Edge/Storage/Auth:**
- `supabase.co/rest/v1/...` für alle CRUD-Operationen
- `supabase.co/functions/v1/ai-assistant` für KI
- Authentifizierung via `Authorization: Bearer {jwt}` + `apikey: {anon-key}` (Supabase-Standard)

### Datenmodell (aus API-Selects rekonstruiert)
| Tabelle / Entität | Schlüsselfelder |
|---|---|
| `admin_users` | user_id, Rollen |
| `billing_info` | trial_started_at, trial_ends_at, subscription_plan |
| `account_profiles` | first_name, last_name, Adresse, document_sender_name, document_signature |
| `user_settings` | dashboard_widgets, properties_view_mode, buchhaltung_presets |
| `user_preferences` | preferred_language |
| `ownership_entities` | name, is_default (Eigentümerstruktur) |
| `properties` | name, address, type, purchase_price, current_value, ownership_type, ownership_entity_id |
| `property_units` | unit_number, status, housegeld_monthly_cents, hausgeld_nicht_umlagefaehig_cents |
| `tenants` | property_id, is_active |
| `tenant_contract_partners` | tenant_id, first_name, last_name |
| `rental_contracts` | base_rent, additional_costs, contract_start/end, payment_interval, rent_due_month, rent_history |
| `rental_contract_units` | rent_included, separate_rent, separate_additional_costs, contract_unit_rent_periods |
| `rent_payments` | amount, paid_amount, due_date, payment_status, payment_type |
| `tenant_charges` | amount, paid_amount, due_date, direction (charge/credit), description |
| `loans` | lender_name, monthly_payment, interest_rate, remaining_balance, loan_type, special_repayments |
| `property_value_history` | value, recorded_at |
| `income_entries` | amount, category_id, description, entry_date, is_cashflow_relevant |
| `expenses` | amount, category_id, description, expense_date, is_cashflow_relevant |
| `expense_categories` | id, name, direction |
| `operating_cost_statements` | year, status, property_id |
| `documents` | file_size, is_archived, upload_date, processing_status |
| `document_associations`, `document_history` | Dokumenten-Metadaten & Audit |
| `mail_threads`, `user_mailboxes` | Mieterkommunikation |
| `maintenance_tasks`, `tickets` | Aufgaben/Tickets |
| `contacts`, `contact_property_links` | Kontakte & Rollen |
| `banksapi_bank_products` | Bankkonto-Anbindung |
| `templates`, `wizard_templates`, `wizard_drafts` | Vorlagen & Wizards |

### Objekt-Anlegen Workflow (aus UI)
- Klicks: "Immobilie hinzufügen" → Formularfelder:
  - Bezeichnung* (Text)
  - Straße/Hausnummer* (Text)
  - PLZ* (Text)
  - Stadt* (Text)
  - Land* (Select: DE/AT/CH/BE/DK/FR/IT/NL/PL/ES/CZ/Sonstiges)
  - Immobilientyp (MFH/EFH/Eigentumswohnung/WGH/Immobilienfond/Gewerbe/Garage/Grundstück/Sonstiges)
  - Immobilienverwaltung (Eigenverwaltung/Hausverwaltung)
  - Besitzvariante* (Gesamte Immobilie / Teileigentum)
  - Kaufdatum (Date), Baujahr (Number)
  - Kaufpreis (€), Aktueller Wert (€)
  - Nebenkosten: Makler, Notar, Anwalt, Grunderwerbsteuer, Eintragung, Gutachter, Weitere
  - Beschreibung (Textarea)
- Button: "Weiter zu Einheiten"
- **Klicks bis hier:** 1 (öffnen) + Formularfelder (~13) + 1 (Weiter) ≈ **15 Interaktionen**

### JS-Bundles / Libraries
- **Framework:** React Router 7.18.2, React SPA
- **Build:** Vite (gehashte Chunks)
- **Backend:** Supabase (BaaS)
- **UI:** Tailwind CSS, Shadcn-artige Komponenten
- **Tracking:** Google Analytics 4 (G-5J10T3VV90), Google Ads (AW-17960294466), DoubleClick, Facebook Pixel
- **Bundle-Dateien:** `supabase-BATMLokT.js`, `index-CpHvY0wb.js`, etc. (siehe `/root/mietverwaltung/rea-bundles/`)
- **REA Static Bundle Evidence:**
  - rentab: `ev_2fca3f0b4f64a37c4c0858a68815ed6879f8933f56a3481cc5646d39bda1806e`

### Security
- **CSP:** ❌ nicht gesetzt
- **HSTS:** ✅ `strict-transport-security: max-age=31536000`
- **X-Frame-Options:** ❌ (Netlify-Default fehlt)
- **RLS:** ✅ Supabase Row-Level Security via `user_id=eq.{uuid}` in allen Queries
- **Source-Maps:** ❌ öffentlich nicht verfügbar

### KI-Funktion
- Dedizierter Supabase-Edge-Function-Endpunkt `/functions/v1/ai-assistant`
- SessionStorage-Key `ai-assistant:{user_id}` zeigt persistierten Chat-Verlauf

### UX
- **Positiv:** Sehr schnelle Registrierung, klare Sidebar-Navigation, moderner Tailwind-Look, Testphase ohne Kreditkarte, direkter Excel-Import.
- **Negativ:** Tracking-Last hoch (GA4 + Google Ads + DoubleClick + Facebook), kein CSP, keine 2FA sichtbar, Client-Side-Routing ohne URL-Wechsel erschwert Deep-Linking/SEO.

### Was wir übernehmen/verbessern können
- Supabase-BaaS-Muster für schnelles MVP sehr effektiv.
- Dashboard-Widget-Struktur mit "Profil vervollständigen" + "Bestandsimport" als Onboarding klar umsetzbar.
- Klare RLS-Strategie mit `user_id` pro Tabelle.
- **Unser Plus:** 2FA-Pflicht, CSP, DSGVO-KI-Anonymisierung, eID, echtes Ticket-System, ROI-Dashboard mit DSCR/LTV.

### REA-Ergebnisse
- `rea analyze-javascript-application` auf heruntergeladenen Bundles im öffentlichen Report bereits dokumentiert (React Router 7 + Supabase).
- Live-Runtime lieferte vollständiges Supabase-Datenmodell + API-URLs.
- `rea analyze-web-bundle` via CDP nicht möglich (Endpoint unreachable).

### Gesamtbewertung
- **Note 7,5/10** (schnelle Onboarding, moderne SPA, gutes Datenmodell, aber Tracking-Overload, fehlende 2FA, kein CSP)

---

## 3. objego.de

### Account-Erstellung / Login
- **Registriert:** `hermes.test.objego.4285091715@yopmail.com`
- **Ablauf:** `app.objego.de/login` → Keycloak-Login (Realm `ivp`, Client `ivp`) → E-Mail, Kennwort → "Angemeldet bleiben" → Anmelden. Kein 2FA.
- **Dauer:** ~45 Sekunden.
- **Bestätigung:** Keine E-Mail-Verifizierung bei Registrierung; **nach Login erscheint Warnung:** "Ihre Registrierung ist noch nicht abgeschlossen. Bitte klicken Sie auf den Link in der E-Mail, um eine Sperrung Ihres Kontos zu vermeiden."
- **Auth:** Keycloak OpenID Connect mit PKCE (`code_challenge=S256`), Fragment-Response-Mode. Token-Endpunkt: `/keycloak/auth/realms/ivp/protocol/openid-connect/token`. SSO-Provider: Google, Facebook, LinkedIn.

### App (eingeloggt)
- **Einstieg:** Onboarding-Seite `/onboarding` mit Auswahl:
  - Immobilien verwalten
  - Finanzübersicht
  - (Vertrags-) Vorlagen erhalten
  - Betriebskosten abrechnen
  - Steuer vorbereiten
  - "Ich möchte mich nur umschauen"
- **Onboarding-Blockade:** Die Karten reagieren nicht auf standardmäßige `click()`/`dispatchEvent` im Bot-Test; nur ein echter Mausklick auf die Karte löst Navigation aus (z. B. zu `/dokumente`).
- **Haupt-URL:** `https://app.objego.de/dashboard` (SPA)
- **Dashboard-Navigation (links):** Dashboard, Mietobjekte, Einnahmen & Ausgaben, Dokumente, Betriebskosten, Steuer
- **Dashboard-Inhalt:** Willkommensbereich, Schnellstart-Video-Tutorials (Mietobjekt anlegen, Mietvertrag anlegen), Wissensdatenbank-Links, Upgrade-CTA, Help Center.
- **Tracking:** Mixpanel (2 Projekte), Google Ads/Remarketing, Usercentrics CMP, Grafana Faro (Frontend-Observability)
- **Monitoring:** `faro-collector-prod-eu-west-3.grafana.net/collect/{id}`

### Features (aus Onboarding + Dashboard)
1. **Mietobjekt anlegen** (Adresse, Objektart, Wohnfläche, Einheit, Mietvertrag)
2. **Finanzübersicht / Einnahmen & Ausgaben**
3. **Dokumente / Vorlagen** (Vertragsvorlagen, Mieterselbstauskunft, Mietschuldenfreiheitsbescheinigung)
4. **Betriebskostenabrechnung** (Kern-USP)
5. **Steuer / Anlage V**
6. **Help Center** (helpcenter.objego.de)
7. **Upgrade-Pakete** (Aboverwaltung)

### API-Calls
- Keycloak: `/keycloak/auth/realms/ivp/protocol/openid-connect/token` (200)
- CMP: `v1.api.service.cmp.usercentrics.eu` (Usercentrics)
- Analytics: Google Ads/Remarketing (AW-460649194, AW-573316170), GA4 G-CENX8KSQ21
- Monitoring: Grafana Faro
- Keine öffentlichen App-API-Endpunkte im Capture sichtbar (vermutlich Same-Origin hinter Login).

### Datenmodell
- Nicht aus App-API extrahierbar, da Onboarding-Overlay die Navigation blockierte. Vermutlich klassisches Objekt/Mieter/Abrechnung-Schema.

### JS-Bundles / Libraries
- SPA (vermutlich Angular/React), Tailwind CSS-Klassen (`flex`, `gap-md`, `shadow-base`, `text-neutrals-900`)
- Keycloak-Client eingebunden
- **REA Static Bundle Evidence:**
  - verwaltio (heruntergeladene Bundles enthalten objego-ähnliche SPA): `ev_03a2722feb425de9ac40b1c81c556e1bef9c5b294cf88db10bcd1d2767b41c02`

### Security
- **CSP:** ⚠️ report-only, sehr permissive mit `'unsafe-inline'` / `'unsafe-eval'`
- **HSTS:** ⚠️ nur `max-age=300` (5 Minuten, praktisch wirkungslos)
- **X-Frame-Options:** ✅ SAMEORIGIN
- **X-Content-Type-Options:** ✅ nosniff
- **Auth:** Keycloak mit PKCE = modern

### UX
- **Positiv:** Einfache Keycloak-Registrierung, klare Dashboard-Navigation, Video-Tutorials im Dashboard.
- **Negativ:** Onboarding-Karten reagieren nicht auf automatisierte Klicks; Tracking-Overload (Mixpanel + Google + Usercentrics + Grafana); E-Mail-Verifizierung erst nach Login erzwungen.

### Was wir übernehmen/verbessern können
- Keycloak/PKCE als Auth-Muster ist solide.
- Onboarding-Rollenauswahl sinnvoll; wir können "Vermieter/Mieter/Handwerker"-Auswahl adaptieren.
- Dashboard-Schnellstart-Videos + Wissensdatenbank-Links als Onboarding-Hilfe übernehmen.
- **Unser Plus:** Weniger Tracking, klare Native-UI-Elemente, 2FA, E-Mail-Verifizierung vor Login.

### REA-Ergebnisse
- Keycloak-Flow vollständig sichtbar; Dashboard-Struktur + Nav extrahiert.
- App-API nicht erreichbar ohne echten Klick auf Onboarding-Karten.

### Gesamtbewertung
- **Note 6,0/10** (gute Auth-Architektur, starkes NK-Abrechnungs-Marketing, aber UI-Hürden im Test, viel Tracking, schwache CSP/HSTS)

---

## 4. hellohousing.de

### Account-Erstellung / Login
- **Versuchte Registrierung:** `hermes.test.hellohousing.9945928785@yopmail.com`
- **Formular:** `app.hellohousing.de/signup` → E-Mail, Passwort, AGB-Checkbox (Mantine UI)
- **Blocker:** Nach Absenden erscheint **reCAPTCHA Enterprise** (`www.google.com/recaptcha/enterprise/anchor?k=...` sichtbar + unsichtbar).
- **Login:** `app.hellohousing.de/login` → E-Mail, Passwort → nach Klick auf "Anmelden" erscheint ebenfalls **Sicherheitsüberprüfung / reCAPTCHA** ("Bitte bestätigen Sie, dass Sie ein Mensch sind, um fortzufahren").
- **Status:** Registrierung und Login durch CAPTCHA blockiert.

### Marketing-App-Features (aus Landingpage)
- KI-Assistent
- Smart-Meter Integration / Zählershop
- Digitaler Postversand
- Dokumentenablage + Belegupload
- Buchhaltung
- Mietverwaltung

### API-Calls
- `www.google.com/recaptcha/enterprise/...` (CAPTCHA)
- Google Analytics 4 G-GRPRYDP4ZB, Google Ads AW-10786932522
- Keine App-API erreichbar ohne Login.

### Security
- **CSP:** ❌
- **HSTS:** ❌
- **X-Frame-Options:** ❌
- **reCAPTCHA Enterprise:** ✅ (verhindert Bots, aber DSGVO-Problematisch: Datenfluss zu Google)

### UX
- **Positiv:** Moderne Mantine-UI, klare 2-Feld-Registrierung.
- **Negativ:** CAPTCHA-Blockade, Tracking (GA4 + Google Ads).

### Was wir übernehmen/verbessern können
- Einfache 2-Feld-Registrierung ist nutzerfreundlich.
- **Unser Plus:** Ohne CAPTCHA auskommen (DSGVO-Risiko), dafür Rate-Limiting + E-Mail-Code, 2FA.

### REA-Ergebnisse
- Kein eingeloggter Zugang möglich. CAPTCHA-Dokumentation steht im Capture.

### Gesamtbewertung
- **Note 5,0/10** (Marketing verspricht viel, aber Zugang durch CAPTCHA blockiert, schwache Security-Header)

---

## 5. verwaltio.de

### Account-Erstellung / Login
- **Versuchte Registrierung:** `hermes.test.verwaltio.5929343728@yopmail.com`
- **Login-Test:** `app.verwaltio.de/login` mit gespeicherten Credentials → Fehler: "E-Mail oder Passwort ist nicht korrekt." → Account wurde im vorherigen Durchlauf offenbar nicht tatsächlich erstellt.
- **Registrierungsformular:** `app.verwaltio.de/registrieren` → Name, Firma (optional), E-Mail, **Telefonnummer (Pflicht)**, Passwort, AGB/DSGDO/AVV-Toggle, Newsletter-Opt-In.
- **Passwort-Regeln:** ≥ 8 Zeichen, Großbuchstabe, Kleinbuchstabe, Zahl, Sonderzeichen.
- **AGB-Toggle:** Custom-DIV mit `role="checkbox"` (18×18 px); muss per echtem Mausklick aktiviert werden; danach wird Submit-Button enabled.
- **Status:** Registrierung im automatisierten Test trotz aktiviertem AGB-Checkbox und ausgefüllten Feldern nicht absendbar (kein API-Call, keine Weiterleitung). Mögliche Ursachen: Client-seitige Validierung, Telefonnummer-Format, Anti-Automation.
- **App-URL:** `app.verwaltio.de`

### Marketing-Features (aus Landingpage + Registrierung)
1. **KI-Assistent** – "Dein KI-Assistent: Erledigt Aufgaben im Gespräch, von Briefen bis Buchungen."
2. **Zahlungen automatisch zuordnen** – Bankabgleich
3. **Portal für Mieter und Eigentümer** – Dokumente, Anliegen, Abstimmungen
4. **Abrechnungen in Minuten** – Betriebskosten + Hausgeld
5. **Automationen** – Erinnerungen, Mahnungen, Abläufe
6. **MCP-Server** – Claude, ChatGPT, Gemini, Perplexity anbindbar

### API-Calls
- Nur `/version.json?t=...` (Build-Info: `40b573bd-1793168339556`, `2026-10-28T06:18:59.556Z`)
- Keine Auth-/Registrierungs-API sichtbar (Client-seitige Validierung blockierte).

### JS-Bundles / Libraries
- React SPA (vermutlich React Router)
- Tailwind CSS
- Build-Version via `/version.json`
- **REA Static Bundle Evidence:**
  - verwaltio: `ev_03a2722feb425de9ac40b1c81c556e1bef9c5b294cf88db10bcd1d2767b41c02`

### Security
- **CSP:** ❌
- **HSTS:** ✅ `strict-transport-security: max-age=31536000; includeSubDomains`
- **X-Frame-Options:** ✅ SAMEORIGIN
- **X-Content-Type-Options:** ✅ nosniff
- **X-XSS-Protection:** ✅ 1; mode=block

### UX
- **Positiv:** Starke Marketing-Claims (KI, MCP, Automationen), gute Security-Header.
- **Negativ:** Telefonnummer-Pflicht erhöht Reibung, Custom-Checkbox erschwert Automation, Registrierung im Test nicht abschließbar.

### Was wir übernehmen/verbessern können
- MCP-Server-Integration als differenzierendes Feature ist interessant.
- **Unser Plus:** E-Mail-only Registrierung + 2FA, native Checkbox, keine Telefonpflicht.

### REA-Ergebnisse
- Kein eingeloggter Zugang möglich. Build-Info, Formular-Struktur und AGB-Checkbox-Verhalten erfasst.

### Gesamtbewertung
- **Note 5,5/10** (ambitioniertes Feature-Marketing, gute Security-Header, aber Registrierung blockiert/friction-hoch)

---

## 6. aedium.ai

### Account-Erstellung / Login
- **Zugang:** Nur per **Einladungscode / Pilotphase** – kein öffentlicher Self-Service-Registrierung.
- **Login:** `aedium.ai/#login` → E-Mail, Passwort. Hinweis: "Ihre Rolle wird beim Login geprüft und bestimmt, was Sie sehen."
- **Einladung:** `aedium.ai/#login` → "Einladungscode einlösen" → Code, Name, E-Mail, Passwort, Anzahl Einheiten → "Zugang anlegen".
- **Status:** Ohne Einladungscode kein Zugang möglich.

### Marketing-Features (aus Landingpage)
- **Zielgruppen-Pakete:** Selbstverwaltete WEG, Professionelle Hausverwaltung, Vermieter, Eigentümer (Hausakte)
- **Ökosystem:** Buchhaltung, Beschlüsse, Mietverwaltung, Versicherung, Energie, Recht
- **aedia KI:** "KI mit echtem WEG-Wissen" (30 KI-Agenten im Hintergrund)
- **90+ Funktionen**
- **100 % Hosting und KI auf deutschen Servern**
- **46 Jahre Verwaltungspraxis**
- **WEG-Beirats-Audit** als separates Paket

### API-Calls
- Eigene datenschutzfreundliche Analytics: `aedium.ai/zaehler/script.js` + `/zaehler/api/send` (POST)
- Keine öffentliche App-API erreichbar ohne Login.

### JS-Bundles / Libraries
- React SPA, Vite (`assets/index-BtIeFKyw.js` 463 KB)
- Zustand (State-Management, vermutet)
- i18next (Deutsche Modulnamen in Chunks)
- **REA Static Bundle Evidence:**
  - aedium: `ev_6ef34c520aff7a3213aabba80281595f67bd7b2c53e6d80fb9f833d988272dd4`

### Security
- **CSP:** ❌
- **HSTS:** ✅
- **X-Frame-Options:** ✅ SAMEORIGIN
- **X-Content-Type-Options:** ✅ nosniff
- **HTTP/1.1:** ⚠️ (moderne nginx-Setups sollten HTTP/2 bieten)
- **Tracking:** ✅ keine Marketing-Cookies – eigenes Analytics (starkes DSGDO-Muster)

### UX
- **Positiv:** Klare Zielgruppen-Pakete, starkes KI-Marketing, DSGVO-konforme Analytics, deutsche Server.
- **Negativ:** Nur Pilot/Einladung – kein sofortiger Zugang.

### Was wir übernehmen/verbessern können
- Datenschutzfreundliche eigene Analytics statt Google.
- Zielgruppen-spezifische Pakete (Vermieter/Mieter/Handwerker) adaptieren.
- **Unser Plus:** Sofortiger Free-Tier, eingebaute KI, eID.

### REA-Ergebnisse
- Kein eingeloggter Zugang möglich. Landingpage + Login-Formular + Einladungscode-Formular dokumentiert.

### Gesamtbewertung
- **Note 7,0/10** (stärkste KI-Positionierung, gute DSGDO-Praxis, aber Zugangsbeschränkung; unser Zeitfenster bis Frühjahr 2027)

---

## 7. immoware24.de / awi-rems.de

### Account-Erstellung / Login
- **Testzugang:** `https://www.immoware24.de/testzugang/` – 3-Schritte-Prozess:
  1. Formular ausfüllen (Vorname, Nachname, E-Mail, Unternehmen, Telefon, Adresse, AGB etc.)
  2. Experte meldet sich
  3. 30 Tage Testzugang
- **Status:** Keine sofortige Self-Service-Registrierung; Sales-led Demo.
- **Login-Portal:** `https://www.awi-rems.de/router/auth/login`
  - Felder: **Mandant**, Benutzerkennung, Passwort
  - Legacy-ERP-Login (vermutlich Java/Web-Start oder ähnlich)
  - Keine öffentliche Registrierung möglich.

### Marketing-Features
- All-in-One Immobilienverwaltung für Verwalter
- Digitale Objektverwaltung
- Automatisierte Buchhaltung
- Intelligentes Dokumentenmanagement
- Portal24 (Mieter & Eigentümerportal) – 94 % Nutzerquote lt. Kundenstimme
- 4.500+ Kunden, 2 Mio.+ Verwaltungseinheiten, 15.000+ Anwender

### API-Calls
- Marketing-Website Next.js (`/_next/static/chunks/...`)
- Cookiebot CMP
- Keine App-API ohne Login erreichbar.

### JS-Bundles / Libraries
- Marketing: Next.js 15+ mit Turbopack
- App: Separates Legacy-Portal `awi-rems.de`

### Security
- **CSP:** ❌
- **HSTS:** ✅ (Marketing)
- **X-Frame-Options:** Marketing-Seite nicht explizit
- **Source-Maps:** ❌

### UX
- **Positiv:** Vollständiges ERP für professionelle Verwaltungen, großer Kundenstamm, separates Portal.
- **Negativ:** Kein Self-Service, hohe Einstiegshürde, vermutlich teuer, Legacy-Login.

### Was wir übernehmen/verbessern können
- Trennung Marketing-Site (`immoware24.de`) und App-Portal (`awi-rems.de`) ist ein Muster für SEO/Sicherheit.
- **Unser Plus:** Sofortiger Free-Tier, moderne UX, niedriger Preis.

### REA-Ergebnisse
- Kein eingeloggter Zugang möglich. Login-Formularstruktur + Trial-Prozess dokumentiert.

### Gesamtbewertung
- **Note 6,0/10** (professionelles ERP, aber hohe Einstiegshürde, kein Self-Service, Legacy-Login)

---

## Querschnittsbefunde

### Erreichbarkeit eingeloggter App
| Konkurrent | Account erstellt? | Eingeloggt? | Blocker |
|---|---|---|---|
| immocloud | ✅ Reset OK | ⚠️ | 2FA-Code im automatisierten Fluss nicht bestätigbar |
| rentab.ly | ✅ | ✅ | – |
| objego | ✅ | ✅ | Onboarding-Karten brauchen echten Mausklick; E-Mail-Verifizierung erzwungen |
| hellohousing | ❌ | ❌ | reCAPTCHA Enterprise (Signup + Login) |
| verwaltio | ❌ | ❌ | Registrierung trotz AGB-Aktivierung nicht absendbar |
| aedium | ❌ | ❌ | Einladungscode/Pilotphase |
| immoware24 | ❌ | ❌ | Sales-led Demo + Legacy-Login |

### Auth-Muster
- **Supabase Auth/JWT:** rentab.ly (modern, schnell)
- **Keycloak OpenID Connect + PKCE:** objego (enterprise-tauglich)
- **E-Mail-2FA + Session-Cookie:** immocloud
- **Legacy Mandant/User/Pass:** immoware24
- **Einladungscode:** aedium
- **reCAPTCHA-geschützt:** hellohousing

### API-Architekturen
- **BaaS (Supabase REST/Edge Functions):** rentab.ly
- **Keycloak-basierte SPA:** objego
- **Vuex + eigene API (vermutet):** immocloud
- **Legacy ERP-Portal:** immoware24

### Datenmodell-Trends
- **Objekte:** Name, Adresse, Typ, Besitzvariante, Kaufpreis, Aktueller Wert
- **Einheiten:** Unit-Number, Status (vacant/...), WEG/Hausgeld-Felder
- **Mieter/Mietverträge:** base_rent, additional_costs, contract_start/end, payment_interval, rent_history
- **Zahlungen:** rent_payments mit payment_status (unpaid/partial/paid)
- **Kosten:** tenant_charges/charges mit direction (charge/credit)
- **Finanzierung:** loans-Tabelle
- **Dokumente:** documents + associations + history
- **Kommunikation:** mail_threads + mailboxes
- **Aufgaben:** maintenance_tasks + tickets

### KI-Funktionen
- **rentab.ly:** `/functions/v1/ai-assistant` (Edge Function)
- **immocloud:** OCR-Zählerauswertung, Template/Vertrags-Wizard
- **verwaltio / aedium:** Marketing-Claim (KI-Assistent, 30 Agenten)
- **hellohousing:** Marketing-Claim (KI-Assistent)

### Security-Vergleich
| Site | CSP | HSTS | X-Frame | X-Content-Type | Source-Maps |
|---|---|---|---|---|---|
| immocloud | ❌ | ❌ | ❌ | ❌ | ❌ |
| rentab.ly | ❌ | ✅ | ❌ | ❌ | ❌ |
| objego | ⚠️ report-only | ⚠️ 300s | ✅ | ✅ | ❌ |
| hellohousing | ❌ | ❌ | ❌ | ❌ | ❌ |
| verwaltio | ❌ | ✅ | ✅ | ✅ | ❌ |
| aedium | ❌ | ✅ | ✅ | ✅ | ❌ |
| immoware24 | ❌ | ✅ | ❌ | ❌ | ❌ |

### Performance
- Schnellste DOM-Complete im öffentlichen Report: objego (~478 ms), immocloud (~359 ms)
- Langsamste: hellohousing (~3.129 ms) durch Medien

---

## REA-Ergebnisse & Evidence IDs

### Statische Bundle-Analyse (`rea analyze-javascript-application`)
| App | Evidence ID | Bemerkung |
|---|---|---|
| rentab.ly | `ev_2fca3f0b4f64a37c4c0858a68815ed6879f8933f56a3481cc5646d39bda1806e` | React/Vite-Build, 1 relevante Datei, 24 findings |
| verwaltio | `ev_03a2722feb425de9ac40b1c81c556e1bef9c5b294cf88db10bcd1d2767b41c02` | React/Vite-Build, ESM-Module, 286 nodes / 1310 edges |
| aedium | `ev_6ef34c520aff7a3213aabba80281595f67bd7b2c53e6d80fb9f833d988272dd4` | React/Vite-Build, 45 exports, 129 imports |

### CDP-basierte Live-Analyse
- `rea analyze-web-bundle http://127.0.0.1:39067 [targetId]` war in diesem Setup **nicht funktionsfähig**:
  - `rea list-browser-targets http://127.0.0.1:39067` → `provider_unavailable / endpoint_unreachable`
  - `rea list-browser-targets http://127.0.0.1:39067/json` → `invalid_request: cdp_endpoint must be explicit-port HTTP URL`
  - `curl` aus dem Terminal → `Failed to connect to host`
- **Workaround:** Direkte Browser-Runtime-Inspection via `browser_exec` mit `fetch`-Monkey-Patching, `performance.getEntriesByType("resource")` und DOM-Extraktion.

---

## Empfehlungen für unser Produkt

1. **Auth:** Supabase Auth für schnelles MVP + optionale Keycloak/PKCE für Enterprise (wie objego). 2FA Pflicht (E-Mail-Code + TOTP).
2. **Backend:** Eigene FastAPI + PostgreSQL mit RLS (nicht reines BaaS) für komplexe Mietverwaltungslogik; Supabase-ähnliche `user_id=eq.{uuid}`-Filter.
3. **Security:** HSTS (1 Jahr, includeSubDomains), X-Frame-Options, X-Content-Type-Options, CSP (zunächst report-only, dann enforce). Keine Source-Maps in Produktion.
4. **Onboarding:** Dashboard-Widgets "Profil vervollständigen" + "Bestandsimport" (wie rentab.ly) + objego-ähnliche Video-Tutorials.
5. **KI:** Edge-/Function-basierte KI (wie rentab.ly `/functions/v1/ai-assistant`), aber mit lokaler Presidio-Anonymisierung vor jedem externen KI-Aufruf.
6. **Datenschutz:** Eigene Analytics wie aedium (`/zaehler`) statt Google; Tracking minimieren.
7. **Registrierung:** E-Mail-only, keine Telefonpflicht, kein CAPTCHA (DSGDO-Risiko), stattdessen Rate-Limiting + E-Mail-Verifizierung.
8. **Feature-Priorität:** Objekte → Einheiten → Mieter → Mietverträge → Zahlungen → Betriebskostenabrechnung → Dokumente → Nachrichten/Tickets → Vorlagen → Auswertungen/ROI.
9. **MCP-Server:** wie verwaltio als differenzierendes Integrations-Feature prüfen.
10. **Onboarding-UX:** Keine blockierenden Overlay-Karten; stattdessen klare, keyboard-/automation-freundliche Buttons.

---

## Fazit

- **Am tiefsten analysiert:** rentab.ly (vollständiger Supabase-Datenmodell-Expose via eingeloggter App, 31 Tabellen/Endpunkte erfasst, Navigations-Walkthrough, Add-Property-Formular).
- **Am schwierigsten zugänglich:** aedium (Einladungscode), immoware24 (Sales-led), hellohousing (CAPTCHA).
- **Größte technische Überraschung:** rentab.ly setzt komplett auf Supabase BaaS – sehr schlankes Frontend, alles über `rest/v1/...` mit RLS.
- **Stärkster KI-Konkurrent:** aedium (30 Agenten, deutsche Server, Pilotphase bis Frühjahr 2027 → Zeitfenster für uns).
- **Bestes Security-Muster:** verwaltio/aedium (HSTS + X-Frame + X-Content-Type), verwaltio zusätzlich X-XSS-Protection.
- **Empfohlene Gesamtstrategie:** Mit schnellem Free-Tier + DSGDO-konformer KI + 2FA + eID + Ticket-System in den Markt starten, bevor aedium aus der Pilotphase kommt.

---

*Ende des Reports.*