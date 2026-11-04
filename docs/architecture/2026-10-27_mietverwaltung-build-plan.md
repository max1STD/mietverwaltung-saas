# MietVerwaltung SaaS — Build-Plan

> **For Hermes:** Plan-Modus. Noch keine Code-Änderungen; dieses Dokument definiert die Bau-Reihenfolge, Meilensteine, Aufwände und Verifikation für den MVP.

**Ziel:** Inbetriebnahme eines DSGVO-konformen MVP für private Kleinvermieter in DACH mit FastAPI/Vue.js/PostgreSQL/Redis/Ollama Cloud.

**Ausgangslage:** Konzepte (`Server-Konzept.md`, `KI-Konzept.md`) und leere `ops/`-Verzeichnisse vorhanden. Kein Backend-/Frontend-Code, keine DB-Schema-Dateien, keine Docker-Compose.

---

## 1. Strategische Reihenfolge

```
1. Foundation zuerst
   └── Docker-Compose, Dev-Umgebung, DB-Schema, Auth, Security, Audit

2. Domain-Core danach
   └── Vermieter-Profil, Objekte, Einheiten, Mieter, Rollen/Rechte

3. Dokumente & Tickets
   └── Upload, Verschlüsselung, Sichtbarkeit, Ticket-System

4. Finanzen & Dashboard
   └── Kosten, Nebenkostenabrechnung, Renditekennzahlen

5. KI-Schicht & Automatisierung
   └── OCR, Anonymisierung, Ollama-Integration, KI-Dokumente

6. Kommunikation & Workflows
   └── E-Mail, Mahnwesen, Fristen-Warner

7. Compliance, PDF, Templates, Production-Hardening
   └── DSGVO-Features, IP-Blocking, PDF-Export, Deploy
```

**Warum diese Reihenfolge?**
- Ohne Auth/Security können keine geschützten Features gebaut werden.
- Ohne Objekte/Einheiten gibt es keine Bezugspunkte für Mieter, Dokumente, Kosten und Tickets.
- Ohne Dokumenten-Storage können weder Mieter-Bewerbungen noch Belege verarbeitet werden.
- Ohne Kosten gibt es keine Abrechnung und kein Dashboard.
- KI-Features setzen auf Tickets, Dokumenten und Kosten auf.
- E-Mail/Workflows setzen auf Daten und KI-Texten auf.

---

## 2. Server-Infrastruktur-Phasen

| Phase | Server | Ressourcen | Kosten/Monat | Zweck | Wann gebaut |
|-------|--------|------------|--------------|-------|-------------|
| **Phase 0** | Lokale Dev-VM (Proxmox LXC) | 2 vCPU, 4 GB RAM, 30 GB SSD | 0 € | Entwicklung & Test | Vor Phase 1 |
| **Phase 1** | 2 Server: Frontend CX22 + Backend CX32 | 2 vCPU/4 GB + 4 vCPU/8 GB | ~22 € | MVP-Launch, erste zahlende Nutzer | Parallel zu Build-Phase 1–4 |
| **Phase 2** | + Database CX22 | 2 vCPU/4 GB | ~6 € | DB auslagern, bessere Isolation & Skalierung | Nach MVP-Stabilisierung |
| **Phase 3** | + Mail/Storage CX22 | 2 vCPU/4 GB | ~6 € | Postfix, Upload-Storage, Backups isolieren | Bei Wachstum > 50 Vermietern |

**Software-Build ist weitgehend unabhängig von der Server-Phase:** Das Docker-Compose-Setup ist von Anfang an mehrere Services bereit (Frontend, Backend, Postgres, Redis, Postfix), kann aber zunächst auf einem CX32 laufen. Die spätere Aufteilung auf mehrere Server ist eine Konfigurations-/Netzwerk-Anpassung, kein Rewrite.

---

## 3. Software-Build-Phasen im Detail

### Phase 0: Projekt-Fundament & Dev-Umgebung

**Ziel:** Entwicklungs-Umgebung läuft; jeder weitere Build-Schritt hat eine gemeinsame Basis.

**Backend:**
- Projektstruktur anlegen (`backend/app/...`, `backend/tests/`, `alembic/`)
- `Dockerfile` für FastAPI
- `requirements.txt` mit FastAPI, SQLAlchemy 2.x, Alembic, Pydantic, python-jose, passlib, argon2-cffi, python-multipart, redis, asyncpg, cryptography, pyotp, httpx
- `docker-compose.yml` + `docker-compose.dev.yml`
- `config.py` mit Pydantic-Settings (`.env` Unterstützung)
- `database.py` mit SQLAlchemy AsyncSession + PostgreSQL-Verbindung
- Alembic initialisieren
- Health-Check-Endpunkt `/health`

