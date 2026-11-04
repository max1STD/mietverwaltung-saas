# Zammad Source-Code-Analyse für MietVerwaltung

Ziel: Verstehen, wie ein professionelles Open-Source Ticket-System aufgebaut ist, um Pattern, Datenmodell und Features für das eigene MietVerwaltung-Ticket-System zu übernehmen.

Quelle: `https://github.com/zammad/zammad` (geklont nach `/root/mietverwaltung/repos/zammad`, shallow clone, 220 MB).

---

## 1. Architektur

### 1.1 Technologie-Stack

| Ebene | Technologie |
|-------|-------------|
| Sprache / Framework | **Ruby 3.4.12** mit **Ruby on Rails 8.1** |
| Datenbank | **PostgreSQL** (einzig unterstützter ORM; `pg` Gem) |
| Session-Store | ActiveRecord-Session-Store |
| Web-Server | Puma |
| Background-Jobs | Delayed Job mit ActiveRecord-Adapter |
| Caching | Redis, optionales Memcached (`dalli`) |
| Frontend Build | **Vite** + `vite_rails` |
| API | **REST** (`/api/v1`) + **GraphQL** (`/graphql`) |
| Auth/OAuth | Doorkeeper + OmniAuth (SAML, OIDC, Google, Microsoft, GitHub, Twitter, …) |
| State Machine | `aasm` Gem (modell-eigene State-Management-Patterns) |
| Authorization | `pundit` |
| i18n / l10n | Eigenes `Translation`-Modell, `twitter_cldr`, CLD für Spracherkennung |

### 1.2 Gesamtarchitektur

Zammad folgt einem **klassischen Rails-MVC**, ist aber stark durch **Concerns / Mixins** und einen **Service-Layer** gegliedert:

- `app/models` – 70+ Modelle, viele mit `include` von fachlichen Modulen (History, Tags, Search-Index, Audit-Logs, Activity-Stream, …).
- `app/controllers` – 168 Controller; REST-API, Webhooks, Channel-Controller, Integrationen.
- `app/services` – Geschäftslogik wird zunehmend in Services ausgelagert (`Service::AI::*`, `Service::Ticket::*`, `Service::ContentTranslation::*`, …).
- `app/graphql` – Moderne Desktop-/Mobile-App kommuniziert primär über GraphQL.
- `lib/` – Domain-Logik, die nicht direkt Rails-ORM ist (z. B. `Escalation`, AI-Provider, LDAP, E-Mail-Parser).
- `db/migrate` – 544 Migrationen; kein `schema.rb`, stattdessen ist der DDL-Zustand rein migrationsbasiert.

### 1.3 Frontend

- **Neues Frontend**: `app/frontend/` mit **Vue 3**, **Pinia**, **Vue Router**, **Vite**, **Apollo Client/GraphQL**, **Tailwind CSS**, **FormKit**, **Tiptap** (Rich Text).
  - Zwei Apps: `apps/desktop` und `apps/mobile` (inkl. PWA).
- **Legacy-Frontend**: `app/assets/javascripts` (CoffeeScript/Backbone-artige Struktur), wird aber abgelöst.
- Realtime-Updates via GraphQL-Subscriptions + Rails ActionCable/WebSocket.

---

## 2. Datenmodell

### 2.1 Tabellen-Übersicht (131 Tabellen)

Kern-Tabellen (Auswahl):

- `users`, `organizations`, `groups`, `roles`, `permissions`
- `roles_users`, `groups_users`, `permissions_roles`, `roles_groups`, `organizations_users`
- `tickets`, `ticket_articles`, `ticket_states`, `ticket_state_types`, `ticket_priorities`
- `ticket_article_types`, `ticket_article_senders`, `ticket_article_flags`
- `histories`, `history_types`, `history_objects`, `history_attributes`
- `tags`, `tag_items`, `tag_objects`
- `stores`, `store_files`, `store_objects`, `store_provider_dbs`
- `slas`, `calendars`
- `triggers`, `jobs`, `macros`, `core_workflows`, `postmaster_filters`
- `channels` (E-Mail, Telegram, WhatsApp, Facebook, SMS, …)
- `webhooks`, `authorizations`, `tokens`, `ldap_sources`
- `mentions`, `links`, `link_types`, `link_objects`
- `overviews`, `taskbars`, `recent_views`
- AI-Tabellen: `ai_agents`, `ai_text_tools`, `ai_provider_connections`, `ai_feature_providers`, `ai_stored_results`, `ai_analytics_runs`, `ai_analytics_usages`

