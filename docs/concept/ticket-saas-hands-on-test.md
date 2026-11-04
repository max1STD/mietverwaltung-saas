# Ticket/Helpdesk SaaS Hands-on Testbericht
## Für MietVerwaltung – Benchmark & Empfehlung

**Datum:** 2026-10-28  
**Tester:** Hermes Agent  
**Ziel:** Die besten kommerziellen Ticket/Helpdesk-SaaS-Lösungen praxisnah testen, vergleichen und ableiten, welche Features für das MietVerwaltung-Ticket-System übernommen werden sollten.

---

## 1. Marktübersicht: Kommerzielle Ticket/Helpdesk-SaaS

### 1.1 Untersuchte Lösungen
| Lösung | Typ | Free/Trial | Preis (ab) | Hosting | Besonderheit |
|---|---|---|---|---|---|
| **Zammad** | Open-Source + Cloud | 30-Tage-Trial (alle Features), danach ab 7 €/Agent | Cloud ab 7 €/Agent, Self-hosted kostenlos | Deutschland / EU | Unser Haupt-Benchmark: DSGVO, EU AI Act, Open-Source |
| **Freshdesk** | Kommerziell | 14-Tage-Trial, danach Free-Programm (2 Agents, 6 Monate) | Free / Growth 15 $/Agent | Freshworks (US/Indien) | Sehr ausgereifter Workflow-Automator |
| **Help Scout** | Kommerziell | 15-Tage-Trial + Free-Plan (5 User, 1 Inbox, 100 Kontakte/Monat) | Standard 25 $/User | Help Scout | Shared-Inbox-Philosophie, sehr clean |
| **Crisp** | Kommerziell | 14-Tage-Trial + Free-Forever (2 Seats) | Mini 45 $/Workspace | Crisp | Chat-first, moderne UI |
| **osTicket** | Open-Source + Cloud | 30-Tage Cloud-Trial, Self-hosted kostenlos | Cloud ab 12 $/Agent | US (Enhancesoft) | Klassisches PHP-Ticketing, robust |
| **Zendesk** | Kommerziell | 14-Tage-Trial, 6 Monate für Startups | ab 19 $/Agent | Zendesk (US) | Marktführer, AI-Agents + Copilot |
| **Intercom** | Kommerziell | 14-Tage-Trial | Starter 74 $/Monat (2 Seats) | Intercom | AI-first Helpdesk (Fin) |
| **FreeScout** | Open-Source | Self-hosted kostenlos, Module ca. 2–20 $ einmalig | Nur Self-hosting | Eigener Server | Leichtgewichtig, modular |

### 1.2 Marktführer & Positionierung
- **Zendesk** ist der globale Marktführer im Enterprise- und Midmarket-Bereich. Stärken: Omnichannel, 1.500+ Integrationen, AI-Agents (Fin/Copilot), Skalierbarkeit.
- **Freshdesk** ist der bekannteste Zendesk-Konkurrent im Mittelstand, sehr preiswert im Einstieg.
- **Zammad** ist in DACH sehr stark, weil Open-Source, DSGVO-konform, in Deutschland gehostet und EU AI Act-konform.
- **Help Scout** ist beliebt bei SaaS- und B2B-Teams wegen der minimalistischen Shared-Inbox-UX.
- **Intercom** setzt konsequent auf AI (Fin AI Agent) und Chat-first.

---

## 2. Hands-on Test der einzelnen Lösungen

### 2.1 Zammad (Haupt-Benchmark)
**Getestete Instanz:** `mietverwaltung-test-de.zammad.com`  
**Account:** `hermes.test.zammad.8029@yopmail.com` / MietVerwaltung Test  
**Plan:** 30-Tage-Trial auf Professional v2, AI aktiviert (500 free calls)

#### Onboarding-Flow
1. Landingpage `zammad.com/de/loslegen`
2. Formular: Name, E-Mail, Passwort, Organisation, Alias (Subdomain)
3. AGB-Haken setzen
4. Instanz wird im Hintergrund aufgebaut (~1–2 Minuten)
5. Auto-Wizard-Login direkt ins Dashboard