**Frontend:**
- Vue.js 3 Projekt anlegen (`frontend/src/`, `frontend/public/`, `frontend/Dockerfile`)
- Vite + Vue Router + Pinia + Tailwind CSS + Axios
- Basis-Layout, Navigation, Theme (Apple-Style)
- API-Client mit zentralem Axios-Instance

**DevOps:**
- Git-Repository initialisieren
- `.gitignore`, `.env.example`
- Hot-Reload für Backend/Frontend in Dev
- Makefile oder Taskfile mit `make dev`, `make test`, `make migrate`

**Milestone:** `docker compose up` startet alle Services; `/health` liefert `ok`.

**Aufwand:** 3–4 PT

**Verifikation:**
- [ ] `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d` läuft ohne Fehler
- [ ] `curl http://localhost:8000/health` → `{"status":"ok"}`
- [ ] Frontend ist unter `http://localhost:8080` erreichbar
- [ ] Alembic kann Migrationen ausführen: `alembic upgrade head`

---

### Phase 1: Auth, Rollen, 2FA, Security, Audit

**Ziel:** Sicherer Login für Vermieter und Mieter; alle späteren Endpunkte sind geschützt.

**Backend:**
- `users`-Tabelle + `vermieter_profile`
- Passwort-Hashing mit Argon2id
- JWT: Access-Token 15 min, Refresh-Token 7 Tage in HTTP-only Secure Cookie
- 2FA: TOTP (QR-Code) + E-Mail-Code-Fallback (6-stellig, 15 min gültig)
- Rollenprüfung (`vermieter`, `mieter`) in jeder Route
- DSGVO-Einwilligung bei Registrierung (Checkbox, Timestamp, Version)
- Audit-Log-Tabelle: `auth_events` (Login, Logout, 2FA, Passwort-Reset, Export, Löschung)
- Rate-Limiting (Redis-basiert) für Login/Registrierung/Upload
- Security-Headers-Middleware
- CSRF-Token für state-changing Requests
- `crypto.py` mit AES-256-GCM für Feld-Verschlüsselung (IBAN, Steuernr, Geburtsdatum)

**Frontend:**
- Login-Seite
- Registrierung mit Einwilligung
- 2FA-Setup (QR-Code, Backup-Codes)
- E-Mail-Code-Fallback-Seite
- Passwort-Reset-Flow
- Auth-Store (Pinia) mit Token-Refresh
- Rollen-basierte Navigation (Vermieter vs. Mieter)

**Milestone:** Registrierung → Login → 2FA → geschütztes Dashboard-Layout.

**Aufwand:** 8–10 PT

**Abhängigkeiten:** Phase 0

**Verifikation:**
- [ ] Unit-Tests: Argon2-Hashing, JWT-Erzeugung/-Validierung, TOTP-Generierung
- [ ] Integrationstest: Registrierung → E-Mail-Code-Login → Token gültig
- [ ] Sicherheitstest: Ungültiger Token → 401; Refresh-Token-Reuse → Verweigerung
- [ ] Audit-Log enthält alle Auth-Events
- [ ] Frontend: 2FA-QR-Code wird gerendert; Login-Flow durchspielbar

---

### Phase 2: Domain-Core — Objekte, Einheiten, Mieter, Vermieter-Profil

**Ziel:** Kerndatenmodell steht; Vermieter kann seine Objekte und Mieter verwalten.

**Backend:**
- SQLAlchemy-Modelle: `objekte`, `einheiten`, `mieter`
- Row-Level Security (RLS) Policies für `vermieter_id`
- CRUD-Endpunkte für Objekte und Einheiten
- CRUD-Endpunkte für Mieter (inkl. Status: aktiv/beendet/bewerbung)
- Mieter-Login erstellen (User anlegen + Einheit zuweisen)
- Feld-Verschlüsselung für `mieter.geburtsdatum`
- Validierungen: PLZ, Mietbeginn < Mietende, Kaltmiete > 0

**Frontend:**
- Vermieter-Portal: Dashboard-Layout
- Objekt-Liste, Objekt-Detail, Objekt anlegen/bearbeiten
- Einheiten-Liste pro Objekt, Einheit anlegen/bearbeiten
- Mieter-Liste, Mieter anlegen/bearbeiten, Login erstellen
- Mieter-Portal: Meine Daten (read-only Stammdaten)

**Milestone:** Vermieter kann 1 Objekt mit Einheiten und Mietern anlegen; Mieter sieht seine Daten.

