# Pre-Build Architektur-Review: DB-Schema v4

**Projekt:** MietVerwaltung SaaS  
**Geprüftes Dokument:** `/root/mietverwaltung/.hermes/plans/2026-11-02_db-schema-v4.md` (33 Tabellen, 34 RLS-Policies, 92 Indizes)  
**Vergleichsbasis:** `/root/mietverwaltung/db-schema-v2.sql`  
**Review-Datum:** 13. November 2026  

## Zusammenfassung

Das Schema v4 hat die großen Multi-Tenant-Probleme aus v3 größtenteils behoben (`vermieter_id` auf fast allen Tenant-Tabellen, Abrechnung pro Einheit, Soft-Delete auf Personendaten). Für einen sauberen Build und den Produktivbetrieb müssen jedoch **12 CRITICAL-Fundstellen** korrigiert werden, bevor Alembic-Migrationen oder Applikationscode darauf aufsetzen. Weitere 20+ WARNINGs/INFOs betreffen Datenintegrität, Performance und DSGVO-Konformität.

**Empfehlung:** Schema korrigieren → als v4.1 finalisieren → erst dann Build-Phase 0 starten. Ein Re-Review nach den Fixes ist erforderlich.

| Schweregrad | Anzahl |
|-------------|--------|
| CRITICAL | 12 |
| WARNING | 18 |
| INFO | 14 |

---

## 1. RLS-Policies & Multi-Tenant-Isolierung

### CRITICAL — `users`: RLS-Policy für Vermieter/Mieter ist funktional falsch
**Tabelle:** `users`  
**Beschreibung:** Die aktuelle Policy erlaubt einem Mieter (`role='mieter'`), die komplette `users`-Zeile seines Vermieters inkl. `password_hash`, `totp_secret`, `backup_codes`, `email_code` zu lesen. Umgekehrt kann ein Vermieter **nicht** die ihm zugeordneten Mieter-Accounts sehen oder anlegen, weil `FOR ALL` + `id = current_vermieter_id` für neue Zeilen nicht greift.  
**Fix:**
```sql
DROP POLICY users_isolation ON users;
CREATE POLICY users_isolation ON users FOR ALL USING (
    id = current_setting('app.current_user_id')::INT
    OR (current_setting('app.current_user_role') = 'vermieter'
        AND vermieter_id = current_setting('app.current_user_id')::INT)
    OR current_setting('app.current_user_role') = 'admin'
);
```
Zusätzlich: Vermieter-Stammdaten, die der Mieter sehen darf (Name, E-Mail), in einer separaten View/Tabelle führen, damit der Mieter nicht die volle `users`-Zeile lesen muss.

### WARNING — `users`: Keine Admin-Policy sichtbar
**Tabelle:** `users`  
**Beschreibung:** Oben genannte Policy fügt Admin-Scope hinzu. Aktuell fehlt jede explizite Admin-RLS; Admin-Center muss alle Tenant-Daten sehen können.  
**Fix:** In jeder Tenant-Tabelle eine Admin-Policy ergänzen (`current_user_role = 'admin'`) oder Admin-Center direkt mit `SECURITY DEFINER`-Functions/Service-Rolle arbeiten lassen.

### WARNING — `referrals`: Keine `vermieter_id`, RLS nur über `referrer_id`
**Tabelle:** `referrals`  
**Beschreibung:** `referrals` nutzt `referrer_id` für Isolierung. Das ist prinzipiell ok, verhindert aber Admin-Sicht und erschwert spätere Tenant-übergreifende Analysen.  
**Fix:** `vermieter_id INT NOT NULL` hinzufügen und befüllen; RLS auf `vermieter_id` umstellen.

---

## 2. Foreign-Key-Konsistenz & Referenzielle Integrität

### WARNING — Soft-deleted Parent-Records bleiben per FK referenziert
**Tabellen:** `kosten`, `abrechnungen`, `mietvertraege`, `dokumente`, etc.  
**Beschreibung:** Viele FKs (z. B. `abrechnungen.objekt_id`, `kosten.einheit_id`, `mietvertraege.mieter_id`) haben weder `ON DELETE CASCADE` noch `ON DELETE SET NULL`. Da die Parent-Tabellen Soft-Delete verwenden, greifen die FK-Aktionen nur beim Hard-Delete. Die App muss also sicherstellen, dass Soft-Delete-Kaskaden in der Business-Logik nachgeführt werden, sonst zeigen Child-Datensätze auf unsichtbare (RLS-gefilterte) Eltern.  
**Fix:** Entscheiden pro Beziehung: (a) `ON DELETE SET NULL` für optionale FKs, (b) Application-Level-Cascade-Delete bei Soft-Delete, (c) in der API verhindern, dass ein aktiver Child-Datensatz auf ein soft-gelöschtes Parent zeigt.

