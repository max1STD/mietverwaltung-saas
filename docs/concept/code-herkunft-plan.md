# Code-Herkunfts-Plan — Was wir adaptieren, selbst schreiben, und reverse engineeren

> **Grundregel:** Wir kopieren keinen Code 1:1 (AGPL/GPL Lizenzen). Wir adaptieren **Algorithmen, Patterns, Datenmodelle und Architekturideen**. Code schreiben wir selbst.

---

## 1. Übersicht: 3 Quellen für unseren Code

```
┌─────────────────────────────────────────────────────────┐
│  GITHUB REPOS (adaptieren)                              │
│  Algorithmen, Patterns, Datenmodelle, Logik           │
│  30 Repos gefunden, 5 im Detail analysiert              │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│  SELBST GESCHRIEBEN (unser Code)                       │
│  FastAPI Backend, Vue.js Frontend, Auth, KI, DSGVO      │
│  ~90% unseres Codes                                    │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│  REVERSE ENGINEERING (von Konkurrenten)               │
│  UX-Patterns, Feature-Design, Workflows              │
│  8 Konkurrenten analysiert                              │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Was wir aus GitHub adaptieren (Patterns, keine Code-Kopien)

### Aus mietfuchs (speedone/mietfuchs) — React/Express/Docker

| Was | Wie | In welcher Build-Phase |
|-----|-----|----------------------|
| **KI-Belegauswertung-Pattern** | Architektur studieren: wie sie OCR → JSON-Schema → KI → strukturierte Ausgabe bauen. Wir implementieren in Python mit Presidio + Ollama. | Phase 7 |
| **NK-Abrechnungs-Logik** | Umlageschlüssel-Algorithmus adaptieren (nach qm/Personen/Verbrauch). Berechnungsformel übernehmen, in Python neu schreiben. | Phase 5 |
| **HeizkostenV + CO₂-Kosten** | Verteilungslogik für Heizkosten (nach Verbrauch, mit Personentage). CO₂-Aufteilung-Algorithmus. | Phase 5 |
| **DACH-spezifische BetrKV-Positionen** | Welche Kostenarten sind umlagefähig? Liste als Vorlage für unseren kostenkategorien-Katalog. | Phase 5 |
| **Clientseitige PDF-Vorverarbeitung** | Pattern: PDF vor OCR vorverarbeiten (PyMuPDF) um Qualität zu verbessern. | Phase 7 |
| **Consent-Management** | Wie sie KI-Einwilligung handhaben. | Phase 1, 10 |

### Aus NebenkostenFix (Nerbry72) — Python!

| Was | Wie | In welcher Build-Phase |
|-----|-----|----------------------|
| **BetrKV-Katalog** | Liste aller umlagefähigen/nicht-umlagefähigen Positionen als Python-Dict/JSON. Fast direkt übernehmbar (nur Daten, kein Code). | Phase 5 |
| **Python NK-Rechenkern** | Berechnungslogik in Python — wir können den Algorithmus adaptieren (Formeln, Personentage, Verteilung). In FastAPI neu implementieren. | Phase 5 |
| **HeizkostenV-Implementierung** | Python-Code für Heizkostenverteilung. Algorithmus übernehmen, in unserem Service integrieren. | Phase 5 |
| **Umlageschlüssel-Validierung** | PLZ-Format, BetrKV-Positionen prüfen. | Phase 5 |

### Aus HaVeWa (fgilde/hausverwaltung) — Java/Spring/PostgreSQL

| Was | Wie | In welcher Build-Phase |
|-----|-----|----------------------|
| **MCP-Server-Design** | Architektur studieren: wie sie den MCP-Server für Claude/ChatGPT gebaut haben. Wir bauen in Python für Ollama Cloud. | Phase 7 (später) |
| **Audit-Log-Architektur** | Welche Events loggen sie? Welche Felder? risk_level-Konzept übernehmen. In SQLAlchemy neu implementieren. | Phase 1, 10 |
| **Ticket/Vorgangs-System** | Workflow-Pattern: offen → in_bearbeitung → erledigt → geschlossen. Status-Machine adaptieren. | Phase 4 |
| **Multi-Mandanten-Pattern** | Wie sie Datenisolation pro Vermieter machen. RLS-Pattern als Referenz. | Phase 1, 2 |
| **DIN-5008-PDF-Layout** | Briefkopf-Format für Geschäftsbriefe nach DIN 5008. Template-Struktur übernehmen. | Phase 9 |
| **Bank-Sync-Pattern** | Wie sie Mieteingänge zuordnen. Für später (Phase 2 Roadmap). | Roadmap |

### Aus mietkartei.de (OliverHennhoefer) — SvelteKit/Docker

| Was | Wie | In welcher Build-Phase |
|-----|-----|----------------------|
| **MCP-Server-Implementierung** | Sauberste Referenz: wie MCP-Server mit Claude/ChatGPT kommuniziert. Protokoll adaptieren, in Python für Ollama bauen. | Phase 7 (später) |
| **Enable-Banking-Bankabgleich** | PSD2/FinTS API-Pattern für späteren Bankabgleich. | Roadmap |
| **SvelteKit → Vue.js Mapping** | Frontend-Architektur-Ideen (Component-Structure, Store-Pattern). In Vue.js neu interpretieren. | Phase 0, 2 |

### Aus immobase (s3gv) — PHP/Symfony/PostgreSQL

| Was | Wie | In welcher Build-Phase |
|-----|-----|----------------------|
| **PostgreSQL-Schema-Validierung** | Unsere 22 Tabellen vs. ihr Schema vergleichen. Welche Felder fehlen uns? Welche haben sie die wir nicht brauchen? | Phase 0, 2 |
| **WEG-Logik** | Vermögensbericht §28 WEG, Hausgeldabrechnung. Für späteres WEG-Feature. | Roadmap |
| **RBAC/2FA-Design** | Rollen-Trennung auf DB-Ebene. Als Referenz für unser RLS-Konzept. | Phase 1 |
| **Modularisierungs-Pattern** | Wie sie Module trennen (Miete vs. WEG vs. Hausgeld). Für unsere Code-Struktur. | Phase 0 |

### Weitere Repos

| Repo | Was adaptieren | Phase |
|------|---------------|-------|
| **bhimrazy/receipt-ocr** | OCR-Engine-Pattern für Beleg-Scan (Bibliothekswahl, Preprocessing) | Phase 7 |
| **Klotzkette/claude-fuer-deutsches-recht** | Deutsche Rechts-Prompt-Wissensbasis für KI-Assistenten (§556, §558, §573 BGB etc.) | Phase 7 |
| **Governikus/AusweisApp2** | eID-Integration-Referenz (SDK-Wrapper, NFC-Protokoll) | Phase 2 (Roadmap) |
| **remsfal/remsfal-backend** | CI/CD-Pipeline-Struktur (GitHub Actions, SonarQube, Testing) | Phase 0, 11 |
| **MicroRealEstate** | UX-Patterns (Dashboard-Layout, Receipt-System, Templates) | Phase 3, 6, 9 |

---

## 3. Was wir selbst schreiben (unser eigener Code ~90%)

### Backend (FastAPI/Python)

| Modul | Was wir schreiben | Warum selbst |
|-------|-----------------|-------------|
| **main.py / config.py** | FastAPI Entry Point, Settings, Pydantic-Config | Kernstruktur — muss unser Code sein |
| **database.py** | SQLAlchemy AsyncSession, PostgreSQL-Verbindung | Zentral für alle Services |
| **auth/** | Registrierung, Login, JWT, 2FA (TOTP+E-Mail), Session-Management | Sicherheit — muss eigen sein |
| **auth/crypto.py** | AES-256-GCM Verschlüsselung (IBAN, Steuernr, Geburtsdatum) | Sensibel — eigen |
| **auth/rate_limit.py** | Redis-basiertes Rate-Limiting (5 Versuche/15 Min) | Security — eigen |
| **auth/csrf.py** | CSRF-Token-Generierung und -Validierung | Security — eigen |
| **middleware/geoip.py** | MaxMind GeoLite2 DACH-Blocking + Whitelist | Security — eigen |
| **middleware/roles.py** | RBAC: server-side Rollenprüfung bei jedem Request | Security — eigen |
| **models/** | Alle 22 SQLAlchemy-Modelle (users, objekte, einheiten, mieter, mietvertraege, etc.) | Unser DB-Schema v2 |
| **routes/objekte.py** | CRUD-Endpunkte für Objekte/Einheiten | Kernfeature |
| **routes/mieter.py** | CRUD für Mieter + Mietvertraege + Login-Erstellung | Kernfeature |
| **routes/tickets.py** | Ticket-System Endpunkte | Kernfeature |
| **routes/kosten.py** | Kosten erfassen, Abrechnung erstellen | Kernfeature |
| **routes/abrechnung.py** | NK-Abrechnung mit abrechnung_positionen | Kernfeature — **Algorithmus adaptiert von NebenkostenFix, in Python neu geschrieben** |
| **routes/dokumente.py** | Upload/Download, Verschlüsselung, Sichtbarkeit | Kernfeature |
| **routes/dashboard.py** | KPI-Berechnung (Brutto/Nettorendite, ROE, DSCR, LTV) | Kernfeature — **Formeln selbst geschrieben** |
| **routes/plans.py** | Plan-Management (Free/Basis/Pro/Business), Upgrade/Downgrade, Wohnungs-Limit | Kernfeature — unser Abo-Modell |
| **routes/dsgvo.py** | Datenexport (Art. 15), Löschung (Art. 17), Einwilligungs-Verwaltung | DSGVO — eigen |
| **services/ki/anonymizer.py** | Presidio-Integration + Custom-Regeln + Mapping-Tabelle | **Presidio als Library, Wrapper selbst geschrieben** |
| **services/ki/ollama.py** | Ollama Cloud API-Client (GLM 5.2 + Kimi K2.6) | **API-Client selbst geschrieben** |
| **services/ki/classifier.py** | Keyword-Classifier (60% ohne KI) + KI-Fallback | **Keywords selbst definiert, Pattern von mietfuchs inspiriert** |
| **services/ki/prompts.py** | Prompt-Templates für alle KI-Use-Cases | **Prompts selbst geschrieben** |
| **services/ki/ocr.py** | Tesseract + PyMuPDF Wrapper | **Tesseract als Library, Wrapper selbst** |
| **services/ki/insights.py** | Smart Insights (täglich, Kimi K2.6) | **Algorithmus selbst geschrieben** |
| **services/pdf.py** | WeasyPrint + Jinja2 PDF-Generierung | **Templates selbst geschrieben, DIN-5008-Layout von HaVeWa inspiriert** |
| **services/templates.py** | Jinja2 Template-Engine + 10 statische Vorlagen | **Vorlagen selbst geschrieben** |
| **services/email.py** | Postfix/SMTP + Jinja2 HTML-Templates | **Eigen** |
| **services/mahnung.py** | Mahn-Workflow (Tag 3/7/14/21) + KI-Mahnungstext | **Workflow selbst, KI-Prompt selbst** |
| **services/fristen.py** | Fristen-Tracking + Warnstufen | **Eigen** |
| **services/events.py** | Event-Queue + Notification-Dispatcher | **Eigen** |
| **services/eid.py** | AusweisIDent API-Client + KOPIE-Wasserzeichen (PIL) | **Eigen** (Phase 2) |
| **utils/audit.py** | Audit-Log-Service | **Eigen, Pattern von HaVeWa inspiriert** |

### Frontend (Vue.js 3)

| Modul | Was wir schreiben | Warum selbst |
|-------|-----------------|-------------|
| **App.vue + Router** | SPA-Routing, rollenbasierte Navigation | Kernstruktur |
| **stores/auth.ts** | Pinia Auth-Store, Token-Refresh | Sicherheit |
| **stores/plan.ts** | Plan-Management, Wohnungs-Limit-Anzeige | Abo-Modell |
| **views/vermieter/** | Dashboard, Objekte, Einheiten, Mieter, Tickets, Kosten, Abrechnung, Dokumente, Einstellungen | Vermieter-Portal |
| **views/mieter/** | Meine Daten, Tickets erstellen, Abrechnungen, Dokumente | Mieter-Portal |
| **views/auth/** | Login, Registrierung, 2FA, Passwort-Reset | Auth-Flow |
| **components/** | Wiederverwendbare UI-Komponenten (Cards, Forms, Modals, Upload, Charts) | **UX-Patterns von MicroRealEstate/immocloud inspiriert, in Vue.js neu geschrieben** |
| **components/ki-assistant/** | KI-Vorschau, Beleg-Scan-UI, Dokument-Generator | **Eigen** |

---

## 4. Was wir per Reverse Engineering von Konkurrenten lernen

> **WICHTIG:** Reverse Engineering = **Produkte nutzen und UX/Features analysieren**. Kein Code-Dekompilierung, keine Sicherheitslücken-Suche.

### Von immocloud (Note 7,0 — Testsieger 2026)

| Was lernen | Wie | Für unsere SaaS |
|-----------|-----|-----------------|
| **Onboarding-Flow** | 3-Schritte-Wizard (Person/Company → Einheiten → Wie gehört) | Unser Onboarding adaptieren: 2-Schritte (Objekt → Mieter), simpler |
| **Dashboard-Layout** | Sidebar + Top-Bar + Karten (Workflows, Objects, Tenancies) | Unser Dashboard-Layout inspirieren |
| **UX-Qualität** | Sehr intuitiv, wenig Klicks | Unser Ziel: mindestens genauso gut |
| **45-Tage-Test** | Länger als 30 Tage → mehr Zeit zum Testen | Unser Trial: 30 Tage (reicht) |
| **E-Mail-2FA** | E-Mail-Verifikation + 2FA per E-Mail | Wir haben TOTP+E-Mail (besser) |
| **Was fehlt bei immocloud** | Kein echtes Ticket-System, keine KI-Schreiben, kein ROI, kein eID | → Unsere Differenzierung! |

### Von rentably (Note 6,5 — Preisbrecher)

| Was lernen | Wie | Für unsere SaaS |
|-----------|-----|-----------------|
| **Free-Tier unbegrenzt** | ziehen Massen an | Unser Free: 2 Wohnungen (Kompromiss) |
| **Pro-Flatrate 9€** | Einfachster Preis | Unser Basis 14,90€ — aber mit KI-USP gerechtfertigt |
| **Dashboard** | Übersicht, Immobilien, Mieter, Zahlungen | Our Layout adaptieren |
| **MCP-Integration** | externer MCP für Claude | Wir bauen eingebaute KI (besser) |
| **Was fehlt bei rentably** | Keine eingebaute KI, keine DSGVO-KI, kein eID | → Unsere Differenzierung! |

### Von hellohousing (Note 6,0)

| Was lernen | Wie | Für unsere SaaS |
|-----------|-----|-----------------|
| **Funkzähler/UVI** | Verbrauchsabhängige Abrechnung mit Funkzähler-Daten | Später (Roadmap) |
| **Preisstruktur** | 4,50€ Basis → 19,50€ Premium | Wir sind teurer aber mit mehr KI |
| **Was fehlt** | Kein Mahnwesen, kein DATEV, keine Tickets | → Unsere Differenzierung! |

### Von objego (Note 5,5)

| Was lernen | Wie | Für unsere SaaS |
|-----------|-----|-----------------|
| **Keycloak-Onboarding** | Use-Case-Auswahl beim Onboarding | Unser Onboarding: Use-Case prüfen |
| **Was fehlt** | Keine KI, keine Automation, kein Mieterportal | → Unsere Differenzierung! |
| **Lektion** | Kostenlos allein reicht nicht — muss auch gut sein | Wir: Free 2 WE + gute UX |

### Von verwaltio (Note 7,0)

| Was lernen | Wie | Für unsere SaaS |
|-----------|-----|-----------------|
| **KI-Assistent** | Integrierter KI-Chat-Assistent | Später (Roadmap) |
| **Pro-Einheit-Preis** | Transparente Preisstruktur | Wir: Staffel nach Wohnungen |
| **Open Banking** | Bankanbindung direkt | Später (Roadmap) |
| **Was gut ist** | KI + Tickets + Portal in einem Produkt | Genau unser Ansatz! |

### Von aedium (Note 7,5* — noch Pilotphase)

| Was lernen | Wie | Für unsere SaaS |
|-----------|-----|-----------------|
| **30 KI-Agenten** | KI für jede Aufgabe separat | Wir: 1 KI (Ollama) für alles, aber gut |
| **Architektur** | KI-Agenten-Orchestrierung | Später evtl. |
| **Lektion** | KI-Fokus ist richtig — aber sie sind noch nicht am Markt | → Zeitfenster für uns! |

### Von immoware24 (Note 7,0)

| Was lernen | Wie | Für unsere SaaS |
|-----------|-----|-----------------|
| **Feature-Umfang** | Alles drin (WEG, Miete, Bank, DATEV) | Wir: erst Miete, WEG später |
| **Komplexität** | Zu komplex für Kleinvermieter | Wir: einfach, fokussiert |
| **Preis** | ab 350€/Monat | Wir: ab 14,90€ — 23x günstiger |
| **Lektion** | Nicht zu viel auf einmal — fokussiert bleiben | |

---

## 5. Zusammenfassung: Code-Herkunft pro Modul

| Modul | Quelle | % adaptiert | % selbst | % RE-inspiriert |
|-------|--------|-------------|---------|-----------------|
| **DB-Schema** | immobase (Validierung) | 10% | 90% | — |
| **Auth/2FA/JWT** | — | 0% | 100% | — |
| **Objekt/Mieter/Mietvertrag CRUD** | HaVeWa (Pattern) | 5% | 95% | — |
| **NK-Abrechnung** | NebenkostenFix + mietfuchs | 30% | 70% | — |
| **BetrKV-Katalog** | NebenkostenFix | 80% (Daten) | 20% | — |
| **HeizkostenV** | mietfuchs | 25% | 75% | — |
| **Ticket-System** | HaVeWa (Workflow) | 10% | 90% | immocloud (UX) |
| **KI-Anonymisierung** | Presidio (Library) | 60% (Library) | 40% (Wrapper) | — |
| **KI-Beleg-Scan** | mietfuchs (Pattern) | 20% | 80% | — |
| **KI-Prompts** | Klotzkette (Recht) | 10% | 90% | — |
| **Ollama Cloud Client** | — | 0% | 100% | rentably (MCP) |
| **Keyword-Classifier** | mietfuchs (Keywords) | 15% | 85% | — |
| **Smart Insights** | — | 0% | 100% | aedium |
| **Dashboard/KPIs** | — | 0% | 100% | immocloud |
| **PDF/Templates** | HaVeWa (DIN-5008) | 15% | 85% | MicroRealEstate |
| **Mahnwesen** | — | 0% | 100% | — |
| **Fristen-Tracker** | — | 0% | 100% | — |
| **Events/Notifications** | — | 0% | 100% | — |
| **E-Mail-Service** | — | 0% | 100% | — |
| **DSGVO (Export/Löschung)** | — | 0% | 100% | — |
| **IP-Blocking (GeoIP)** | — | 0% | 100% | — |
| **Plan-Management (Abo)** | — | 0% | 100% | rentably |
| **eID-Integration** | AusweisApp2 (Referenz) | 10% | 90% | — |
| **Frontend UX** | — | 0% | 100% | immocloud, MicroRealEstate |
| **CI/CD Pipeline** | remsfal (Struktur) | 20% | 80% | — |
| **Docker Setup** | ops/ (bereits erstellt) | 50% | 50% | — |

**Gesamt:** ~10% adaptiert, ~85% selbst geschrieben, ~5% RE-inspiriert

---

## 6. Was WIR besser machen als alle Konkurrenten

| Feature | Konkurrenten | Wir |
|---------|-------------|-----|
| **KI-Automatisierung** | immocloud (nur OCR), rentably (extern), aedium (Pilot) | Eingebaut, Presidio-Anonymisierung, Ollama Cloud |
| **Ticket-System** | immocloud (Vorgänge), hellohousing (❌), objego (❌) | Echtes Ticket-System in allen Plänen |
| **eID** | Niemand | AusweisIDent + KOPIE-Upload (Phase 2) |
| **DSGVO-KI** | Niemand dokumentiert | Presidio + Audit-Log |
| **Smart Insights** | Niemand (aedium Pilot) | Täglich KI-generiert |
| **ROI/Kennzahlen** | Niemand | Brutto/Netto/ROE/DSCR/LTV |
| **Mahnwesen** | hellohousing (❌), objego (❌) | Automatisch Tag 3/7/14/21 |
| **Onboarding** | Alle haken irgendwo | Reibungsloser Self-Service |
| **Preis** | immoware24 ab 350€ | Ab 14,90€ — 23x günstiger |