**Aufwand:** 6–8 PT

**Abhängigkeiten:** Phase 1

**Verifikation:**
- [ ] RLS-Test: Vermieter A sieht nur eigene Objekte/Einheiten/Mieter
- [ ] Mieter sieht nur seine eigene Einheit
- [ ] End-to-End: Objekt anlegen → Einheit hinzufügen → Mieter anlegen → Mieter-Login funktioniert
- [ ] Feld-Verschlüsselung: `geburtsdatum` ist in DB verschlüsselt, in API entschlüsselt

---

### Phase 3: Dokumenten-Management & Upload

**Ziel:** Dateien können sicher hochgeladen, verschlüsselt gespeichert und rollenbasiert freigegeben werden.

**Backend:**
- `dokumente`-Tabelle (metadaten + Sichtbarkeit)
- Upload-Endpunkt mit Datei-Validierung (Typ: PDF/JPG/PNG, max 10 MB, Magic-Bytes)
- AES-256 at-rest Verschlüsselung im Upload-Verzeichnis
- Ordnerstruktur: `objekte/{id}/`, `mieter/{id}/`, `belege/{objekt_id}/`, `generiert/{mieter_id}/`
- Sichtbarkeit: `vermieter`, `mieter`, `beide`, `handwerker`
- `dokument_freigaben`-Tabelle für gezielte Freigaben
- Download-Endpunkt mit Entschlüsselung + Rollenprüfung
- Löschung mit Audit-Log

**Frontend:**
- Upload-Komponente (Drag & Drop, Fortschritt)
- Dokumenten-Galerie pro Objekt/Einheit/Mieter
- Sichtbarkeit auswählen
- Download-Button
- Lösch-Button (Vermieter)

**Milestone:** Vermieter und Mieter können Dokumente hochladen; Mieter sieht nur freigegebene Dokumente.

**Aufwand:** 5–7 PT

**Abhängigkeiten:** Phase 2

**Verifikation:**
- [ ] Datei wird verschlüsselt auf Disk geschrieben; Rohdatei nicht lesbar
- [ ] Download liefert Original-Datei zurück
- [ ] Mieter sieht nur Dokumente mit Sichtbarkeit `mieter` oder `beide`
- [ ] Upload über 10 MB wird abgewiesen
- [ ] Falscher MIME-Type (z. B. `.exe` als `.pdf`) wird durch Magic-Bytes erkannt

---

### Phase 4: Ticket-System

**Ziel:** Mieter kann Störungen melden; Vermieter kann verwalten; KI kann vorgeschaltet werden.

**Backend:**
- `tickets`-Tabelle (`ticket_nr` wie `TKT-2026-001`, Kategorie, Priorität, Status)
- `ticket_kommentare`-Tabelle
- CRUD-Endpunkte (Mieter darf nur eigene Tickets erstellen/lesen)
- Ticketnummer-Generierung (Jahr + fortlaufend pro Vermieter)
- Status-Workflow: offen → in_bearbeitung → erledigt → geschlossen
- E-Mail-Trigger bei neuem Ticket / Statusänderung (vorerst per Log/Stub, E-Mail-Service folgt in Phase 6)

**Frontend:**
- Mieter-Portal: Ticket erstellen, Ticket-Liste, Ticket-Detail mit Kommentaren
- Vermieter-Portal: Alle Tickets, Filter, Ticket-Detail, Status ändern, kommentieren

**Milestone:** Mieter erstellt Ticket `TKT-2026-001`; Vermieter bearbeitet es.

**Aufwand:** 5–6 PT

**Abhängigkeiten:** Phase 2 (Phase 3 optional, aber Dokumente an Tickets später nachrüstbar)

**Verifikation:**
- [ ] Ticket-Nummer ist eindeutig pro Vermieter/Jahr
- [ ] Mieter kann nur eigene Tickets sehen
- [ ] Status-Änderung ist erlaubt nur für Vermieter
- [ ] Kommentare werden chronologisch geladen

---

### Phase 5: Kosten & Nebenkostenabrechnung

**Ziel:** Vermieter erfasst Kosten; System erstellt NK-Abrechnung pro Einheit.

**Backend:**
- `kosten`-Tabelle (Kategorie, Betrag, Datum, umlagefähig, Umlageart)
- `mietzahlungen`-Tabelle
- Erfassungs-Endpunkte für Kosten und Mietzahlungen
- Umlage-Logik: nach qm (Standard), nach Personen, nach Verbrauch
- `abrechnungen`-Tabelle mit Gesamtkosten, Anteil, Vorauszahlungen, Ergebnis
- Abrechnung erstellen (Jahr + Einheit)
- Verteilungsberechnung lokal (reine Mathematik)
- Plausibilitätsprüfung (negative Beträge, Summe > 0)

