# Studie: Open-Source-Dokumenten-Tools für das Mietverwaltung-SaaS

**Datum:** 15. November 2026  
**Autor:** Hermes Agent  
**Scope:** Bewertung von Paperless-ngx, Stirling PDF und weiteren Open-Source-Tools als Ergänzung für die Dokumentenverwaltung im Mietverwaltung-SaaS.

---

## 1. Zusammenfassung / Executive Summary

Das Mietverwaltung-SaaS hat aktuell eine eigene **Dokumenten-Generierung** (PDF: Mahnung, Wohnungsgeberbestätigung) und **OCR** (Tesseract), aber kein zentrales Dokumentenarchiv mit Volltextsuche, Versionierung oder automatischer Klassifizierung.

**Empfehlung:**
- **Kurzfristig (MVP):** Integration von **Paperless-ngx** als externes, selbst gehostetes Dokumentenarchiv. Es bietet OCR, Volltextsuche, Tags, REST-API und passt am besten zu einem Mietverwaltungs-Workflow (Mietverträge, Nebenkostenabrechnungen, Korrespondenz).
- **Ergänzend:** **Stirling PDF** als PDF-Swiss-Army-Knife für gelegentliche Manipulationen (Merge, Split, Komprimieren, OCR), wenn diese Funktionen nicht selbst gebaut werden sollen.
- **Später optional:** **DocuSeal** für elektronische Unterschriften (Mietverträge online signieren lassen).
- **Nicht empfohlen für MVP:** Mayan EDMS (zu schwer), Docspell (zu kleine Community), reine Nextcloud-Lösung (kein DMS-Metadatenmodell).

---

## 2. Anforderungen an ein Dokumentenmanagement im Mietverwaltungs-Kontext

| Anforderung | Gewichtung | Begründung |
|-------------|------------|------------|
| Selbst-Hosting / Datenhoheit | Hoch | Mietverträge und Finanzdaten dürfen nicht in US-Clouds landen (DSGVO). |
| OCR & Volltextsuche | Hoch | Scans von Mietverträgen, Kostenabrechnungen etc. müssen durchsuchbar sein. |
| REST-API | Hoch | Einbindung in bestehende Mieter/Objekt/Mietvertrag-Entitäten. |
| Tagging / Metadaten | Hoch | Dokumente müssen Mieter, Objekt, Mietvertrag, Jahr, Typ zugeordnet werden. |
| Versionierung | Mittel | Vertragsänderungen und Abrechnungskorrekturen nachvollziehbar. |
| geringer Admin-Aufwand | Hoch | Projekt hat begrenzte Ops-Kapazität. |
| PDF-Manipulation | Mittel | Merge, Split, Komprimieren, ggf. Formularfelder. |
| E-Signatur | Niedrig-Mittel | Für später: Mietverträge digital signieren lassen. |
| Lizenzkompatibilität | Hoch | Kommerzielle Nutzung muss möglich sein. |

---

## 3. Paperless-ngx

### 3.1 Was ist es?
Paperless-ngx ist ein selbst gehostetes Dokumentenmanagement-System für Privatanwender und kleine Teams. Es wandelt Papierdokumente, PDFs und Bilder in eine durchsuchbare digitale Ablage um.

### 3.2 Technische Basis
- **Stack:** Django, PostgreSQL, Redis, Celery, Tesseract OCR, optional Tika/Gotenberg für Office-Dokumente.
- **Lizenz:** GPL-3.0 (kommerzielle Nutzung möglich, aber Copyleft).
- **Deployment:** Docker Compose (offizielle Templates vorhanden).
- **API:** Vollständige REST-API (Token/Basic/Session/OIDC), browsable unter `/api/schema/view/`.
- **Stars:** ca. 48.000 GitHub-Stars, sehr aktive Community.

### 3.3 Für uns relevante Features
- **OCR & Volltextsuche** über Tantivy/PostgreSQL.
- **Auto-Tagging & Korrespondenten-Erkennung** via trainierbaren Regeln (z. B. „Vermieter XY“ = Mieter-ID).
- **Custom Fields** für Metadaten wie Mieter-ID, Objekt-ID, Mietvertrags-ID.
- **Workflows** (Consume-Templates) für automatisierte Ablage.
- **Document Links** zwischen Dokumenten.
- **Versionierung** von Dokumenten.
- **REST-Upload** `/api/documents/post_document/` mit Multipart.
- **Download/Preview/Thumbnail** Endpunkte.
- **Object-Level Permissions** (Owner, View/Change für User/Groups).

