# MietVerwaltung SaaS — Finaler Build-Plan v2

> **Aktualisiert am:** 28. Oktober 2026
> **Änderungen v1→v2:** DB-Schema v2 (22 Tabellen), Preise nach Wohnungen, eID-Integration, KI-Anonymisierung mit Presidio, Security-Gaps behoben, Repo-Insights integriert, Ausweis KOPIE-Wasserzeichen

**Ziel:** DSGVO-konformes MVP für private Kleinvermieter in DACH mit FastAPI/Vue.js/PostgreSQL/Redis/Ollama Cloud.

**Dauer:** ~90 Personentage (4-5 Monate bei Vollzeit)

---

## 0. Entscheidungen (alle finalisiert)

| # | Thema | Entscheidung |
|---|-------|-------------|
| 1 | DB-Schema | v2 — 22 Tabellen (inkl. mietvertraege, abrechnung_positionen, audit_logs, einwilligungen, user_sessions, events, notifications, fristen, kostenkategorien) |
| 2 | Preise | Free 0€ (2 Wohnungen) / Basis 14,90€ (5 WE) / Pro 29,90€ (25 WE) / Business 49,90€ (∞) — nach Wohnungen, nicht Objekten |
| 3 | Identität | MVP: persönliche Kontrolle + Vermerk. Phase 2: eID via AusweisIDent + Ausweis-Upload mit KOPIE-Wasserzeichen |
| 4 | KI-Anonymisierung | Presidio (NER-basiert) statt Regex — DSGVO-Experten-Empfehlung |
| 5 | Security | +CSRF-Token, +CSP-Nonces, +Auth-Rate-Limiting, +Session-Management (user_sessions) |
| 6 | Repo-Insights | NK-Logik von mietfuchs/NebenkostenFix adaptieren, BetrKV-Katalog übernehmen, MCP-Server nach mietkartei/HaVeWa |
| 7 | Ausweis | MVP: persönlich. Upload mit KOPIE + sofortige Löschung ab Phase 2 (Pro-Plan) |
| 8 | Free-Tier | 2 Wohnungen (erweitert von 1 — wettbewerbsfähig mit rentably/objego) |

---

## 1. Strategische Reihenfolge

```
1. Foundation → Docker, Dev-Umgebung, DB-Schema v2, Auth, Security, Audit
2. Domain-Core → Vermieter, Objekte, Einheiten, Mieter, Mietvertraege
3. Dokumente & Tickets → Upload, Verschlüsselung, Ticket-System
4. Finanzen → Kosten, NK-Abrechnung (mit abrechnung_positionen), Dashboard, Kennzahlen
5. KI-Schicht → Presidio-Anonymisierung, Ollama, OCR, KI-Dokumente
6. Kommunikation → E-Mail, Mahnwesen, Fristen-Warner
7. Compliance → DSGVO, IP-Blocking, PDF-Export, Production-Hardening
```

---

## 2. Software-Build-Phasen

### Phase 0: Projekt-Fundament & Dev-Umgebung (3-4 PT)

**Backend:**
- Projektstruktur: `backend/app/{main.py,config.py,database.py}`, `backend/app/{models,routes,services,middleware,utils}/`
- `Dockerfile` für FastAPI (Python 3.13 + Tesseract + WeasyPrint + Presidio)
- `requirements.txt`: FastAPI, SQLAlchemy 2.x, Alembic, Pydantic, python-jose, passlib, argon2-cffi, redis, asyncpg, cryptography, pyotp, httpx, presidio, spacy, pymupdf, weasyprint, jinja2
- `docker-compose.yml` + `docker-compose.dev.yml`
- DB-Schema v2 als Alembic-Initial-Migration (alle 22 Tabellen)
- Health-Check `/health`