### 2.2 Ticket-Modell

`Ticket` hat folgende Schlüsselfelder:

- `group_id`, `priority_id`, `state_id`, `organization_id`
- `number` (eindeutig), `title`
- `owner_id` (Agent), `customer_id`
- Zeitstempel: `first_response_at`, `close_at`, `last_contact_at`, `last_contact_agent_at`, `last_contact_customer_at`, `pending_time`
- Eskalation: `escalation_at`, `first_response_escalation_at`, `update_escalation_at`, `close_escalation_at`
- Statistik: `first_response_in_min`, `update_in_min`, `close_in_min`, `*_diff_in_min`
- `preferences` (JSON/Text), `article_count`, `type`, `time_unit`
- `ai_agent_running` (Flag für laufende KI-Agenten)

Beziehungen:

```ruby
has_many :articles, class_name: 'Ticket::Article'
has_one  :shared_draft, class_name: 'Ticket::SharedDraftZoom'
belongs_to :state,  class_name: 'Ticket::State'
belongs_to :priority, class_name: 'Ticket::Priority'
belongs_to :owner,  class_name: 'User'
belongs_to :customer, class_name: 'User'
belongs_to :group
has_many :ai_stored_results, class_name: 'AI::StoredResult', as: :related_object
```

### 2.3 Ticket-Artikel (Kommentare / Notizen / E-Mails)

`Ticket::Article` speichert jede einzelne Kommunikation/Notiz:

- `ticket_id`, `type_id` (z. B. E-Mail, Telefon, Chat, Note), `sender_id` (Kunde/Agent/System)
- `from`, `to`, `cc`, `subject`, `reply_to`, `message_id`, `message_id_md5`
- `content_type` (`text/plain` oder `text/html`), `body` (bis 20 MB)
- `internal` (Sichtbarkeit), `detected_language` (Spracherkennung)
- `origin_by_id` (tatsächlicher Absender bei Stellvertretung)
- Beliebige Anhänge über `Store.list(object: 'Ticket::Article', o_id: id)`

### 2.4 Ticket-Historie / Audit-Log

- **Generisches Historien-System** in `histories`:
  - `history_type` (z. B. `created`, `updated`, `merged_into`, `received_merge`)
  - `history_object` (z. B. `Ticket`, `Ticket::Article`)
  - `history_attribute` (z. B. `state`, `group_id`)
  - `o_id` + `related_o_id`, `id_from`/`id_to`, `value_from`/`value_to`
- `History.add(...)` wird über `HasHistory` Concern automatisch bei Änderungen geschrieben.
- Zusätzlich modernes `audit_logs` mit JSON-Diff (`value_from`/`value_to`) und polymorphem `auditable`.

### 2.5 Zuweisung: Agent / Gruppe / Rolle

- **Gruppen (`groups`)**: Tickets gehören immer zu einer Gruppe. Gruppen sind baumartig verschachtelbar (`parent_id`, max. Tiefe 10).
- **Agent-Zuordnung**: `groups_users` mit `access` (`full`, `read` o. ä.).
- **Rollen & Rechte**: `roles` → `permissions_roles`; `roles_users`, `roles_groups`.
- **Owner**: `tickets.owner_id` (konkreter Agent). `owner_id == 1` bedeutet „nicht zugewiesen“.
- Auto-Zuweisung via Setting `ticket_auto_assignment` + Selector.

### 2.6 Prioritäten

`ticket_priorities`:

- `name`, `default_create`, `ui_icon`, `ui_color`, `active`
- Standard-Priorität beim Erstellen via `default_create = true`.

### 2.7 Tags / Kategorien

