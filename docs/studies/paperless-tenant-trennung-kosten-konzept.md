# Konzept: Tenant-Trennung und Mehrkosten bei Paperless-ngx-Einbindung

**Datum:** 16. November 2026  
**Autor:** Hermes Agent  
**Scope:** Was Paperless-ngx für das Mietverwaltung-SaaS konkret besser macht, was nicht, wie wir saubere Tenant-Trennung aufbauen, und welche Mehrkosten pro Vermieter entstehen.

---

## 1. Ausgangslage

Paperless-ngx ist ein selbst gehostetes Dokumentenmanagement-System. Es bietet OCR, Volltextsuche, Vorschau und Speicherung. Für unser Mietverwaltung-SaaS muss aber klar sein:

- Was genau übernimmt Paperless für uns?
- Was bleibt bei uns?
- Wie trennen wir Vermieter-Daten sauber voneinander?
- Was kostet das pro Vermieter?

---

## 2. Was Paperless-ngx für uns besser macht

| Funktion | Was Paperless leistet | Warum das für uns wertvoll ist |
|----------|-----------------------|--------------------------------|
| **OCR** | Tesseract-basierte Texterkennung für PDFs und Bilder | Wir müssen keinen eigenen OCR-Wrapper bauen |
| **Volltextsuche** | Suchindex über alle Dokumenteninhalte | Wir müssen keinen eigenen Suchindex (Elasticsearch/Meilisearch) betreiben |
| **PDF-Vorschau / Thumbnails** | Browser-fähige Preview und Download-Links | Wir müssen keinen PDF-Renderer selbst bauen |
| **Asynchrone Verarbeitung** | Upload liefert Task, Consumer verarbeitet im Hintergrund | Wir müssen keine eigene Background-Job-Pipeline für OCR bauen |
| **Dokumenten-Versionierung** | Versionen pro Dokument speichern | Für Vertragsänderungen und Abrechnungskorrekturen |
| **Metadaten (Tags, Custom Fields)** | Zuordnung von Mieter/Objekt/Vertrag möglich | Wir können Dokumente strukturiert kategorisieren |
| **Reife & Community** | Ca. 48.000 GitHub-Stars, aktive Entwicklung | Weniger Bugfixes und Edge-Cases selbst lösen |
| **Selbst-Hosting** | Läuft auf eigener Infrastruktur | DSGVO-konform, Datenhoheit |

**Zusammengefasst:** Paperless ist besser, sobald OCR und Volltextsuche ins Spiel kommen. Ohne diese beiden Features wäre eine Eigenentwicklung deutlich einfacher zu rechtfertigen.

---

## 3. Was Paperless-ngx für uns NICHT besser macht

| Funktion | Problem | Was wir selbst machen müssen |
|----------|---------|------------------------------|
| **Multi-Tenancy** | Paperless kennt keine echte Mandanten-Trennung | Berechtigungen und Tenant-Filter in unserer App |
| **Vermieter-spezifisches Datenmodell** | Mieter/Objekt/Einheit/Vertrag sind unser Domain-Modell | Mapping-Tabelle `dokumente` in unserer DB |
| **Nutzer-Authentifizierung** | Paperless hat eigenes Login | Kein direkter Nutzer-Login; unsere App spricht für Nutzer |
| **Admin-Zugriffsschutz** | Paperless-Admin sieht alle Dokumente | Prozess/Policy oder Verschlüsselung |
| **UI/Design** | Paperless-UI passt nicht zu unserem SaaS | Unsere App zeigt alles im eigenen Design |
| **Preisstaffelung / Abrechnung** | Kein Bezug zu unserem Billing | Eigenes Monitoring / Limits |
| **Compliance-Granularität** | Kein feingranulares Audit-Log pro Mandant | Eigenes Audit-Log |

**Zusammengefasst:** Paperless ist ein großartiges Dokumentenarchiv, aber kein mandantenfähiges SaaS-Backend. Alles, was Vermieter, Berechtigungen und unser Domain-Modell betrifft, bleibt bei uns.

---

## 4. Tenant-Trennung: die richtige Architektur

Es gibt vier mögliche Sicherheitsstufen:

