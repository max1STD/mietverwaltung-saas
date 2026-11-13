# Pre-Build Architektur-Review: Build Plan v2 vs. Current State (v4)

> **Datum:** 13. November 2026  
> **Review-Objekt:** `2026-10-28_build-plan-v2.md` (399 Zeilen)  
> **Current State:** DB-Schema v4 (33 Tabellen), WE-basiertes Pricing (9,75 €/WE), kein Free-Plan, 14-Tage-Trial mit Kreditkarte, Native Dev (kein Docker), Resend statt Postfix, Proxmox MVP + Hetzner Go-Live.

---

## Zusammenfassung

Build Plan v2 ist **fundamental veraltet** und darf nicht 1:1 ausgeführt werden. Er verweist durchgehend auf DB-Schema v2 (22 Tabellen) und die alte Plan-Pyramide (Free/Basis/Pro/Business mit 14,90/29,90/49,90 €), während das Projekt bereits auf Schema v4 (33 Tabellen) und WE-basiertes Pricing (9,75 €/WE) umgestellt ist. Zudem wurde die Dev-Strategie von Docker auf Native Dev geändert. Die Phasenstruktur ist großteilig noch brauchbar, aber Subscription/Stripe-Billing, das zentrale Onboarding, Mieter-Bewerbung und der Admin-Center fehlen als eigenständige Phasen vollständig. Die Zeitschätzungen unterschätzen den Mehraufwand durch v4 (+11 Tabellen), Native Dev und Stripe-Integration.

**Empfehlung:** Build Plan v3 schreiben, bevor Phase 0 startet.

---

## 1. Discrepanzen: Outdated Schema / Pricing / Annahmen

### 1.1 DB-Schema v2 statt v4

| Stelle im Build Plan v2 | Geplanter Stand v2 | Aktueller Stand v4 | Bewertung |
|-------------------------|-------------------|--------------------|-----------|
| Zeile 16 | "DB-Schema v2 — 22 Tabellen" | **v4 mit 33 Tabellen** | ❌ Kritisch: ganze Datenbasis falsch |
| Zeile 47, 50, 63, 96, 99, 121, 139, 159, 161, 162, 237, 239 | Tabellen wie `mietvertraege`, `abrechnung_positionen`, `events`, `notifications`, `fristen`, `kostenkategorien`, `user_sessions`, `einwilligungen` werden als v2-Neuheiten geframed | Sind in v4 bereits enthalten; zusätzlich fehlen `subscriptions`, `plan_usage`, `bankverbindungen`, `mieter_historie`, `einheit_ausstattung`, `bewerbungen`, `ticket_sla`, `ticket_trigger`, `onboarding_progress`, `ai_stored_results`, `referrals`, `handwerker` | ❌ Veraltet und unvollständig |
| Phase 0 Milestone | "Alembic-Migration erzeugt alle 22 Tabellen" | Müssen **33 Tabellen + 34 RLS-Policies + 92 Indizes** erzeugen | ❌ Milestone falsch |
| Phase 2 | `mietvertraege`, `mietvertrag_aenderungen`, `kostenkategorien` als Phase-2-Neuheiten | In v4 vorhanden, aber zusätzlich `mieter_historie`, `einheit_ausstattung`, `bewerbungen`, `bankverbindungen` nötig | ❌ Unvollständig |
| Phase 5 | `abrechnung_positionen` als Neuheit geframed | In v4 vorhanden, aber `abrechnungen.einheit_id` und UNIQUE-Constraint pro Einheit/Jahr fehlen im Plan | ⚠️ Semantik nicht aktualisiert |

### 1.2 Pricing-Model veraltet