- Tags sind **generisch** für beliebige Objekte:
  - `tag_items` (Namen), `tag_objects` (Objekt-Typ wie `Ticket`), `tags` (Verknüpfung `tag_item` + `tag_object` + `o_id`).
- Beliebige Kategorien können über `ObjectManager::Attribute` als Custom Fields ergänzt werden.

### 2.8 Anhänge / Datei-Uploads

- **Store-Pattern**: `stores` verknüpft Objekt + Datei.
- `store_files` speichert SHA + Provider; `store_provider_dbs` hält Binärdaten (bis 200 MB).
- Deduplizierung über SHA.
- Anhänge werden in `Ticket::Article` über `Store.list(object: 'Ticket::Article', o_id: article.id)` geholt.
- Upload-Cache (`UploadCache`) für Formulare vor dem Speichern.
- Inline-Bilder in HTML-Artikeln via `cid:` aufgelöst.

---

## 3. Ticket-Workflow

### 3.1 Stati

`ticket_states` sind in `ticket_state_types` kategorisiert:

- `new`, `open`, `closed`, `merged`
- `pending reminder`, `pending action`
- Kategorien im Code: `:open`, `:closed`, `:work_on`, `:work_on_all`, `:viewable`, `:pending_reminder`, `:pending_action`, `:merged`

`Ticket::State.by_category(:open)` liefert alle offenen Stati.

### 3.2 Status-Übergänge

- Jeder `ticket_state` kann ein `next_state_id` haben.
- `Ticket.process_pending` läuft regelmäßig:
  - Pending-Action → nächster Status wenn `pending_time` erreicht.
  - Pending-Reminder → sendet Erinnerung an Agenten.
- Geschlossene Tickets können zeitlich begrenzt wiedereröffnet werden (`reopen_time_in_days`).

### 3.3 State-Machine

- Kein globales AASM-Modell auf Ticket-Ebene.
- Stati werden über **StateTypes** und **Default-Flags** (`default_create`, `default_follow_up`, `default_close`) gesteuert.
- Übergänge werden in Callbacks (`Ticket::SetsCloseTime`, `Ticket::ResetsPendingTimeSeconds`, `Ticket::ChecksReopenAfterCertainTime`) und Services abgebildet.

### 3.4 Eskalation / SLA

- `slas` haben `first_response_time`, `response_time`, `update_time`, `solution_time` und eine `condition` (Selektor, auf welche Tickets sie greifen).
- `calendars` definieren Geschäftszeiten/Feiertage (Gem `biz`).
- `Escalation` berechnet in Geschäftszeiten:
  - `first_response_escalation_at`, `update_escalation_at`, `close_escalation_at`
  - `escalation_at` = nächstes anstehendes Eskalationsdatum
- `Ticket.process_escalation` läuft periodisch, sendet Warnung/Eskalations-Events an Agenten.

### 3.5 Auto-Reply

- Auto-Reply ist **kein separater Workflow**, sondern wird über **Trigger** realisiert:
  - Aktion `notification.email` mit Empfänger `ticket.customer` und Template.
- Eingehende E-Mails durchlaufen `PostmasterFilter` bevor Trigger greifen.

### 3.6 Trigger / Automatisierungen

- **Trigger** (`triggers`) – eventbasiert bei Ticket-/Artikel-Änderungen:
  - `condition` + `perform` als serialisierte Hashes.
  - Perform-Actions: `notification.email`, `notification.sms`, `notification.webhook`, `article.note`, `attribute_updates`, `ai.ai_agent`, `checklist.add_from_template`, `delete`.
- **Jobs** (`jobs`) – zeitgesteuert (cron-artig via `timeplan`):
  - Laufen alle 10 Minuten, matchen Tickets/Objekte via Selektor und führe `perform_changes` aus.
- **Macros** – manuelle Agenten-Aktionen, gleiche Perform-Syntax.
- **Core Workflows** – feld-/bildschirmabhängige Validierung/Sichtbarkeit.

Ausführung läuft über `CanPerformChanges`, das Actions in Phasen `initial`, `before_save`, `after_save`, `after_commit` ausführt.