### Stufe 1: Shared Instance + App-Filter (einfach, aber nicht audit-sicher)
- Eine Paperless-Instanz für alle Vermieter.
- Ein Service-Account `mietverwaltung-app` besitzt alle Dokumente.
- Unsere App filtert per `vermieter_id` in der `dokumente`-Tabelle.
- **Problem:** Wenn ein Bug in unserer App oder ein Leak im Service-Token passiert, sind alle Daten potenziell zugänglich.

### Stufe 2: Shared Instance + pro-Vermieter Paperless-User (empfohlen für MVP)
- Jeder Vermieter bekommt einen eigenen Paperless-Benutzer mit eigenem API-Token.
- Dokumente werden mit diesem Benutzer als **Owner** hochgeladen.
- Paperless-Permission-System sorgt dafür, dass Vermieter A nur seine eigenen Dokumente über seinen Token sieht.
- Unsere App verwaltet die Token sicher und wählt beim API-Aufruf den richtigen Token.
- **Vorteil:** Paperless selbst erzwingt die Trennung auf Objekt-Ebene.
- **Restrisiko:** Paperless-Admin-Account sieht weiterhin alle Dokumente.

### Stufe 3: Pro-Vermieter Paperless-Instanz (100 % Trennung, aber teuer)
- Pro Vermieter läuft eine eigene Paperless-Datenbank und ein eigener Speicherpfad.
- **Vorteil:** Absolute Datenbank- und Dateisystem-Trennung.
- **Nachteil:** Hoher Ressourcenverbrauch, Container-Verwaltung, Backup-Komplexität.
- **Eignung:** Nicht für MVP, erst ab sehr hohen Sicherheitsanforderungen oder wenigen Enterprise-Kunden.

### Stufe 4: Shared Instance + client-seitige Verschlüsselung (maximale Sicherheit, aber einschränkend)
- Dokumente werden vor dem Upload mit einem pro-Vermieter-Schlüssel verschlüsselt.
- Paperless speichert nur verschlüsselte Daten.
- **Vorteil:** Selbst Admin sieht nur Cipher-Text.
- **Nachteil:** OCR und Volltextsuche in Paperless funktionieren nicht mehr, weil Paperless den Inhalt nicht lesen kann.
- **Eignung:** Nur sinnvoll, wenn OCR/Suche nicht benötigt werden.

---

## 5. Empfohlene Architektur für den Start

**Stufe 2: Shared Instance + pro-Vermieter Paperless-User**

Diese Variante bietet den besten Kompromiss aus Sicherheit, Kosten und Aufwand.

### Konkrete Umsetzung

1. **Paperless-ngx intern betreiben**
   - Nur über internes Docker-Netzwerk oder localhost erreichbar.
   - Kein öffentlicher Port, keine öffentliche URL.

2. **Pro Vermieter ein Paperless-User**
   - Beim Anlegen eines Vermieters in unserer App wird automatisch ein Paperless-Benutzer erstellt.
   - API-Token wird verschlüsselt in unserer Datenbank gespeichert.
   - Token wird niemals an das Frontend weitergegeben.

3. **Dokumente mit Owner hochladen**
   - Upload-Aufruf an Paperless verwendet den Vermieter-Token.
   - Dokument wird mit diesem Benutzer als Owner angelegt.
   - Custom Fields: `vermieter_id`, `entity_type`, `entity_id`, `typ`, `jahr`.

4. **Berechtigungsprüfung doppelt**
   - Paperless-Permission-System: Owner darf nur eigene Dokumente sehen.
   - Unsere App: `vermieter_id`-Filter auf jeder Datenbankabfrage.

5. **Keine Paperless-UI für Endnutzer**
   - Vermieter kennen keinen Paperless-Login.
   - Admin-Zugriff auf Paperless-UI nur bei Notfall/Wartung.

6. **Audit-Log**
   - Jeder Upload, Download, Vorschau und Löschvorgang wird in unserem Audit-Log protokolliert.

---

## 6. Was ist mit Admin-Zugriff?

