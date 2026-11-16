# Konzept: Paperless-ngx als „unsichtbares“ Dokumentenarchiv im Mietverwaltung-SaaS

**Datum:** 16. November 2026  
**Autor:** Hermes Agent  
**Scope:** Nahtlose Integration von Paperless-ngx ohne Design-Bruch und ohne dass Vermieter die Paperless-Oberfläche jemals sehen müssen.

---

## 1. Vision in einem Satz

Paperless-ngx läuft als leistungsstarke Backend-Maschine für OCR, Volltextsuche und Speicherung. Der Vermieter hochlädt, sucht, kategorisiert und öffnet Dokumente ausschließlich in der gewohnten Mietverwaltung-Oberfläche.

---

## 2. Warum diese Art der Einbindung?

| Problem bei direkter Paperless-Nutzung | Lösung durch „unsichtbares Archiv“ |
|----------------------------------------|------------------------------------|
| Nutzer müssen sich in zweitem System anmelden | Kein Paperless-Login nötig |
| Paperless-UI passt nicht zum SaaS-Design | Nutzer sieht nur unser UI |
| Berechtigungen müssen doppelt gepflegt werden | Rechteprüfung bleibt in unserem Backend |
| Upload liefert keine sofortige Dokumenten-ID | Unsere App speichert Metadaten sofort, Paperless-ID kommt asynchron nach |
| Schwierige Zuordnung zu Mieter/Objekt/Vertrag | Klare Verknüpfung über `entity_type` + `entity_id` |

---

## 3. Wo Dokumente im UI erscheinen

| Bereich | Reiter | Typische Dokumente |
|---------|--------|--------------------|
| **Objekt-Detail** | „Dokumente“ | Grundriss, Energieausweis, Kaufvertrag/Notarvertrag, Versicherungen |
| **Einheit-Detail** | „Dokumente“ | Übergabeprotokolle, Fotos, Instandhaltungsrechnungen, Begehungsprotokolle |
| **Mieter-Detail** | „Dokumente“ | Mietvertrag, Schufa, Einkommensnachweis, Kaution, Korrespondenz |
| **Mietvertrag-Detail** | „Dokumente“ | Vertrag, Anhänge, Abrechnungen, sonstige Vertragsdokumente |
| **Globale Navigation** | „Dokumente“ | Zentrale Suche über alle Entitäten und Jahre hinweg |

---

## 4. Datenmodell

### Tabelle `dokumente`

| Feld | Typ | Bedeutung |
|------|-----|-----------|
| `id` | UUID / BigInt | Interner Primärschlüssel |
| `vermieter_id` | Integer | Eigentümer / Berechtigung |
| `entity_type` | Enum | `objekt`, `einheit`, `mieter`, `mietvertrag` |
| `entity_id` | Integer | Fremdschlüssel zur jeweiligen Entität |
| `paperless_document_id` | Integer | ID des Dokuments in Paperless-ngx |
| `paperless_task_id` | String (optional) | Asynchroner Upload-Task |
| `typ` | Enum | `mietvertrag`, `nebenkostenabrechnung`, `korrespondenz`, `foto`, `rechnung`, `sonstiges` |
| `titel` | String | Anzeigename |
| `jahr` | Integer (optional) | z. B. für Abrechnungen |
| `file_name` | String | Originaldateiname |
| `file_size` | Integer | In Bytes |
| `content_type` | String | MIME-Type |
| `uploaded_at` | Timestamp | Upload-Zeitpunkt |
| `created_at` / `updated_at` | Timestamp | Standard |

---

## 5. Upload-Flow

```
1. Nutzer klickt im UI auf „Dokument hochladen“
          |
          v
2. Datei wird an /api/v1/dokumente/upload geschickt
          |
          v
3. Backend prüft Berechtigung auf Mieter/Objekt/Vertrag
          |
          v
4. Backend lädt Datei zu Paperless-ngx hoch
   POST /api/documents/post_document/
   Header: Authorization: Token <paperless-token>
   Body: Multipart mit title, tags, custom_fields
          |
          v
5. Paperless antwortet mit task_id (asynchron)
          |
          v
6. Backend speichert sofort Eintrag in `dokumente`
   Status: „wird verarbeitet“
          |
          v
7. Paperless Consumer erledigt OCR/Indexing
          |
          v
8. Optional: Backend fragt task_id ab und aktualisiert
   paperless_document_id + Status: „bereit“
```

---

## 6. Anzeige, Vorschau und Download

| Aktion | Flow |
|--------|------|
| **Liste laden** | `GET /api/v1/dokumente?entity_type=mieter&entity_id=123` → eigene Tabelle |
| **Vorschau** | Klick auf Dokument → `GET /api/v1/dokumente/{id}/preview` → Backend streamt Paperless-Preview |
| **Download** | `GET /api/v1/dokumente/{id}/download` → Backend streamt Paperless-Download |
| **Suche** | Globale Suchbox → `GET /api/v1/dokumente/search?q=Heizkosten+2026` → Backend fragt Paperless `/api/documents/?query=...` ab und filtert nach `vermieter_id` |