**Frontend:**
- Kosten-Liste pro Objekt/Einheit, Kosten erfassen
- Mietzahlungen erfassen/markieren
- Abrechnungs-Übersicht pro Einheit
- Abrechnung starten → Vorschau

**Milestone:** Vermieter erfasst Heizkosten und erstellt eine NK-Abrechnung für eine Einheit.

**Aufwand:** 7–9 PT

**Abhängigkeiten:** Phase 2

**Verifikation:**
- [ ] Unit-Tests für Umlageberechnung (nach qm, nach Personen, nach Verbrauch)
- [ ] Abrechnungssumme stimmt mit Summe der Kosten überein
- [ ] Nicht-umlagefähige Kosten werden nicht verteilt
- [ ] Mieter sieht nur eigene Abrechnungen

---

### Phase 6: Dashboard & Kennzahlen

**Ziel:** Vermieter sieht Finanzkennzahlen pro Objekt/Einheit.

**Backend:**
- Berechnungs-Engine für:
  - Bruttomietrendite
  - Nettomietrendite
  - Eigenkapitalrendite (ROE)
  - Cash-on-Cash Return
  - Cashflow vor Steuern
  - DSCR
  - LTV
  - Gesamtrendite
- Finanzierungsfelder am Objekt (optional): Darlehen, Eigenkapital, Zinssatz, Tilgung
- Endpunkt `/dashboard/summary` und `/dashboard/object/{id}`
- Offene Tickets, fällige Mietzahlungen, anstehende Fristen

**Frontend:**
- Vermieter-Dashboard mit KPI-Cards
- Chart-Komponente (z. B. vue-chartjs) für Kostenentwicklung
- Objekt-Detail-Dashboard
- Einheiten-Übersicht mit Kennzahlen

**Milestone:** Dashboard zeigt korrekte Renditekennzahlen für ein Beispiel-Objekt.

**Aufwand:** 5–7 PT

**Abhängigkeiten:** Phase 5 (zumindest Mietzahlungen + Kosten)

**Verifikation:**
- [ ] Unit-Tests mit bekannten Eingaben: Bruttomietrendite = erwartet
- [ ] ROE/DSCR/LTV mit und ohne Finanzierungsdaten berechnen
- [ ] Mieter-Dashboard zeigt keine Finanzkennzahlen

---

### Phase 7: KI-Schicht — OCR, Anonymisierung, Ollama, KI-Dokumente

**Ziel:** KI-Features sind DSGVO-konform angebunden; Dokumente werden verarbeitet.

**Backend:**
- Tesseract + PyMuPDF Integration
- OCR-Service für PDF/JPG/PNG
- Anonymisierungs-Engine mit Regex-Regeln + Mapping
- Deanonymisierung mit Mapping-Tabelle
- Ollama Cloud API-Client (GLM 5.2 + Kimi K2.6)
- Keyword-Classifier für Ticket-Kategorien
- Prompt-Templates in `services/ki/prompts.py`
- Redis-Cache für KI-Aufrufe
- Audit-Log für alle KI-Aufrufe (anonymisierter Prompt, Modell, Zeitstempel)
- Health-Check für KI-Verfügbarkeit
- Regelbasierte Fallbacks

**KI-Use-Cases im MVP:**
1. Ticket-Auto-Kategorisierung (Keyword → ggf. GLM)
2. Ticket-Priorität (Keyword/GLM)
3. Antwort-Entwurf für Vermieter (GLM)
4. Dokument-Klassifikation (GLM)
5. Beleg-Scan: Betrag + Kategorie + Umlagefähigkeit (OCR + GLM)
6. Abrechnungserklärungstext (GLM)
7. Mahnung Stufe 1–3 (GLM)
8. Mieterhöhung § 558 BGB (Kimi K2.6)
9. Mieter-Bewerbung: Ausweis-Daten extrahieren (OCR → Bild löschen), Lohnabrechnung Netto extrahieren, Schufa strukturieren (GLM)
10. Smart Insights (Kimi K2.6, täglich)

**Frontend:**
- "KI-Assistent"-UI für Ticket-Antwort-Entwürfe (Vorschlag + Akzeptieren/Bearbeiten)
- Beleg-Scan-UI (Foto hochladen → Vorschlag der extrahierten Felder)
- Dokumenten-Klassifikations-Indikator
- KI-Generierte Dokumente: Auswahl Template → Vorschau → PDF generieren
- Mieter-Bewerbungs-Formular mit Upload-Feldern