| Stelle | Build Plan v2 / v2-Schema-Doku | Aktueller Stand v3/v4 | Bewertung |
|--------|--------------------------------|----------------------|-----------|
| Zeile 18 | "Free 0 € (2 Wohnungen) / Basis 14,90 € (5 WE) / Pro 29,90 € (25 WE) / Business 49,90 € (∞)" | **Kein Free-Plan; WE-basiert 9,75 €/WE (1–5 WE), 7,50 €/WE (6–25 WE), 5,90 €/WE (26–49 WE), ab 50 WE Anfrage** | ❌ Kritisch |
| Zeile 23 | "Free-Tier 2 Wohnungen" | **Free-Plan entfernt**; 14-Tage-Trial mit Kreditkarte | ❌ Kritisch |
| Zeile 104 | "Wohnungs-Limit-Prüfung pro Plan (Free 2 / Basis 5 / Pro 25 / Business ∞)" | Prüfung auf **tatsächliche WE-Anzahl gegen `subscriptions` + `plan_usage`**; Preisstaffel statt fester Pläne | ❌ Kritisch |
| Zeile 106 | "Plan-Management: Upgrade/Downgrade, Add-ons (Extra Wohnung 1 €)" | **Keine festen Pläne mehr**; stattdessen pro-WE-Abrechnung, Abo-Widget live im Dashboard | ❌ Kritisch |
| Zeile 110 | "Plan-Anzeige: 'Wohnungen: 3/5 (Basis)'" | Muss z. B. "7 Wohnungen · 51,75 €/Monat" anzeigen | ❌ Veraltet |
| v4-Schema-Doku Zeile 1094 ff. | Noch alte Plan-Limits in `subscriptions` (free/basis/pro/business mit 14,90/29,90/49,90 €) | Widerspricht dem aktuell beschlossenen WE-Modell | ⚠️ Auch Schema-Doku ist hier nicht konsistent — Build Plan v3 muss die Quelle der Wahrheit definieren |

### 1.3 Technologie- & Hosting-Annahmen veraltet

| Stelle | Build Plan v2 | Aktueller Stand | Bewertung |
|--------|---------------|-----------------|-----------|
| Phase 0, Zeile 47–49 | Dockerfile, docker-compose.yml, docker-compose.dev.yml | **Native Dev**: Kein Docker auf Server; Backend `uvicorn`, Frontend `npx vite`, PostgreSQL 17 nativ, Redis ggf. optional/nachinstallieren | ❌ Kritisch für Phase 0 |
| Phase 0, Zeile 61 | `make dev` startet Docker Compose | Muss stattdessen Native-Dev-Skripte starten | ❌ Kritisch |
| Phase 8, Zeile 235 | "Postfix in Docker" | **Resend** (Transactional E-Mail-Service) statt eigener Mailserver | ❌ Kritisch (Deliverability) |
| Phase 10, Zeile 278 | "Fail2Ban, Docker-Hardening" | Docker-Hardening entfällt; Native-Hardening + systemd + SOPS/age nötig | ❌ Kritisch |
| Phase 11, Zeile 293 | "CloudPanel/nginx Reverse Proxy" | Laut Skill: **nginx**, kein CloudPanel; Proxmox-MVP mit Cloudflared-Tunnel | ⚠️ Anpassen |
| Phase 11, Zeile 293 | "Docker-Compose-Override für Produktion" | Produktion soll über GitHub Actions + SSH + native Services laufen; Docker-Override nicht mehr primär | ❌ Kritisch |
| Phase 0, Zeile 48 | Python 3.13 | ARCHITECTURE.md spricht von Python 3.12; Version klären | ⚠️ Inkonsistent |

### 1.4 Security & Compliance-Lücken im Plan

| Stelle | Build Plan v2 | Aktueller Stand / Anforderung | Bewertung |
|--------|---------------|-------------------------------|-----------|
| Phase 1, Zeile 82 | Feld-Verschlüsselung: IBAN, Steuernr, Geburtsdatum | v4 legt `bankverbindungen.iban_enc` und `mieter.birth_date_enc` fest; Steuernummer nicht als separate Spalte in v4 definiert | ⚠️ Prüfen/ergänzen |
| Phase 1 | Session-Management, Audit-Logs | v4 hat `user_sessions`, `audit_logs`, `einwilligungen` — passt grob, aber Mieter-RLS-Policies fehlen im Plan | ⚠️ Unvollständig |
| Phase 10 | DSGVO-Export, Löschung, VVT, AVV | Skill fordert zusätzlich: PII-Filter-Middleware, structlog, definierte Log-Aufbewahrung, Admin-Center mit Impersonate-Audit | ⚠️ Erweitern |
| Fehlend | — | Admin-Center für interne Verwaltung (Vermieter sperren, KI-Kosten, Stripe-Refunds, Feature-Flags) | ❌ Fehlt komplett |

