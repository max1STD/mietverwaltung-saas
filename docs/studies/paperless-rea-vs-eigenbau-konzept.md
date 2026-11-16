# Konzept: Paperless-ngx per REA (Reverse Engineer Anything) reverse-engineern und selbst bauen

**Datum:** 16. November 2026  
**Autor:** Hermes Agent  
**Scope:** Bewertung des Ansatzes, Paperless-ngx durch Reverse Engineering als Eigenentwicklung nachzubauen, statt es direkt einzubinden.

---

## 1. Ausgangslage

GitHub Topic „reverse-engineer-anything“ ist keine einzelne Software, sondern ein Trend/Ansatz: Agenten oder Menschen analysieren bestehende Anwendungen (Binärdateien, Web-Apps, APIs, Datenbanken) und bauen funktional äquivalente Eigenlösungen. Die Repositories darunter sind meist:

- Curated Lists mit REA-Fällen (`awesome-reverse-engineer-anything`, `awesome-rea`)
- Skill-Sammlungen und Prompts (`REA_Skill`, `rea-pro-max`)
- Spezialwerkzeuge für Binär-Analyse (`DecompileAnything`, `REA-Windows-Github`)
- Agent-Workflows für Code-Rekonstruktion (`rea-pro-max`, `ReaFuse`)

Die Idee für unser Projekt wäre: **Paperless-ngx analysieren und eine schlankere Eigenvariante bauen**, die exakt auf unser Mietverwaltung-SaaS zugeschnitten ist.

---

## 2. Was müssten wir reverse-engineern?

Paperless-ngx ist Open Source. „Reverse Engineering“ würde hier also primär bedeuten:

1. **Quellcode lesen und verstehen** (kein klassisches RE von Binärdateien).
2. **Datenmodell, API-Verhalten und Dateiverarbeitung** nachvollziehen.
3. **OCR-Pipeline** (Tesseract) und Consumer-Logik replizieren.
4. **Volltextsuche** (PostgreSQL oder Tantivy) nachbauen.
5. **Upload/Tagging/Custom-Fields/Versionierung** in unserem Stack umsetzen.

---

## 3. Pro — Warum REA / Eigenbau sinnvoll sein könnte

### 3.1 Vollständige Kontrolle über Architektur

| Aspekt | Vorteil |
|--------|---------|
| Datenmodell | Exakt auf Mieter, Objekte, Einheiten, Verträge zugeschnitten |
| API | Nur die Endpunkte, die wir wirklich brauchen |
| Lizenz | Kein GPL-Copyleft, eigener Code bleibt proprietär |
| UI/UX | 100 % unser Design, keine eingebettete Paperless-Oberfläche |

### 3.2 Kein zusätzlicher Container-Stack

Wir würden nicht gleichzeitig Django, PostgreSQL-Instanz für Paperless, Redis, Celery, Gotenberg und Tika betreiben müssen. Stattdessen alles in unserem bestehenden FastAPI-Stack.

### 3.3 Kein Auth-Sync-Problem

Berechtigungen laufen komplett über unsere bestehende User/Role-Logik. Kein OIDC, kein Remote-User-Header, kein Service-Account-Management.

### 3.4 Optimierter Scope

Paperless-ngx kann viel mehr, als wir brauchen (Benutzergruppen, E-Mail-Import, komplexe Workflows). Eine Eigenlösung würde nur MVP-Features enthalten.

### 3.5 Wiederverwendbare Komponenten

Wir haben bereits:
- Python/FastAPI-Backend
- PostgreSQL
- SQLAlchemy
- PDF-Generierung
- Audit-Log

Diese Basis kann direkt erweitert werden.

---

## 4. Contra — Warum REA / Eigenbau riskant ist

### 4.1 Reverse Engineering ist hier teilweise irreführend

Paperless-ngx ist Open Source. Es gibt also keinen geschlossenen Black-Box-Code, den wir „knacken“ müssten. Der Arbeitsschritt wäre in Wahrheit ein **Code-Review und eine Neuimplementierung** — kein klassisches RE.

### 4.2 OCR + Volltextsuche sind komplexer als sie aussehen

| Feature | Was Paperless bereits hat | Was wir selbst bauen müssten |
|---------|----------------------------|------------------------------|
| OCR | Tesseract + intelligente Vorverarbeitung (DPI, Deskewing) | Eigenen Wrapper bauen |
| Volltextsuche | Tantivy-Index oder PostgreSQL-Fulltext mit Ranking | Eigenen Index/Schema entwerfen |
| Thumbnails/PDF-Preview | Pillow + Preview-Rendering | Eigene Pipeline |
| Async Consumer | Celery + Redis | Eigene Background-Jobs (z. B. Dramatiq/APScheduler) |
| Office-Dokumente → PDF | Gotenberg + Tika | Weitere Container oder Bibliotheken |

### 4.3 Hoher Zeitaufwand

| Modul | Geschätzter Aufwand |
|-------|---------------------|
| Datenmodell + Upload | 1–2 Tage |
| Listenansicht + Download | 1–2 Tage |
| OCR-Integration (Tesseract) | 2–4 Tage |
| Volltextsuche (Postgres Fulltext oder Meilisearch) | 3–5 Tage |
| PDF-Preview + Thumbnails | 2–3 Tage |
| Frontend-Reiter in 4 Views | 3–5 Tage |
| Versionierung + Löschkonzept | 1–2 Tage |
| Tests + Edge Cases | 3–5 Tage |
| **Gesamt** | **ca. 2–4 Wochen** für einen soliden MVP |