### 3.4 Integrationsmöglichkeit
Paperless-ngx würde **parallel** zum Mietverwaltung-SaaS laufen. Unsere App speichert nur die `paperless_document_id` am Mieter, Objekt oder Mietvertrag und ruft bei Bedarf Preview/Download ab.

```
[Mietverwaltung-SaaS]  <-- REST/Token -->  [Paperless-ngx]
     |
     | speichert paperless_document_id
     v
[PostgreSQL: mieter_dokumente]
```

### 3.5 Pro / Contra

| Pro | Contra |
|-----|--------|
| Reifer, stabiler Stack | GPL-3.0: eigene Änderungen müssen offengelegt werden, wenn verteilt |
| Sehr gute OCR & Suche | zusätzlicher Container-Stack (PostgreSQL, Redis, Paperless) |
| Starke Auto-Klassifizierung | Trennung von Auth: Nutzer müssen in Paperless separat existieren oder über OIDC/Remote-User angebunden werden |
| Einfacher REST-Upload | UI-Design passt nicht 1:1 zu unserem SaaS-Look |
| Große Community, viele How-Tos | consume-Verhalten asynchron: Upload liefert Task-ID, nicht sofort Dokumenten-ID |

---

## 4. Stirling PDF

### 4.1 Was ist es?
Stirling PDF ist eine Open-Source-PDF-Plattform mit 50+ Werkzeugen zum Bearbeiten, Konvertieren, Komprimieren, Signieren, Redigieren und OCR von PDFs.

### 4.2 Technische Basis
- **Stack:** Java/Spring, TypeScript, Python (AI-Engine optional).
- **Lizenz:** Open-Core. Community-Edition ist kostenlos, aber einige Enterprise-Features (SSO, erweiterte Pipelines) sind kostenpflichtig.
- **Deployment:** Docker (`latest`, `latest-fat` mit AI, `latest-ultra-lite`), JAR.
- **API:** REST-API für fast alle Tools; Server-JAR ohne UI verfügbar.
- **Stars:** ca. 96.000 GitHub-Stars.

### 4.3 Für uns relevante Features
- **PDF-Merge/Split/Rotate/Compress**.
- **OCR** für gescannte PDFs.
- **PDF-Formulare** erstellen/ausfüllen.
- **Redaktion** für sensitive Daten.
- **Signatur** (einfache elektronische Signatur).
- **Pipelines** für automatisierte Verarbeitung (Team/Enterprise).
- **REST-API** für alle Operationen.

### 4.4 Integrationsmöglichkeit
Stirling PDF ist **kein Archiv**, sondern eine **PDF-Werkzeugkiste**. Sinnvoller Einsatz:
- Vor dem Upload nach Paperless: PDFs komprimieren oder OCR erzwingen.
- Vor dem Versand an Mieter: mehrere PDFs mergen oder Seiten neu sortieren.
- Im Frontend: „PDF zusammenfassen“ / „PDF komprimieren“ Buttons, die an Stirling-API delegieren.

```
[Mietverwaltung-SaaS]  <-- REST -->  [Stirling PDF]
     |
     | generiertes/empfangenes PDF
     v
[Manipulation] --> [zurück an App oder nach Paperless]
```

### 4.5 Pro / Contra

| Pro | Contra |
|-----|--------|
| Sehr einfacher Docker-Start | Kein Dokumentenarchiv, keine Volltextsuche über eigenen Bestand |
| Umfangreiche PDF-Tools | Open-Core: einige Features kostenpflichtig |
| Große Community | UI/UX passt nicht zu unserem Design |
| REST-API für fast alles | Für reine Archivierung die falsche Wahl |
| Läuft ohne Datenbank | Keine dauerhafte Dokumentenverknüpfung zu Mieter/Objekt |

---

## 5. Alternativen im Überblick