---

## 2. Ist die Phasen-Reihenfolge noch korrekt?

**Grundstruktur bleibt gültig:** Foundation → Auth → Domain-Core → Dokumente/Tickets (parallel) → Finanzen → Dashboard → KI → Kommunikation → PDF → Compliance → Deploy.

### 2.1 Bewertung pro Übergang

| Übergang | Bewertung | Begründung |
|----------|-----------|------------|
| 0 → 1 | ✅ OK | Foundation muss zuerst kommen. |
| 1 → 2 | ✅ OK | Auth/Security vor Domänendaten. |
| 2 → 3 / 2 → 4 | ✅ OK | Dokumente und Tickets können parallel nach Domain-Core laufen. |
| 2 → 5 | ✅ OK | Kosten/Abrechnung braucht Objekte/Einheiten. |
| 5 → 6 | ✅ OK | Dashboard braucht Finanzdaten. |
| 3/4/5 → 7 | ✅ OK | KI braucht Dokumente, Tickets und Kosten als Input. |
| 7 → 8 | ⚠️ **Verkürzt** | E-Mail/Mahnung braucht nicht nur KI, sondern auch `mietzahlungen` (Phase 5) und Subscription-Status für Trial-Ablauf. |
| 8 → 9 | ✅ OK | PDF braucht E-Mail-Trigger und Template-Daten. |
| 9 → 10 | ✅ OK | Compliance/Hardening kommt vor Deploy. |
| 10 → 11 | ✅ OK | Production Deploy zuletzt. |

### 2.2 Probleme mit der aktuellen Phasen-Reihenfolge

1. **Subscription/Billing fehlt als eigene Phase.** In v2 wird das Abo-Management nur in Phase 2 als Nebenaspekt erwähnt. Für WE-basiertes Pricing, Stripe-Trial mit Kreditkarte und automatische Abbuchung ist das unzureichend. Das Abo-System muss **vor oder spätestens parallel zu Phase 2** stehen, da bereits die Registrierung das Trial-Status-Handling erfordert.

2. **Onboarding ist keine Phase.** `onboarding_progress` (v4) und die "Setup-Checkliste" sind zentral für die 14-Tage-Trial-Conversion, aber im Build Plan nur implizit enthalten.

3. **Mieter-Bewerbung (bewerbungen-Tabelle) fehlt als Phase.** Sie ist im Skill explizit MVP, wird aber in v2 nur über `mieter` abgehandelt.

4. **Admin-Center fehlt komplett.** Für interne Verwaltung (Kundensperre, KI-Kosten, Stripe-Refunds, Audit) ist ein eigenständiges Admin-Portal nötig — idealerweise parallel zum Haupt-MVP.

---

## 3. Fehlende MVP-Features im Build Plan v2

### 3.1 Kritisch fehlend (blockieren MVP)

| Feature | Wo es hingehört | Warum es fehlt |
|---------|-----------------|----------------|
| **Stripe-Subscription & WE-basierte Abrechnung** | Neue Phase 1.5 oder integriert in Phase 1/2 | Nur in Phase 2 als "Plan-Management" erwähnt; fester Plan statt pro-WE |
| **14-Tage-Trial mit Kreditkarte (Netflix-Style)** | Phase 1 / Registrierung | v2 geht noch von Free-Plan / 30 Tage No-CC aus |
| **Account-Sperre nach Trial/Kündigung** | Phase 1 / Subscription | Kein Free-Fallback; Daten 30 Tage aufbewahren |
| **Onboarding-Checkliste + Progress-Tracking** | Phase 1 oder 2 | Tabelle `onboarding_progress` in v4, aber keine Phase |
| **Mieter-Bewerbung (Ausweis/Lohn/Schufa)** | Phase 2 (Domain-Core) | Tabelle `bewerbungen` in v4, im Skill MVP, im Plan nicht erwähnt |
| **Einheit-Ausstattung & Mieter-Historie** | Phase 2 | Tabellen `einheit_ausstattung`, `mieter_historie` in v4 |
| **Bankverbindungen (Vermieter + Mieter-Kaution)** | Phase 2/3 | Tabelle `bankverbindungen` in v4 |
| **Objekt-Foto-Upload (filesystem, nicht BYTEA)** | Phase 2/3 | v4 hat `foto_url`, nicht `objekt_foto_data` |
| **Ticket SLA & Trigger (Zammad-Pattern)** | Phase 4 | Tabellen `ticket_sla`, `ticket_trigger` in v4 |
| **Resend-E-Mail + Webhook-Handling** | Phase 8 | Plan nutzt Postfix |
| **Admin-Center (internes Tool)** | Eigene Phase / parallel | Nicht im Plan enthalten |
| **Structured Logging + PII-Filter** | Phase 0/1 | Skill explizit gefordert, Plan nicht erwähnt |

