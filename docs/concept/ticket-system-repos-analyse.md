# Open-Source Ticket-Systeme — Recherche & Analyse für MietVerwaltung

**Datum:** 2026-10-28  
**Projekt:** MietVerwaltung SaaS (Hauptreferenz: Zammad)  
**Ziel:** Passende Open-Source Ticket-Systeme finden, die 5 besten klonen & analysieren, gemeinsame Best Practices extrahieren und eine Empfehlung für unseren Workflow ableiten.  
**Speicher:** Alle Klone wurden mit `git clone --depth 1` durchgeführt (~750 MB gesamt).

---

## 1. GitHub-Übersicht: 15 Open-Source Ticket-/Helpdesk-Systeme

Gesucht wurde nach: `open source ticket system self-hosted`, `best ticketing system python`, `helpdesk open source self-hosted`, `issue tracker open source`, `customer support ticket system`.

| Repository | Stars | Sprache | Lizenz | Letztes Update | Kurzbeschreibung |
|---|---|---|---|---|---|
| [chatwoot/chatwoot](https://github.com/chatwoot/chatwoot) | 38.501 | Ruby | MIT* | 2026-10-28 | Omnichannel Customer Support Platform (Intercom/Zendesk Alternative), Captain AI Agent |
| [uvdesk/community-skeleton](https://github.com/uvdesk/community-skeleton) | 19.636 | PHP (Symfony) | OSL-3.0 | 2026-10-07 | E-Commerce-fokussierte Helpdesk-Lösung mit Workflow-Engine |
| [glpi-project/glpi](https://github.com/glpi-project/glpi) | 6.525 | PHP | GPL-3.0 | 2026-10-28 | ITSM/ITIL-konform: Tickets + Asset Management + Finanzen |
| [zammad/zammad](https://github.com/zammad/zammad) | 6.046 | Ruby (Rails) | AGPL-3.0 | 2026-10-28 | Webbasierter Helpdesk, offizielle Referenz für MietVerwaltung |
| [freescout-help-desk/freescout](https://github.com/freescout-help-desk/freescout) | 4.619 | PHP (Laravel) | AGPL-3.0 | 2026-10-28 | Leichtgewichtiger Shared Inbox / Helpdesk, Zendesk/Help Scout Alternative |
| [osTicket/osTicket](https://github.com/osTicket/osTicket) | 3.995 | PHP | GPL-2.0 | 2026-06-17 | Veteran unter den Open-Source Ticket-Systemen |
| [frappe/helpdesk](https://github.com/frappe/helpdesk) | 3.451 | Python (Frappe) + Vue | AGPL-3.0 | 2026-10-27 | Modernes Frappe-basiertes Helpdesk mit SLA & Kundenportal |
| [Peppermint-Lab/peppermint](https://github.com/Peppermint-Lab/peppermint) | 3.161 | TypeScript/Node | NOASSERTION | 2025-09-21 | Schlanke, moderne Helpdesk-Lösung mit PostgreSQL |
| [helpyio/helpy](https://github.com/helpyio/helpy) | 2.467 | Ruby (Rails) | MIT | 2023-03-08 | Mobile-friendly Helpdesk mit Knowledge Base & Community |
| [shacker/django-todo](https://github.com/shacker/django-todo) | 853 | Python (Django) | BSD-3-Clause | 2026-08-29 | Multi-User Todo/Ticketing für Django-Projekte |
| [Bytedesk/bytedesk](https://github.com/Bytedesk/bytedesk) | 514 | JavaScript | AGPL-3.0 | 2026-10-27 | IM + AI Live-Chat + E-Mail + Ticket Support |
| [aottr/paw](https://github.com/aottr/paw) | 21 | Python (Django) | MIT | 2026-02-22 | Kleines Python-Ticketsystem |
| [stepandel/tickets.md](https://github.com/stepandel/tickets.md) | 4 | Go | MIT | 2026-05-20 | File-basiertes Markdown-Ticket-System für Agent/Human-Kollaboration |
| [navapbc/rebar](https://github.com/navapbc/rebar) | 4 | Python | Apache-2.0 | 2026-10-28 | LLM-first, git-backed, event-sourced Ticket-System + MCP |
| [Open-HelpDesk/open-helpdesk](https://github.com/Open-HelpDesk/open-helpdesk) | 3 | TypeScript/Next.js | AGPL-3.0+EE | 2026-10-26 | Moderner Helpdesk mit SLA, KB, Kundenportal, EU-freundlich |

\* Chatwoot README nennt MIT, Badge zeigt teilweise `NOASSERTION` (API-Metadaten).

### Top-5-Auswahl zum Klonen

1. **Zammad** — Hauptreferenz des Projekts, reifster Workflow, SLA, Multi-Channel, PostgreSQL.
2. **Peppermint** — Moderne, schlanke Architektur (Fastify/Prisma/PostgreSQL), gute Vergleichsbasis.
3. **osTicket** — Klassischer, bewährter Ticket-Workflow, einfaches PHP-Modell.
4. **Chatwoot** — Omnichannel + eingebauter AI Agent (Captain), Ruby/Vue/PostgreSQL.
5. **Frappe Helpdesk** — Python-basiert (Frappe), Vue-Frontend, integrierte SLA, Kundenportal.

---

## 2. Top 5 im Detail

### 2.1 Zammad (zammad/zammad)

**Meta:** 6.046 ⭐ | Ruby on Rails | PostgreSQL/MySQL + Elasticsearch | AGPL-3.0 | 220 MB (depth 1)

#### Architektur
- Monolithische Rails-App, GraphQL-API (`app/graphql/gql`), REST-API, WebSocket/ActionCable für Live-Updates.
- Frontend: eigene CoffeeScript/JS-App (`app/frontend`, `app/assets/javascripts/app`).
- Background-Jobs, Scheduler, Transaction-Dispatcher für Events/Notifications.
- Eingebaute Kanäle: E-Mail, Chat, Telefon, Twitter/X, Facebook, WhatsApp, Telegram.

#### Datenmodell
- **Ticket** (`app/models/ticket.rb`): gehört zu `Group`, `Organization`, `State`, `Priority`, `Owner` (Agent), `Customer`.
- **Ticket::Article** (`app/models/ticket/article.rb`): Kommunikations-Thread (E-Mail, Notiz, Chat, etc.), mit `sender` + `type`, Anhänge inline, Spracherkennung.
- **Ticket::State / Ticket::StateType** (`app/models/ticket/state.rb`, `state_type.rb`): Zustände sind konfigurierbar; StateType kategorisiert in `open`, `closed`, `pending reminder`, `pending action`, `merged`, etc.
- **Ticket::Priority**: konfigurierbare Prioritäten mit Default.
- **ObjectManager**: erlaubt kundenspezifische Felder am Ticket/Benutzer.

#### Ticket-Workflow / Stati
```ruby
# StateType-Kategorien in Zammad
CATEGORIES = {
  open:       ['new', 'open', 'pending reminder', 'pending action'],
  work_on:    %w[new open],
  closed:     %w[closed],
  merged:     %w[merged],
  resolved:   %w[closed merged removed]
}
```
- **new → open → closed/merged**
- **pending reminder / pending action** mit `pending_time` und automatischem Weiterschalten (`Ticket.process_pending`).
- **Auto-Assign**: `Ticket#auto_assign` wählt Tickets per konfigurierbarer Regel einem Agenten zu.
- **Escalation**: `Ticket::Escalation` + `Escalation`-Service berechnet Fristen neu und verschickt Warnungen/Eskalationen.

#### API
- GraphQL primär (`app/graphql/gql/mutations/ticket/*`, `queries/ticket/*`).
- REST weiterhin vorhanden für Anhänge, E-Mail-Integration etc.
- Webhooks für externe Systeme.

#### Auth
- Rails-Session-basiert, OAuth/LDAP/SAML/2FA möglich.
- Rollen & Berechtigungen (`ticket.agent`, `ticket.customer`, `admin.*`).
- Benutzerklassen: Agent, Customer, Organisation.

#### Notifications
- `OnlineNotification` + `NotificationFactory` + E-Mail-Templates (`app/views/mailer/*`).
- Typen: "Assigned to you", "Escalation", "Reminder reached", "New ticket", etc.
- Echtzeit-Benachrichtigungen über WebSocket/Push.

#### SLA
- `Sla`-Modell (`app/models/sla.rb`) mit Bedingungen (`condition` JSON), Kalender, Response-Time **oder** Update-Time (nur eins erlaubt).
- Eskalationsberechnung: `first_response_escalation_at`, `update_escalation_at`, `close_escalation_at` am Ticket.

#### File-Upload / Anhänge
- `Attachment` als polymorphe Relation; Upload-Cache für Formulare.
- Anhänge werden an `Ticket::Article` geklebt; inline-Bilder per `cid:` referenziert.

#### KI-Integration
- `lib/ai/provider/open_ai.rb`, `zammad_ai.rb`, `custom_open_ai.rb`.
- Features im Code: Ticket-Zusammenfassung (`ai_assistance/summarize`), KB-Antwort-Vorschläge, Text-Übersetzung von Artikeln, KI-gestützte Knowledge-Base-Antworten.
- Kein „Agent-solved-by-AI“, sondern **Assistenz für Agenten**.

#### Multi-Tenant
- Nicht echt-Multi-Tenant; Isolation über `Organization` + `Group` + Berechtigungen.
- One-Instance-per-customer ist der Standard-SaaS-Modus.

#### DSGVO
- `DataPrivacyTask` (`app/models/data_privacy_task.rb`) für Löschung/Auskunft.
- Pseudonymisierung, Audit-Log, Einwilligung, Rollenkonzept.

---

### 2.2 Peppermint (Peppermint-Lab/peppermint)

**Meta:** 3.161 ⭐ | TypeScript / Node.js / Fastify / Prisma | PostgreSQL | NOASSERTION | 7,7 MB (depth 1)

#### Architektur
- Monorepo mit `apps/api` (Fastify), `apps/client` (Next.js/React), `apps/docs`.
- Turbo + Yarn Workspaces.
- Docker-Compose mit PostgreSQL.

#### Datenmodell (Prisma)
- `User`, `Role` (mit `permissions` JSON-Array), `Team`.
- `Ticket`: `id`, `title`, `detail`, `priority` (String), `status` (`TicketStatus` enum), `type`, `isComplete`, `assignedTo`, `client`, `team`.
- `Comment`: Text, public/reply/edited, user.
- `TicketFile`: `filename`, `path`, `mime`, `encoding`, `size`.
- `TimeTracking` direkt am Ticket.

#### Ticket-Workflow / Stati
```prisma
enum TicketStatus {
  hold
  needs_support
  in_progress
  in_review
  done
}
```
- Zusätzlich `isComplete` Boolean für einfachen Abschluss.
- Ticket-Nummer (`Number`) ist autoincrement.

#### API
- REST-Endpunkte unter `/api/v1/ticket/*`, `/api/v1/tickets/*`.
- Permission-Middleware `requirePermission(["issue::create", ...])`.

#### Auth
- JWT (`lib/jwt.ts`) + `Session`-Tabelle (`sessionToken`, expires, userAgent, ipAddress).
- Passwort-Hashing mit `bcrypt`.
- OAuth/OIDC/SAML-Provider als Konfigurationstabellen.
- Rollen: `isAdmin` + JSON-Permissions (`issue::create`, `issue::read`, etc.).

#### Notifications
- E-Mail-Versand via Nodemailer (`sendAssignedEmail`, `sendComment`, `sendTicketCreate`, `sendTicketStatus`).
- In-App-Notifications Tabelle (`notifications`) + Webhooks (Discord/Generic).
- Kein SLA, keine geplanten Escalation-Jobs.

#### SLA
- **Nicht vorhanden** in der Community-Version.

#### File-Upload
- `TicketFile` speichert `path` relativ/lokal, mime, encoding, size.

#### KI-Integration
- **Nicht vorhanden** im geklonten Code.

#### Multi-Tenant
- **Nicht echt-Multi-Tenant**; einfache Organisation/Tenant-ID taucht nur in OAuth-IMAP-Konfiguration (`tenantId`) auf.

#### DSGVO
- Nur OAuth-Consent-Felder, keine ausgereiften Privacy-Features.

---

### 2.3 osTicket (osTicket/osTicket)

**Meta:** 3.995 ⭐ | PHP 8.2–8.4 | MySQL | GPL-2.0 | 162 MB (depth 1)

#### Architektur
- Klassische PHP-App: `include/class.*.php` Domain-Modelle, `scp/` Staff-Control-Panel, `api/` REST-API.
- ORM-artig: `VerySimpleModel`, Meta-Definition pro Klasse.

#### Datenmodell
- **Ticket** (`include/class.ticket.php`): `ticket_id`, `number`, `user_id`, `status_id`, `dept_id`, `sla_id`, `staff_id`, `team_id`, `topic_id`, `source`.
- **Thread** (`include/class.thread.php`): generischer Thread für Tickets & Tasks, enthält Entries + Events + Collaborators.
- **TicketStatus**: `name`, `state`, `mode`, `flags`, `properties` (JSON).
- **TicketPriority**: `priority`, `priority_desc`, `priority_color`, `priority_urgency`.
- **SLA** (`include/class.sla.php`): `grace_period` (Stunden), `schedule_id`, Flags.

#### Ticket-Workflow / Stati
- Standard: **Open → Answered → Closed / Resolved**.
- `isoverdue`, `isanswered`, `closed`, `reopened`, `duedate`, `est_duedate`.
- Status ist konfigurierbar über Admin-Panel (`state`/`mode`).

#### API
- REST-API (`api/`) + API-Keys (`%TABLE_PREFIX%api_key`).
- Canned Responses, Ticket-Filter, Custom Forms.

#### Auth
- Sessions, lokale Benutzer + LDAP/SSO via Plugins.
- Rollen & Berechtigungen (`ticket.create`, `ticket.assign`, `ticket.close`, etc.).

#### Notifications
- E-Mail-Benachrichtigungen, Auto-Responder, Templates.
- Alerts bei SLA-Überschreitung (sofern Flag gesetzt).

#### SLA
- SLA-Plan mit **Grace Period in Stunden** und Business-Hours-Schedule.
- Flags: `FLAG_ACTIVE`, `FLAG_ESCALATE`, `FLAG_NOALERTS`, `FLAG_TRANSIENT`.
- Eskalation = Prioritätsanhebung + Benachrichtigung.

#### File-Upload
- `AttachmentFile` (`include/class.file.php`) mit `FileStorageBackend` (lokal/Plugins).
- `Attachment`-Tabelle verknüpft Files mit Objekten (inline/extern).

#### KI-Integration
- **Nicht vorhanden**.

#### Multi-Tenant
- **Nicht Multi-Tenant**; Isolation über Helpdesk-Instanz.

#### DSGVO
- Datenschutz-Feld-Flag (`isPrivacyForced()`), keine ausgereifte DSGVO-Automatisierung.

---

### 2.4 Chatwoot (chatwoot/chatwoot)

**Meta:** 38.501 ⭐ | Ruby on Rails | PostgreSQL + Redis | MIT | 308 MB (depth 1)

#### Architektur
- Monolithische Rails-App mit separatem `enterprise/` Ordner für Premium-Features.
- Vue.js-Frontend im Dashboard.
- Redis für Pub/Sub, Sidekiq-Jobs, Caching.

#### Datenmodell
- **Conversation** (`app/models/conversation.rb`) ist das zentrale „Ticket“.
- **Account** = Tenant (Multi-Tenant via `account_id`).
- **Message** gehört zu Conversation; Attachments über `active_storage`.
- **Contact** statt „Customer“.

#### Ticket-Workflow / Stati
```ruby
enum status: { open: 0, resolved: 1, pending: 2, snoozed: 3 }
enum priority: { low: 0, medium: 1, high: 2, urgent: 3 }
```
- **open → pending → resolved** oder Snooze.
- Auto-Resolve nach Inaktivität (`auto_resolve_after`).
- Toggle-Status-Methoden einfach gehalten (kein State-Machine-Gem).

#### API
- REST-API (`app/controllers/api/v1/accounts/conversations_controller.rb`), Swagger/OpenAPI.
- Webhooks, Dashboard Apps, Shopify/Slack/Linear-Integrationen.

#### Auth
- Account-basierte Authentifizierung, OAuth, SSO (SAML im Enterprise-Ordner).
- MFA (`enforce_mfa` Setting).

#### Notifications
- `Notification`-Modell mit `notification_type` Enum:
  - `conversation_creation`, `conversation_assignment`, `assigned_conversation_new_message`, `conversation_mention`, `sla_missed_first_response`, `sla_missed_next_response`, `sla_missed_resolution`.
- Push + E-Mail, abonnierbar pro Typ (`notification_settings`).

#### SLA
- **Enterprise-Feature** (`enterprise/app/models/sla_policy.rb`).
- `SlaPolicy`: `first_response_time_threshold`, `next_response_time_threshold`, `resolution_time_threshold`, `only_during_business_hours`.
- `AppliedSla` / `SlaEvent` tracken Einhaltung/Misserfolg.

#### File-Upload
- Rails `active_storage` für Attachments.

#### KI-Integration
- **Captain AI** (`lib/captain/*`):
  - `ReplySuggestionService` — Vorschläge für Agenten-Antworten.
  - `SummaryService` — Zusammenfassung einer Conversation.
  - `FollowUpService`, `CsatUtilityAnalysisService`, etc.
- LLM-Integration über `RubyLLM`, konfigurierbarer Endpunkt/API-Key.

#### Multi-Tenant
- **Echte Multi-Tenant-Isolation** über `account_id` in nahezu allen Tabellen.
- SaaS-fähige Architektur.

#### DSGVO
- `PRIVACY_URL` Config, Löschung/Export über Account, Audit-Trail via `audits` Tabelle.
- DS-GVO-relevant: Echte Tenant-Isolation hilft bei Datenhoheit pro Account.

---

### 2.5 Frappe Helpdesk (frappe/helpdesk)

**Meta:** 3.451 ⭐ | Python (Frappe Framework) + Vue (Frappe UI) | MariaDB/PostgreSQL | AGPL-3.0 | 50 MB (depth 1)

#### Architektur
- Basiert auf **Frappe Framework** (full-stack Python/JS Framework).
- DocType-basiertes Datenmodell: `HD Ticket`, `HD Ticket Status`, `HD Ticket Priority`, `HD Service Level Agreement`.
- Vue3-Frontend (`desk/src`).

#### Datenmodell
- **HD Ticket** (`helpdesk/helpdesk/doctype/hd_ticket/hd_ticket.py/.json`):
  - Felder: `subject`, `raised_by`, `status`, `priority`, `ticket_type`, `agent_group`, `description`, `sla`, `response_by`, `resolution_by`, `agreement_status`, `feedback_rating`, `_assign`.
- **HD Ticket Status** (`hd_ticket_status.json`): `label_agent`, `label_customer`, `category` (`Open | Paused | Resolved`), `color`, `order`.
- **HD Ticket Priority**: `Urgent | High | Medium | Low`.
- **HD Service Level Agreement**: Prioritäten-Tabellen, Response-/Resolution-Zeiten, Bedingungen, Workdays/Holidays.

#### Ticket-Workflow / Stati
- Status-Kategorien treiben SLA-Uhr:
  - **Open** → SLA läuft weiter.
  - **Paused** → SLA pausiert (z. B. warten auf Kunde).
  - **Resolved** → SLA stoppt.
- Standard: **Open → Replied → Awaiting Response → Resolved → Closed**.
- Kundensicht kann anderes Label haben (`different_view`).

#### API
- Frappe-REST-API + eigene Whitelisted-Methoden (`@frappe.whitelist()`).
- Eigene API-Dateien (`helpdesk/helpdesk/doctype/hd_ticket/api.py`, `helpdesk/api/auth.py`).

#### Auth
- Nutzt Frappe-User & Rollen (`System Manager`, `Agent Manager`, `Agent`, `HD Customer`).
- `@agent_only` Decorator, `is_customer_manager`, `has_desk_access`.

#### Notifications
- E-Mail-Versand über Frappe `sendmail`.
- Acknowledgement-E-Mail, Feedback-E-Mail bei Statusänderung.
- In-App-Notifications über Frappe Notification Log.

#### SLA
- Sehr ausgereift: `HDServiceLevelAgreement.apply(doc)`:
  - Setzt Default-Priority.
  - Startet/Stoppt die Uhr je `status_category`.
  - Berechnet `response_by`, `resolution_by`, `first_response_time`, `resolution_failed_by`.
  - Verwaltet Feiertage/Workdays.

#### File-Upload
- Frappe-Dateisystem (`/files/`), Attachments an Communication/Ticket.
- Inline-Media-Erkennung und E-Mail-Einbettung.

#### KI-Integration
- **Nicht direkt im Core** vorhanden; Knowledge-Base / LLM-Copy kommt in `studio/helpdesk/components/knowledge_base/PortalCopyForLLM.vue`.
- Frappe-Ökosystem bietet aber LLM-Apps als Erweiterung.

#### Multi-Tenant
- Frappe nativ Multi-Tenant-fähig (eine Site = ein Tenant).
- Im selben Code über Sites isolierbar.

#### DSGVO
- Frappe liefert Audit-Trail, Datenexport, Löschung.
- Ticket-Key ermöglicht anonymisierten Kundenportal-Zugriff.

---

## 3. „Secrets“ — Best Practices, die alle guten Ticket-Systeme gemeinsam haben

### 3.1 Status-Modell
- **Nicht einfach nur „offen/geschlossen“**: reife Systeme unterscheiden `new/open/in_progress/pending/reminder/resolved/closed/merged`.
- **Status-Kategorie** (Zammad `StateType`, Frappe `category`): definiert, ob SLA läuft, pausiert oder stoppt.
- **Unterschiedliche Sichten**: Agent sieht internen Status, Kunde sieht ggf. anderes Label (Frappe `label_customer`).
- **Automatische Status-Transitionen**: pending reminder nach Ablauf der Zeit → zurück zu open; Auto-Resolve nach Inaktivität.

### 3.2 Zuweisung
- **Besitzer/Agent** auf Ticket-Ebene, optional **Team**.
- **Auto-Assignment** anhand von Gruppe/Team/Workload/Regeln.
- **Claiming**: Agent übernimmt aktiv; Vermeidung von Doppelbearbeitung.
- **Rollenbasiert**: Kunde sieht nur eigene Tickets, Agent sieht zugewiesene/Gruppen-Tickets, Admin alles.

### 3.3 Kommentare / Verlauf
- **Thread/Article/Communication-Modell** separat vom Ticket.
- **Interne vs. öffentliche Kommentare** (Zammad: note vs. email; osTicket: internal note vs. message; Frappe: `_comment` vs. communication).
- **Edit-History** mit `previous` (Peppermint), `editedAt`.
- **Ereignis-Log**: Statusänderungen, Zuweisungen, SLA-Änderungen, Anhänge.

### 3.4 Prioritäten
- Standard: **Low / Normal / Medium / High / Urgent**.
- Priorität beeinflusst SLA-Zeiten (Frappe SLA hat Response-/Resolution-Zeiten pro Priorität).
- Farbige Badges/Kennzeichnung.

### 3.5 Auto-Kategorisierung / Triage
- **E-Mail-Filter / Regeln**: Zuweisung nach Absender, Betreff, Schlüsselwort, Help-Topic.
- **KI-Triage** (Chatwoot Captain, Zammad AI): Vorschläge für Kategorie, Priorität, Antwort, KB-Artikel.
- **Keyword-basierte Kategorisierung** vor KI (günstiger, deterministisch).

### 3.6 SLA & Escalation
- **Zwei Ziele**: First Response Time & Resolution Time.
- **Business Hours / Kalender**: nur innerhalb der Arbeitszeiten zählen.
- **Paused-Status**: Wenn auf Kunden gewartet wird, stoppt die Uhr.
- **Eskalation**: Benachrichtigung an Manager/Admin + ggf. Prioritätsanhebung.
- **Bedingte SLAs**: unterschiedliche SLAs je Kategorie/Priorität/Kunde (Zammad `condition`, Frappe `condition_json`).

### 3.7 Notifications
- **Push-First**: WebSocket/In-App, dann E-Mail.
- **Event-Typen**: neues Ticket, Zuweisung, Statusänderung, neuer Kommentar, SLA-Eskalation, Erinnerung.
- **Opt-out/Settings**: Benutzer kann pro Kanal und Event-Typ abonnieren.
- **Templates**: mehrsprachige E-Mail-Templates mit Variablen.

### 3.8 File-Upload
- **Polymorphe Attachments** an Ticket/Comment/Communication.
- **Inline vs. Attachment** unterscheiden (E-Mail-Einbettung).
- **Metadata**: mime, size, hash, storage backend.

### 3.9 Auth & Berechtigungen
- **Rollen-basiert + Berechtigungen pro Aktion** (`ticket.create`, `issue::read`, etc.).
- **Datenisolation** bei SaaS: `account_id` / `tenant_id` / `vermieter_id` in jeder Abfrage.
- **2FA**, Session-Management, Audit-Log.

### 3.10 KI-Integration
- **Assistenz, keine autonome Entscheidung** (DSGVO-konform): Vorschläge, Zusammenfassung, Antwort-Entwurf, KB-Suche.
- **Anonymisierung/Pseudonymisierung** vor externem LLM-Aufruf.
- **Keyword-Classifier** als Gate vor teurem KI-Aufruf.

---

## 4. Empfehlung für MietVerwaltung

### 4.1 Architektur-Patterns übernehmen
| Bereich | Empfohlener Ansatz | Inspiriert von |
|---|---|---|
| **Backend** | Python + FastAPI + PostgreSQL (bestätigter Stack) | Frappe Helpdesk (Python), Peppermint (Fastify/Prisma) |
| **Frontend** | Vue.js 3 + Tailwind (bestätigt) | Chatwoot, Frappe Helpdesk |
| **Datenmodell** | `tickets`, `ticket_kommentare`, `ticket_status_history`, `sla_policies` | Zammad, Frappe, osTicket |
| **Tenant-Isolation** | `vermieter_id` / `mieter_id` in jeder Tabelle + RLS | Chatwoot `account_id`, MietVerwaltung v2 Schema |
| **Notifications** | In-App + E-Mail + Event-Queue | Zammad, Chatwoot |
| **File-Upload** | Polymorphe Attachments, lokaler Storage/S3-Plugin | Zammad, Chatwoot ActiveStorage |
| **KI** | Keyword-Classifier → Ollama Cloud (anonymisiert) → Entwurf lokal anreichern | Zammad AI, Chatwoot Captain, MietVerwaltung KI-Konzept |

### 4.2 Vorgeschlagener Ticket-Workflow für MietVerwaltung

#### Stati
| Status (intern) | Kategorie | Kundensicht | Bedeutung |
|---|---|---|---|
| `offen` | Open | „Offen“ | Neu erstellt, noch nicht bearbeitet |
| `in_bearbeitung` | Open | „In Bearbeitung“ | Vermieter/Handwerker arbeitet daran |
| `wartend_auf_mieter` | Paused | „Warte auf Rückmeldung“ | Antwort/Klärung durch Mieter nötig |
| `wartend_auf_handwerker` | Paused | „Handwerker beauftragt“ | Externer Handwerker wurde eingeschaltet |
| `erledigt` | Resolved | „Erledigt“ | Problem gelöst, noch nicht geschlossen |
| `geschlossen` | Resolved | „Geschlossen“ | Ticket endgültig abgeschlossen |
| `abgelehnt` | Resolved | „Abgelehnt“ | Kein berechtigter Mangel / nicht zuständig |

> **Prinzip**: Mindestens zwei Sichten (Agent vs. Mieter) und SLA-pausierende Status einführen.

#### Prioritäten
- `dringend` (z. B. Wasserschaden, Heizungsausfall im Winter)
- `normal` (Standard-Mängel)
- `niedrig` (Kosmetik, Wünsche)

#### Zuweisung
- **Default**: Ticket wird dem Vermieter zugewiesen.
- **Handwerker-Workflow**: Vermieter kann Ticket an Handwerker-User weiterleiten (read-only Zugriff auf Ticket + Adresse + Mieter-Kontakt + freigegebene Dokumente).
- **Auto-Kategorisierung**: Keywords („Heizung“, „Wasser“, „Schimmel“, „Schlüssel“) → Ticket-Typ + Priorität.

### 4.3 SLA-Empfehlung
- **First Response Time**:
  - Dringend: 2 Stunden (während Geschäftszeiten)
  - Normal: 24 Stunden
  - Niedrig: 72 Stunden
- **Resolution Time**:
  - Dringend: 24–48 Stunden
  - Normal: 7 Tage
  - Niedrig: 14 Tage
- **Business Hours**: Montag–Freitag 08:00–18:00, Sa 08:00–12:00 (DACH-typisch); Feiertage berücksichtigen.
- **Paused-Status**: `wartend_auf_mieter` und `wartend_auf_handwerker` stoppen die SLA-Uhr.
- **Escalation**: Bei 80% der Frist Erinnerung, bei 100% Eskalation an Vermieter + Dashboard-Badge.

### 4.4 KI-Hilfe
| Use-Case | Umsetzung |
|---|---|
| **Auto-Kategorie** | Keyword-Classifier (60–70% Treffer) + KI-Fallback |
| **Auto-Priorität** | Regelbasierter Scoring + KI-Plausibilisierung |
| **Antwort-Entwurf Vermieter** | KI liest Ticket + Kommentare, schlägt höfliche Antwort vor |
| **Lösungsvorschlag Mieter** | KI schlägt erste Hilfe/Checkliste vor (kein Ersatz für Bearbeitung) |
| **Zusammenfassung** | Bei langen Tickets für Vermieter |
| **Handwerker-Info** | KI erzeugt automatisch Kurzinfo (Adresse, Kontakt, Problem) für Weiterleitung |

> **Wichtig**: Kein automatisierter Score, der die Vermieter-Entscheidung ersetzt (DSGVO Art. 22). Mensch entscheidet, KI assistiert.

### 4.5 Handwerker-Workflow
1. Vermieter öffnet Ticket, klickt „Handwerker beauftragen“.
2. Auswahl aus Handwerker-Verzeichnis (später) oder E-Mail-Einladung.
3. Handwerker bekommt eigenen Login/Rolle mit Rechten:
   - Zugewiesene Tickets lesen/kommentieren.
   - Status auf `erledigt` setzen.
   - Rechnungen/Fotos/Stundenzettel hochladen.
   - Objekt-Adresse + Mieter Name/Telefon sehen.
4. Vermieter bestätigt Erledigung → Status `geschlossen`.
5. Rechnung kann an Kosten/Nebenkosten gekoppelt werden (Phase 7).

### 4.6 DSGVO-konforme Umsetzung
- **Anonymisierung vor KI**: Presidio (NER-basiert) für Namen, Adressen, IBANs etc.
- **Audit-Log**: jede Statusänderung, Zuweisung, KI-Nutzung protokollieren.
- **Löschfristen**: Tickets mit personenbezogenen Daten nach Mietvertragsende + Aufbewahrungsfrist löschen.
- **Einwilligung**: Bei Registrierung versionierte Checkbox.
- **Recht auf Auskunft/Löschung**: Endpunkt für Datenexport + Löschung.

### 4.7 Empfohlene Datenbank-Struktur (Erweiterung v2 Schema)

```sql
-- Tickets
CREATE TABLE tickets (
  id SERIAL PRIMARY KEY,
  vermieter_id INT NOT NULL,
  mieter_id INT NOT NULL,
  einheit_id INT NOT NULL,
  ticket_nr VARCHAR(32) UNIQUE NOT NULL, -- z.B. TKT-2026-001
  betreff VARCHAR(255) NOT NULL,
  beschreibung TEXT,
  status VARCHAR(32) NOT NULL DEFAULT 'offen',
  status_kategorie VARCHAR(16) NOT NULL DEFAULT 'Open', -- Open|Paused|Resolved
  prioritaet VARCHAR(16) NOT NULL DEFAULT 'normal',
  kategorie VARCHAR(32), -- heizung|wasser|elektrik|schimmel|sonstiges
  zugewiesen_an INT, -- user_id (Vermieter/Handwerker)
  zugewiesen_rolle VARCHAR(16),
  sla_policy_id INT,
  response_by TIMESTAMP,
  resolution_by TIMESTAMP,
  first_responded_at TIMESTAMP,
  resolved_at TIMESTAMP,
  closed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_at TIMESTAMP
);

-- Kommentare / Verlauf
CREATE TABLE ticket_kommentare (
  id SERIAL PRIMARY KEY,
  ticket_id INT NOT NULL REFERENCES tickets(id),
  user_id INT NOT NULL,
  text TEXT NOT NULL,
  public BOOLEAN DEFAULT TRUE, -- intern vs. sichtbar für Mieter
  edited BOOLEAN DEFAULT FALSE,
  previous TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- SLA-Policies
CREATE TABLE sla_policies (
  id SERIAL PRIMARY KEY,
  vermieter_id INT NOT NULL,
  name VARCHAR(128) NOT NULL,
  prioritaet VARCHAR(16) NOT NULL,
  response_time_minutes INT,
  resolution_time_minutes INT,
  arbeitszeiten JSONB,
  default_sla BOOLEAN DEFAULT FALSE
);

-- Attachments (polymorph)
CREATE TABLE ticket_anhaenge (
  id SERIAL PRIMARY KEY,
  ticket_id INT REFERENCES tickets(id),
  kommentar_id INT REFERENCES ticket_kommentare(id),
  dateiname VARCHAR(255),
  mime VARCHAR(128),
  size_bytes INT,
  file_hash VARCHAR(64),
  storage_path VARCHAR(512),
  sichtbarkeit VARCHAR(16) DEFAULT 'beide',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Status-History / Audit
CREATE TABLE ticket_status_history (
  id SERIAL PRIMARY KEY,
  ticket_id INT NOT NULL,
  status_alt VARCHAR(32),
  status_neu VARCHAR(32),
  geaendert_von INT NOT NULL,
  grund TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 4.8 UI/UX-Empfehlung
- **Dashboard-Zeile**: Offene Tickets pro Objekt, SLA-Risiko farbig, 1-Klick-Zuweisung.
- **Ticket-Liste**: Filter nach Status, Priorität, Objekt, Mieter, zugewiesen.
- **Ticket-Detail**: Timeline-View (neueste unten/oben konfigurierbar), intern/öffentlich umschaltbar.
- **Mieter-Portal**: 3 Tabs (Start, Tickets, Dokumente); Ticket erstellen mit Kategorie + Foto.
- **Mobile First**: Foto-Upload direkt aus Ticket heraus; Push-Benachrichtigungen später.

---

## 5. Fazit

- **Zammad** bleibt die wichtigste Referenz für Workflow, SLA, Notifications und KI-Assistenz.
- **Frappe Helpdesk** ist architektonisch dem MietVerwaltung-Stack am nächsten (Python + Vue) und bietet ein sehr gutes SLA/Status-Modell.
- **Chatwoot** liefert die beste Multi-Tenant-/SaaS-Isolation und den modernsten AI-Agent-Ansatz (Captain).
- **Peppermint** zeigt eine schlanke Fastify/Prisma-Implementierung, ist aber noch unreif (kein SLA, keine KI).
- **osTicket** ist robust, aber veraltet im Code-Stil; dennoch gute klassische Workflow-Patterns.

**Empfohlene Pattern-Kombination für MietVerwaltung:**
1. Ticket-Stati nach Zammad/Frappe mit Open/Paused/Resolved-Kategorien.
2. SLA nach Frappe (Response-/Resolution-Zeit pro Priorität + Business Hours).
3. Multi-Tenant nach Chatwoot (`vermieter_id` / `mieter_id` + RLS).
4. Notifications nach Zammad/Chatwoot (Event-Typen + Push + E-Mail).
5. KI-Assistenz nach Zammad/Chatwoot (Zusammenfassung, Entwurf, Kategorie) mit Presidio-Anonymisierung.
6. Handwerker-Workflow als eigenständige Rolle mit dokumenten-basierter Freigabe.

---

## Anhang: Geklonte Repos

| Repo | Ordner | Größe (depth 1) |
|---|---|---|
| Zammad | `/root/mietverwaltung/repos/ticket-systems/zammad` | ~220 MB |
| Peppermint | `/root/mietverwaltung/repos/ticket-systems/peppermint` | ~7,7 MB |
| osTicket | `/root/mietverwaltung/repos/ticket-systems/osticket` | ~162 MB |
| Chatwoot | `/root/mietverwaltung/repos/ticket-systems/chatwoot` | ~308 MB |
| Frappe Helpdesk | `/root/mietverwaltung/repos/ticket-systems/frappe-helpdesk` | ~50 MB |

Gesamter Speicherbedarf: ca. **750 MB** — innerhalb der 4 GB-Vorgabe dank `--depth 1`.