**Onboarding-Note:** 9/10 – schnell, deutsches Interface, keine Kreditkarte, sofort produktiv.

#### Dashboard
- Linke Sidebar: Dashboard, Overviews, First-Steps-Checkliste
- Widgets: Wartezeit heute, Eskalationen, Kanalverteilung, zugewiesene Tickets, Bearbeitungsrate, Wiederöffnungsrate
- Activity Stream (noch leer beim Start)
- „My Stats“ für Agenten-Performance

**Dashboard-Note:** 8/10 – übersichtlich, aber etwas technisch/klassisch.

#### Ticket erstellen
- Pfad: Inbox-Overviews → „Unassigned & Open Tickets“ oder direkt `#ticket/create/email`
- Beispielticket und Test-Ticket-Funktion in der First-Steps-Checkliste vorhanden
- Felder im Ticket-Detail: Titel, Kunde, Gruppe, Besitzer, Status, Priorität, Tags, verknüpfte Tickets
- Status-Werte: new, open, pending reminder, pending close, closed
- Prioritäten: 1 low, 2 normal, 3 high

**Klicks Ticket erstellen:** ~3–4 Klicks bis zur Ticket-Maske (je nach Weg).  
**Ticket-Erstellung-Note:** 8/10 – klar, aber neuen Kunden-Ticket-Dialog nicht sofort offensichtlich.

#### Ticket-Verlauf & Kollaboration
- Chronologischer Verlauf aller Artikel (Kunden-Nachrichten, Agent-Antworten, interne Notizen, System-Logs)
- Aktionen pro Artikel: reply, forward, split, internal note, set to internal
- Sidebar rechts: Ticket-Attribute, Historie, Merge, Kunde wechseln
- Update-Button finalisiert Änderungen

**Verlauf-Note:** 9/10 – sehr nachvollziehbar, vollständige Historie.

#### Zuweisung an Agenten
- Dropdown OWNER im Ticket-Detail
- Gruppe (Group) bestimmt, wer das Ticket sieht
- Agenten-Rollen: Admin, Agent, Customer
- Automatische Zuweisung möglich über Trigger / AI Agents

**Zuweisung-Note:** 8/10 – einfach, aber UI etwas kompakt.

#### Automatisierungen (getestet in Admin → Manage)
- **Trigger (Echtzeit-Regeln):** 3 Beispiel-Trigger vorhanden: auto reply new tickets, auto reply follow-up, customer notification on owner change
- **Scheduler (zeitgesteuert):** leer, aber voll konfigurierbar
- **Macros:** Beispiel „Close & Tag as Spam“
- **Text Modules:** vorgefertigte Antwortbausteine (`ai`, `br`, `cnr`, `dmr`, …)
- **SLAs:** SLA Management mit Response Time / Update Time / Solution Time
- **Overviews:** benutzerdefinierte Listen (My Assigned, Unassigned & Open, Escalated)
- **Webhook-Integration** verfügbar

**Automatisierungen-Note:** 9/10 – sehr mächtig, aber Regelsprache braucht Einarbeitung.

#### KI-Features (Zammad 7.0, im Trial aktiviert)
Getestete Konfigurationsseiten:
- **Admin → AI → Ticket Summary**
  - Services: Customer Intent, Conversation Summary, Open Questions, Upcoming Events, Customer Sentiment
  - Summary Selector per Bedingungen
  - Generation: On ticket detail opening oder On sidebar activation
- **Admin → AI → Writing Assistant**
  - Vordefinierte Werkzeuge: Expand draft, Fix spelling/grammar, Rewrite complex, Summarize to half, Translate to English
  - Eigene Tools können angelegt werden
- **Admin → AI → AI Agents**
  - Agent-Typen: Ticket Categorizer, Ticket Group Dispatcher, Ticket Prioritizer, Ticket Tagger, Ticket Text Extractor, Ticket Title Rewriter
  - Ausführung über Trigger oder Scheduler
- **Admin → AI → AI Providers**
  - Unterstützt: Zammad AI, OpenAI, Ollama, Anthropic, Azure AI, Mistral AI, Custom OpenAI-compatible