### 3.2 Wichtig, aber nicht MVP-blockierend

| Feature | Begründung |
|---------|------------|
| **Adress-Autocomplete** | Konzept-Dokument existiert; im Plan nicht explizit |
| **Form-Validation-Framework (24 Formulare)** | Konzept existiert; müsste in Phase 0/1 etabliert werden |
| **E-Rechnung (XRechnung/ZUGFeRD)** | Admin-Center-Anforderung, aber nicht im MVP-Build-Plan |
| **DATEV-Export / Anlage V** | Roadmap, aber heise-Must-Have |
| **Handwerker-Logins** | Schema vorhanden, aber als "später" gekennzeichnet |
| **PWA / Push-Benachrichtigungen** | Skill: PWA-fähig; Plan: nicht explizit |
| **Referral-Programm** | Tabelle `referrals` in v4, aber nicht im MVP-Scope |

---

## 4. Zeitabschätzungen: Realistisch?

### 4.1 Gesamtaufwand v2 vs. v4-Schätzung

| Komponente | v2-Schätzung | Realistisch für v4 + Native + Stripe | Delta |
|------------|--------------|----------------------------------------|-------|
| Phase 0 — Fundament | 3,5–4 PT | **6–9 PT** | +60–125 % |
| Phase 1 — Auth/Security | 11 PT | **12–15 PT** | +10–36 % |
| Phase 2 — Domain-Core | 8,5 PT | **12–16 PT** | +41–88 % |
| Phase 3 — Dokumente | 6,5 PT | **6–8 PT** | −8 bis +23 % |
| Phase 4 — Tickets | 6 PT | **7–10 PT** | +17–67 % |
| Phase 5 — Kosten/Abrechnung | 10 PT | **14–18 PT** | +40–80 % |
| Phase 6 — Dashboard | 6,5 PT | **7–9 PT** | +8–38 % |
| Phase 7 — KI-Schicht | 15 PT | **18–24 PT** | +20–60 % |
| Phase 8 — E-Mail/Mahnung/Fristen | 8,5 PT | **10–14 PT** | +18–65 % |
| Phase 9 — PDF/Templates | 6,5 PT | **6–8 PT** | −8 bis +23 % |
| Phase 10 — DSGVO/Hardening | 9 PT | **10–14 PT** | +11–56 % |
| Phase 11 — Production Deploy | 5,5 PT | **8–12 PT** | +45–118 % |
| **Subscription/Billing-Phase** | — | **+8–12 PT** | neu |
| **Admin-Center** | — | **+6–10 PT** | neu |
| **SUMME** | **~97 PT** | **~130–175 PT** | **+34–80 %** |

### 4.2 Begründung für höheren Aufwand

1. **+11 Tabellen in v4** erfordern mehr Modelle, Schemas, RLS-Policies, Services, Tests.
2. **Native Dev** ersetzt `docker compose up` durch Systemd-Services, fnm/Node, Python-Venv, PostgreSQL-Setup, Redis-Installation/Alternative.
3. **Stripe-Integration** (Subscription, Trial, Webhooks, Proration, Reconciliation-Cron, Missbrauchsschutz) ist komplexer als die alte "Plan-Management"-Box.
4. **WE-basiertes Pricing** erfordert Slider, Live-Kalkulation, Staffel-Logik, Anfrage-Workflow ab 50 WE.
5. **Resend statt Postfix** erfordert Webhook-Handling, Bounce-Logik, E-Mail-Status-Tracking.
6. **KI-Schicht** mit Presidio + OCR + 9 Use-Cases ist eher 18–24 PT als 15 PT.