**Milestone:** Ausweis-Bild wird hochgeladen → OCR extrahiert Name → Bild wird gelöscht → Vermerk gespeichert; Mahnung wird KI-generiert und als PDF exportiert.

**Aufwand:** 12–15 PT

**Abhängigkeiten:** Phase 3, Phase 4, Phase 5

**Verifikation:**
- [ ] Anonymisierungstest: Personendaten werden vor KI-Aufruf ersetzt
- [ ] Deanonymisierungstest: Platzhalter werden korrekt zurückersetzt
- [ ] Ausweis-Bild ist nach OCR nicht mehr im Upload-Speicher
- [ ] Keyword-Classifier deckt > 60 % der Test-Tickets korrekt ab
- [ ] KI-Health-Check erkennt Ausfall und schaltet Fallbacks ein
- [ ] Audit-Log enthält alle KI-Aufrufe ohne Personendaten

---

### Phase 8: E-Mail, Mahnungen, Fristen-Warner

**Ziel:** Automatisierte Kommunikation und Fristen-Überwachung.

**Backend:**
- Postfix in Docker
- E-Mail-Service mit Jinja2-HTML-Templates
- SMTP-Versand über Postfix
- E-Mail-Events: Registrierung, Willkommen Mieter, neues Ticket, Ticket-Antwort, Statusänderung, 2FA-Code, Passwort-Reset, Abrechnung, Mahnung, Frist-Warnung
- Mahn-Workflow (Tag 3/7/14/21 nach fälliger Miete)
- Fristen-Check täglich per Cron/Scheduler:
  - Mietende in 6/3/1 Monaten
  - Kündigungsfristen
  - Abrechnungsfristen (1 Jahr nach Mietende)
- Scheduler-Job (APScheduler oder eigener Celery-Worker; im MVP reicht APScheduler im Backend)

**Frontend:**
- E-Mail-Vorlagen-Admin (optional MVP-lite: nur Backend-Templates)
- Mahnungs-Übersicht: offene Mieten, vorgeschlagene Stufen
- Fristen-Kalender für Vermieter
- Benachrichtigungs-Einstellungen

**Milestone:** Fällige Miete löst am Tag 7 Mahnung Stufe 1 aus; Mieter erhält E-Mail mit PDF.

**Aufwand:** 6–8 PT

**Abhängigkeiten:** Phase 4 (Tickets), Phase 5 (Mietzahlungen), Phase 7 (KI-Texte)

**Verifikation:**
- [ ] E-Mail-Versand in Dev geht an Mailhog; Produktion an Postfix
- [ ] Mahn-Workflow wird täglich getriggert und nur bei fälligen Mieten ausgeführt
- [ ] Fristen-Warnungen werden korrekt berechnet
- [ ] E-Mail enthält korrekten Absender, Antwortadresse und DSGVO-Impressum

---

### Phase 9: PDF-Export & Templates

**Ziel:** Dokumente und Abrechnungen werden als PDF mit Briefkopf exportiert.

**Backend:**
- WeasyPrint-Integration
- Jinja2-Templates für Briefkopf (Vermieter-Logo, Adresse, Bankdaten)
- 10 statische Vorlagen:
  1. Wohnungsgeberbestätigung
  2. Meldebescheinigung
  3. Übergabeprotokoll Einzug
  4. Übergabeprotokoll Auszug
  5. Kaution-Abrechnung
  6. Nebenkostenabrechnung (Zahlen-Template)
  7. Standard-Mietvertrag
  8. Einzugsbestätigung
  9. Auszugsbestätigung
  10. Schufa-Einverständnis
- 8 KI-generierte Dokumente:
  1. Mahnung Stufe 1
  2. Mahnung Stufe 2
  3. Mahnung Stufe 3
  4. Mieterhöhung § 558 BGB
  5. Abmahnung
  6. Kündigung
  7. Abrechnungserklärungstext
  8. Individuelles Anschreiben
- PDF-Download-Endpunkt

**Frontend:**
- "Dokument generieren"-Dialog pro Einheit/Mieter
- Vorschau des generierten PDFs
- Download/Senden-Buttons

**Milestone:** Wohnungsgeberbestätigung wird mit Vermieter-Briefkopf als PDF generiert.

**Aufwand:** 5–7 PT

**Abhängigkeiten:** Phase 3 (Dokumente), Phase 7 (KI), Phase 8 (E-Mail)