---

## 4. KI-Features

### 4.1 Architektur: Provider + Features

KI ist vollständig über `AI::ProviderConnection` + `AI::FeatureProvider` entkoppelt:

- `ai_provider_connections` speichert Endpoint, Token, Modell, Embedding-Config.
- Unterstützte Provider (Adapter in `lib/ai/provider/*.rb`):
  - **OpenAI** (`gpt-4.1` default, `text-embedding-3-small`)
  - **Anthropic**
  - **Azure OpenAI**
  - **Mistral**
  - **Ollama**
  - **Zammad AI** (eigener hosted Service `https://ai.zammad.com`)
  - **Custom OpenAI-compatible**
- `AI::FeatureProvider` routed Features zu einer Connection.
- Provider-Health wird in `status` JSONB der Connection gespeichert.

### 4.2 KI-Ticketzusammenfassung

- Service: `Service::AI::Feature::TicketSummarize`
- Identifier: `ticket_summarize`
- Prompts: ERB-Templates in `app/services/service/ai/feature/prompts/{system,user}/ticket_summarize.txt.erb`
- System-Prompt: „Summarize ticket conversations into structured, concise sections. Always respond in `<locale>`“.
- User-Prompt: XML-Struktur mit `<title>` und `<article>`-Blöcken (sender, visibility, text, OCR-Text von Anhängen).
- Output ist **JSON** mit:
  - `language`
  - `customer_request` (~30 Wörter)
  - `conversation_summary` (2–4 Absätze)
  - `open_questions` (optionell)
  - `upcoming_events` (optionell)
  - `customer_mood` / `customer_emotion` (optionell)
- Ergebnisse werden in `ai_stored_results` gecacht; Cache-Schlüssel enthält Ticket + Artikel-Version.
- Job `TicketAIAssistanceSummarizeJob` führt die Zusammenfassung asynchron aus und pushed per GraphQL-Subscription ans Frontend.

### 4.3 KI-Schreibassistent (Text Tools)

- Modell: `AI::TextTool` + `Service::AI::Feature::TextTool`
- Identifier: `text_tool`
- Admin definiert **Instruktion** (`instruction`) pro Text Tool; optional Gruppen-Zuordnung.
- System-Prompt: Instruktion + `fixed_instructions`
- User-Prompt: aktueller Editor-Inhalt
- Kein JSON-Output, HTML-Text wird zurückgegeben und in den Editor eingefügt.
- Analytics über `ai_analytics_usages` inkl. Bewertung (thumbs up/down).

### 4.4 KI-Agenten für Automatisierung

- Modell: `AI::Agent`
- Jeder Agent hat:
  - `agent_type` (z. B. `TicketCategorizer`, `TicketPrioritizer`, `TicketGroupDispatcher`, `TicketTitleRewriter`, `TicketTagger`, `TicketTextExtractor`, `CustomAiAgent`)
  - `definition` (Role, Instruction, Instruction Context, Entity Context, Result Structure)
  - `action_definition` (Mapping der KI-Ausgabe auf Ticket-Attribute via Perform-Changes-Syntax)
- Ausführung:
  - Trigger/Job können `ai.ai_agent` als Action aufrufen.
  - `TriggerAIAgentJob` sperrt pro Ticket+Agent (`ActiveJobLock`) und führt `Service::AI::Agent::Run` aus.
  - `Service::AI::Agent::Run` baut Prompt-Kontext (`Service::AI::Agent::Run::Context`), ruft `Service::AI::Feature::AIAgent` auf, wendet Ergebnis via `ticket.perform_changes(...)` an.
  - `tickets.ai_agent_running` verhindert parallele Läufe.

### 4.5 Spracherkennung

- Gem: `cld` (Chrome Language Detection)
- Helper: `LanguageDetectionHelper.detect(text)`
- Automatisch bei Artikel-Erstellung: `Ticket::Article#detect_language` (`before_validation :detect_language, on: :create`).
- Speichert ISO-Code in `ticket_articles.detected_language`.
- Setting `language_detection_article` schaltet Feature an/aus.