---

## 5. Was muss für Build Plan v3 aktualisiert werden?

### 5.1 Konzept- & Datenbasis-Updates

- [ ] Alle Schema-Referenzen auf **v4 (33 Tabellen)** umstellen.
- [ ] Tabellenliste v4 in Phase 0 übernehmen (`subscriptions`, `plan_usage`, `bankverbindungen`, `mieter_historie`, `einheit_ausstattung`, `bewerbungen`, `ticket_sla`, `ticket_trigger`, `onboarding_progress`, `ai_stored_results`, `referrals`, `handwerker`).
- [ ] Preismodell komplett ersetzen: **WE-basiert 9,75 €/WE**, Staffelpreise, kein Free-Plan, 14-Tage-Trial mit Kreditkarte.
- [ ] `subscriptions`/`plan_usage` in v4 nicht mehr als Free/Basis/Pro/Business mit 14,90/29,90/49,90 € modellieren, sondern als pro-WE-Abo.

### 5.2 Neue Phasen / Phase-Änderungen

- [ ] **Neue Phase 1.5: Subscription & Stripe Billing**
  - Stripe Customer + Subscription + Checkout Session
  - Trial mit Kreditkarte
  - Webhook-Endpunkte (`checkout.session.completed`, `invoice.paid`, `invoice.payment_failed`, `customer.subscription.deleted`)
  - Reconciliation-Cron
  - WE-basierte Preisberechnung
  - Account-Sperre nach Trial/Kündigung
- [ ] **Phase 2 erweitern:** Mieter-Bewerbung, Einheit-Ausstattung, Mieter-Historie, Bankverbindungen, Objekt-Foto-Upload, WE-Limit-Prüfung.
- [ ] **Phase 4 erweitern:** Ticket SLA & Trigger.
- [ ] **Phase 0 umschreiben:** Native Dev statt Docker.
- [ ] **Phase 8 umschreiben:** Resend statt Postfix.
- [ ] **Phase 10/11 umschreiben:** Native-Hardening, systemd, nginx, SOPS/age, WAL-G.
- [ ] **Neue separate Phase oder Stream: Admin-Center** (parallel zum MVP sinnvoll).

### 5.3 Technische Details

- [ ] `make dev` muss Native-Dev-Services starten (Backend-venv, Frontend-vite, PostgreSQL prüfen, Redis optional).
- [ ] Dockerfiles optional beibehalten (z. B. für CI-Tests oder späteres Go-Live), aber **nicht primärer Dev-Pfad**.
- [ ] RLS-Policies für Mieter-Logins explizit ergänzen.
- [ ] PII-Filter-Middleware + structlog in Phase 0/1 etablieren.
- [ ] Health-Check erweitert um DB, Redis, Ollama, Stripe.

### 5.4 Risiken & Nächste Schritte

- [ ] Risiko-Liste aktualisieren: Docker-Entfernung, Stripe-Komplexität, WE-basiertes Pricing-UX.
- [ ] Nächste Schritte: nicht "Phase 0 starten", sondern "Build Plan v3 finalisieren + Stripe-Testkonto + Resend-Konto + Native-Dev-Skripte".

---

## 6. Abhängigkeiten zwischen den Phasen

### 6.1 Aktueller Abhängigkeitsgraph (v2)

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
                           Phase 9 ──► Phase 10 ──► Phase 11