### WARNING — `mietvertraege.mieter_id ON DELETE CASCADE`
**Tabelle:** `mietvertraege`  
**Beschreibung:** `ON DELETE CASCADE` auf `mieter_id` ist riskant in Kombination mit Soft-Delete: Wenn `mieter` soft-gelöscht wird, bleibt der Vertrag bestehen (weil kein Hard-Delete), aber ein späterer Hard-Delete eines Mieters (z. B. DSGVO-Löschung nach Frist) löscht alle seine Verträge unwiderruflich, was steuerrechtlich problematisch sein kann.  
**Fix:** `ON DELETE RESTRICT` oder `SET NULL` verwenden; Löschung nur über Application-Workflow, der Verträge archiviert.

### INFO — `users.vermieter_id` ohne `ON DELETE`
**Tabelle:** `users`  
**Beschreibung:** Default `NO ACTION` verhindert Löschung eines Vermieters, solange Mieter-Accounts existieren. Das ist korrekt, sollte aber dokumentiert werden.  
**Fix:** Bei DSGVO-Löschung eines Vermieters muss der Workflow alle Mieter-Accounts zuerst löschen/übertragen.

---

## 3. Index-Strategie

### WARNING — Fehlende Composite-Indizes für RLS-Lookups auf großen Tabellen
**Tabellen:** `mieter`, `mietvertraege`, `kosten`, `tickets`, `abrechnungen`, `dokumente`, `mietzahlungen`, `ticket_kommentare`, `notifications`  
**Beschreibung:** Fast alle Indizes sind single-column auf `vermieter_id` (z. B. `idx_mieter_vermieter ON mieter(vermieter_id)`). Wenn die App unter RLS nach `id` sucht (`WHERE id = X AND vermieter_id = Y`), benötigt PostgreSQL entweder zwei Index-Scans oder muss über `vermieter_id` filtern. Bei Skalierung entsteht hier schnell ein Hot-Spot.  
**Fix:** Für die großen Tenant-Tabellen Composite-Indizes `(vermieter_id, id)` ergänzen:
```sql
CREATE INDEX idx_mieter_vermieter_id ON mieter(vermieter_id, id) WHERE deleted_at IS NULL;
CREATE INDEX idx_mietvertraege_vermieter_id ON mietvertraege(vermieter_id, id) WHERE deleted_at IS NULL;
CREATE INDEX idx_kosten_vermieter_id ON kosten(vermieter_id, id) WHERE deleted_at IS NULL;
CREATE INDEX idx_tickets_vermieter_id ON tickets(vermieter_id, id);
CREATE INDEX idx_abrechnungen_vermieter_id ON abrechnungen(vermieter_id, id) WHERE deleted_at IS NULL;
CREATE INDEX idx_dokumente_vermieter_id ON dokumente(vermieter_id, id) WHERE deleted_at IS NULL;
CREATE INDEX idx_mietzahlungen_vermieter_id ON mietzahlungen(vermieter_id, id);
CREATE INDEX idx_ticket_kommentare_vermieter_id ON ticket_kommentare(vermieter_id, id);
CREATE INDEX idx_notifications_vermieter_id ON notifications(vermieter_id, id);
```

### WARNING — `ai_stored_results`: Cache-Lookup unvollständig
**Tabelle:** `ai_stored_results`  
**Beschreibung:** Index `idx_ai_stored_results_usecase ON ai_stored_results(vermieter_id, use_case)` fehlt `prompt_hash`, der für einen Cache-Hit zwingend geprüft werden muss.  
**Fix:** `CREATE INDEX idx_ai_results_lookup ON ai_stored_results(vermieter_id, use_case, prompt_hash);`

---

## 4. Fehlende Felder / MVP-Feature-Lücken