### 4.6 Weitere KI-Features

- **Übersetzung** (`Service::AI::Feature::Translate`) – Artikel/Knowledge-Base in andere Sprachen, gecacht in `Service::ContentTranslation::StoredTranslation`.
- **OCR** (`Service::AI::Feature::OCR`) – Bilder werden vor der Zusammenfassung/Indexierung via KI OCR'd.
- **Knowledge-Base-Antwort aus Ticket** (`knowledge_base_answer_from_ticket`).
- **Vector Search** (`Service::AI::VectorDB::*`) für ähnliche Knowledge-Base-Artikel; Embeddings werden in pgvector-ähnlicher Tabelle (AI::VectorDB) gespeichert.

---

## 5. API & Integrationen

### 5.1 REST API

- Basis-Pfad: `/api/v1`
- Routes sind in `config/routes/*.rb` aufgeteilt (z. B. `ticket.rb`, `user.rb`, `trigger.rb`, `webhook.rb`).
- JSON-API mit CRUD + spezialisierten Actions:
  - `/api/v1/tickets`, `/api/v1/ticket_articles`, `/api/v1/ticket_attachment/...`
  - `/api/v1/tickets/:id/summarize` (KI)
  - `/api/v1/tickets/:id/knowledge_base_answers`
  - `/api/v1/ticket_overviews`
- Auth: Session-Cookie oder OAuth-Access-Token.
- Keine klassischen ActiveModel-Serializer; Controller nutzen `model_*_render`-Helpers und asset-artige JSON-Ausgaben.

### 5.2 GraphQL API

- Single Endpoint: `/graphql`
- 610+ GraphQL-Dateien, 311+ Types.
- Moderne Desktop-App und Mobile-App nutzen ausschließlich GraphQL + Apollo Client.
- Subscriptions für Realtime (Ticket-Updates, AI-Assistance, Link-Updates, Checklisten).

### 5.3 Integrationen

| Integration | Mechanismus |
|-------------|-------------|
| **GitHub / GitLab** | `Integration::IssueTrackerController` + Services `Service::Ticket::ExternalReferences::IssueTracker::*`; speichert Issue-Links in `ticket.preferences` |
| **Microsoft 365 / Google** | OAuth-Flow über `ExternalCredential` + `ExternalCredentialsController`; Mailbox/Graph API als Channel |
| **Telegram** | `telegram-bot-ruby` Gem; Webhook-Endpoint `ChannelsTelegramController#webhook`; Bot-Messages werden zu Tickets/Artikeln |
| **WhatsApp** | `whatsapp_sdk` Gem; Webhook-Verifizierung + Payload-Verarbeitung in `Whatsapp::Webhook::*` |
| **Facebook** | Channel über `koala` Gem |
| **SMS / Twilio / MessageBird** | Channel-Controller |
| **CTI (Placetel, Sipgate)** | `Integration::CtiController` + `cti_logs` |
| **LDAP** | `Integration::LdapController` + `Ldap`/`Ldap::User`/`Ldap::Group`; Import-Jobs |
| **Exchange** | Autodiscover + Viewpoint Gems |
| **S/MIME, PGP** | `smime_certificates`, `pgp_keys` |
| **iDoit / Check_MK** | `Integration::*Controller` |

### 5.4 Webhooks

- Modell: `webhooks`
- Trigger können `notification.webhook` als Action ausführen → `TriggerWebhookJob`.
- Payload: Standard `{ ticket: ..., article: ..., event: { type, execution, changes, user_id }, webhook: ... }` oder individualisiertes Template/Pre-Defined-Webhooks.
- Signatur, Basic-Auth, Bearer-Token, SSL-Verify, benutzerdefinierte HTTP-Methoden.
- Retry-Logik: 5 Versuche mit exponentiellem Backoff.

### 5.5 LDAP / SSO

- LDAP-Server als `ldap_sources` gespeichert; regelmäßige Synchronisation als `ImportJob`.
- SSO:
  - OmniAuth-Callbacks: `/auth/:provider/callback`
  - SAML (`omniauth-saml`), OpenID Connect (`omniauth_openid_connect`)
  - Eigener SSO-Endpunkt `/auth/sso`