```

### 6.2 Bewertung

| Aspekt | Bewertung | Begründung |
|--------|-----------|------------|
| Zirkuläre Abhängigkeiten | ✅ **Keine** | Der Graph ist DAG (gerichtet, azyklisch). |
| Fehlende Abhängigkeiten | ⚠️ **Mehrere** | Siehe unten. |
| Parallelisierbarkeit | ✅ Grundsätzlich korrekt | Phase 3 + 4 parallel; Phase 6 parallel zu 7; Phase 9 parallel zu 8. |

### 6.3 Fehlende / unzureichende Abhängigkeiten

| Fehlende Abhängigkeit | Warum wichtig |
|-----------------------|---------------|
| **Phase 8 (E-Mail) → Subscription (neu)** | Mahnungen und Fristen-Warner dürfen nur bei aktivem/zahlendem Account laufen; Trial-Ablauf-E-Mails brauchen Subscription-Status. |
| **Phase 8 → Phase 5 (mietzahlungen)** | Automatisches Mahnwesen braucht `mietzahlungen` und `mahnstufe`. |
| **Phase 7 (KI) → Phase 1 (Audit-Log + Einwilligungen)** | Jeder KI-Aufruf muss geloggt werden; Einwilligungen für KI-Nutzung müssen vorhanden sein. |
| **Phase 10 (DSGVO) → Phase 8 (E-Mail-Logs)** | DSGVO-Export muss versendete Benachrichtigungen (`notifications`) enthalten. |
| **Phase 2 → Phase 1.5 (Subscription)** | WE-Limit-Prüfung beim Anlegen einer Einheit braucht Subscription-Status. |
| **Phase 6 (Dashboard) → Phase 1.5 (Subscription)** | Dashboard-Widget "Dein Abo: X Wohnungen · Y €/Monat" braucht Live-Preisberechnung. |
| **Phase 4 (Tickets) → Phase 2 (Bewerbungen)** | Bewerbungs-Tickets / Mieter-Zuordnung aus Bewerbung heraus. |

### 6.4 Empfohlener Graph für v3

```
Phase 0 ──► Phase 1 ──► Phase 1.5 ──► Phase 2
(Foundation) (Auth)   (Subscription)  (Domain-Core)
                              │              │
                              │              ├──► Phase 3 (Dokumente)
                              │              ├──► Phase 4 (Tickets)
                              │              └──► Phase 5 (Kosten/Abrechnung)
                              │                   │
                              │                   ▼
                              │                Phase 6 (Dashboard)
                              │                   │
                              ▼                   ▼
                           Phase 7 (KI-Schicht)
                              │
                              ├──► Phase 8 (E-Mail/Mahnung/Fristen)
                              │         │
                              │         ▼
                              │      Phase 9 (PDF/Templates)
                              │         │
                              ▼         ▼
                           Phase 10 (DSGVO/Hardening)
                              │
                              ▼
                           Phase 11 (Production Deploy)

Parallel (ab Phase 1):
  Admin-Center ─────────────────────────────────────────────► Phase 11
```

---

## 7. Auswirkungen: Kein Docker → Phase 0 ändert sich

### 7.1 Wegfallende Phase-0-Artefakte

| Artefakt | Status in v3 |
|----------|--------------|
| `Dockerfile` für FastAPI | Optional / CI-only; nicht primärer Dev-Pfad |
| `docker-compose.yml` + `docker-compose.dev.yml` | Nicht für Dev verwenden; ggf. für lokale Tests beibehalten |
| `make dev` via `docker compose up` | Ersetzen durch Native-Dev-Skripte |
| Docker-Hot-Reload | Ersetzen durch `uvicorn --reload` + Vite HMR |
| PostgreSQL via Docker | Verwende **bereits installierte** PostgreSQL 17 nativ |
| Redis via Docker | Redis **noch nicht installiert** — installieren oder für MVP alternative Lösung (z. B. Redis via Package-Manager + systemd) |

### 7.2 Neue Phase-0-Artefakte

| Artefakt | Zweck |
|----------|-------|
| `scripts/setup-dev.sh` | Python-Venv, Node (fnm), DB-User, Redis prüfen/installieren |
| `scripts/run-backend.sh` | `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` |
| `scripts/run-frontend.sh` | `npx vite dev --host 0.0.0.0 --port 5173` |
| `systemd/` (oder `supervisord.conf`) | Backend + Frontend + Worker als Dienste für Server |
| `Makefile`-Targets `dev-native`, `migrate-native`, `lint-native`, `test-native` | Ohne `docker compose exec` |
| `.env.example` | Native URLs: `DATABASE_URL=postgresql+asyncpg://...`, `REDIS_URL=redis://localhost:6379/0` |
| Health-Check | System-Health umfasst DB + Redis + Ollama + Stripe-Testmodus |
| nginx-Konfiguration (lokal) | Für Reverse Proxy bei Proxmox-MVP |