**Verifikation:**
- [ ] Generiertes PDF enthält korrekten Briefkopf und alle Variablen
- [ ] KI-generierte Mahnung enthält korrekte Fristen und Beträge
- [ ] PDF ist im Dokumenten-Storage abgelegt und als Dokument verknüpft
- [ ] PDF-Rendering ist DSGVO-konform (keine ungewollten Personendaten)

---

### Phase 10: DSGVO, IP-Blocking, Compliance, Hardening

**Ziel:** App ist datenschutzkonform und produktionsreif gehärtet.

**Backend:**
- DSGVO-Export (Art. 15): ZIP mit DB-Daten + Dokumenten des Nutzers
- DSGVO-Löschung (Art. 17): Account + Daten löschen, Aufbewahrungsfristen beachten (Mietvertragsdaten 10 J, Abrechnungen 6 J)
- Einwilligungs-Historie
- Vollständiges Audit-Log
- AVV-Verzeichnis (Dokumentation)
- IP-Blocking: MaxMind GeoLite2, nur DE/AT/CH + Whitelist
- nginx GeoIP-Konfiguration
- Security-Headers (HSTS, CSP, X-Frame-Options, X-Content-Type, Referrer)
- Fail2Ban für SSH/nginx
- Docker-Hardening: non-root, read-only, cap_drop, interne Netzwerke
- Backup-Skript (`scripts/backup.sh`)
- Restore-Skript (`scripts/restore.sh`)
- Health-Check-Skript (`scripts/health-check.sh`)

**Frontend:**
- Datenschutz-Einstellungen (Export anfordern, Account löschen)
- Impressum/DSGVO-Seiten
- Cookie-/Einwilligungs-Dialog

**Milestone:** Datenschutz-Export liefert vollständige Nutzerdaten; nicht-DACH-IP wird blockiert.

**Aufwand:** 6–8 PT

**Abhängigkeiten:** Alle vorherigen Phasen

**Verifikation:**
- [ ] DSGVO-Export enthält alle Daten des authentifizierten Nutzers
- [ ] Löschung löscht/sofort-anonymisiert gemäß Aufbewahrungsfristen
- [ ] Aufruf aus Nicht-DACH-Land → 403
- [ ] Security-Header sind in nginx gesetzt
- [ ] Backup läuft und lässt sich auf Dev-DB wiederherstellen
- [ ] Penetrationstest-Light: SQL-Injection, XSS, Auth-Bypass

---

### Phase 11: Production Deployment & Stabilisierung

**Ziel:** MVP läuft produktiv auf Hetzner Phase-1-Servern.

**Backend/Frontend:**
- Produktions-Builds
- `.env.production`
- CloudPanel/NGINX Reverse Proxy Konfiguration
- SSL via Let's Encrypt
- DNS-Einträge (A-Record, MX, SPF, DKIM, DMARC)
- Docker-Compose-Override für Produktion
- Migrationen in Produktion ausführen
- Monitoring/Alerting (Prometheus + Alertmanager, falls in ops/ gewünscht; sonst einfacher Cron-Health-Check)

**DevOps:**
- Deployment-Skript `scripts/deploy.sh`
- Rollback-Plan
- Load-Test mit kleinem Datensatz
- Dokumentation für Betrieb

**Milestone:** `https://mietverwaltung.de` ist erreichbar; erste Test-Registrierung funktioniert.

**Aufwand:** 4–6 PT

**Abhängigkeiten:** Phase 10

**Verifikation:**
- [ ] Produktive URL liefert Frontend
- [ ] `/api/health` liefert `ok`
- [ ] SSL-Labs-Test zeigt A+
- [ ] E-Mail wird korrekt zugestellt (nicht im Spam)
- [ ] Rollback-Skript funktioniert in unter 5 Minuten
- [ ] Smoke-Test mit 5 Beispiel-Vermietern und je 1 Objekt + Mieter

---

## 4. Aufwandsübersicht