### 5.1 Mayan EDMS
- **Stack:** Django, PostgreSQL.
- **Lizenz:** Apache 2.0 (seit 2024 – sehr kommerziell-freundlich).
- **Features:** Enterprise-DMS, Workflows, Fine-Grained Permissions, Metadata, Versioning, Audit-Log.
- **Einschätzung:** Zu mächtig und ressourcenintensiv für den MVP. Sinnvoll, wenn später Compliance/Workflows wichtig werden.

### 5.2 Docspell
- **Stack:** Scala, PostgreSQL/MariaDB/H2, SOLR.
- **Lizenz:** AGPL-3.0 (starkes Copyleft).
- **Features:** OCR, Auto-Tagging, Volltextsuche, REST-API, E-Mail-Import.
- **Einschätzung:** Kleine Community, AGPL ist für kommerzielle SaaS-Einbindung problematisch. Nur wenn Datenschutz-Maximalismus wichtiger als Ökosystem ist.

### 5.3 Teedy (sismics/docs fork)
- **Stack:** Java/Jetty, H2/PostgreSQL.
- **Lizenz:** GPL-2.0.
- **Features:** Lightweight, OCR, Workflows, AES-Verschlüsselung, REST-API, LDAP/OIDC, Audit-Log.
- **Einschätzung:** Gute Alternative zu Paperless-ngx, aber kleineres Ökosystem. Paperless-ngx hat bessere Auto-Klassifizierung und mehr Community-Templates.

### 5.4 DocuSeal
- **Stack:** Ruby on Rails, PostgreSQL/MySQL/SQLite.
- **Lizenz:** AGPL-3.0 (Open Source), Pro-Lizenz für erweiterte Features.
- **Features:** E-Signatur, Templates, Audit-Trail, REST-API, Embeddable Form, Webhooks.
- **Einschätzung:** Nicht als Archiv gedacht, sondern für elektronische Signaturen. Später interessant für Mietverträge, aber nicht für Dokumentenverwaltung.

### 5.5 Nextcloud + Files / Collectives
- **Features:** Dateiablage, Sharing, Kommentare, einfache Volltextsuche.
- **Einschätzung:** Kein echtes DMS-Metadatenmodell. Nur sinnvoll, wenn der Nutzer ohnehin Nextcloud betreibt und nur Dateien ablegen will.

---

## 6. Vergleichstabelle

| Kriterium | Paperless-ngx | Stirling PDF | Mayan EDMS | Teedy | DocuSeal |
|-----------|---------------|--------------|------------|-------|----------|
| Archivierung | ✅ | ❌ | ✅ | ✅ | ❌ |
| OCR | ✅ | ✅ | ✅ | ✅ | ❌ |
| Volltextsuche | ✅ | ❌ | ✅ | ✅ | ❌ |
| REST-API | ✅ | ✅ | ✅ | ✅ | ✅ |
| Auto-Tagging | ✅ | ❌ | ✅ | teilweise | ❌ |
| Versionierung | ✅ | ❌ | ✅ | ✅ | ❌ |
| PDF-Tools | Grundlegend | ✅ Umfangreich | Grundlegend | Grundlegend | Nur Signatur |
| E-Signatur | ❌ | Einfach | ❌ | ❌ | ✅ |
| Deployment-Aufwand | Mittel | Sehr gering | Hoch | Mittel | Gering |
| Lizenz | GPL-3.0 | Open-Core | Apache 2.0 | GPL-2.0 | AGPL-3.0 |
| Community / Reife | Sehr groß | Sehr groß | Mittel | Klein | Mittel |
| Passend für MVP | ✅ | Ergänzend | ❌ | Alternativ | Später |

---

## 7. Empfohlenes Architektur-Szenario

### 7.1 Phase 1: Paperless-ngx als externes Archiv
1. Paperless-ngx via Docker Compose neben dem Mietverwaltung-SaaS betreiben.
2. API-Token in `.env` hinterlegen.
3. Neue Tabelle `dokumente` (oder `mieter_dokumente`, `objekt_dokumente`, `mietvertrag_dokumente`) mit `paperless_document_id`, `typ`, `titel`, `uploaded_at`.
4. Frontend: „Dokument hochladen“ → Backend leitet an Paperless-ngx weiter, speichert ID.
5. Frontend: Dokumentenliste mit Preview/Download-Links von Paperless-ngx.
6. Paperless-Workflows: Auto-Tag „Mietverwaltung“ + Custom Fields für Mieter-ID/Objekt-ID.