**Praxis-Beobachtung:** Die KI-Features sind aktiv (Banner „AI Enabled successfully“), im Trial sind 500 Calls inklusive. Im reinen Text-Modus des Browsers konnten die Sidebar-Buttons für Summary/Writing Assistant nicht sichtbar gemacht werden (vermutlich Icon-Buttons in einer Rich-UI). Die Konfigurationsmöglichkeiten sind aber dokumentiert und sehr umfangreich.

**KI-Features-Note:** 9/10 – transparent, wählbarer Provider, EU-konform.

#### Notifications
- E-Mail-Benachrichtigungen für: New Ticket, Ticket update, Ticket reminder reached, Ticket escalation
- Gruppenbasierte Limits möglich
- In-App-Sounds wählbar
- Keine Push im Browser gefunden, aber mobile Web-App / PWA über Browser möglich

#### File-Upload
- Ticket-Editor: „select attachment“
- Max. Dateigröße lt. Plan: 10 MB Attachments + 20 GB Disk Space im Starter

#### Mobile-App
- Keine native App getestet; Zammad hat responsive Web-UI und Progressive-Web-App-Fähigkeit.

#### Stärken & Schwächen Zammad
| Gut | Stört |
|---|---|
| DSGVO / EU Hosting / EU AI Act | UI teils etwas „technisch“ |
| Open-Source, kein Vendor Lock-in | Mobile Experience nicht herausragend |
| Extrem mächtige Automatisierung | Einarbeitungszeit für Trigger/Scheduler |
| Wählbare KI-Provider (Ollama lokal) | AI-Buttons in Rich-Editor nicht sofort auffindbar |
| Sehr gute Wiederverwendung (Text Modules, Macros) | Onboarding-Wizard manchmal langsam |

**Gesamtnote Zammad:** 9/10

---

### 2.2 Freshdesk
**Status:** Registrierung blockiert durch Cloudflare-Bot-Schutz (`www.freshworks.com/freshdesk/signup/` zeigt „Performing security verification“).  
**Analyse basiert auf:** Offizielle Dokumentation, Pricing-Seiten, Vergleichstabellen.

#### Erkennbare Features
- 14-Tage-Trial mit vollem Funktionsumfang
- Free-Programm: 2 Agents, 6 Monate
- Kanäle: E-Mail, Social (Twitter/Facebook), Portal, Chat (Freshchat), Telefonie
- Automatisierung: Workflow Automator (ab Growth)
- SLA-Management (ab Pro)
- KI: Freddy AI (ab Pro/Enterprise) – Auto-Kategorisierung, Vorschläge
- Mobile Apps iOS/Android
- 1.500+ Marketplace-Apps

#### Stärken & Schwächen Freshdesk
| Gut | Stört |
|---|---|
| Sehr reifer Funktionsumfang | Free-Tier stark limitiert (keine Automatisierung) |
| Große Integrationen | Cloudflare-Bot-Schutz erschwert schnelles Testen |
| Gute Skalierbarkeit | Benötigt ab Growth, um wirklich mächtig zu sein |

**Gesamtnote Freshdesk (basierend auf Recherche):** 8/10

---

### 2.3 Help Scout
**Status:** Registrierung blockiert, weil YOPmail als Weiterleitungsdienst nicht akzeptiert wird („Forwarding services are not allowed. Please enter a valid email address.“).  
**Analyse basiert auf:** Offizielle Dokumentation, Free-Plan-Beschreibung.

#### Erkennbare Features
- Free-Plan: 5 User, 1 Inbox, 1 Docs-Site, 10 Tags, 10 Saved Replies, 100 Kontakte/Monat
- Shared Inbox (E-Mail + Instagram/Messenger)
- Docs Knowledge Base
- Beacon Help Widget (Chat + Kontaktformular)
- AI: AI Answers (3 Monate Free-Trial), AI Drafts, AI Summarize, AI Assist
- Automatisierung: Inbox Auto Reply
- Reporting: 30 Tage Volume/Responses/Happiness

#### Stärken & Schwächen Help Scout
| Gut | Stört |
|---|---|
| Sehr saubere, human-first UX | Keine echte Trial ohne echte E-Mail |
| Shared Inbox sehr intuitiv | Free-Plan limitiert auf 100 Kontakte/Monat |
| Beacon-Widget schön integriert | Weniger mächtige Automatisierung als Zammad |