| Phase | Backend (PT) | Frontend (PT) | DevOps/Security (PT) | QA/Tests (PT) | Gesamt (PT) |
|-------|--------------|---------------|------------------------|---------------|-------------|
| 0 — Fundament | 2 | 1 | 1 | 0,5 | **3,5–4** |
| 1 — Auth/Security | 6 | 2,5 | 1 | 1 | **10–10,5** |
| 2 — Domain-Core | 4 | 2 | 0,5 | 1 | **7,5** |
| 3 — Dokumente | 3,5 | 1,5 | 0,5 | 1 | **6,5** |
| 4 — Tickets | 3 | 2 | 0,5 | 0,5 | **6** |
| 5 — Kosten/Abrechnung | 5 | 2 | 0,5 | 1,5 | **9** |
| 6 — Dashboard | 2,5 | 2,5 | 0,5 | 1 | **6,5** |
| 7 — KI-Schicht | 8 | 3 | 1 | 2 | **14** |
| 8 — E-Mail/Mahnung/Fristen | 4 | 1,5 | 1 | 1 | **7,5** |
| 9 — PDF/Templates | 3 | 2 | 0,5 | 1 | **6,5** |
| 10 — DSGVO/Blocking/Hardening | 3 | 1,5 | 2 | 1,5 | **8** |
| 11 — Production Deploy | 1 | 1 | 2,5 | 1 | **5,5** |
| **Summe** | **45** | **22** | **11,5** | **12,5** | **~90 PT** |

**Annahmen:**
- 1 Personentag (PT) = 6–8 effektive Arbeitsstunden
- Ein erfahrener Full-Stack-Entwickler mit Python/FastAPI + Vue.js
- Keine externe Abhängigkeit auf Design/UX/QA
- Ollama Cloud API ist verfügbar und dokumentiert
- Tesseract/PyMuPDF/WeasyPrint laufen in Container ohne große Probleme

**Realistische Gesamtdauer:** Bei 100 % Fokus ca. 4–5 Monate (inkl. Puffer für rechtliche Reviews, KI-Feinjustierung, Bugfixing).

---

## 5. Abhängigkeitsgraph

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

**Wichtige Abhängigkeiten:**
- Phase 7 (KI) braucht Phase 3 (Dokumente), Phase 4 (Tickets) und Phase 5 (Kosten).
- Phase 8 (E-Mail/Mahnung) braucht Phase 4 (Tickets), Phase 5 (Mietzahlungen) und Phase 7 (KI-Texte).
- Phase 9 (PDF) braucht Phase 3 (Storage), Phase 7 (KI) und Phase 8 (Versand).
- Phase 10 (Compliance) ist der letzte Software-Block und greift auf alle vorherigen Features zurück.
- Phase 11 (Deploy) schließt alles ab.

**Parallelisierbare Arbeiten:**
- Phase 3 (Dokumente) und Phase 4 (Tickets) können parallel nach Phase 2 laufen.
- Phase 6 (Dashboard) kann parallel zu Phase 7 (KI) entwickelt werden, sobald Phase 5 fertig ist.
- Phase 9 (PDF/Templates) kann parallel zu Phase 8 (E-Mail) laufen, sobald Phase 7 fertig ist.

---

## 6. Backend vs. Frontend pro Phase

| Phase | Backend-Schwerpunkt | Frontend-Schwerpunkt |
|-------|---------------------|----------------------|
| 0 | Docker, FastAPI-Setup, DB, Alembic | Vue-Setup, Tailwind, Axios, Routing |
| 1 | Auth, JWT, 2FA, RLS, Audit, Verschlüsselung | Login, 2FA, Registrierung, Auth-Store |
| 2 | Objekt/Einheit/Mieter CRUD, Validierung, RLS | Vermieter-Portal, Objekt-/Mieter-Views, Mieter-Profil |
| 3 | Upload, Verschlüsselung at-rest, Sichtbarkeit, Download | Upload-Komponente, Dokumenten-Galerie |
| 4 | Ticket-Modell, Workflow, Kommentare, Ticketnummern | Ticket-Liste, Ticket-Detail, Status-Buttons |
| 5 | Kosten, Abrechnung, Umlage-Logik, Mietzahlungen | Kosten-Formulare, Abrechnungs-Vorschau |
| 6 | Kennzahlen-Engine, Dashboard-Endpunkte | Dashboard-Cards, Charts |
| 7 | OCR, Anonymisierung, Ollama-Client, Prompts, Cache | KI-Vorschläge, Beleg-Scan, Bewerbungs-Upload |
| 8 | Postfix, E-Mail-Service, Mahn-Workflow, Scheduler | Mahnungs-Übersicht, Fristen-Kalender |
| 9 | WeasyPrint, Jinja2-Templates, PDF-Endpunkte | Dokument-Generator, PDF-Vorschau |
| 10 | DSGVO-Export/Löschung, GeoIP, Hardening, Backup | Datenschutz-Seiten, Impressum |
| 11 | Produktions-Build, Migrations-Skripte, nginx | Production-Optimierung, PWA-Manifest |

---

## 7. Testing & Verifikation pro Phase