**Frontend:**
- Vue.js 3 + Vite + Vue Router + Pinia + Tailwind CSS + Axios
- Apple-Style Layout, Navigation, Theme (Navy #0D3B70)
- API-Client mit zentralem Axios-Instance

**DevOps:**
- Git-Repo, `.gitignore`, `.env.example`
- Hot-Reload für Dev
- Makefile: `make dev`, `make test`, `make migrate`

**Milestone:** `docker compose up` läuft; `/health` liefert `ok`; Alembic-Migration erzeugt alle 22 Tabellen.

---

### Phase 1: Auth, Rollen, 2FA, Security, Audit (8-10 PT)

**Backend:**
- `users`-Tabelle (inkl. totp_secret, backup_codes, email_code, failed_login_count, locked_until, dsdvo_consent_at)
- `user_sessions`-Tabelle (Geräte-Verwaltung, Session-Revocation) **NEU v2**
- `einwilligungen`-Tabelle (versionierte DSGVO-Einwilligung) **NEU v2**
- `audit_logs`-Tabelle (alle sicherheitsrelevanten Aktionen, risk_level) **NEU v2**
- Argon2id Passwort-Hashing
- JWT: Access 15min + Refresh 7d in HTTP-only Secure Cookies
- 2FA: TOTP + E-Mail-Code-Fallback
- **CSRF-Token** für alle state-changing Requests (nicht nur SameSite) **NEU v2**
- **CSP-Header mit Nonces** (nicht 'unsafe-inline') **NEU v2**
- **Auth-Rate-Limiting**: 5 Versuche/15 Min pro IP+E-Mail **NEU v2**
- **Session-Management**: Alle-Geräte-Logout, verdächtige-Login-Erkennung **NEU v2**
- Rollenprüfung bei JEDEM Request (server-side)
- `crypto.py` mit AES-256-GCM (IBAN, Steuernr, Geburtsdatum)

**Frontend:**
- Login, Registrierung mit Einwilligung, 2FA-Setup, Passwort-Reset
- Auth-Store (Pinia) mit Token-Refresh
- Rollen-basierte Navigation

**Milestone:** Registrierung → Login → 2FA → geschütztes Dashboard.

---

### Phase 2: Domain-Core — Objekte, Einheiten, Mieter, Mietvertraege (7-8 PT)

**Backend:**
- SQLAlchemy-Modelle: `objekte`, `einheiten`, `mieter`, `mietvertraege` **NEU: mietvertraege separat!**
- `mietvertrag_aenderungen` (Vertragsänderungs-Historie) **NEU v2**
- `kostenkategorien` (pro Vermieter konfigurierbar) **NEU v2**
- RLS Policies für `vermieter_id`
- CRUD für Objekte/Einheiten/Mieter/Mietvertraege
- Mieter-Login erstellen
- Feld-Verschlüsselung: `mieter.geburtsdatum`
- Validierungen: PLZ, Mietbeginn < Mietende, Kaltmiete > 0
- **Wohnungs-Limit-Prüfung** pro Plan (Free 2 / Basis 5 / Pro 25 / Business ∞) **NEU v2**
- **Plan-Management**: Upgrade/Downgrade, Add-ons (Extra Wohnung 1€) **NEU v2**

**Frontend:**
- Vermieter-Portal: Dashboard, Objekt-/Einheiten-/Mieter-Verwaltung
- Mieter-Portal: Meine Daten (read-only)
- **Plan-Anzeige**: "Wohnungen: 3/5 (Basis)" mit Upgrade-Hinweis **NEU v2**

**Milestone:** Vermieter legt Objekt → Einheit → Mieter → Mietvertrag an; Wohnungs-Limit wird geprüft.

**Repo-Insights:** PostgreSQL-Schema von immobase als Validierung referenzieren. Mietvertrag-Trennung (Person vs. Vertrag) nach HaVeWa-Pattern.

---

### Phase 3: Dokumenten-Management & Upload (5-7 PT)

**Backend:**
- `dokumente`-Tabelle (inkl. file_hash SHA-256) **NEU v2**
- `dokument_freigaben`-Tabelle
- Upload mit Validierung (PDF/JPG/PNG, max 10MB, Magic-Bytes)
- AES-256 at-rest Verschlüsselung
- Sichtbarkeit: vermieter/mieter/beide/handwerker
- Download mit Rollenprüfung
- Löschung mit Audit-Log

**Frontend:**
- Upload-Komponente (Drag & Drop), Dokumenten-Galerie, Download/Lösch

**Milestone:** Vermieter und Mieter können Dokumente hochladen; Mieter sieht nur freigegebene.

---

### Phase 4: Ticket-System (5-6 PT)

**Backend:**
- `tickets` (inkl. ki_kategorisiert, ki_prioritaet Flags) **NEU v2**
- `ticket_kommentare` (inkl. ist_ki_entwurf Flag) **NEU v2**
- Ticketnummer-Generierung (TKT-2026-001)
- Status-Workflow: offen → in_bearbeitung → erledigt → geschlossen
- **Keyword-Classifier** (lokal, 60% ohne KI): heizung/wasser/elektrik/schimmel Keywords **NEU v2**
- E-Mail-Trigger (Stub, Phase 8)

**Frontend:**
- Mieter: Ticket erstellen, Liste, Detail mit Kommentaren
- Vermieter: Alle Tickets, Filter, Status ändern

**Milestone:** Mieter erstellt Ticket → Keyword-Classifier kategorisiert automatisch → Vermieter bearbeitet.

**Repo-Insights:** Keyword-Pattern nach mietfuchs adaptieren.

---

### Phase 5: Kosten & Nebenkostenabrechnung (8-10 PT)

**Backend:**
- `kosten` (inkl. abrechnung_id, abgerechnet_am, ki_kategorisiert) **NEU v2**
- `mietzahlungen` (inkl. betrag_soll/ist, mahnstufe, zahlungsreferenz) **NEU v2**
- `abrechnungen` (inkl. zeitraum_von/bis, einwendungsfrist_bis, rechtskraeftig_seit) **NEU v2**
- `abrechnung_positionen` (einzelne Positionen nachvollziehbar — BetrKV) **NEU v2**
- Umlage-Logik: nach qm/Personen/Verbrauch
- **BetrKV-Katalog** (adaptiert von NebenkostenFix) **NEU v2**
- **HeizkostenV** (adaptiert von mietfuchs) **NEU v2**
- Verteilungsberechnung (reine Mathematik)
- Plausibilitätsprüfung

**Frontend:**
- Kosten erfassen, Beleg-Scan-Upload, Abrechnungs-Vorschau
- Mietzahlungen erfassen/markieren

**Milestone:** Vermieter erfasst Heizkosten → System erstellt NK-Abrechnung mit einzelnen Positionen (abrechnung_positionen).

**Repo-Insights:** BetrKV-Katalog von NebenkostenFix (Python!) adaptieren. HeizkostenV/CO₂-Logik von mietfuchs.

---

### Phase 6: Dashboard & Kennzahlen (5-7 PT)

**Backend:**
- Berechnungs-Engine: Bruttomietrendite, Nettomietrendite, ROE, Cash-on-Cash, DSCR, LTV, Gesamtrendite
- Finanzierungsfelder am Objekt: Darlehen, Eigenkapital, Zinssatz, Tilgung
- Endpunkte: `/dashboard/summary`, `/dashboard/object/{id}`
- Offene Tickets, fällige Mietzahlungen, anstehende Fristen

**Frontend:**
- KPI-Cards, Chart-Komponente (vue-chartjs)
- Objekt-Detail-Dashboard, Einheiten-Übersicht

**Milestone:** Dashboard zeigt korrekte Kennzahlen (mit und ohne Finanzierung).

---

### Phase 7: KI-Schicht — Presidio, OCR, Ollama, KI-Dokumente (12-15 PT)

**Backend:**
- Tesseract + PyMuPDF OCR-Integration
- **Presidio (NER-basiert) Anonymisierungs-Engine** — ersetzt reine Regex **NEU v2**
  - Deutsche Modelle (spaCy de_core_news_lg)
  - Erkennt: Namen, Adressen, IBAN, Telefon, Geburtsdatum, Steuernummern
  - Mapping-Tabelle (verschlüsselt) für Deanonymisierung
- **Keyword-Classifier** (vorgeschaltet, 60% ohne KI)
- Ollama Cloud API-Client (GLM 5.2 + Kimi K2.6)
- Prompt-Templates in `services/ki/prompts.py`
- Redis-Cache für KI-Aufrufe
- Audit-Log für alle KI-Aufrufe (anonymisierter Prompt, Modell, Zeitstempel)
- Health-Check + regelbasierte Fallbacks

**KI-Use-Cases im MVP:**
1. Ticket-Auto-Kategorisierung (Keyword → ggf. GLM)
2. Ticket-Priorität (Keyword/GLM)
3. Antwort-Entwurf für Vermieter (GLM)
4. Dokument-Klassifikation (GLM)
5. Beleg-Scan: Betrag + Kategorie + Umlagefähigkeit (OCR + GLM)
6. Abrechnungserklärungstext (GLM)
7. Mahnung Stufe 1-3 (GLM)
8. Mieterhöhung §558 BGB (Kimi K2.6)
9. Smart Insights (Kimi K2.6, täglich, batched)

**Frontend:**
- KI-Assistent-UI für Ticket-Antwort-Entwürfe
- Beleg-Scan-UI (Foto → Vorschlag extrahierter Felder)
- KI-generierte Dokumente: Template → Vorschau → PDF

**Milestone:** Beleg wird hochgeladen → Presidio anonymisiert → OCR + GLM extrahiert Betrag/Kategorie → Ergebnis in Kosten-Eintrag.

**Repo-Insights:** KI-Belegauswertung nach mietfuchs-Vorbild (mit unserer Presidio-Anonymisierung). MCP-Server-Struktur nach mietkartei/HaVeWa als Referenz für später.

---

### Phase 8: E-Mail, Mahnungen, Fristen-Warner (6-8 PT)

**Backend:**
- Postfix in Docker
- E-Mail-Service mit Jinja2-HTML-Templates
- `events`-Tabelle (Event-Queue für Automatisierungen) **NEU v2**
- `notifications`-Tabelle (versendete Benachrichtigungen mit Status) **NEU v2**
- `fristen`-Tabelle (zentrales Fristen-Tracking mit Warnstufen) **NEU v2**
- E-Mail-Events: Registrierung, Willkommen, Ticket, Abrechnung, Mahnung, Frist, 2FA, Reset
- **Automatisches Mahnwesen** (Tag 3/7/14/21 via events + notifications) **NEU v2**
- **Fristen-Check** täglich per Scheduler (Mietende 6/3/1 Monate, Abrechnungsfrist 12 Monate) **NEU v2**

**Frontend:**
- Mahnungs-Übersicht, Fristen-Kalender, Benachrichtigungs-Einstellungen

**Milestone:** Fällige Miete → Event ausgelöst → Notification erstellt → Mahnung per E-Mail mit PDF.

---

### Phase 9: PDF-Export & Templates (5-7 PT)

**Backend:**
- WeasyPrint + Jinja2
- Briefkopf (Vermieter-Logo, Adresse, Bankdaten)
- 10 statische Vorlagen (Wohnungsgeberbestätigung, etc.)
- 8 KI-generierte Dokumente (Mahnungen, Mieterhöhung, etc.)
- PDF-Download-Endpunkt

**Frontend:**
- "Dokument generieren"-Dialog, PDF-Vorschau, Download/Senden

**Milestone:** Wohnungsgeberbestätigung als PDF mit Briefkopf generiert.

---

### Phase 10: DSGVO, IP-Blocking, Compliance, Hardening (6-8 PT)

**Backend:**
- DSGVO-Export (Art. 15): ZIP mit DB-Daten + Dokumenten
- DSGVO-Löschung (Art. 17): Soft-Delete (deleted_at), Aufbewahrungsfristen (10J/6J)
- **DSGVO Art. 16/18/20/21** (Berichtigung, Einschränkung, Übertragbarkeit, Widerspruch) **NEU v2**
- Einwilligungs-Historie (einwilligungen-Tabelle)
- **VVT** (Verzeichnis Verarbeitungstätigkeiten, Art. 30) **NEU v2**
- **AVV** mit Hetzner, Ollama Cloud, MaxMind **NEU v2**
- IP-Blocking: MaxMind GeoLite2, nur DE/AT/CH + Whitelist
- Security-Headers (HSTS, CSP-Nonces, X-Frame-Options)
- Fail2Ban, Docker-Hardening
- Backup/Restore-Skripte

**Frontend:**
- Datenschutz-Einstellungen (Export, löschen), Impressum, DSGVO-Seiten, Cookie-Dialog

**Milestone:** DSGVO-Export liefert vollständige Daten; Nicht-DACH-IP wird blockiert.

---

### Phase 11: Production Deployment (4-6 PT)

- Produktions-Builds, `.env.production`
- CloudPanel/nginx Reverse Proxy, SSL (Let's Encrypt)
- DNS (A-Record, MX, SPF, DKIM, DMARC)
- Docker-Compose-Override für Produktion
- Migrationen ausführen
- Monitoring (Prometheus + Grafana aus ops/)
- Deploy-Script, Rollback-Plan
- Smoke-Test mit 5 Beispiel-Vermietern

**Milestone:** `https://mietverwaltung.de` erreichbar; erste Registrierung funktioniert.

---

## 3. Aufwandsübersicht

| Phase | Backend | Frontend | DevOps | QA | Gesamt |
|-------|---------|----------|---------|-----|--------|
| 0 — Fundament | 2 | 1 | 1 | 0,5 | **3,5-4** |
| 1 — Auth/Security | 7 | 2,5 | 1 | 1 | **11** |
| 2 — Domain-Core | 5 | 2 | 0,5 | 1 | **8,5** |
| 3 — Dokumente | 3,5 | 1,5 | 0,5 | 1 | **6,5** |
| 4 — Tickets | 3 | 2 | 0,5 | 0,5 | **6** |
| 5 — Kosten/Abrechnung | 6 | 2 | 0,5 | 1,5 | **10** |
| 6 — Dashboard | 2,5 | 2,5 | 0,5 | 1 | **6,5** |
| 7 — KI-Schicht | 9 | 3 | 1 | 2 | **15** |
| 8 — E-Mail/Mahnung/Fristen | 5 | 1,5 | 1 | 1 | **8,5** |
| 9 — PDF/Templates | 3 | 2 | 0,5 | 1 | **6,5** |
| 10 — DSGVO/Hardening | 4 | 1,5 | 2 | 1,5 | **9** |
| 11 — Production Deploy | 1 | 1 | 2,5 | 1 | **5,5** |
| **Summe** | **51** | **22** | **11,5** | **12,5** | **~97 PT** |

**Gesamtdauer:** ~4-5 Monate bei Vollzeit (inkl. Puffer)

---

## 4. Abhängigkeitsgraph

```
Phase 0 ──► Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4
                              │         │         │
                              ▼         ▼         ▼
                           Phase 5 ──► Phase 6 ──► Phase 7
                              │                   │
                              ▼                   ▼
                           Phase 8 ◄──────────────┘
                              │
                              ▼
                           Phase 9
                              │
                              ▼
                           Phase 10
                              │
                              ▼
                           Phase 11
```

**Parallelisierbar:**
- Phase 3 + Phase 4 parallel nach Phase 2
- Phase 6 parallel zu Phase 7 (sobald Phase 5 fertig)
- Phase 9 parallel zu Phase 8 (sobald Phase 7 fertig)

---

## 5. Repo-Insights (was wir adaptieren)

| Von Repo | Was adaptieren | In welcher Phase |
|----------|---------------|-----------------|
| **mietfuchs** | KI-Belegauswertung-Pattern, NK-Logik, HeizkostenV, CO₂ | Phase 5, 7 |
| **NebenkostenFix** | BetrKV-Katalog (Python!), Umlageschlüssel | Phase 5 |
| **HaVeWa** | MCP-Server-Design, Audit-Log, Ticket-System | Phase 4, 7, 8 |
| **mietkartei** | MCP-Server-Implementierung, Bankabgleich | Phase 7 (später) |
| **immobase** | PostgreSQL-Schema-Validierung, WEG-Logik | Phase 2 (Schema) |
| **remsfal** | CI/CD-Pipeline, Testing | Phase 0, 11 |
| **MicroRealEstate** | UX-Patterns, Templates | Phase 3, 6, 9 |

**WICHTIG:** Alle Repos sind AGPL/GPL. Wir adaptieren **Algorithmen und Patterns**, kopieren keinen Code 1:1.

---

## 6. Risiken

| Risiko | Wahrsch. | Auswirkung | Gegenmaßnahme |
|--------|---------|-----------|---------------|
| Ollama Cloud API-Ausfall | Mittel | Hoch | Fallbacks, Caching, Health-Check |
| Tesseract OCR ungenau bei Handschrift | Hoch | Mittel | KI-Nachbearbeitung, manuelle Korrektur |
| DSGVO-Unsicherheit bei KI-Dokumenten | Mittel | Hoch | "Bitte rechtlich prüfen", keine autom. Entscheidungen |
| Presidio nicht ausreichend für alle Datentypen | Niedrig | Mittel | Custom-Regeln ergänzen, Quality-Feedback-Loop |
| WeasyPrint in Docker | Mittel | Mittel | Frühes Docker-Testing |
| Postfix Deliverability | Mittel | Hoch | DKIM/SPF/DMARC, Fallback SendGrid |
| aedium kommt aus Pilotphase | Mittel | Hoch | Schneller marktreif werden |
| Frontend-Komplexität | Hoch | Mittel | Strikte Komponenten-Struktur |

---

## 7. Nächste Schritte

1. **Phase 0 starten** — Projektstruktur, Docker, Dev-Umgebung
2. **Domain kaufen** + Hetzner-Account
3. **Ollama Cloud API-Key** beschaffen
4. **MaxMind GeoLite2-Account** anlegen
5. **Presidio + spaCy German Model** testen
6. **Git-Repo** anlegen + erster Commit
7. **AusweisIDent Testzugang** bei ausweisident.de bestellen (für Phase 2)
8. **Rechtlichen Disclaimer** für KI-Dokumente

---

**Plan erstellt:** 27. Oktober 2026  
**Aktualisiert:** 28. Oktober 2026 (v2)  
**Status:** Bereit für Implementation — sobald User "baue" sagt