### CRITICAL — `users`: Keine Vermieter-Stammdaten (Adresse, Firma, Steuernr)
**Tabelle:** `users`  
**Beschreibung:** In v2 gab es `vermieter_profile` mit Adresse, PLZ, Ort, Telefon, E-Mail, Steuernr, IBAN/BIC, Logo-Pfad. v4 entfernte `vermieter_profile` mit der Begründung „Vermieter = users“, fügte diese Felder aber nicht in `users` ein. Damit fehlen Briefkopf-Daten für PDF-Dokumente, Mahnungen, Wohnungsgeberbestätigung, XRechnung/ZUGFeRD und Admin-Center-Rechnungen.  
**Fix:** Entweder `users` um folgende Felder erweitern:
```sql
company VARCHAR(200),
address VARCHAR(255) NOT NULL,
plz VARCHAR(10) NOT NULL,
city VARCHAR(100) NOT NULL,
phone VARCHAR(30),
tax_number_enc BYTEA,  -- AES-256
logo_path VARCHAR(500),
letterhead_color VARCHAR(7) DEFAULT '#0D3B70'
```
oder eine separate `vermieter_profile`-Tabelle (wie v2) wieder einführen, die über `user_id` mit `users` verknüpft ist.

### CRITICAL — `bankverbindungen`: Kein `deleted_at`, obwohl DSGVO-Übersicht es vorsieht
**Tabelle:** `bankverbindungen`  
**Beschreibung:** Die DSGVO-Aufbewahrungstabelle im Schema-Dokument listet `bankverbindungen` mit Soft-Delete und 10-Jahres-Frist. Die DDL hat aber kein `deleted_at`.  
**Fix:** `deleted_at TIMESTAMPTZ` hinzufügen und Indizes anpassen (`WHERE deleted_at IS NULL`).

### CRITICAL — `subscriptions`: Veraltetes Fixed-Plan-Modell statt WE-basiertem Pro-WE
**Tabelle:** `subscriptions`  
**Beschreibung:** `plan` ist als `CHECK (plan IN ('free','basis','pro','business'))` definiert. Das widerspricht dem aktuellen Abo-Modell v3 („Free-Plan ENTFERNT“, „KEINE festen Pläne“, Preis pro Wohneinheit 9,75 €/WE mit Staffeln 1–5 / 6–25 / 26–49 / 50+ Anfrage). Damit kann das Backend WE-basierte Abrechnung, Staffelpreise und 14-Tage-Netflix-Trial nicht sauber abbilden.  
**Fix:** Tabelle neu modellieren, z. B.:
```sql
CREATE TABLE subscriptions (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active','cancelled','past_due')),
    trial_ends_at TIMESTAMPTZ,
    billing_interval VARCHAR(10) NOT NULL CHECK (billing_interval IN ('monthly','yearly')),
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    unit_count INT NOT NULL DEFAULT 0,          -- abgerechnete WE
    price_per_unit DECIMAL(10,2) NOT NULL,      -- z. B. 9.75
    total_amount DECIMAL(10,2) NOT NULL,        -- errechneter Betrag
    currency VARCHAR(3) DEFAULT 'EUR',
    payment_provider_id VARCHAR(100),           -- Stripe/PayPal Subscription ID
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);
CREATE UNIQUE INDEX idx_subscriptions_user_active ON subscriptions(user_id) WHERE deleted_at IS NULL;
```

### CRITICAL — `plan_usage`: Kein UNIQUE-Constraint auf `user_id`
**Tabelle:** `plan_usage`  
**Beschreibung:** Ohne `UNIQUE(user_id)` können mehrere Zeilen pro Vermieter entstehen. Die Business-Logik geht aber von 1:1 aus („Account trackt live WE-Anzahl“).  
**Fix:** `CREATE UNIQUE INDEX idx_plan_usage_user ON plan_usage(user_id);` bzw. Tabellen-Constraint.

### CRITICAL — `subscriptions`: Kein UNIQUE-Constraint auf `user_id`
**Tabelle:** `subscriptions`  
**Beschreibung:** Ohne Eindeutigkeit kann ein Vermieter mehrere aktive Subscriptions haben, was Rechnungsstellung, Trial-Logik und Cancellation durcheinanderbringt.  
**Fix:** `CREATE UNIQUE INDEX idx_subscriptions_user_active ON subscriptions(user_id) WHERE deleted_at IS NULL;`