**Testpyramide:**
- **Unit-Tests** (pytest / vitest): Geschäftslogik, Berechnungen, Anonymisierung, Validierung
- **Integrationstests** (pytest + TestClient / Playwright): API-Endpunkte, Auth-Flow, Datei-Upload
- **End-to-End-Tests** (Playwright): Kritische User-Journeys (Registrierung → Objekt → Mieter → Ticket → Abrechnung)
- **Sicherheitstests** (manuell + automatisiert): RLS, Auth-Bypass, XSS, SQL-Injection, GeoIP
- **Performance-/Load-Tests** (locust): Login, Dashboard, Datei-Download

**Phase-spezifische Testfokus:**

| Phase | Test-Schwerpunkt |
|-------|------------------|
| 0 | Container starten, Health-Check, Migrationen laufen |
| 1 | Passwort-Hashing, JWT-Lebensdauer, 2FA-Codes, RLS-Isolation, Rate-Limiting |
| 2 | CRUD-Rechte, Mieter-Login-Erstellung, Datenisolation |
| 3 | Datei-Verschlüsselung, Magic-Bytes, Sichtbarkeit, Download-Rechte |
| 4 | Ticket-Workflow, Ticketnummern, Kommentar-Rechte |
| 5 | Umlageberechnung, Abrechnungs-Summen, Plausibilität |
| 6 | Kennzahlen-Formeln, Dashboard-Daten korrekt |
| 7 | Anonymisierung/Deanonymisierung, OCR-Genauigkeit, KI-Fallback, Bild-Löschung |
| 8 | E-Mail-Zustellung, Mahn-Workflow-Timing, Fristenberechnung |
| 9 | PDF-Rendering, Variablen-Ersetzung, Briefkopf korrekt |
| 10 | DSGVO-Export-Vollständigkeit, GeoIP-Blocking, Backup-Restore, Security-Header |
| 11 | Produktions-Smoke-Test, Rollback, SSL-Test, DNS/MX-Einträge |

**Definition of Done pro Phase:**
- Alle neuen Unit-/Integrationstests grün
- Keine bekannten Sicherheitslücken in der Phase
- Code-Review abgeschlossen
- Dokumentation aktualisiert (API-Docs, README, Betriebshandbuch)
- Feature in Dev-Umgebung manuell durchgespielt

---

## 8. Risiken & offene Punkte

| Risiko | Wahrscheinlichkeit | Auswirkung | Gegenmaßnahme |
|--------|-------------------|------------|---------------|
| Ollama Cloud API-Limit / Ausfall | Mittel | Hoch | Regelbasierte Fallbacks, Caching, Health-Check |
| Tesseract OCR für handschriftliche Belege ungenau | Hoch | Mittel | KI-Nachbearbeitung, manuelle Korrektur-UI |
| DSGVO-rechtliche Unsicherheit bei KI-Dokumenten | Mittel | Hoch | Immer "Bitte rechtlich prüfen lassen" hinzufügen, keine autom. Entscheidungen |
| MaxMind GeoLite2 Lizenz/Verfügbarkeit | Niedrig | Mittel | Alternative GeoIP-DB oder IP-Whitelist-Fallback |
| WeasyPrint CSS-Rendering in Docker | Mittel | Mittel | Frühes Docker-Testing, stabile Base-Images |
| Postfix Reputation/Deliverability | Mittel | Hoch | DKIM/SPF/DMARC, Mailgun/SendGrid als Fallback prüfen |
| Row-Level Security Performance | Niedrig | Mittel | Indexe auf `vermieter_id`/`mieter_id`, SQLAlchemy-Test |
| Frontend-Komplexität wächst schnell | Hoch | Mittel | Strikte Komponenten-Struktur, Storybook später |

---

## 9. Nächste Schritte (Empfohlene Aktionen)

1. **Phase 0 starten:** Projektstruktur, Docker-Compose, Dev-Umgebung aufsetzen.
2. **Entscheidung:** Domain kaufen (`mietverwaltung.de` oder Alternative) und Hetzner-Account bereitstellen.
3. **Ollama Cloud API-Key beschaffen** und Testquota klären.
4. **MaxMind GeoLite2-Account** anlegen und Download-Prozess etablieren.
5. **Rechtlichen Disclaimer** für KI-generierte Dokumente finalisieren (immer "Bitte rechtlich prüfen lassen").
6. **Git-Repository** anlegen und ersten Commit machen.
7. **Backlog/Tracking-Tool** wählen (z. B. GitHub Issues) für die Phasen.

---

**Plan erstellt am:** 2026-10-27
**Autor:** Hermes Agent (Software-Architektur)
**Status:** Plan-Modus, bereit für Implementation