- Doorkeeper (`oauth_applications`, `oauth_access_tokens`) ermöglicht externe OAuth-Apps.

---

## 6. Empfehlung für MietVerwaltung

### 6.1 Patterns / Architektur, die wir übernehmen sollten

1. **Trennung Kommunikation vs. Ticket-Kern**
   - `tickets` = Metadaten, Zuweisung, Status, SLA.
   - `ticket_articles` = jede einzelne Nachricht/Notiz.
   - Ermöglicht Multi-Channel (E-Mail, Chat, WhatsApp, Telefon) mit einem einheitlichen Datenmodell.

2. **Generisches Historien-System**
   - Nicht pro Objekt eine Historientabelle, sondern `histories` + `history_objects`/`history_attributes`.
   - Einfach erweiterbar für Mieter, Verträge, Rechnungen, Tickets.

3. **Generisches Tag-System**
   - `tags` + `tag_items` + `tag_objects` ermöglicht Tagging über alle Objekte hinweg.

4. **Store-Pattern für Dateien**
   - Deduplizierung via SHA, Trennung von Metadaten (`stores`) und Binärdaten (`store_files`).
   - Einfacher Upload-Cache vor dem endgültigen Speichern.

5. **Trigger / Job / Macro mit einheitlicher Perform-Syntax**
   - `condition` + `perform` als JSON/Hash.
   - Actions: Attribut ändern, E-Mail/SMS/Webhook senden, Notiz anlegen, KI-Agent ausführen, Checkliste anhängen.

6. **Service-Layer für komplexe Domain-Logik**
   - `Service::*`-Klassen statt dicke Modelle (vorbildlich bei KI, Eskalation, Übersetzung).

7. **GraphQL-First für modernes Frontend**
   - Subscriptions für Live-Updates, Apollo Client, getrennte Desktop/Mobile Apps.

8. **KI-Provider-Abstraktion**
   - `ProviderConnection` + `FeatureProvider` erlaubt Anschluss beliebter LLMs (OpenAI, Anthropic, Ollama, eigener Endpoint) ohne Code-Änderung.

9. **SLA + Geschäftszeiten**
   - `biz` Gem oder ähnliche Bibliothek für echte Geschäftszeit-Berechnung.
   - SLA-Regeln mit Selektoren (Gruppe, Priorität, Kategorie).

10. **Selektor-Framework**
    - Zammad nutzt ein `CanSelector` Concern, um überall (Overviews, Triggers, Jobs, SLAs) gleiche Filter-Syntax zu verwenden.

### 6.2 Unser Ticket-Datenmodell im Vergleich zu Zammad

| Konzept | Zammad | Empfehlung MietVerwaltung |
|---------|--------|---------------------------|
| Ticket | `tickets` (Gruppe, Status, Priorität, Kunde, Agent) | `tickets` analog; zusätzlich `property_id`, `unit_id`, `contract_id` |
| Nachrichten | `ticket_articles` | `ticket_messages` / `ticket_articles` |
| Status | `ticket_states` + `ticket_state_types` | ähnlich; Miet-spezifisch z. B. `open`, `waiting_on_tenant`, `waiting_on_landlord`, `resolved`, `closed` |
| Prioritäten | `ticket_priorities` | `ticket_priorities` + Farbe/Icon |
| Kategorien | Tags + `ObjectManager::Attribute` | `ticket_categories` (Baum) oder Tags |
| Zuweisung | Gruppe + Owner | `property_id` → automatische Gruppen-Zuordnung; `assigned_to` für Agent |
| Historie | `histories` | generisches `histories` übernehmen |
| Anhänge | `stores` / `store_files` | Store-Pattern übernehmen |
| SLA | `slas` + `calendars` | SLA für Miet-Anfragen (z. B. 48h Reaktionszeit) |
| Checklisten | `checklists` | Checklisten für Übergabe / Schadensfälle |

### 6.3 KI-Features, die wir übernehmen sollten