### CRITICAL — `dokumente`: Dokument-Sichtbarkeit (`sichtbarkeit`) fehlt
**Tabelle:** `dokumente`  
**Beschreibung:** Das Skill-Konzept definiert explizit eine `sichtbarkeit`-Enum (`vermieter`, `mieter`, `beide`, `handwerker`). v2-SQL hatte diese Spalte. v4 hat nur `type`, wodurch die Basis-Sichtbarkeit eines Dokuments nicht modelliert ist.  
**Fix:**
```sql
ALTER TABLE dokumente ADD COLUMN sichtbarkeit VARCHAR(20) NOT NULL DEFAULT 'vermieter'
    CHECK (sichtbarkeit IN ('vermieter','mieter','beide','handwerker'));
```

### CRITICAL — `dokument_freigaben`: Ziel-`user_id` fehlt, stattdessen nur `role`
**Tabelle:** `dokument_freigaben`  
**Beschreibung:** v2 hatte `user_id` (der Handwerker) und `freigegeben_von` (Vermieter). v4 hat `role VARCHAR(20)` eingeführt, kann damit aber keine gezielte Freigabe an einen einzelnen Handwerker-Benutzer realisieren – genau das ist aber im Skill gefordert.  
**Fix:**
```sql
ALTER TABLE dokument_freigaben
    DROP COLUMN role,
    ADD COLUMN user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ADD COLUMN freigegeben_von INT REFERENCES users(id);
```

### WARNING — `users`: `email_verified` und `is_active` aus v2 entfallen
**Tabelle:** `users`  
**Beschreibung:** Regressions gegenüber v2. E-Mail-Verifizierung und Account-Sperrung (`is_active`) werden für ein Login-System in der Regel benötigt.  
**Fix:**
```sql
ALTER TABLE users ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;
```

### WARNING — `mieter`: `status = 'bewerber'` überlappt mit Tabelle `bewerbungen`
**Tabelle:** `mieter`  
**Beschreibung:** Bewerber sollten in `bewerbungen` geführt werden und erst bei Annahme in `mieter` übernommen werden. Die doppelte Modellierung birgt Inkonsistenz-Risiko.  
**Fix:** `mieter.status` auf `('aktiv','ehemalig')` reduzieren; Bewerber ausschließlich über `bewerbungen` abbilden.

### INFO — `mieter.since` ist redundant zu `mietvertraege.mietbeginn`
**Tabelle:** `mieter`  
**Beschreibung:** Da ein Mieter historisch mehrere Verträge haben kann, ist `since` in `mieter` nicht eindeutig.  
**Fix:** Entfernen oder als virtuelle Spalte/View lösen (`MIN(mietbeginn)`).

### INFO — `abrechnungen.objekt_id` ist redundant
**Tabelle:** `abrechnungen`  
**Beschreibung:** `objekt_id` ist über `einheit_id -> einheiten.objekt_id` ableitbar.  
**Fix:** Entweder entfernen oder als `GENERATED` Spalte ableiten, um Inkonsistenzen zu vermeiden.

---

## 5. Datentypen

### INFO — `objekte.zinssatz` / `tilgung`: `DECIMAL(5,2)` statt `NUMERIC(5,3)`
**Tabelle:** `objekte`  
**Beschreibung:** v2 nutzte `NUMERIC(5,3)` für Zinssatz/Tilgung. v4 verwendet `DECIMAL(5,2)`. Für Standardzinsen (3,50 %) reichen 2 Nachkommastellen, bei genaueren Berechnungen (z. B. 3,475 %) gehen Daten verloren.  
**Fix:** `DECIMAL(5,3)` oder `DECIMAL(6,4)` verwenden, wenn Präzision wichtig ist.

### INFO — `objekte.foto_url` vs. `dokumente.file_path` — Namensinkonsistenz
**Tabelle:** `objekte`  
**Beschreibung:** `foto_url` und `dokumente.file_path` speichern beide Filesystem-Pfade. Unterschiedliche Namen erschweren die File-Storage-Abstraktion.  
**Fix:** `objekte.foto_url` in `foto_path` umbenennen oder beides konsistent als `file_path`/`path` führen.

### INFO — Geldbeträge generell korrekt als `DECIMAL`/`NUMERIC`
**Beschreibung:** Keine `FLOAT`/`DOUBLE` Typen für Geldbeträge gefunden. Korrekt.

### INFO — Zeitstempel generell als `TIMESTAMPTZ`
**Beschreibung:** Keine `TIMESTAMP WITHOUT TIME ZONE` gefunden. Korrekt.

---

## 6. Enum-/Check-Constraints