Vergleich: Paperless-Einbindung nach bestehendem Konzept wäre in **ca. 1 Woche** einsatzbereit.

### 4.4 Langfristige Wartung

Paperless-ngx wird aktiv weiterentwickelt. Wenn wir selbst bauen, müssen wir:
- OCR-Probleme selbst debuggen,
- neue PDF-/Office-Formate unterstützen,
- Sicherheitsupdates für Dateiuploads selbst umsetzen,
- Suchindex warten.

### 4.5 Fehleranfälligkeit bei skurrilen PDFs

Paperless hat jahrelang Edge Cases gelernt (gescannte Misch-PDFs, kaputte Office-Dokumente, falsche MIME-Types). Dieses Wissen müssten wir mühsam neu aufbauen.

---

## 5. Was „REA“ konkret für uns bedeuten würde

### Variante A: Agent-gestütztes Code-Review
- Wir/du/Hermes lesen den Paperless-Quellcode.
- Extraktion der relevanten Module: Consumer, Document-Model, Tesseract-Wrapper, API-Schema.
- Neuimplementierung in unserem Stack.
- **Nutzen:** Gutes Verständnis, aber kein echter Zeitgewinn gegenüber klassischem Engineering.

### Variante B: Reimplementierung ohne Paperless-Code als Vorlage
- Wir bauen ein minimales DMS basierend auf bekannten Patterns.
- **Nutzen:** Sauberer Code, keine GPL-Probleme.
- **Nachteil:** Länger, weil wir nicht auf bewährte Paperless-Implementierung zurückgreifen.

### Variante C: Hybrider Ansatz (Empfehlung)
- **Eigenes DMS sofort bauen** für einfache Dateiablage.
- **Paperless-ngx optional** später als OCR/Such-Backend anbinden, falls der Bedarf wächst.
- **Vorteil:** Schneller MVP + Zukunftssicherheit.

---

## 6. Entscheidungsmatrix

| Kriterium | Paperless direkt einbinden | Eigenbau per REA |
|-----------|---------------------------|------------------|
| Time-to-MVP | ⭐⭐⭐⭐⭐ Schnell (1 Woche) | ⭐⭐⭐ Langsam (2–4 Wochen) |
| Langfristige Wartung | ⭐⭐⭐⭐ Community-Updates | ⭐⭐⭐ Eigene Verantwortung |
| DSGVO / Self-Hosting | ⭐⭐⭐⭐⭐ Möglich | ⭐⭐⭐⭐⭐ Möglich |
| Design-Kontrolle | ⭐⭐⭐ Unsere UI, Paperless im Hintergrund | ⭐⭐⭐⭐⭐ 100 % eigene UI |
| Lizenzflexibilität | ⭐⭐ GPL-3.0 zu prüfen | ⭐⭐⭐⭐⭐ Eigener Code |
| OCR + Suche out-of-the-box | ⭐⭐⭐⭐⭐ Vorhanden | ⭐⭐⭐ Muss gebaut werden |
| Skalierung | ⭐⭐⭐⭐ Erprobt | ⭐⭐⭐ Hängt von Eigenbau ab |
| Lernkurve / Risiko | ⭐⭐⭐⭐ Gering | ⭐⭐⭐ Hoch |

---

## 7. Fazit / Empfehlung

**Für unseren aktuellen Stand ist der Eigenbau per REA nicht die effizienteste Route.**

Paperless-ngx direkt einzubinden (wie im vorherigen Konzept beschrieben) spart 1–3 Wochen Entwicklung und liefert sofortige OCR + Volltextsuche. Der vermeintliche „Reverse Engineering“-Vorteil entfällt, weil Paperless Open Source ist — wir würden also nichts knacken, sondern lediglich den Code studieren und neu schreiben.

**Empfohlener Weg:**
1. **Kurzfristig:** Paperless-ngx als unsichtbares Archiv einbinden (bestehendes Konzept).
2. **Optional später:** Wenn die Eigenlösung strategisch gewünscht ist, schrittweise eigene DMS-Features ergänzen und Paperless-ngx nur noch als OCR-Engine zu nutzen.

---

## 8. Risiko-Minderung für den empfohlenen Weg

| Bedenken | Gegenmaßnahme |
|----------|---------------|
| GPL-Lizenz | Eigenen Code nicht mit Paperless verlinken; nutze nur REST-API |
| Zusätzliche Infrastruktur | Paperless-Container optional; nur aktivieren, wenn gewünscht |
| Auth-Sync | Service-Account pro Vermieter, Berechtigungen in unserem Backend |
| UI-Fragmentierung | Kein Paperless-Login für Endnutzer; alles über unsere UI |

---

## 9. Nächste Schritte

1. Entscheidung: Paperless direkt einbinden oder doch Eigenbau?
2. Falls Paperless: Infra-Docker-Compose + API-Client + `dokumente`-Tabelle bauen.
3. Falls Eigenbau: Minimal-DMS (Upload/Download/Liste) zuerst, OCR/Suche später.

---

*Ende des Konzepts.*