### 7.2 Phase 2: Stirling PDF als PDF-Werkzeug
1. Stirling PDF Container starten (optional, nur wenn benötigt).
2. Backend-Endpunkte für häufige Operationen:
   - `/api/v1/dokumente/{id}/compress`
   - `/api/v1/dokumente/merge`
   - `/api/v1/dokumente/{id}/ocr` (falls Paperless-OCR nicht reicht)
3. Frontend: Aktionen-Buttons im Dokumenten-Detail.

### 7.3 Phase 3: DocuSeal für E-Signatur (optional)
1. DocuSeal self-hosted für Mietverträge.
2. Template mit Mietvertragsfeldern.
3. API-Integration: Senden an Mieter zur Unterschrift, Webhook-Empfang nach Signatur, Archivierung in Paperless-ngx.

---

## 8. Pro / Contra der Integration insgesamt

### Pro
- **Schneller Gewinn:** Ohne eigenes DMS bauen zu müssen, sofort OCR + Archiv + Suche.
- **DSGVO-konform:** Daten bleiben auf eigener Infrastruktur.
- **Fokus bleibt beim Kernprodukt:** Wir müssen keine OCR-Pipeline, keine PDF-Viewer-Engine, keinen Suchindex selbst pflegen.
- **Erweiterbar:** Paperless-ngx kann später durch Mayan EDMS ersetzt werden, wenn Enterprise-Features nötig werden.

### Contra
- **Zusätzliche Infrastruktur:** Mindestens ein weiterer Container-Stack.
- **Auth-Synchronisation:** Paperless-ngx hat eigenes User-Management. Single-Sign-On via OIDC/Remote-User ist möglich, aber zusätzlicher Aufwand.
- **Lizenz GPL-3.0:** Bei kommerzieller SaaS-Nutzung und Verteilung beachten; in der Regel kein Problem bei Self-Hosting, aber juristisch zu prüfen.
- **UI-Fragmentierung:** Nutzer wechseln zwischen unserer App und Paperless-ngx, wenn nicht sauber eingebettet.

---

## 9. Empfehlung

1. **Paperless-ngx als primäres Dokumentenarchiv einführen.** Es ist der beste Kompromiss aus Reife, Features, API und Community für einen Mietverwaltungs-Workflow.
2. **Stirling PDF als optionale PDF-Werkzeugkiste bereitstellen**, aber nicht zwingend im MVP. Es ist nützlich, wenn häufig PDFs vor der Archivierung manipuliert werden müssen.
3. **DocuSeal erst in einer späteren Phase evaluieren**, wenn elektronische Signaturen für Mietverträge gefordert werden.
4. **Mayan EDMS nicht für den MVP wählen** – der Admin-Overhead und die Komplexität überwiegen.
5. **Lizenz und Datenschutz mit dem Hausjuristen / Datenschutzbeauftragten abgleichen** vor produktivem Einsatz.

---

## 10. Nächste Schritte / TODOs

- [ ] Entscheidung des Product-Owners: Paperless-ngx ja/nein?
- [ ] Lizenz-Check GPL-3.0 im kommerziellen SaaS-Kontext (Self-Hosting vs. Verteilung).
- [ ] PoC: Paperless-ngx in Docker Compose neben dem Projekt starten.
- [ ] PoC: Upload eines Mietvertrags-PDFs via REST-API und Speicherung der `paperless_document_id` in unserer DB.
- [ ] Design: Datenmodell `dokumente` (Zuordnung Mieter/Objekt/Mietvertrag + Typ + Jahr).
- [ ] Auth-Strategie: API-Token vs. OIDC/Remote-User vs. separater Paperless-Benutzer pro Vermieter.
- [ ] Optional: Stirling PDF Container für PDF-Komprimierung/Merge vorbereiten.

---

*Ende der Studie.*