### WARNING — `tickets`: Keine CHECK-Constraints für `status`, `priority`, `category`
**Tabelle:** `tickets`  
**Beschreibung:** `status`, `priority`, `category` sind reine `VARCHAR` ohne CHECK. Das widerspricht dem Skill-Konzept (`offen/in_bearbeitung/erledigt/geschlossen/abgelehnt`, `dringend/normal/niedrig`, `heizung/wasser/elektrik/schimmel/sonstiges`) und ist ein Inkonsistenz-Risiko.  
**Fix:**
```sql
ALTER TABLE tickets ADD CONSTRAINT chk_tickets_status
    CHECK (status IN ('offen','in_bearbeitung','wartend_auf_mieter','wartend_auf_handwerker','erledigt','geschlossen','abgelehnt'));
ALTER TABLE tickets ADD CONSTRAINT chk_tickets_priority
    CHECK (priority IN ('dringend','normal','niedrig'));
ALTER TABLE tickets ADD CONSTRAINT chk_tickets_category
    CHECK (category IN ('heizung','wasser','elektrik','schimmel','sonstiges'));
```

### WARNING — `objekte.typ`: Kein CHECK-Constraint
**Tabelle:** `objekte`  
**Beschreibung:** v2 hatte `CHECK (typ IN ('EFH','MFH','DHH','Wohnanlage','Geschaeft'))`. v4 hat nur einen Kommentar.  
**Fix:** CHECK-Constraint hinzufügen oder zumindest in der App validieren.

### WARNING — `einheiten.energy_class`: Kein CHECK-Constraint
**Tabelle:** `einheiten`  
**Beschreibung:** Soll laut Kommentar A+ bis H sein.  
**Fix:** `CHECK (energy_class IN ('A+','A','B','C','D','E','F','G','H'))`.

### WARNING — `dokumente.type`: Kein CHECK-Constraint
**Tabelle:** `dokumente`  
**Beschreibung:** v2 hatte CHECK. v4 hat nur Kommentar.  
**Fix:** `CHECK (type IN ('vertrag','protokoll','bewerbung','rechnung','foto','sonstiges', ...))`.

### WARNING — `fristen.warn_level`: Kein CHECK-Constraint
**Tabelle:** `fristen`  
**Beschreibung:** `warn_level` sollte `green`/`yellow`/`red` sein.  
**Fix:** `CHECK (warn_level IN ('green','yellow','red'))`.

### WARNING — `notifications.status`: Kein CHECK-Constraint
**Tabelle:** `notifications`  
**Beschreibung:** v2 hatte `CHECK (status IN ('pending','sent','failed','read'))`. v4 hat keinen CHECK.  
**Fix:** CHECK-Constraint ergänzen.

### WARNING — `mietzahlungen.mahnstufe`: Kein CHECK-Constraint
**Tabelle:** `mietzahlungen`  
**Beschreibung:** Sollte 0–3 sein.  
**Fix:** `CHECK (mahnstufe BETWEEN 0 AND 3)`.

### INFO — `handwerker.rating`: Kein CHECK-Constraint
**Tabelle:** `handwerker`  
**Beschreibung:** Sollte typischerweise 1–5 oder 0–5 sein.  
**Fix:** `CHECK (rating BETWEEN 1 AND 5)`.

### INFO — `ticket_sla.biz_days`: Kein CHECK-Constraint
**Tabelle:** `ticket_sla`  
**Beschreibung:** Default `mtwtf` ist nicht selbsterklärend; ohne CHECK können beliebige Zeichenketten landen.  
**Fix:** Länge prüfen und ggf. auf 7 Zeichen beschränken (`CHECK (length(biz_days) = 7)`).

### INFO — `ticket_trigger.trigger_type`: Kein CHECK-Constraint
**Tabelle:** `ticket_trigger`  
**Beschreibung:** v2 nutzte `status`; v4 nutzt `trigger_type` ohne CHECK.  
**Fix:** `CHECK (trigger_type IN ('event','scheduler','manual'))`.

### INFO — `einheit_ausstattung.feature`: Kein CHECK-Constraint
**Tabelle:** `einheit_ausstattung`  
**Beschreibung:** Feature-Werte werden nur kommentiert (`bad_wanne`, `bad_dusche`, `einbaukueche`, ...).  
**Fix:** CHECK-Constraint oder separate Lookup-Tabelle `einheit_ausstattung_katalog`.

---

## 7. Soft-Delete, RLS & Unique-Constraints

