# MietVerwaltung SaaS — Arbeitsplan (Stand 19.11.2026)

## Ziel
Die live nutzbaren Kern-Features stabilisieren, bevor komplexere Module (KI, Mahnungen, Admin) folgen.

## Arbeitspakete

### Paket 1: Domain-Core stabilisieren (Phase 4) ✅ ABGESCHLOSSEN
**Scope:** Objekte, Einheiten, Mieter, Mietverträge, Bankverbindungen, Kostenkategorien.

- [x] End-to-End-Test Objekt anlegen + speichern + wieder anzeigen
- [x] End-to-End-Test Einheit anlegen + speichern + wieder anzeigen
- [x] Mieter-CRUD testen und ggf. reparieren (inkl. Login erstellen)
- [x] Mietvertrag-CRUD testen und ggf. reparieren
- [x] Bankverbindungen + Kostenkategorien verifizieren
- [x] Frontend-Views auf fehlende Felder / Fehlermeldungen prüfen (Build grün)
- [x] Tests ergänzen/fixen, Backend-Testsuite grün halten (215/215)
- [x] Commit + Push

**Erledigt:**
- Harte Löschregeln für Objekt/Einheit mit aktivem Mietvertrag (HTTP 409)
- Cross-Tenant-Isolation für Objekte, Einheiten, Mieter, Mietverträge
- Einheit-Schema: `objekt_id` ist Pflichtfeld
- Domain-Core-Flow-Test und Isolationstest hinzugefügt
- Bankverbindungen + Kostenkategorien CRUD-Tests grün

### Paket 2: Öffentliche IDs (Issue #39) ✅ ABGESCHLOSSEN
**Scope:** Globale, fortlaufende, eindeutige Nummern für Objekte, Einheiten, Zähler.

- [x] PostgreSQL-Sequences anlegen
- [x] DB-Migration für `objekt_nummer`, `einheit_nummer`, `zaehler_nummer`
- [x] Modelle und Schemas erweitern
- [x] API-Response Mapping anpassen
- [x] Frontend zeigt neue Nummern anstelle interner ID
- [x] Bestehende Datensätze nachträglich nummerieren
- [x] Commit + Push, Issue #39 kommentieren

**Erledigt:**
- Migration `1a2b3c4d5e6f`: `public_id` für Zähler mit Sequence + Backfill
- `Zaehler`-Modell und `-Response` um `public_id` erweitert
- API liefert `public_id` für Zähler
- Frontend: Spalte/Nr.-Anzeige in Objekt-, Einheit- und Zähler-Listen/-Details
- Test-Whitelist um neue Alembic-Version erweitert
- `test_public_ids.py` um Zähler-Public-ID erweitert (6/6 grün)

### Paket 3: Dokumente an Objekte/Einheiten (Phase 6) ✅ ABGESCHLOSSEN
**Scope:** PDFs/Fotos/Videos dauerhaft zu Objekten/Einheiten speichern.

- [x] Upload-Endpunkt für Objekt-/Einheit-Dokumente prüfen/ergänzen
- [x] Speicherpfad verifizert (`vermieter_{id}/{entity_type}/{entity_id}/{uuid}_{filename}`)
- [x] Verknüpfung `entity_type` / `entity_id` für Objekt/Einheit nutzen
- [x] Galerie/Komponente in Objekt-Detail und Einheit-Detail einbauen (bereits vorhanden, funktionsfähig)
- [x] Löschen + Download testen
- [x] Commit + Push

**Erledigt:**
- `DokumenteListe`-Komponente in Objekt-Detail und Einheit-Detail integriert
- Upload/Download/Löschen/OCR funktionsfähig
- Ownership-Prüfung im `DokumentService`: Upload nur an eigene Objekte/Einheiten
- Test `test_upload_to_fremdes_objekt_scheitert` hinzugefügt
- 217/217 Backend-Tests grün, Frontend-Build grün

### Paket 4: Stripe-Billing Grundgerüst (Phase 2) ✅ ABGESCHLOSSEN
**Scope:** Trial-Checkout, Webhooks, Abo-Widget.

- [x] Stripe-Test-Keys in `.env` hinterlegen
- [x] `POST /api/v1/stripe/checkout-session` implementieren
- [x] Webhook-Handler für `checkout.session.completed`, `invoice.paid`, `invoice.payment_failed`
- [x] `GET /api/v1/subscriptions/me` + Dashboard-Widget
- [x] Trial-Ablauf → Account-Sperre im Login prüfen
- [x] Tests mit Stripe-Mock-Events
- [x] Commit + Push

**Erledigt:**
- Trial-Ablauf blockiert Login und geschützte Routen für Vermieter
- `customer.subscription.updated` Webhook-Handler + Route
- `STRIPE_PUBLISHABLE_KEY` in `.env.example` und `config.py`
- SettingsView mit Abo-Tab (Konto / Abo / Sicherheit)
- 221/221 Backend-Tests grün, Frontend-Build grün

## Reihenfolge
Paket 1 ✅ → Paket 2 → Paket 3 → Paket 4

## Kommunikation
- Nach jedem Paket kurze Statusmeldung.
- Blocker oder Abweichungen sofort melden.
- Der Nutzer kann jederzeit die Reihenfolge ändern.
