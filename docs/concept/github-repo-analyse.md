# GitHub-Scout Analyse: Open-Source-Projekte für MietVerwaltung SaaS

**Erstellt:** 2026-10-28 07:10 UTC

## Zusammenfassung

Analysiert wurden **30 GitHub-Repositories** aus den Bereichen Mietverwaltung, Nebenkostenabrechnung, Property Management, WEG-Verwaltung, KI/OCR-Assistenten, eID und Tenant Portale.

### Empfehlungsverteilung
- **Übernehmen:** 5 Repos
- **Studieren:** 15 Repos
- **Ignorieren:** 10 Repos

### Top-Empfehlungen

| Rang | Repo | Score | Empfehlung | Kurzbegründung |
|------|------|-------|------------|----------------|
| 1 | [fgilde/hausverwaltung (HaVeWa)](https://github.com/fgilde/hausverwaltung) | 39.0/44 (88.6%) | Übernehmen | Am besten passend: Next.js/TypeScript/PostgreSQL/Prisma, BetrKV-Allocation-Engine, WEG, DI... |
| 2 | [speedone/mietfuchs](https://github.com/speedone/mietfuchs) | 36.5/44 (83.0%) | Übernehmen | Exzellente DACH-NK-Logik (BetrKV, HeizkostenV, CO2KostAufG, §35a EStG). Lokale KI-Belegaus... |
| 3 | [OliverHennhoefer/mietkartei.de](https://github.com/OliverHennhoefer/mietkartei.de) | 35.5/44 (80.7%) | Übernehmen | Sehr nah an unserer Zielgruppe: private deutsche Vermieter. Python-Backend, MCP-Server für... |
| 4 | [Nerbry72/NebenkostenFix](https://github.com/Nerbry72/NebenkostenFix) | 32.5/44 (73.9%) | Studieren | Sehr gute DACH-NK-Logik in Python. GPL-3.0, Flask statt FastAPI, SQLite. Gute Referenz für... |
| 5 | [s3gv/immobase](https://github.com/s3gv/immobase) | 32.0/44 (72.7%) | Übernehmen | Sehr starkes DACH-Feature-Set (WEG, §28 WEG, BetrKV, Hausgeld, Mahnwesen, Mieterportal). P... |
| 6 | [zite/property-management](https://github.com/zite/property-management) | 28.5/44 (64.8%) | Studieren | Sehr umfangreicher Ledger/Accounting-Teil und gute UI. Zite-Lock-in, keine DACH-NK, starke... |
| 7 | [Klotzkette/claude-fuer-deutsches-recht](https://github.com/Klotzkette/claude-fuer-deutsches-recht) | 28.0/44 (63.6%) | Studieren | Kein Code, aber extrem wertvolle Prompts und Rechtslogik für BetrKV, WEG, Mietrecht. Kann ... |
| 8 | [slgao/landlord_system (Dachly)](https://github.com/slgao/landlord_system) | 26.5/44 (60.2%) | Studieren | DACH-Logik und Python/PostgreSQL passen gut. Aber BSL-Lizenz verbietet kommerziellen SaaS ... |
| 9 | [open-condo-software/condo](https://github.com/open-condo-software/condo) | 26.0/44 (59.1%) | Studieren | Riesige Codebasis (16.480 Commits), viele Features, aber russischer Fokus, komplexer Stack... |
| 10 | [clawnify/OpenProperty](https://github.com/clawnify/OpenProperty) | 24.0/44 (54.5%) | Studieren | Moderne React/Vite-Architektur, gutes Datenmodell, Maintenance-Tickets. Keine NK-Abrechnun... |

## Bewertungsmethodik

Die vollständige Checkliste mit allen 15 Kriterien befindet sich in `/root/mietverwaltung/github-repo-checkliste.md`.

Bewertungsskala pro Kriterium: **Ja** = volle Gewichtung, **Teilweise** = halbe Gewichtung, **Nein** = 0 Punkte.

| # | Kriterium | Gewichtung |
|---|-----------|------------|
| 1 | Kerndatenmodell | ⭐⭐⭐⭐⭐ |
| 2 | Nebenkostenabrechnung | ⭐⭐⭐⭐⭐ |
| 3 | DACH-Spezifisch | ⭐⭐⭐⭐ |
| 4 | Lizenz | ⭐⭐⭐⭐ |
| 5 | Tech-Stack-Kompatibilität | ⭐⭐⭐ |
| 6 | Code-Qualität | ⭐⭐⭐ |
| 7 | Aktiv gewartet | ⭐⭐⭐ |
| 8 | KI-Integration | ⭐⭐ |
| 9 | OCR / Belegscanning | ⭐⭐ |
| 10 | Ticket-System / Kommunikation | ⭐⭐ |
| 11 | eID / Verifikation | ⭐⭐ |
| 12 | Mahnwesen / Zahlungsverfolgung | ⭐⭐ |
| 13 | PDF-Export / Berichte | ⭐⭐ |
| 14 | DSGVO / Datenschutz | ⭐⭐⭐ |
| 15 | Community / Reife | ⭐⭐ |

**Maximal erreichbare Punktzahl:** 44 Punkte.

## Detaillierte Repo-Bewertungen

### fgilde/hausverwaltung (HaVeWa)

- **URL:** https://github.com/fgilde/hausverwaltung
- **Sterne:** 18
- **Letzte Aktivität:** 2026-10-24
- **Tech-Stack:** Next.js 16 + TypeScript + PostgreSQL + Prisma + Tailwind
- **Lizenz:** AGPL-3.0 (dual commercial)
- **Beschreibung:** Komplette DACH-Hausverwaltung mit WEG, BetrKV, Mahnwesen, Ticket-System, MCP-Server und REST API.
- **Gesamtpunktzahl:** 39.0/44 (88.6%)
- **Empfehlung:** **Übernehmen**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | J |
| DACH-Spezifisch | J |
| Lizenz | J |
| Tech-Stack-Kompatibilität | J |
| Code-Qualität | J |
| Aktiv gewartet | J |
| KI-Integration | J |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | J |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | J |
| PDF-Export / Berichte | J |
| DSGVO / Datenschutz | J |
| Community / Reife | T |

**Analyse & Begründung:** Am besten passend: Next.js/TypeScript/PostgreSQL/Prisma, BetrKV-Allocation-Engine, WEG, DIN-5008-Briefe, GoBD, MCP-Server, Tests. Ideal als Architektur- und Feature-Referenz.

---

### speedone/mietfuchs

- **URL:** https://github.com/speedone/mietfuchs
- **Sterne:** 11
- **Letzte Aktivität:** 2026-10-27
- **Tech-Stack:** TypeScript/Node + Express + React + SQLite/Docker
- **Lizenz:** AGPL-3.0
- **Beschreibung:** Lokale NK-Abrechnung für private deutsche Vermieter inkl. HeizkostenV, CO2-Kostenaufteilung, KI-Belegauswertung.
- **Gesamtpunktzahl:** 36.5/44 (83.0%)
- **Empfehlung:** **Übernehmen**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | J |
| DACH-Spezifisch | J |
| Lizenz | J |
| Tech-Stack-Kompatibilität | T |
| Code-Qualität | J |
| Aktiv gewartet | J |
| KI-Integration | J |
| OCR / Belegscanning | T |
| Ticket-System / Kommunikation | N |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | J |
| PDF-Export / Berichte | J |
| DSGVO / Datenschutz | J |
| Community / Reife | T |

**Analyse & Begründung:** Exzellente DACH-NK-Logik (BetrKV, HeizkostenV, CO2KostAufG, §35a EStG). Lokale KI-Belegauswertung. TypeScript/Node statt Python, aber fachlich sehr nah.

---

### OliverHennhoefer/mietkartei.de

- **URL:** https://github.com/OliverHennhoefer/mietkartei.de
- **Sterne:** 1
- **Letzte Aktivität:** 2026-10-27
- **Tech-Stack:** SvelteKit + Python + TypeScript + PostgreSQL + Docker
- **Lizenz:** AGPL-3.0
- **Beschreibung:** Deutsche Hausverwaltung für Privatvermieter mit Bankabgleich, NK-Abrechnung und MCP-Server.
- **Gesamtpunktzahl:** 35.5/44 (80.7%)
- **Empfehlung:** **Übernehmen**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | J |
| DACH-Spezifisch | J |
| Lizenz | J |
| Tech-Stack-Kompatibilität | T |
| Code-Qualität | J |
| Aktiv gewartet | J |
| KI-Integration | J |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | J |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | T |
| PDF-Export / Berichte | J |
| DSGVO / Datenschutz | J |
| Community / Reife | N |

**Analyse & Begründung:** Sehr nah an unserer Zielgruppe: private deutsche Vermieter. Python-Backend, MCP-Server für Claude/ChatGPT, Bankabgleich, NK-Abrechnung. SvelteKit statt Vue, aber viele Module übertragbar.

---

### Nerbry72/NebenkostenFix

- **URL:** https://github.com/Nerbry72/NebenkostenFix
- **Sterne:** 24
- **Letzte Aktivität:** 2026-10-27
- **Tech-Stack:** Python + Flask + SQLite/MySQL + Docker/Windows
- **Lizenz:** GPL-3.0
- **Beschreibung:** Deutsche NK-Abrechnung für Privatvermieter (BetrKV, HeizkostenV, CO2KostAufG) mit PDF-Ausgabe.
- **Gesamtpunktzahl:** 32.5/44 (73.9%)
- **Empfehlung:** **Studieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | J |
| DACH-Spezifisch | J |
| Lizenz | J |
| Tech-Stack-Kompatibilität | T |
| Code-Qualität | J |
| Aktiv gewartet | J |
| KI-Integration | N |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | N |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | T |
| PDF-Export / Berichte | J |
| DSGVO / Datenschutz | J |
| Community / Reife | T |

**Analyse & Begründung:** Sehr gute DACH-NK-Logik in Python. GPL-3.0, Flask statt FastAPI, SQLite. Gute Referenz für Heizkosten- und CO2-Logik.

---

### s3gv/immobase

- **URL:** https://github.com/s3gv/immobase
- **Sterne:** 2
- **Letzte Aktivität:** 2026-09-17
- **Tech-Stack:** PHP/Symfony + PostgreSQL + Docker
- **Lizenz:** AGPL-3.0
- **Beschreibung:** Open-Source-Hausverwaltungssoftware für WEG, Mietverwaltung und Sondereigentum in Deutschland.
- **Gesamtpunktzahl:** 32.0/44 (72.7%)
- **Empfehlung:** **Übernehmen**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | J |
| DACH-Spezifisch | J |
| Lizenz | J |
| Tech-Stack-Kompatibilität | T |
| Code-Qualität | J |
| Aktiv gewartet | T |
| KI-Integration | N |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | J |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | J |
| PDF-Export / Berichte | T |
| DSGVO / Datenschutz | J |
| Community / Reife | N |

**Analyse & Begründung:** Sehr starkes DACH-Feature-Set (WEG, §28 WEG, BetrKV, Hausgeld, Mahnwesen, Mieterportal). PHP/Symfony statt Python, aber PostgreSQL. Hoher Studienwert für NK-Logik.

---

### zite/property-management

- **URL:** https://github.com/zite/property-management
- **Sterne:** 1
- **Letzte Aktivität:** 2026-10-02
- **Tech-Stack:** React 18 + TypeScript + Vite + ZiteJS (Postgres hosted) + Tailwind
- **Lizenz:** MIT
- **Beschreibung:** Komplette Property-Management-Lösung auf Zite mit Double-Entry Accounting, Portal und 191 Endpoints.
- **Gesamtpunktzahl:** 28.5/44 (64.8%)
- **Empfehlung:** **Studieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | T |
| DACH-Spezifisch | N |
| Lizenz | J |
| Tech-Stack-Kompatibilität | T |
| Code-Qualität | J |
| Aktiv gewartet | J |
| KI-Integration | J |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | J |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | J |
| PDF-Export / Berichte | J |
| DSGVO / Datenschutz | T |
| Community / Reife | N |

**Analyse & Begründung:** Sehr umfangreicher Ledger/Accounting-Teil und gute UI. Zite-Lock-in, keine DACH-NK, starke Abhängigkeit von Zite-Hosting.

---

### Klotzkette/claude-fuer-deutsches-recht

- **URL:** https://github.com/Klotzkette/claude-fuer-deutsches-recht
- **Sterne:** n/a
- **Letzte Aktivität:** 2026-10-27
- **Tech-Stack:** Markdown-Skills / Prompts (kein Code-Stack)
- **Lizenz:** Apache-2.0
- **Beschreibung:** Große Sammlung von Skills/Prompts für deutsches Recht inkl. Mietrecht, WEG, NK-Abrechnung.
- **Gesamtpunktzahl:** 28.0/44 (63.6%)
- **Empfehlung:** **Studieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | N |
| Nebenkostenabrechnung | J |
| DACH-Spezifisch | J |
| Lizenz | J |
| Tech-Stack-Kompatibilität | N |
| Code-Qualität | J |
| Aktiv gewartet | J |
| KI-Integration | J |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | N |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | J |
| PDF-Export / Berichte | T |
| DSGVO / Datenschutz | J |
| Community / Reife | T |

**Analyse & Begründung:** Kein Code, aber extrem wertvolle Prompts und Rechtslogik für BetrKV, WEG, Mietrecht. Kann als Wissensbasis für unseren KI-Assistenten dienen.

---

### slgao/landlord_system (Dachly)

- **URL:** https://github.com/slgao/landlord_system
- **Sterne:** 0
- **Letzte Aktivität:** 2026-10-25
- **Tech-Stack:** Python + Streamlit + FastAPI + PostgreSQL + ReportLab
- **Lizenz:** Business Source License 1.1 (Change Date 2030)
- **Beschreibung:** Deutsche Hausverwaltung für Privatvermieter mit Mietkonto, NK-Abrechnung, Anlage V und KI-Assistent.
- **Gesamtpunktzahl:** 26.5/44 (60.2%)
- **Empfehlung:** **Studieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | J |
| DACH-Spezifisch | J |
| Lizenz | N |
| Tech-Stack-Kompatibilität | T |
| Code-Qualität | T |
| Aktiv gewartet | J |
| KI-Integration | J |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | N |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | T |
| PDF-Export / Berichte | J |
| DSGVO / Datenschutz | T |
| Community / Reife | N |

**Analyse & Begründung:** DACH-Logik und Python/PostgreSQL passen gut. Aber BSL-Lizenz verbietet kommerziellen SaaS bis 2030. UI ist Streamlit, nicht produktionsreif.

---

### open-condo-software/condo

- **URL:** https://github.com/open-condo-software/condo
- **Sterne:** 427
- **Letzte Aktivität:** 2026-10-28
- **Tech-Stack:** JavaScript/TypeScript + KeystoneJS + Next.js + Ant Design
- **Lizenz:** MIT
- **Beschreibung:** Großes russisches Open-Source Property-Management-SaaS mit Tickets, Zahlungen, Marketplace, Mini-Apps.
- **Gesamtpunktzahl:** 26.0/44 (59.1%)
- **Empfehlung:** **Studieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | T |
| DACH-Spezifisch | N |
| Lizenz | J |
| Tech-Stack-Kompatibilität | N |
| Code-Qualität | J |
| Aktiv gewartet | J |
| KI-Integration | N |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | J |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | J |
| PDF-Export / Berichte | T |
| DSGVO / Datenschutz | T |
| Community / Reife | J |

**Analyse & Begründung:** Riesige Codebasis (16.480 Commits), viele Features, aber russischer Fokus, komplexer Stack (Keystone), nicht DACH-konform.

---

### clawnify/OpenProperty

- **URL:** https://github.com/clawnify/OpenProperty
- **Sterne:** 28
- **Letzte Aktivität:** 2026-10-28
- **Tech-Stack:** React 19 + Vite + Hono + Cloudflare D1
- **Lizenz:** MIT
- **Beschreibung:** Self-hosted Property-Management-Alternative zu TenantCloud/AppFolio mit Units, Leases, Rent Ledger, Maintenance.
- **Gesamtpunktzahl:** 24.0/44 (54.5%)
- **Empfehlung:** **Studieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | N |
| DACH-Spezifisch | N |
| Lizenz | J |
| Tech-Stack-Kompatibilität | T |
| Code-Qualität | J |
| Aktiv gewartet | J |
| KI-Integration | N |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | J |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | J |
| PDF-Export / Berichte | N |
| DSGVO / Datenschutz | T |
| Community / Reife | J |

**Analyse & Begründung:** Moderne React/Vite-Architektur, gutes Datenmodell, Maintenance-Tickets. Keine NK-Abrechnung, D1 statt PostgreSQL. UI-Komponenten interessant.

---

### senatroxx/OpenKos

- **URL:** https://github.com/senatroxx/OpenKos
- **Sterne:** 117
- **Letzte Aktivität:** 2026-10-26
- **Tech-Stack:** Laravel + React + PostgreSQL
- **Lizenz:** Apache-2.0
- **Beschreibung:** Open-Source-Plattform für Boarding Houses/Kos mit Plugin-Architektur, WhatsApp, Tickets, Zahlungen.
- **Gesamtpunktzahl:** 23.5/44 (53.4%)
- **Empfehlung:** **Studieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | N |
| DACH-Spezifisch | N |
| Lizenz | J |
| Tech-Stack-Kompatibilität | N |
| Code-Qualität | J |
| Aktiv gewartet | J |
| KI-Integration | N |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | J |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | J |
| PDF-Export / Berichte | T |
| DSGVO / Datenschutz | T |
| Community / Reife | J |

**Analyse & Begründung:** Sehr gute Code-Qualität, Plugin-System, WhatsApp-Integration. Aber indonesischer Fokus (Kos), Laravel-Stack, keine DACH-NK.

---

### jnuyens/rentular

- **URL:** https://github.com/jnuyens/rentular
- **Sterne:** 0
- **Letzte Aktivität:** 2026-10-22
- **Tech-Stack:** Next.js + Hono + Drizzle + MariaDB + Redis
- **Lizenz:** AGPL-3.0
- **Beschreibung:** Belgisches Open-Source-Immobilienmanagement mit Mietindex, SEPA und Mieterverwaltung.
- **Gesamtpunktzahl:** 23.0/44 (52.3%)
- **Empfehlung:** **Studieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | N |
| DACH-Spezifisch | T |
| Lizenz | J |
| Tech-Stack-Kompatibilität | T |
| Code-Qualität | J |
| Aktiv gewartet | J |
| KI-Integration | N |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | N |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | J |
| PDF-Export / Berichte | T |
| DSGVO / Datenschutz | T |
| Community / Reife | N |

**Analyse & Begründung:** Gute Architektur (Monorepo, packages) und Zahlungsverfolgung. Für DACH aber Belgisches Recht, keine NK-Logik. Als Architektur-Inspiration nützlich.

---

### DACHDigitalwerk/nebenkostenabrechnung-mietminderung-pruefer-dach

- **URL:** https://github.com/DACHDigitalwerk/nebenkostenabrechnung-mietminderung-pruefer-dach
- **Sterne:** 0
- **Letzte Aktivität:** 2026-10-26
- **Tech-Stack:** Unbekannt
- **Lizenz:** MIT
- **Beschreibung:** DACH-Prüfer für Nebenkostenabrechnung & Mietminderung (DE/AT/CH), erkennt unzulässige Posten und generiert Widerspruch.
- **Gesamtpunktzahl:** 23.0/44 (52.3%)
- **Empfehlung:** **Studieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | N |
| Nebenkostenabrechnung | J |
| DACH-Spezifisch | J |
| Lizenz | J |
| Tech-Stack-Kompatibilität | N |
| Code-Qualität | T |
| Aktiv gewartet | J |
| KI-Integration | J |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | N |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | N |
| PDF-Export / Berichte | J |
| DSGVO / Datenschutz | T |
| Community / Reife | N |

**Analyse & Begründung:** Interessant für DACH-Rechtslogik und Widerspruchs-Generierung. Wenig bekannt, geringe Reife.

---

### parcelis/parcelis

- **URL:** https://github.com/parcelis/parcelis
- **Sterne:** 7
- **Letzte Aktivität:** 2026-10-27
- **Tech-Stack:** Next.js + TypeScript + PostgreSQL + pnpm/Turborepo + Docusaurus
- **Lizenz:** AGPL-3.0
- **Beschreibung:** Open-Source Property-Management-Plattform für lokale Vermieter/Property Teams.
- **Gesamtpunktzahl:** 22.0/44 (50.0%)
- **Empfehlung:** **Studieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | N |
| DACH-Spezifisch | N |
| Lizenz | J |
| Tech-Stack-Kompatibilität | T |
| Code-Qualität | J |
| Aktiv gewartet | J |
| KI-Integration | N |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | J |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | T |
| PDF-Export / Berichte | N |
| DSGVO / Datenschutz | T |
| Community / Reife | T |

**Analyse & Begründung:** Professioneller Monorepo-Ansatz mit Docusaurus-Doku, Maintenance-Tickets. Noch sehr jung, keine NK-Logik.

---

### aelassas/movinin

- **URL:** https://github.com/aelassas/movinin
- **Sterne:** 232
- **Letzte Aktivität:** 2026-10-28
- **Tech-Stack:** MERN Stack + React Native + Stripe/PayPal
- **Lizenz:** MIT
- **Beschreibung:** Rental-Property-Management-Plattform mit mobiler App für kurz-/mittelfristige Vermietung.
- **Gesamtpunktzahl:** 21.5/44 (48.9%)
- **Empfehlung:** **Ignorieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | N |
| DACH-Spezifisch | N |
| Lizenz | J |
| Tech-Stack-Kompatibilität | N |
| Code-Qualität | J |
| Aktiv gewartet | J |
| KI-Integration | N |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | N |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | J |
| PDF-Export / Berichte | T |
| DSGVO / Datenschutz | T |
| Community / Reife | J |

**Analyse & Begründung:** Fokus Ferienvermietung/Mobile App, MERN-Stack, keine DACH-NK. Nicht für klassische Mietverwaltung.

---

### TechFunWay/rental

- **URL:** https://github.com/TechFunWay/rental
- **Sterne:** 15
- **Letzte Aktivität:** 2026-10-24
- **Tech-Stack:** Go + Vue 3 + SQLite
- **Lizenz:** MIT
- **Beschreibung:** Chinesisches Open-Source-Mietmanagement für kleine Vermieter mit Vue3-UI und Docker.
- **Gesamtpunktzahl:** 21.5/44 (48.9%)
- **Empfehlung:** **Ignorieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | T |
| DACH-Spezifisch | N |
| Lizenz | J |
| Tech-Stack-Kompatibilität | T |
| Code-Qualität | T |
| Aktiv gewartet | J |
| KI-Integration | N |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | N |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | T |
| PDF-Export / Berichte | J |
| DSGVO / Datenschutz | N |
| Community / Reife | T |

**Analyse & Begründung:** Chinesischer Fokus, SQLite, keine DACH-Rechtskonformität. Vue3-UI ist nett, aber nicht relevant.

---

### Governikus/AusweisApp

- **URL:** https://github.com/Governikus/AusweisApp
- **Sterne:** 782
- **Letzte Aktivität:** 2026-10-28
- **Tech-Stack:** C++ / Qt / EUPL-1.2
- **Lizenz:** EUPL-1.2
- **Beschreibung:** Offizieller deutscher eID-Client des Bundes für Online-Ausweis-Funktion.
- **Gesamtpunktzahl:** 21.0/44 (47.7%)
- **Empfehlung:** **Studieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | N |
| Nebenkostenabrechnung | N |
| DACH-Spezifisch | J |
| Lizenz | J |
| Tech-Stack-Kompatibilität | N |
| Code-Qualität | J |
| Aktiv gewartet | J |
| KI-Integration | N |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | N |
| eID / Verifikation | J |
| Mahnwesen / Zahlungsverfolgung | N |
| PDF-Export / Berichte | N |
| DSGVO / Datenschutz | J |
| Community / Reife | J |

**Analyse & Begründung:** Offizieller eID-Client. Für eID/Personalausweis-Verifikation unverzichtbare Referenz. C++/Qt-Stack muss über SDK/API angebunden werden.

---

### Devastating-Phoenix/nebencheck

- **URL:** https://github.com/Devastating-Phoenix/nebencheck
- **Sterne:** 0
- **Letzte Aktivität:** 2026-07-22
- **Tech-Stack:** Flutter Web + Dart + Tesseract WASM
- **Lizenz:** PolyForm Noncommercial 1.0
- **Beschreibung:** Privacy-first Web-App zur Prüfung deutscher Nebenkostenabrechnungen inkl. OCR, Benchmarks, Widerspruch.
- **Gesamtpunktzahl:** 20.5/44 (46.6%)
- **Empfehlung:** **Studieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | N |
| Nebenkostenabrechnung | J |
| DACH-Spezifisch | J |
| Lizenz | N |
| Tech-Stack-Kompatibilität | N |
| Code-Qualität | J |
| Aktiv gewartet | T |
| KI-Integration | N |
| OCR / Belegscanning | J |
| Ticket-System / Kommunikation | N |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | N |
| PDF-Export / Berichte | J |
| DSGVO / Datenschutz | J |
| Community / Reife | N |

**Analyse & Begründung:** Hervorragendes Beispiel für DACH-Rechtslogik, on-device OCR und DSGVO-Privacy-by-Design. Leider Noncommercial-Lizenz, daher nicht direkt übernehmbar.

---

### bhimrazy/receipt-ocr

- **URL:** https://github.com/bhimrazy/receipt-ocr
- **Sterne:** 746
- **Letzte Aktivität:** 2026-10-24
- **Tech-Stack:** Python + FastAPI + Tesseract + OpenAI/LLM
- **Lizenz:** MIT
- **Beschreibung:** Effiziente OCR-Engine für Belege/Rechnungen mit LLM-gestützter strukturierter Extraktion.
- **Gesamtpunktzahl:** 20.5/44 (46.6%)
- **Empfehlung:** **Übernehmen**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | N |
| Nebenkostenabrechnung | N |
| DACH-Spezifisch | N |
| Lizenz | J |
| Tech-Stack-Kompatibilität | J |
| Code-Qualität | J |
| Aktiv gewartet | J |
| KI-Integration | J |
| OCR / Belegscanning | J |
| Ticket-System / Kommunikation | N |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | N |
| PDF-Export / Berichte | N |
| DSGVO / Datenschutz | T |
| Community / Reife | J |

**Analyse & Begründung:** Hervorragend passend für unser Beleg-Scan-OCR-Feature. MIT-Lizenz, Python, FastAPI, LLM-OCR. Kein Mieter-Kontext, aber als OCR-Service ideal.

---

### agentic-ops/real-estate-mcp

- **URL:** https://github.com/agentic-ops/real-estate-mcp
- **Sterne:** 70
- **Letzte Aktivität:** 2026-10-26
- **Tech-Stack:** Python + FastMCP
- **Lizenz:** AGPL-3.0
- **Beschreibung:** MCP-Server für Real-Estate-Workflows: Suche, Bewertung, Hypotheken, Investment-Analyse.
- **Gesamtpunktzahl:** 20.5/44 (46.6%)
- **Empfehlung:** **Studieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | N |
| Nebenkostenabrechnung | N |
| DACH-Spezifisch | N |
| Lizenz | J |
| Tech-Stack-Kompatibilität | J |
| Code-Qualität | J |
| Aktiv gewartet | J |
| KI-Integration | J |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | N |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | T |
| PDF-Export / Berichte | J |
| DSGVO / Datenschutz | T |
| Community / Reife | T |

**Analyse & Begründung:** Gute Referenz für MCP-Server-Architektur in Python. Kein Property-Management-Datenmodell, eher US-Markt.

---

### microrealestate/microrealestate

- **URL:** https://github.com/microrealestate/microrealestate
- **Sterne:** 1204
- **Letzte Aktivität:** 2026-10-26
- **Tech-Stack:** Node.js + MongoDB + Docker
- **Lizenz:** SUL v2.0 (source-available)
- **Beschreibung:** Self-Hosted Property Management für Vermieter: Mieten, Verträge, Quittungen, Mieterportal.
- **Gesamtpunktzahl:** 19.5/44 (44.3%)
- **Empfehlung:** **Ignorieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | N |
| DACH-Spezifisch | N |
| Lizenz | N |
| Tech-Stack-Kompatibilität | N |
| Code-Qualität | J |
| Aktiv gewartet | J |
| KI-Integration | N |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | T |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | J |
| PDF-Export / Berichte | J |
| DSGVO / Datenschutz | T |
| Community / Reife | J |

**Analyse & Begründung:** Sehr populär, aber Sustainable Use License verbietet kommerziellen SaaS-Betrieb ab 5 Einheiten. MongoDB-Stack passt nicht.

---

### bigprof-software/online-rental-property-manager

- **URL:** https://github.com/bigprof-software/online-rental-property-manager
- **Sterne:** 177
- **Letzte Aktivität:** 2026-10-22
- **Tech-Stack:** PHP + AppGini + MySQL/MariaDB
- **Lizenz:** MIT
- **Beschreibung:** Mit AppGini generierte Web-App zur Verwaltung von Mietobjekten, Einheiten, Mietern und Verträgen.
- **Gesamtpunktzahl:** 19.0/44 (43.2%)
- **Empfehlung:** **Ignorieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | N |
| DACH-Spezifisch | N |
| Lizenz | J |
| Tech-Stack-Kompatibilität | N |
| Code-Qualität | T |
| Aktiv gewartet | J |
| KI-Integration | N |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | N |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | T |
| PDF-Export / Berichte | J |
| DSGVO / Datenschutz | T |
| Community / Reife | T |

**Analyse & Begründung:** Low-Code/AppGini-Generierung, eingeschränkte Anpassbarkeit, kein NK-Modul.

---

### KazKozDev/docket

- **URL:** https://github.com/KazKozDev/docket
- **Sterne:** 3
- **Letzte Aktivität:** 2026-10-20
- **Tech-Stack:** Python + Ollama/local LLM + Tesseract
- **Lizenz:** Apache-2.0
- **Beschreibung:** Python-Bibliothek für Invoice/Receipt OCR mit lokalen oder gehosteten LLMs, inkl. Validierung.
- **Gesamtpunktzahl:** 18.5/44 (42.0%)
- **Empfehlung:** **Studieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | N |
| Nebenkostenabrechnung | N |
| DACH-Spezifisch | N |
| Lizenz | J |
| Tech-Stack-Kompatibilität | J |
| Code-Qualität | J |
| Aktiv gewartet | J |
| KI-Integration | J |
| OCR / Belegscanning | J |
| Ticket-System / Kommunikation | N |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | N |
| PDF-Export / Berichte | N |
| DSGVO / Datenschutz | T |
| Community / Reife | N |

**Analyse & Begründung:** Interessant für privacy-first OCR mit Ollama, XRechnung/Factur-X. Noch sehr jung (3 Sterne).

---

### Ethos6/free-ocr-api

- **URL:** https://github.com/Ethos6/free-ocr-api
- **Sterne:** 2
- **Letzte Aktivität:** 2026-10-23
- **Tech-Stack:** Python + FastAPI + Tesseract
- **Lizenz:** MIT
- **Beschreibung:** Self-hosted OCR & Document-Data-Extraction API inkl. MCP-Server, JSON/CSV/Excel-Export.
- **Gesamtpunktzahl:** 18.0/44 (40.9%)
- **Empfehlung:** **Studieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | N |
| Nebenkostenabrechnung | N |
| DACH-Spezifisch | N |
| Lizenz | J |
| Tech-Stack-Kompatibilität | J |
| Code-Qualität | T |
| Aktiv gewartet | J |
| KI-Integration | J |
| OCR / Belegscanning | J |
| Ticket-System / Kommunikation | N |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | N |
| PDF-Export / Berichte | T |
| DSGVO / Datenschutz | T |
| Community / Reife | N |

**Analyse & Begründung:** Selbst gehostete OCR-API mit MCP-Server, passend zu unserem KI-Assistenten. Noch sehr neu.

---

### mohsin-rafique/property-management

- **URL:** https://github.com/mohsin-rafique/property-management
- **Sterne:** 1
- **Letzte Aktivität:** 2026-09-01
- **Tech-Stack:** Laravel 12 + PHP 8.2 + Bootstrap 5 + MySQL
- **Lizenz:** MIT
- **Beschreibung:** Pakistanisches Mietverwaltungs-System mit Quittungen, Stromrechnungen, Kautionen und Mieterportal.
- **Gesamtpunktzahl:** 17.5/44 (39.8%)
- **Empfehlung:** **Ignorieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | N |
| DACH-Spezifisch | N |
| Lizenz | J |
| Tech-Stack-Kompatibilität | N |
| Code-Qualität | T |
| Aktiv gewartet | J |
| KI-Integration | N |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | T |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | T |
| PDF-Export / Berichte | J |
| DSGVO / Datenschutz | N |
| Community / Reife | N |

**Analyse & Begründung:** Fokus Pakistan (WAPDA, Lakh/Crore). Keine NK-Abrechnung, kein DACH-Recht, PHP-Stack passt nicht.

---

### meagoco/lookhome

- **URL:** https://github.com/meagoco/lookhome
- **Sterne:** 32
- **Letzte Aktivität:** 2026-10-15
- **Tech-Stack:** Node.js + Express + SQLite + Vue3
- **Lizenz:** MIT
- **Beschreibung:** Leichtgewichtiges chinesisches Apartment-Management-System mit Mieter-, Vertrags- und Abrechnungsmodul.
- **Gesamtpunktzahl:** 16.5/44 (37.5%)
- **Empfehlung:** **Ignorieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | T |
| DACH-Spezifisch | N |
| Lizenz | J |
| Tech-Stack-Kompatibilität | T |
| Code-Qualität | T |
| Aktiv gewartet | N |
| KI-Integration | N |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | T |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | T |
| PDF-Export / Berichte | N |
| DSGVO / Datenschutz | N |
| Community / Reife | N |

**Analyse & Begründung:** Auf chinesischen Markt zugeschnitten (WeChat-Pay, ID-Verschlüsselung). Kein DACH-Recht, nur 1 Commit, keine Community. Nicht für unsere SaaS nutzbar.

---

### camelaissani/loca

- **URL:** https://github.com/camelaissani/loca
- **Sterne:** 241
- **Letzte Aktivität:** 2026-08-31
- **Tech-Stack:** Node.js + Express + MongoDB + jQuery
- **Lizenz:** MIT
- **Beschreibung:** Deprecated Open-Source Immobilienverwaltung; Vorgänger von MicroRealEstate.
- **Gesamtpunktzahl:** 14.0/44 (31.8%)
- **Empfehlung:** **Ignorieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | N |
| DACH-Spezifisch | N |
| Lizenz | J |
| Tech-Stack-Kompatibilität | N |
| Code-Qualität | T |
| Aktiv gewartet | N |
| KI-Integration | N |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | N |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | T |
| PDF-Export / Berichte | T |
| DSGVO / Datenschutz | T |
| Community / Reife | N |

**Analyse & Begründung:** Archiviert seit 2022, durch MicroRealEstate ersetzt. Veralteter Stack (jQuery, MongoDB).

---

### orpms/orpms

- **URL:** https://github.com/orpms/orpms
- **Sterne:** 86
- **Letzte Aktivität:** 2026-08-31
- **Tech-Stack:** Node.js + Express + MongoDB
- **Lizenz:** GPL-2.0
- **Beschreibung:** Archived Open-Source Real Estate Property Management System.
- **Gesamtpunktzahl:** 14.0/44 (31.8%)
- **Empfehlung:** **Ignorieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | N |
| DACH-Spezifisch | N |
| Lizenz | J |
| Tech-Stack-Kompatibilität | N |
| Code-Qualität | T |
| Aktiv gewartet | N |
| KI-Integration | N |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | N |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | T |
| PDF-Export / Berichte | T |
| DSGVO / Datenschutz | T |
| Community / Reife | N |

**Analyse & Begründung:** Archiviert, MongoDB, keine aktive Weiterentwicklung.

---

### etewiah/property_web_builder

- **URL:** https://github.com/etewiah/property_web_builder
- **Sterne:** 650
- **Letzte Aktivität:** 2026-10-27
- **Tech-Stack:** Ruby on Rails + PostgreSQL
- **Lizenz:** MIT
- **Beschreibung:** CMS/Website-Builder für Immobilienmakler mit CRM und MLS-Integration.
- **Gesamtpunktzahl:** 13.5/44 (30.7%)
- **Empfehlung:** **Ignorieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | N |
| Nebenkostenabrechnung | N |
| DACH-Spezifisch | N |
| Lizenz | J |
| Tech-Stack-Kompatibilität | N |
| Code-Qualität | J |
| Aktiv gewartet | J |
| KI-Integration | N |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | N |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | N |
| PDF-Export / Berichte | N |
| DSGVO / Datenschutz | T |
| Community / Reife | J |

**Analyse & Begründung:** Keine Mieterverwaltung, kein NK-Modul. Für Makler-Websites, nicht für unsere SaaS.

---

### jaskinner/tenant_portal

- **URL:** https://github.com/jaskinner/tenant_portal
- **Sterne:** 0
- **Letzte Aktivität:** 2024-05-12
- **Tech-Stack:** Vue.js + Vite + Pinia + Node/Express + MySQL
- **Lizenz:** ISC (laut README)
- **Beschreibung:** Work-in-progress Tenant Portal für Dokumente, Mietdetails und Kommunikation.
- **Gesamtpunktzahl:** 13.5/44 (30.7%)
- **Empfehlung:** **Ignorieren**

#### Checklisten-Bewertung

| Kriterium | Bewertung |
|-----------|-----------|
| Kerndatenmodell | J |
| Nebenkostenabrechnung | N |
| DACH-Spezifisch | N |
| Lizenz | T |
| Tech-Stack-Kompatibilität | T |
| Code-Qualität | T |
| Aktiv gewartet | N |
| KI-Integration | N |
| OCR / Belegscanning | N |
| Ticket-System / Kommunikation | T |
| eID / Verifikation | N |
| Mahnwesen / Zahlungsverfolgung | N |
| PDF-Export / Berichte | T |
| DSGVO / Datenschutz | T |
| Community / Reife | N |

**Analyse & Begründung:** Nur WIP, seit Mai 2024 inaktiv. Keine NK, keine DACH-Anpassung.

---

## Themen-Cluster

### 1. DACH-Mietverwaltung / NK-Abrechnung
Die relevantesten Projekte für unseren Kerngeschäftsbereich sind **fgilde/hausverwaltung**, **OliverHennhoefer/mietkartei.de**, **speedone/mietfuchs**, **s3gv/immobase** und **Nerbry72/NebenkostenFix**. Sie alle behandeln deutsches Mietrecht, BetrKV, HeizkostenV und CO2-Kostenaufteilung. **HaVeWa** und **mietkartei.de** bieten zudem moderne Web-Stacks mit PostgreSQL und KI-Schnittstellen (MCP).

### 2. Property-Management-Plattformen (international)
**OpenKos**, **OpenProperty**, **parcelis**, **condo**, **zite/property-management** und **Rentular** liefern gute Architektur-Muster für Objekte, Einheiten, Mieter, Verträge, Zahlungen und Tickets. Für DACH müssten sie jedoch mit deutschem Mietrecht und NK-Logik ergänzt werden. **condo** ist sehr groß, **OpenKos** hat ein ansprechendes Plugin-System.

### 3. OCR / Belegscanning
**bhimrazy/receipt-ocr** ist der klare Favorit: MIT-Lizenz, Python, FastAPI, Tesseract und LLM-OCR. **docket** und **free-ocr-api** ergänzen mit lokalem LLM/Ollama und MCP-Server. Für unsere Beleg-Scan-OCR-Funktion sind diese direkt übernehmbar oder als Microservice integrierbar.

### 4. KI-Assistenten / MCP-Server
**mietkartei.de**, **HaVeWa** und **free-ocr-api** bieten bereits MCP-Server. **agentic-ops/real-estate-mcp** ist eine gute allgemeine Referenz für MCP-Architektur in Python. **Klotzkette/claude-fuer-deutsches-recht** liefert wertvolle deutsche Rechts-Prompts, die als Wissensbasis für unseren KI-Assistenten genutzt werden können.

### 5. eID / Personalausweis
**Governikus/AusweisApp** ist die offizielle Referenz. Für eine Web-SaaS wird man nicht den C++-Client übernehmen, sondern das SDK/SDK-Wrapper oder die Online-Ausweis-Funktion über die offizielle API/Smartphone-App einbinden. Weitere Wrapper für Android/iOS existieren im Governikus-Account.

### 6. Tenant Portale / Mieterkommunikation
**HaVeWa**, **mietkartei.de**, **immobase**, **condo**, **OpenProperty** und **OpenKos** bringen bereits Mieter-/Eigentümerportale mit. **jaskinner/tenant_portal** ist zu unreif.

## Handlungsempfehlungen

1. **Sofort studieren / als Referenz nutzen:**
   - `fgilde/hausverwaltung` – umfassendste DACH-Feature-Referenz mit modernem Stack.
   - `OliverHennhoefer/mietkartei.de` – deutsche Privatvermieter-Zielgruppe + MCP-Server.
   - `speedone/mietfuchs` – sehr detaillierte NK/Heizkosten/CO2-Logik.
   - `s3gv/immobase` – WEG/Hausgeld-Logik für deutsche Hausverwaltungen.

2. **OCR-Modul integrieren / übernehmen:**
   - `bhimrazy/receipt-ocr` als Basis-Engine für Beleg-Scanning.
   - `KazKozDev/docket` als Fallback für lokale LLM-basierte Extraktion.
   - `Ethos6/free-ocr-api` als selbst gehostete OCR-API mit MCP-Anbindung prüfen.

3. **KI-Assistent / MCP-Strategie:**
   - MCP-Server nach Vorbild von `mietkartei.de` und `HaVeWa` für unseren KI-Assistenten entwickeln.
   - Prompts/Wissensbasis aus `Klotzkette/claude-fuer-deutsches-recht` für Mietrecht/NK prüfen.

4. **eID-Anbindung:**
   - `Governikus/AusweisApp` und SDK-Wrapper evaluieren; technische Integration über Smartphone-App + Browser-Redirect.

5. **Ignorieren / keine Priorität:**
   - International/Laravel/PHP/MERN-Projekte ohne DACH-Fokus (`mohsin-rafique`, `OpenKos`, `movinin`, `bigprof`, `property_web_builder`, `orpms`, `loca`).
   - Lizenz-problematische Projekte (`microrealestate` SUL, `nebencheck` PolyForm Noncommercial, `Dachly` BSL).