### CRITICAL — `users.email`: UNIQUE-Constraint nicht partial, blockiert Re-Registrierung
**Tabelle:** `users`  
**Beschreibung:** `email VARCHAR(255) UNIQUE NOT NULL` erzeugt einen nicht-partiellen Unique-Index. Wenn ein Account soft-gelöscht wird, kann sich derselbe Nutzer nicht erneut registrieren.  
**Fix:**
```sql
ALTER TABLE users DROP CONSTRAINT users_email_key;  -- Name ggf. anpassen
CREATE UNIQUE INDEX idx_users_email_active ON users(email) WHERE deleted_at IS NULL;
```

### CRITICAL — `abrechnungen`: Unique-Constraint `(einheit_id, jahr)` nicht partial
**Tabelle:** `abrechnungen`  
**Beschreibung:** `UNIQUE (einheit_id, jahr)` erlaubt keine neue Abrechnung für denselben Einheit/Jahr-Kombination, nachdem eine frühere soft-gelöscht wurde.  
**Fix:**
```sql
ALTER TABLE abrechnungen DROP CONSTRAINT uq_abrechnungen_einheit_jahr;
CREATE UNIQUE INDEX uq_abrechnungen_einheit_jahr_active
    ON abrechnungen(einheit_id, jahr) WHERE deleted_at IS NULL;
```

### CRITICAL — `kosten`: `deleted_at` fehlt trotz DSGVO-Aufbewahrungstabelle
**Tabelle:** `kosten`  
**Beschreibung:** Die DSGVO-Tabelle im v4-Dokument fordert Soft-Delete für `kosten` mit 10-Jahres-Aufbewahrung. Die DDL hat kein `deleted_at`.  
**Fix:** `ALTER TABLE kosten ADD COLUMN deleted_at TIMESTAMPTZ;` und Indizes anpassen.

### CRITICAL — `abrechnung_positionen`: `deleted_at` fehlt trotz DSGVO-Aufbewahrungstabelle
**Tabelle:** `abrechnung_positionen`  
**Beschreibung:** Ebenfalls in der DSGVO-Tabelle als Soft-Delete geführt, aber nicht in der DDL.  
**Fix:** `ALTER TABLE abrechnung_positionen ADD COLUMN deleted_at TIMESTAMPTZ;`

### WARNING — `tickets`: `deleted_at` fehlt, obwohl Soft-Delete-Konvention für Geschäftsobjekte gilt
**Tabelle:** `tickets`  
**Beschreibung:** Die v4-Konvention sagt: „Soft-Delete auf allen Personendaten- und Geschäftsobjekt-Tabellen.“ `tickets` ist ein Geschäftsobjekt, hat aber nur `closed_at`. Das ist nicht zwingend falsch, aber inkonsistent und erschwert spätere Lösch-/Archivierungs-Workflows.  
**Fix:** Entweder `deleted_at TIMESTAMPTZ` ergänzen oder explizit dokumentieren, dass Tickets nur geschlossen, nie gelöscht werden (DSGVO-konform prüfen).

### WARNING — `bankverbindungen.is_default`: Mehrere Defaults pro Vermieter/Mieter möglich
**Tabelle:** `bankverbindungen`  
**Beschreibung:** Ohne partiellen Unique-Index kann es mehrere `is_default = TRUE` Zeilen geben.  
**Fix:**
```sql
CREATE UNIQUE INDEX idx_bankverbindungen_default_vermieter
    ON bankverbindungen(vermieter_id) WHERE is_default = TRUE AND mieter_id IS NULL AND deleted_at IS NULL;
CREATE UNIQUE INDEX idx_bankverbindungen_default_mieter
    ON bankverbindungen(mieter_id) WHERE is_default = TRUE AND deleted_at IS NULL;
```

### INFO — `mietzahlungen`: Kein `deleted_at`, aber DSGVO-Tabelle sieht Hard-Delete vor
**Tabelle:** `mietzahlungen`  
**Beschreibung:** DSGVO-Tabelle: „Hard-Delete nach Anonymisierung“. Das Schema hat keinen `deleted_at` und auch keine Anonymisierungs-Spalten. Das ist prinzipiell ok, muss aber im Lösch-Cron umgesetzt werden.  
**Fix:** Lösch-Workflow dokumentieren; ggf. `anonymized_at` + `anonymized` hinzufügen.

---

## 8. Alembic-Migrations-Readiness