### 7.3 Phase-0-Milestone neu

**Alt:** `docker compose up` läuft; `/health` liefert `ok`; Alembic-Migration erzeugt alle 22 Tabellen.

**Neu:**
- Native Dev-Umgebung läuft (`uvicorn` + Vite).
- PostgreSQL 17 ist erreichbar und enthält Alembic-Initial-Migration für **alle 33 v4-Tabellen + RLS-Policies + Indizes**.
- Redis läuft (oder ist für MVP explizit als optional markiert).
- `/health` liefert `ok` für Backend, DB und Redis.
- Kein Docker für den Dev-Workflow nötig.

### 7.4 Zusätzliche Risiken durch Native Dev

| Risiko | Gegenmaßnahme |
|--------|---------------|
| Server hat nur 4 GB RAM / 2 CPU | Schlanke Services, Redis optional, später Upgrade |
| Kein Docker = mehr manuelles Setup | `setup-dev.sh` + dokumentierte Schritte |
| Prozess-Management (Crash, Reboot) | systemd-Services oder supervisord |
| GitHub Actions muss nativen Server bedienen | Deploy-Skripte via SSH: git pull + venv + npm install + alembic + service restart |
| PostgreSQL-Backups selbst verantworten | WAL-G PITR oder zumindest tägliche `pg_dump` + Offsite |

---

## 8. Kritische Inkonsistenzen innerhalb der bestehenden Dokumentation

Neben dem Build Plan sind auch folgende Konzeptdokumente **nicht konsistent** mit dem vom Nutzer definierten Current State. Build Plan v3 sollte die Quelle der Wahrheit klären:

| Dokument | Inkonsistenz |
|----------|--------------|
| `docs/concept/Abo-Modell-v3.md` | Noch 3 feste Pläne (Basis/Pro/Business 14,90/29,90/49,90 €) und "14 Tage ohne KK"; widerspricht WE-basiertem 9,75-€-Modell und Netflix-Trial mit KK. |
| `docs/concept/Abo-Abschluss-Prozess-Konzept.md` | Header spricht noch "Free 0 € / Basis 14,90 € / Pro 29,90 € / Business 49,90 €"; trotzdem im Fließtext WE-basierte Elemente. |
| `docs/architecture/2026-11-02_db-schema-v4.md` | Abschnitt "Plan-Limits & Subscription-Logik" listet noch Free/Basis/Pro/Business mit alten Preisen, obwohl v4 sonst WE-basiert ist. |
| `Makefile` / `docker-compose.yml` / `docker-compose.dev.yml` | Noch Docker-basiert; widersprechen der bestätigten Native-Dev-Entscheidung. |
| `ARCHITECTURE.md` | Deploy-Abschnitt noch mit Docker-Build; KI-Modell "Kimi K.6" statt "Kimi K2.6". |

---

## 9. Empfohlene nächste Schritte

1. **Build Plan v3 schreiben** auf Basis dieses Reviews (v4-Schema, WE-Pricing, Native Dev, Resend, Stripe).
2. **Konzeptdokumente synchronisieren:** `Abo-Modell-v3.md`, `Abo-Abschluss-Prozess-Konzept.md`, `db-schema-v4.md` (Plan-Limits-Abschnitt), `ARCHITECTURE.md`, `Makefile`, Docker-Files.
3. **Stripe-Testkonto** anlegen und erste Subscription-API-Design-Dokumentation erstellen.
4. **Resend-Konto** anlegen + Domain/DNS-Konfiguration vorbereiten.
5. **Native-Dev-Skripte** (`setup-dev.sh`, `run-backend.sh`, `run-frontend.sh`) erstellen.
6. **PostgreSQL-User + DB** für Dev anlegen; Redis installieren.
7. **Alembic-Initial-Migration** für alle 33 v4-Tabellen erstellen.
8. **GitHub-Issues** für alle hier identifizierten Inkonsistenzen anlegen, damit sie nicht stillschweigend verloren gehen.

---

*Review erstellt durch Pre-Build Architektur-Review auf Basis von Build Plan v2, SKILL.md (mietverwaltung-saas), DB-Schema v4 und aktuellem Repository-Stand.*