---

## 7. Authentifizierung und Berechtigungen

Keine Synchronisation einzelner Nutzer zwischen App und Paperless.

### Lösung: Service-Account pro Vermieter

- Pro Vermieter-Account in unserer App wird ein API-Token in Paperless-ngx angelegt.
- Token wird verschlüsselt in unserer DB gespeichert (z. B. `vermieter.paperless_api_token`).
- Beim Upload schreibt unsere App das `vermieter_id` Custom-Field in das Dokument.
- Beim Download/Vorschau/Suche prüft unser Backend, ob das angefragte Dokument zum Vermieter gehört, bevor Paperless kontaktiert wird.

### Vorteile

- Einfachste Lösung ohne OIDC/Remote-User-Header.
- Paperless kann weiterhin mit seinem Admin-Account verwaltet werden.
- Berechtigungen bleiben vollständig in unserer App.

---

## 8. Design-Einbettung

Dokumenten-Reiter folgen dem bestehenden Apple-style / Navy-Design:

- Überschrift mit Icon (z. B. 📄 bleibt weg, stattdessen Lucide `FileText`).
- Kachel-basierte Upload-Zone oder schlichter Button „Datei auswählen“.
- Liste als Tabelle/Karten mit: Titel, Typ-Tag, Jahr, Dateigröße, Datum, Aktionen (Vorschau, Download, Löschen).
- Vorschau in einem modalen Overlay (PDF-Viewer inline).
- Kein externes Tab-Fenster, keine Paperless-URL wird dem Nutzer angezeigt.

---

## 9. Technischer Stack

| Komponente | Tool |
|------------|------|
| Dokumenten-Backend | FastAPI-Endpunkte + Paperless-ngx REST-Client |
| Archiv-Speicher + OCR | Paperless-ngx (Docker Compose) |
| Dateiupload | multipart/form-data über Backend (Proxy) |
| Vorschau/Download | Backend streamt von Paperless an Frontend |
| Datenbank | Erweitert um Tabelle `dokumente` |
| Frontend | Vue 3 + Pinia Store `dokumente.ts` |

---

## 10. Deployment

Paperless-ngx läuft als zusätzlicher Docker-Compose-Stack:

- `paperless-web`
- `paperless-redis`
- `paperless-db`
- `paperless-gotenberg` (Office-Dokumente → PDF)
- `paperless-tika` (Metadaten-Extraktion)

Verbindung zur App über internes Docker-Netzwerk oder `localhost` + API-Token.

---

## 11. Pro / Contra der Integration

### Pro

- Sofortige OCR + Volltextsuche ohne Eigenbau.
- DSGVO-konformes Self-Hosting.
- Kein sichtbarer Design-Bruch.
- Berechtigungen bleiben zentral in unserer App.
- Erweiterbar: später DocuSeal für E-Signaturen oder Stirling PDF für Manipulationen ergänzen.

### Contra

- Zusätzlicher Container-Stack.
- Asynchroner Upload erfordert Task-Polling oder Webhook.
- Lizenz GPL-3.0: bei kommerzieller SaaS-Verteilung abzuklären (Self-Hosting in der Regel unproblematisch).
- Keine Echtzeit-Dokumenten-ID nach Upload, deshalb Status-Handling nötig.

---

## 12. Empfohlene Umsetzungsphasen

### Phase 1: Backend-Grundgerüst
1. Migration für `dokumente`-Tabelle.
2. Paperless-Config in `.env` (URL + API-Token).
3. Paperless-Client-Service (`upload`, `download`, `preview`, `search`).
4. REST-Endpunkte: Upload, Liste, Download, Vorschau, Löschen.
5. Tests.

### Phase 2: Frontend-Reiter
1. Pinia-Store `dokumente.ts`.
2. Wiederverwendbare `DokumentePanel.vue`-Komponente.
3. Einbindung in Objekt/Einheit/Mieter/Mietvertrag-Detail.
4. Upload-Dialog + Vorschau-Modal.

### Phase 3: Suche + Polishing
1. Globale Dokumenten-Seite mit Suche.
2. Task-Status-Anzeige („wird verarbeitet“ / „bereit“).
3. Löschen in unserer DB + optional in Paperless.
4. Sortierung/Filter nach Typ und Jahr.

---

## 13. Entscheidungsempfehlung

**Umsetzen.** Diese Architektur nutzt Paperless-ngx als leistungsstarke Engine, ohne die Nutzer mit einer zweiten UI zu konfrontieren. Der Mehraufwand gegenüber einem reinen Datei-Upload ist moderat, der Gewinn an OCR, Volltextsuche und DSGVO-konformem Archiv erheblich.

Voraussetzung vor dem Start:
- Lizenz-Check GPL-3.0 im geplanten Vertriebsmodell.
- Festlegung: Docker-Compose lokal/privat oder später im Kunden-Stack.

---

*Ende des Konzepts.*