### WARNING — Migration v2 → v4 ist hochkomplex
**Beschreibung:** v2 nutzt UUIDs, v4 nutzt `INT GENERATED ALWAYS AS IDENTITY`; v2 hat `vermieter_profile`, v4 verlagert alles auf `users`; v2 hatte Fixed-Plans, v4 soll WE-basiert sein. Eine Datenmigration würde alle PK/FK-Werte konvertieren, Tabellen zusammenführen und das Abo-Modell neu aufbauen müssen.  
**Fix:** Für den MVP-Neustart empfohlen: keine Migration aus v2, sondern frisches v4.1-Schema mit korrekten Fixes. Falls alte Daten erhalten bleiben müssen: dedizierte ETL-Migration in einer eigenen Phase planen, nicht im Build-MVP.

### WARNING — Fehlende `updated_at`-Automatisierung
**Beschreibung:** Viele Tabellen haben `updated_at`, aber es gibt keine Datenbank-Trigger oder `GENERATED` Spalten, die dieses Feld automatisch aktualisieren. Alembic migriert nur das Schema; die App muss jedes `updated_at` explizit setzen.  
**Fix:** Entweder (a) in jedem Repository/Service-Layer `updated_at = NOW()` setzen, oder (b) globale PostgreSQL-Trigger-Funktion für `updated_at` erstellen und auf alle Tabellen anwenden.

### WARNING — `users`: Mieter-Constraint verkompliziert Migrationen
**Tabelle:** `users`  
**Beschreibung:** `CHECK ((role='mieter' AND vermieter_id IS NOT NULL) OR (role!='mieter' AND vermieter_id IS NULL))` ist korrekt, erschwert aber das nachträgliche Befüllen von Test-/Migrationsdaten.  
**Fix:** Bei Alembic-Seeds/Testdata den Constraint temporär deaktivieren oder immer korrekte `vermieter_id` setzen.

### INFO — `SERIAL` → `IDENTITY` korrekt umgesetzt
**Beschreibung:** Alle Primärschlüssel verwenden `GENERATED ALWAYS AS IDENTITY`. Das vereinfacht Alembic-Migrationen gegenüber `SERIAL`.

---

## Nicht durchgeführte Live-Validierung

Ein Versuch, das extrahierte DDL in einer temporären PostgreSQL-17-Datenbank (`mv_schema_audit_v4`) zu laden, scheiterte an einem serverseitigen Fehler („could not open shared memory segment“). Die Ursache liegt in der Laufzeitumgebung, nicht am Schema. Eine erneute Syntax-Validierung sollte nach den oben genannten Korrekturen mit einer sauberen DB-Session wiederholt werden.

---

## Empfohlene Nacharbeiten (Priorisiert)

1. **Sofort (CRITICAL):** `users`-RLS-Policy korrigieren.
2. **Sofort (CRITICAL):** `subscriptions` und `plan_usage` auf WE-basiertes Pro-WE-Modell umstellen.
3. **Sofort (CRITICAL):** Vermieter-Stammdaten wiederherstellen (in `users` oder `vermieter_profile`).
4. **Sofort (CRITICAL):** `deleted_at` auf `kosten`, `abrechnung_positionen`, `bankverbindungen` ergänzen.
5. **Sofort (CRITICAL):** `dokumente.sichtbarkeit` und `dokument_freigaben.user_id` hinzufügen.
6. **Sofort (CRITICAL):** Partielle Unique-Indizes für `users.email` und `abrechnungen(einheit_id, jahr)` erstellen.
7. **Sofort (CRITICAL):** `plan_usage` und `subscriptions` auf eine Zeile pro Vermieter beschränken.
8. **Vor Build:** CHECK-Constraints (`tickets`, `objekte`, `einheiten`, `dokumente`, `fristen`, `notifications`, `mietzahlungen`) ergänzen.
9. **Vor Build:** Composite-Indizes `(vermieter_id, id)` auf großen Tenant-Tabellen ergänzen.
10. **Vor Build:** Soft-Delete für `tickets` entscheiden und umsetzen/dokumentieren.
11. **Vor Build:** `users.email_verified` und `users.is_active` wieder einführen.
12. **Vor Build:** `updated_at`-Strategie (Trigger vs. App-Layer) festlegen und dokumentieren.

**Ergebnis nach Korrektur:** Schema v4.1 als finalisierte Grundlage für den Build freigeben.