**Gesamtnote Help Scout (basierend auf Recherche):** 7,5/10

---

### 2.4 Crisp
**Status:** Registrierung nicht erfolgreich abgeschlossen – Formular akzeptierte Eingaben, aber „Continue“ löste keinen Seitenwechsel aus (möglicherweise reCAPTCHA/hCaptcha oder Button-Handler blockiert).  
**Analyse basiert auf:** Registrierungsseite + offizielle Informationen.

#### Erkennbare Features
- Free-Forever: 2 Seats, Chat-Widget, Mobile Apps, Push Notifications, 100 Kundenprofile, **keine AI-Credits**
- Bezahlte Pläne: Mini 45 $, Essentials 95 $, Plus 295 $/Workspace
- Ticketing-System erst ab Plus
- Hugo AI Agent (trainierbar auf Website, PDFs, Q&A)
- Kanäle: E-Mail, Chat, WhatsApp, Messenger, Instagram, SMS, Voice
- Workflows/Automatisierung ab Essentials
- Knowledge Base

#### Stärken & Schwächen Crisp
| Gut | Stört |
|---|---|
| Moderne, schnelle UI | Ticketing erst im teuren Plus-Plan |
| Gute Chat-Erfahrung | Kostenlose Variante sehr eingeschränkt |
| Hugo AI trainierbar | Registrierung im Test nicht durchführbar |

**Gesamtnote Crisp (basierend auf Recherche):** 7/10

---

### 2.5 osTicket
**Status:** Cloud-Trial-Registrierung nicht erfolgreich – Formularfelder ausgefüllt, aber „Get Started Now“ löste keine Bestätigung/Weiterleitung aus (möglicherweise reCAPTCHA, manuelle Verarbeitung, E-Mail-Bestätigung erforderlich).  
**Analyse basiert auf:** Offizielle Features-Seite, Docs, Vergleiche.

#### Erkennbare Features
- Kostenlos Self-hosted, Cloud ab 12 $/Agent
- Ticket Filter (Routing, Auto-Assign, Auto-Response, SLA)
- Help Topics & Custom Forms
- SLA Plans (Overdue Alerts, Priority Escalation)
- Assign / Transfer / Referral
- E-Mail-to-Ticket (POP3/IMAP/Piping)
- Canned Responses
- Knowledge Base
- Keine eigenen KI-Features (lt. Hersteller)

#### Stärken & Schwächen osTicket
| Gut | Stört |
|---|---|
| Lange bewährt, stabil | UI veraltet |
| Self-hosted kostenlos | Cloud-Trial im Test nicht zugänglich |
| Gute SLA-/Filter-Automatisierung | Keine KI out-of-the-box |

**Gesamtnote osTicket (basierend auf Recherche):** 6,5/10

---

## 3. Vergleichstabelle: Features im Überblick

| Feature | Zammad | Freshdesk | Help Scout | Crisp | osTicket |
|---|---|---|---|---|---|
| Free-/Trial-Zugang | ✅ 30 Tage Trial | ⚠️ Cloudflare-Block | ⚠️ Nur echte E-Mail | ⚠️ Registrierung blockiert | ⚠️ Registrierung blockiert |
| E-Mail-Ticketing | ✅ | ✅ | ✅ | ✅ (Plus) | ✅ |
| Web-Formular | ✅ | ✅ | ✅ (Beacon) | ✅ | ✅ |
| Chat | ✅ | ✅ (Freshchat) | ✅ (Beacon) | ✅ | ❌ |
| Kanal-Einheit | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| SLA | ✅ | ✅ (ab Pro) | ✅ (ab Plus) | ⚠️ | ✅ |
| Trigger/Echtzeit | ✅ | ✅ (ab Growth) | ⚠️ Auto-Reply | ✅ (ab Essentials) | ✅ |
| Zeitgesteuert (Scheduler) | ✅ | ✅ | ⚠️ | ✅ | ⚠️ |
| Textbausteine/Macros | ✅ | ✅ | ✅ (Saved Replies) | ✅ | ✅ (Canned) |
| Auto-Assign | ✅ | ✅ | ✅ | ✅ | ✅ |
| Tags | ✅ | ✅ | ✅ (10 Free) | ✅ | ✅ |
| KI-Zusammenfassung | ✅ | ✅ (Freddy) | ✅ (AI Summarize) | ✅ (Hugo) | ❌ |
| KI-Schreibassistent | ✅ | ✅ | ✅ (AI Drafts/Assist) | ✅ | ❌ |
| KI-Agenten (Routing etc.) | ✅ | ✅ | ✅ (AI Answers) | ✅ | ❌ |
| Wählbarer KI-Provider | ✅ | ❌ | ❌ | ❌ | ❌ |
| EU Hosting / DSGVO | ✅ | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| Mobile App | Web/PWA | ✅ Native | ✅ Native | ✅ Native | ❌ |
| Onboarding-Qualität | 9/10 | – | – | – | – |
| UX-Note | 8/10 | 8/10* | 9/10* | 8/10* | 5/10* |
| Gesamtnote | **9/10** | 8/10 | 7,5/10 | 7/10 | 6,5/10 |