1. **KI-Zusammenfassung pro Ticket**
   - Prompt-Vorlage für `customer_request`, `conversation_summary`, `open_questions`.
   - Caching pro Ticket + Artikel-Version.
2. **KI-Schreibassistent für Agenten**
   - Vorlagen: „höfliche Antwort“, „Frist setzen“, „Handwerker beauftragen“.
3. **KI-Agenten für Automatisierung**
   - Ticket-Kategorisierung (z. B. `heating`, `plumbing`, `rental_payment`)
   - Priorisierung / Dringlichkeitserkennung
   - automatische Gruppen-Zuweisung basierend auf Mietobjekt/Kategorie
4. ** automatische Spracherkennung**
   - CLD oder LibreTranslate; nützlich für mehrsprachige Mieter.
5. **OCR für hochgeladene Bilder/Rechnungen**
   - Extrahiert Text aus Fotos von Schäden/Rechnungen.
6. **Ähnliche Tickets / Wissensdatenbank**
   - Embeddings für FAQs/Vorlagen; Vektordatenbank in PostgreSQL mit `pgvector`.

### 6.4 Integrationen, die wir brauchen

- **E-Mail** (Eingang/Ausgang mit IMAP/SMTP) – Pflicht
- **WhatsApp Business / Telegram** – für Mieter-Kommunikation
- **Microsoft 365 / Google OAuth** – für E-Mail-Accounts
- **LDAP / SSO** – für Verwaltungs-Mitarbeiter
- **Webhooks** – an externe Buchhaltung / CRM / Property-Management-APIs
- **GitHub/GitLab** – weniger relevant für MietVerwaltung; stattdessen Schnittstellen zu Handwerker-Portalen / Dienstleistern

### 6.5 Was macht Zammad besser als wir?

- **Reife Multi-Channel-Architektur** (E-Mail, Chat, Telefon, Social Media) mit einheitlichem Artikel-Modell.
- **Sehr flexibles Berechtigungs- und Gruppenkonzept** (Baum, Rollen, Rechte, Agent/Customer).
- **Mächtiges Trigger/Job/Macro-System** mit generischer Perform-Engine.
- **KI-Feature-Infrastruktur** (Provider-Abstraktion, Prompt-Templates, Analytics, Caching, Vektordatenbank).
- **Generische Historie, Tags, Object-Manager** für Custom Fields ohne Migration.
- **Reife GraphQL-Realtime-App**.

### 6.6 Was machen wir besser / sollten beibehalten

- **Domain-Fokus Mietverwaltung**: Zammad ist generisch; wir können direkt Miet-Entitäten (`properties`, `units`, `contracts`, `tenants`, `owners`) einbetten.
- **Vereinfachte UX**: Zammad hat 130+ Tabellen und viel Komplexität; wir können bewusst reduzieren.
- **DACH-Compliance**: Deutsche Mietrecht-Features, DSGVO-Features, GoBD-konforme Historie/Audit-Logs.
- **Schnellere Time-to-Value**: Ohne den Legacy-Übergang (CoffeeScript → Vue) starten wir direkt mit moderner Tech-Stack.

---

## 7. Fazit

Zammad ist ein exzellentes Referenzbeispiel für ein skalierbares, kanalübergreifendes Ticket-System. Die wichtigsten Bausteine für MietVerwaltung sind:

- **Ticket + Article** als Kernmodell
- **Generische Historie, Tags, Anhänge**
- **Trigger/Job/Macro-Automatisierung**
- **SLA + Geschäftszeiten**
- **KI-Provider-Abstraktion** mit Prompt-Templates, Caching und Agenten
- **GraphQL-First-Frontend** mit Subscriptions

Wir sollten diese Pattern übernehmen, aber auf Mietverwaltung fokussieren: Mietobjekte, Einheiten, Verträge und Mieter direkt mit Tickets verknüpfen; DSGVO/GoBD-Audit-Logs von Anfang an; KI gezielt für Zusammenfassung, Schreibassistent, Kategorisierung und automatische Zuweisung nutzen.