| Szenario | Lösung |
|----------|--------|
| Vermieter A sieht Dokumente von Vermieter B | Verhindert durch Paperless-Owner + App-Filter |
| Ich als Admin sehe alle Dokumente in Paperless | Technisch möglich, daher: Paperless-Admin-Zugang nur für Wartung, keine Routine-Nutzung |
| Ich will als Admin grundsätzlich nichts sehen | Erfordert Verschlüsselung → dann fällt OCR/Suche weg |
| Externer Angreifer greift Paperless direkt an | Verhindert durch Netzwerk-Trennung: Paperless ist nicht öffentlich |

**Empfehlung:** Akzeptiere, dass der Admin technisch Zugriff hat, aber dokumentiere und beschränke diesen Zugriff durch Policy. Das ist bei Self-Hosting-SaaS üblich und juristisch mit DSGVO vereinbar, solange Zugriffe protokolliert und legitimiert sind.

---

## 7. Mehrkosten pro Vermieter

### Kostenmodell Shared Instance (empfohlen)

| Ressource | Basis-Kosten (pro Server) | Pro-Vermieter-Anteil |
|-----------|---------------------------|----------------------|
| Server / VM | ca. 5–20 €/Monat | ca. 0,05–0,50 €/Monat |
| RAM (1–2 GB für Paperless) | im Server enthalten | ca. 0,01–0,10 €/Monat |
| CPU (OCR verbraucht nur beim Upload) | shared | vernachlässigbar |
| Speicher für Dokumente | ca. 0,02–0,05 €/GB/Monat | ca. 0,50–2,00 €/Monat bei moderater Menge |
| Backup | ca. 1–5 €/Monat | ca. 0,01–0,05 €/Monat |
| **Gesamt pro Vermieter** | – | **ca. 0,50–3,00 €/Monat** |

Bei 100 Vermietern und einem durchschnittlichen Dokumentenvolumen liegen die Mehrkosten also im **Unter-3-Euro-Bereich pro Vermieter und Monat**.

### Kostenmodell Pro-Vermieter-Instanz

| Ressource | Kosten pro Vermieter |
|-----------|----------------------|
| Paperless-Container | ca. 200–400 MB RAM |
| Datenbank-Overhead | ca. 100–200 MB RAM |
| Speicher | individuell |
| Verwaltung / Updates | deutlich höher |
| **Gesamt pro Vermieter** | **ca. 2–8 €/Monat plus Verwaltungsaufwand** |

Zusätzlich steigen Backup-, Monitoring- und Update-Kosten stark.

### Vergleich

| Modell | Trennung | Kosten/Vermieter | Komplexität |
|--------|----------|------------------|-------------|
| Shared + App-Filter | Mittel | Sehr günstig | Gering |
| **Shared + pro-User (empfohlen)** | **Hoch** | **Günstig** | **Mittel** |
| Pro-Vermieter-Instanz | Sehr hoch | Teuer | Hoch |
| Shared + Verschlüsselung | Maximal | Günstig | Hoch, mit Funktionsverlust |

---

## 8. Fazit

### Was Paperless besser macht
OCR, Volltextsuche, Vorschau, asynchrone Verarbeitung, Versionierung — all das müssten wir sonst selbst bauen und warten.

### Was wir selbst machen müssen
Multi-Tenancy, Vermieter-Mapping, Berechtigungen, UI, Audit-Log und das Verhindern direkter Paperless-Zugriffe.

### Empfohlene Tenant-Trennung
**Shared Paperless-Instanz mit pro-Vermieter Paperless-User.** Das ist die beste Balance aus Sicherheit, Kosten und Aufwand für den MVP. Für absolute Admin-Freihheit bräuchte man Verschlüsselung, die aber OCR und Suche zerstört.

### Kosten
Bei Shared-Instanz mit pro-Vermieter-User: **ca. 0,50–3,00 €/Monat pro Vermieter** bei moderater Dokumentenmenge.

---

## 9. Nächste Schritte

1. Entscheidung: Shared + pro-User, oder eine der anderen Varianten?
2. Aufbau der Docker-Compose für Paperless-ngx.
3. Automatische Erstellung eines Paperless-Users pro Vermieter bei Registrierung.
4. Implementierung des `dokumente`-Datenmodells und der Upload-API.
5. Frontend-Reiter „Dokumente“ in Objekt/Einheit/Mieter/Mietvertrag.

---

*Ende des Konzepts.*