*Einschätzung auf Basis Recherche, da Live-Test blockiert.

---

## 4. Empfehlung für MietVerwaltung

### 4.1 Features, die wir unbedingt übernehmen sollten

#### Von Zammad (Priorität hoch)
1. **Deutsches/EU-konformes Ticketing-Datenmodell**
   - Ticket mit Artikeln (Kunden-Nachricht, Agent-Antwort, interne Notiz)
   - Status: new, open, pending reminder, pending close, closed
   - Prioritäten: low, normal, high
   - Gruppen-/Besitzer-Zuweisung
2. **Zammad-ähnliche First-Steps-Checkliste im Onboarding**
   - „Erstelle ein Test-Ticket“, „Lade Kollegen ein“, „E-Mail einrichten“, „Textbausteine anlegen“, „Makros erstellen“
3. **Textbausteine + Makros**
   - Schnellantworten mit Platzhaltern (`#{ticket.customer.lastname}`)
   - Makros für wiederkehrende Aktionen (z. B. „Schließen & als Spam taggen“)
4. **Trigger + zeitgesteuerte Scheduler**
   - Auto-Reply bei neuem Ticket
   - Kundenbenachrichtigung bei Besitzerwechsel
   - Eskalations-Erinnerungen
5. **SLA-Management**
   - Response-Time-, Update-Time-, Solution-Time-Ziele
   - Separate Eskalations-Übersicht
6. **KI mit wählbarem Provider / Souveränität**
   - Ticket-Zusammenfassung (Customer Intent, Sentiment, Open Questions)
   - Schreibassistent (Expand, Fix grammar, Rewrite, Translate)
   - KI-Agenten für Kategorisierung, Gruppen-Routing, Priorisierung
   - Bevorzugt lokale/EU-Modelle oder selbst gewählten Provider
7. **Notification-Center**
   - Gruppenbasierte E-Mail-Benachrichtigungen
   - In-App-Notifications + Sounds
   - Out-of-Office

#### Von Help Scout / Crisp (UX-Inspiration)
8. **Saubere, aufgeräumte Shared-Inbox-Optik**
   - Weniger technische Widgets, mehr Fokus auf Konversation
   - Beacon-ähnliches Widget für Mieter (Hilfecenter + Kontakt)
9. **Klare Unterscheidung „Konversation“ vs. „Ticket-Attribute“**
   - Links die Nachrichten, rechts die Meta-Daten
10. **KI-Chatbot für Selbstbedienung**
    - Mieter stellt Frage → Bot schlägt Wissensdatenbank-Artikel vor → Optional Ticket erstellen

#### Von Zendesk / Freshdesk (Enterprise)
11. **Omnichannel-Routing**
    - E-Mail, Chat, WhatsApp, Portal in einer Inbox
12. **Bessere Reporting/Analytics**
    - Agenten-Performance, Kanalverteilung, Eskalationsstatistik
13. **Mobile Experience**
    - Progressive Web App oder native App für Hausverwalter unterwegs

### 4.2 Wie unser Ticket-Workflow aussehen sollte

**Für Mieter / Kunden (Endnutzer):**
1. Mieter öffnet das MietVerwaltung-Portal oder die App.
2. Er sieht sein Objekt, Mietvertrag und offene Tickets.
3. Er klickt „Neues Ticket“ und wählt ein Thema (z. B. „Mangel“, „Nebenkostenabrechnung“, „Umzug“, „Sonstiges“).
4. Formularfelder passen sich dem Thema an (Custom Forms wie osTicket).
5. Der Mieter kann Dateien (Fotos, Rechnungen) anhängen.
6. Sofortiges Auto-Reply: „Wir haben Ihr Ticket #MV-2026-001 erhalten. Bearbeitungsziel: 48 Stunden.“
7. Mieter kann jederzeit Status und Verlauf einsehen.

**Für Hausverwalter / Agenten (Backoffice):**
1. Dashboard zeigt offene Tickets, Eskalationen, SLA-Countdown, „meine Tickets“.
2. Unassigned & Open Tickets – Liste mit Titel, Kunde, Objekt, Gruppe, SLA, erstellt am.
3. Klick öffnet Ticket-Detail: Konversation links, Attribute rechts.
4. KI-Sidebar zeigt Zusammenfassung, Sentiment, offene Fragen, nächste Schritte.
5. Agent antwortet per Textbaustein oder KI-Schreibassistent.
6. Statuswechsel + Zuweisung erfolgt in der Sidebar.
7. Trigger informiert Mieter über Statusänderung.
8. Scheduler prüft nachts überfällige Tickets und eskaliert an den Chef.

### 4.3 Was die Profis besser machen als wir
- **Mächtige Automatisierung:** Zammad/Freshdesk haben Trigger, Scheduler, Macros, SLA aus einer Hand.
- **KI-Souveränität:** Zammad erlaubt wählbare Provider – einzigartig.
- **Omnichannel:** Zendesk/Intercom vereinen E-Mail, Chat, Social nahtlos.
- **Mobile Reife:** Crisp/Zendesk haben richtige Apps, Zammad nur PWA.
- **Reife Analytics:** Zendesk/Freshdesk bieten Standard-Reports, die bei uns fehlen.

### 4.4 Was wir besser machen können als die Profis
- **Branchenspezifische Daten:** Mieter-Objekt-Vertrag-Verknüpfung ist für uns nativ, bei generischen Helpdesks nur via Custom Fields/Zapier möglich.
- **Deutsches DSGVO- / WEG-/Mietrecht-Bewusstsein:** Wir können Datenspeicherung, Aktenordnung, Fristen direkt berücksichtigen.
- **Vereinfachte UX für kleine Hausverwaltungen:** Profis sind oft überfrachtet; wir können schlank bleiben.
- **Kein Vendor Lock-in / Open-Source-Freundlichkeit:** Wir können wie Zammad/FreeScout offene Standards nutzen.
- **Kostenlose Einstiegstufe für kleinere Verwaltungen:** Ähnlich Zammad-Starter oder Help-Scout-Free.

---

## 5. Zusammenfassung & Top-Empfehlung

- **Haupt-Benchmark für Funktionsumfang und Compliance:** Zammad.
- **Haupt-Benchmark für moderne UX:** Help Scout / Crisp.
- **Haupt-Benchmark für Enterprise-Skalierung:** Zendesk / Freshdesk.
- **Empfohlene Strategie für MietVerwaltung:**
  1. Datenmodell und Workflow an Zammad orientieren (Tickets, Artikel, Gruppen, Status, SLA, Trigger, Makros).
  2. UX/Optik an Help Scout/Crisp orientieren (clean, konversationszentriert, mobile-first).
  3. Branchenspezifische Felder und Verknüpfungen (Mieter, Objekt, Vertrag, Dokumente) von Anfang einbauen.
  4. KI-Features mit wählbarem Provider (OpenAI, Azure, lokal/Ollama) vorsehen, aber nicht zwingend voraussetzen.
  5. SLA-/Eskalations-Automatisierung als Differentiator gegenüber einfachen Mietverwaltungs-Tools.

**Datei erstellt:** `/root/mietverwaltung/ticket-saas-hands-on-test.md`
