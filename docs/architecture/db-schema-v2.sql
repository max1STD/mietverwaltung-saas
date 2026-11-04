-- ============================================================
-- MietVerwaltung SaaS — Datenbank-Schema (überarbeitet v2)
-- PostgreSQL 17 · UUIDs · Row-Level Security · Soft-Delete
-- ============================================================
-- Änderungen v1 → v2:
--   NEU: mietvertraege (Mietverträge separat von Mieter)
--   NEU: abrechnung_positionen (einzelne Kostenpositionen)
--   NEU: audit_logs (DSGVO zwingend)
--   NEU: einwilligungen (versionierte Einwilligung)
--   NEU: events / notifications (Automatisierungen)
--   NEU: user_sessions (Session-Verwaltung, Geräte-Logout)
--   NEU: user_devices (Geräte-Tracking)
--   NEU: kostenkategorien (pro Vermieter konfigurierbar)
--   ERWEITERT: users (2FA-Secret, Backup-Codes, TOTP)
--   ERWEITERT: alle Tabellen mit deleted_at (Soft-Delete)
--   ERWEITERT: alle Tabellen mit updated_at, created_by
--   BEHOBEN: mieter.vermieter_id Redundanz entfernt (via FK ableitbar)
--   BEHOBEN: mietzahlungen.einheit_id Redundanz entfernt
-- ============================================================

-- === Extensions ===
CREATE EXTENSION IF NOT EXISTS "pgcrypto";      -- AES-256-GCM Feld-Verschlüsselung
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";       -- UUID-Generierung

-- === Hilfsfunktion: Timestamp mit Zeitzone ===
-- Alle Zeitstempel als timestamptz (UTC gespeichert, Frontend zeigt lokal)

-- ============================================================
-- 1. users — Login-Accounts (alle Rollen)
-- ============================================================
CREATE TABLE users (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email               VARCHAR(255) UNIQUE NOT NULL,
    password_hash       TEXT NOT NULL,                    -- Argon2id
    role                VARCHAR(20) NOT NULL CHECK (role IN ('vermieter','mieter','handwerker','admin')),
    vorname             VARCHAR(100) NOT NULL,
    nachname            VARCHAR(100) NOT NULL,
    phone               VARCHAR(30),

    -- 2FA / Security
    totp_secret         TEXT,                            -- TOTP-Secret (verschlüsselt), NULL = 2FA nicht aktiviert
    totp_enabled        BOOLEAN NOT NULL DEFAULT FALSE,
    twoFA_method        VARCHAR(10) DEFAULT 'email',     -- 'totp' oder 'email'
    backup_codes        TEXT,                            -- JSON-Array von gehashten Backup-Codes (verschlüsselt)
    email_code          VARCHAR(6),                      -- Aktueller E-Mail-2FA-Code
    email_code_expires  TIMESTAMPTZ,                     -- Gültigkeit des E-Mail-Codes (15 Min)

    -- Session-Sicherheit
    last_login          TIMESTAMPTZ,
    last_login_ip       INET,
    failed_login_count  INTEGER NOT NULL DEFAULT 0,
    locked_until        TIMESTAMPTZ,                     -- Bei zu vielen Fehlversuchen
    password_changed_at TIMESTAMPTZ,

    -- Status
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    email_verified      BOOLEAN NOT NULL DEFAULT FALSE,
    email_verified_at   TIMESTAMPTZ,

    -- DSGVO
    dsdvo_consent_at    TIMESTAMPTZ,                     -- Wann DSGVO-Einwilligung erteilt
    dsdvo_consent_version VARCHAR(20),                   -- Version der Datenschutzerklärung

    -- Meta
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ,                     -- Soft-Delete (DSGVO Löschung)
    created_by          UUID REFERENCES users(id),

    CONSTRAINT chk_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- === Row-Level Security ===
-- Vermieter sieht nur Daten mit seiner vermieter_id
-- Mieter sieht nur Daten mit seiner mieter_id
-- (Policies werden nach allen Tabellen erstellt)

-- ============================================================
-- 2. user_sessions — Aktive Sessions (Geräte-Verwaltung)
-- ============================================================
CREATE TABLE user_sessions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash  TEXT NOT NULL,                    -- Hash des Refresh-Tokens (nie plain speichern)
    device_name         VARCHAR(200),                    -- "Chrome / Windows" etc.
    device_ip           INET,
    device_user_agent   TEXT,
    expires_at          TIMESTAMPTZ NOT NULL,
    revoked_at          TIMESTAMPTZ,                     -- Wenn Session manuell beendet
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);

-- ============================================================
-- 3. einwilligungen — Versionierte DSGVO-Einwilligungen
-- ============================================================
CREATE TABLE einwilligungen (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    purpose             VARCHAR(100) NOT NULL,            -- 'registration', 'ausweis_upload', 'schufa', 'ki_processing'
    consent_given       BOOLEAN NOT NULL,
    consent_text        TEXT NOT NULL,                    -- Text dem zustimmend wurde
    consent_version     VARCHAR(20) NOT NULL,             -- Version der Datenschutzerklärung
    consent_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    withdrawn_at        TIMESTAMPTZ,                      -- Wenn Einwilligung zurückgezogen
    ip_address          INET,                             -- IP bei Einwilligung (Audit)
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_einwilligungen_user ON einwilligungen(user_id);
CREATE INDEX idx_einwilligungen_purpose ON einwilligungen(purpose);

-- ============================================================
-- 4. vermieter_profile — Vermieter-Stammdaten
-- ============================================================
CREATE TABLE vermieter_profile (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Stammdaten
    firma               VARCHAR(200),                    -- NULL = Privatperson
    vorname             VARCHAR(100) NOT NULL,
    nachname            VARCHAR(100) NOT NULL,
    adresse             VARCHAR(200) NOT NULL,
    plz                 VARCHAR(10) NOT NULL,
    ort                 VARCHAR(100) NOT NULL,
    phone               VARCHAR(30),
    email               VARCHAR(255) NOT NULL,

    -- Sensible Daten (Feld-Verschlüsselung AES-256-GCM)
    steuernr            TEXT,                             -- VERSCHLÜSSELT
    iban                TEXT,                             -- VERSCHLÜSSELT
    bic                 TEXT,                             -- VERSCHLÜSSELT

    -- Branding (für PDF-Briefkopf)
    logo_path           VARCHAR(500),                    -- Pfad zum verschlüsselten Logo
    briefkopf_farbe     VARCHAR(7) DEFAULT '#0D3B70',   -- Navy Standard

    -- Meta
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ
);
CREATE UNIQUE INDEX idx_vermieter_user ON vermieter_profile(user_id) WHERE deleted_at IS NULL;

-- ============================================================
-- 5. objekte — Immobilien
-- ============================================================
CREATE TABLE objekte (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vermieter_id        UUID NOT NULL REFERENCES vermieter_profile(id) ON DELETE CASCADE,

    -- Stammdaten
    name                VARCHAR(200) NOT NULL,            -- "Hauptstraße 5"
    adresse             VARCHAR(200) NOT NULL,
    plz                 VARCHAR(10) NOT NULL,
    ort                 VARCHAR(100) NOT NULL,
    baujahr             INTEGER,
    typ                 VARCHAR(20) NOT NULL CHECK (typ IN ('EFH','MFH','DHH','Wohnanlage','Geschaeft')),
    gesamtflaeche_qm    NUMERIC(10,2),

    -- Finanzzahlen (für ROI)
    kaufpreis           NUMERIC(12,2),
    kaufdatum           DATE,
    aktueller_wert      NUMERIC(12,2),                   -- Optional, KI kann schätzen
    jahreswertsteigerung NUMERIC(5,2) DEFAULT 2.00,      -- % pro Jahr (Schätzwert)

    -- Finanzierung (optional, für Nettorendite/ROE)
    darlehensbetrag     NUMERIC(12,2),
    eigenkapital        NUMERIC(12,2),
    zinssatz            NUMERIC(5,3),                    -- z.B. 3.500
    tilgungssatz        NUMERIC(5,3),                    -- z.B. 2.000
    zinsbindung_bis     DATE,
    sondertilgung       BOOLEAN DEFAULT FALSE,

    -- Meta
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ,
    created_by          UUID REFERENCES users(id)
);
CREATE INDEX idx_objekte_vermieter ON objekte(vermieter_id) WHERE deleted_at IS NULL;

-- ============================================================
-- 6. einheiten — Wohneinheiten innerhalb eines Objekts
-- ============================================================
CREATE TABLE einheiten (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    objekt_id           UUID NOT NULL REFERENCES objekte(id) ON DELETE CASCADE,

    bezeichnung         VARCHAR(100) NOT NULL,            -- "EG links", "1.OG rechts"
    flaeche_qm          NUMERIC(8,2) NOT NULL,
    zimmer              INTEGER,
    etage               VARCHAR(20),
    aktuell_vermietet   BOOLEAN NOT NULL DEFAULT FALSE,

    -- Meta
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ,
    created_by          UUID REFERENCES users(id)
);
CREATE INDEX idx_einheiten_objekt ON einheiten(objekt_id) WHERE deleted_at IS NULL;

-- ============================================================
-- 7. mieter — Mieter-Stammdaten (Person, nicht Vertrag!)
-- ============================================================
-- NEU: Mietvertragsdaten (Miete, Kaution, Mietbeginn) sind
--      in die neue Tabelle mietvertraege ausgelagert.
--      mieter = die PERSON, mietvertraege = der VERTRAG.
-- ============================================================
CREATE TABLE mieter (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID REFERENCES users(id),        -- Mieter-Login (NULL bis Login erstellt)

    -- Stammdaten (Person)
    vorname             VARCHAR(100) NOT NULL,
    nachname            VARCHAR(100) NOT NULL,
    geburtsdatum        DATE,                             -- VERSCHLÜSSELT (AES-256-GCM)
    email               VARCHAR(255),
    phone               VARCHAR(30),
    nationality         VARCHAR(3),                      -- ISO-Ländercode (für DACH-Prüfung)

    -- Bewerbungs-Status
    bewerbungs_status   VARCHAR(20) DEFAULT 'eingang' CHECK (bewerbungs_status IN
                        ('eingang','dokumente_vollstaendig','geprueft','angenommen','abgelehnt')),

    -- Identitätsnachweis
    identitaet_verifiziert  BOOLEAN NOT NULL DEFAULT FALSE,
    identitaet_verifiziert_am TIMESTAMPTZ,
    identitaet_methode       VARCHAR(20),                -- 'persoenlich', 'video', 'eid', 'upload_ocr'

    -- Meta
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ,
    created_by          UUID REFERENCES users(id)
);
CREATE INDEX idx_mieter_user ON mieter(user_id) WHERE deleted_at IS NULL;

-- ============================================================
-- 8. mietvertraege — Mietverträge (NEU in v2)
-- ============================================================
-- Trennt die Person (mieter) vom Vertrag (mietvertraege).
-- Ermöglicht: Vertragsänderungen, Staffelmiete, Indexmiete,
-- Verlängerungen, historische Mieter in derselben Einheit.
-- ============================================================
CREATE TABLE mietvertraege (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    einheit_id          UUID NOT NULL REFERENCES einheiten(id) ON DELETE CASCADE,
    mieter_id           UUID NOT NULL REFERENCES mieter(id) ON DELETE CASCADE,
    vermieter_id        UUID NOT NULL REFERENCES vermieter_profile(id) ON DELETE CASCADE,

    -- Vertragsdaten
    mietbeginn          DATE NOT NULL,
    mietende            DATE,                             -- NULL = unbefristet
    kundigungsfrist_monate INTEGER DEFAULT 3,
    kundigung_eingegangen_am DATE,                       -- NULL = nicht gekündigt

    -- Miete (aktuell; bei Staffelmiete = aktueller Stand)
    kaltmiete           NUMERIC(10,2) NOT NULL,
    nk_vorschuss        NUMERIC(10,2) NOT NULL DEFAULT 0,
    gesamtmiete         NUMERIC(10,2) GENERATED ALWAYS AS (kaltmiete + nk_vorschuss) STORED,

    -- Kaution
    kaution             NUMERIC(10,2),
    kaution_bei         VARCHAR(100),                    -- "Sparkasse Stade", "Mietkautionskonto"

    -- Vertragsart
    vertragsart         VARCHAR(20) DEFAULT 'standard' CHECK (vertragsart IN
                        ('standard','staffelmiete','indexmiete','zeitbefristet')),

    -- Status
    status              VARCHAR(20) DEFAULT 'aktiv' CHECK (status IN
                        ('aktiv','gekuendigt','beendet','zukunft')),

    -- Meta
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ,
    created_by          UUID REFERENCES users(id)
);
CREATE INDEX idx_mietvertraege_einheit ON mietvertraege(einheit_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_mietvertraege_mieter ON mietvertraege(mieter_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_mietvertraege_vermieter ON mietvertraege(vermieter_id) WHERE deleted_at IS NULL;

-- ============================================================
-- 9. mietvertrag_aenderungen — Vertragsänderungs-Historie
-- ============================================================
-- Bei Staffelmiete/Vertragsänderungen: Historie aller Änderungen
-- ============================================================
CREATE TABLE mietvertrag_aenderungen (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mietvertrag_id      UUID NOT NULL REFERENCES mietvertraege(id) ON DELETE CASCADE,
    feld                VARCHAR(50) NOT NULL,              -- 'kaltmiete', 'nk_vorschuss', etc.
    alter_wert          TEXT,
    neuer_wert          TEXT,
    gueltig_ab          DATE NOT NULL,
    grund               VARCHAR(200),                     -- 'Staffelmiete §557a', 'Mieterhöhung §558'
    geaendert_am        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    geaendert_von       UUID REFERENCES users(id)
);
CREATE INDEX idx_aenderungen_vertrag ON mietvertrag_aenderungen(mietvertrag_id);

-- ============================================================
-- 10. tickets — Störungsmeldungen
-- ============================================================
CREATE TABLE tickets (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_nr           VARCHAR(20) NOT NULL,             -- "TKT-2026-001" (lesbar)
    einheit_id          UUID NOT NULL REFERENCES einheiten(id) ON DELETE CASCADE,
    mietvertrag_id      UUID REFERENCES mietvertraege(id),-- NULL = vermieteter Vermieter selbst
    mieter_id           UUID NOT NULL REFERENCES mieter(id),
    vermieter_id        UUID NOT NULL REFERENCES vermieter_profile(id) ON DELETE CASCADE,

    titel               VARCHAR(200) NOT NULL,
    beschreibung        TEXT NOT NULL,
    kategorie           VARCHAR(20) CHECK (kategorie IN
                        ('heizung','wasser','elektrik','schimmel','sonstiges')),
    prioritaet          VARCHAR(10) CHECK (prioritaet IN ('dringend','normal','niedrig')),
    status              VARCHAR(20) DEFAULT 'offen' CHECK (status IN
                        ('offen','in_bearbeitung','erledigt','geschlossen')),

    -- KI-Metadaten
    ki_kategorisiert   BOOLEAN DEFAULT FALSE,            -- TRUE = von KI kategorisiert
    ki_prioritaet       BOOLEAN DEFAULT FALSE,            -- TRUE = von KI priorisiert

    -- Zuweisung (später: Handwerker)
    assigned_to         UUID REFERENCES users(id),        -- NULL = nicht zugewiesen

    created_by          UUID NOT NULL REFERENCES users(id),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at           TIMESTAMPTZ,
    deleted_at          TIMESTAMPTZ
);
CREATE UNIQUE INDEX idx_tickets_nr_vermieter ON tickets(ticket_nr, vermieter_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_tickets_einheit ON tickets(einheit_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_tickets_mieter ON tickets(mieter_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_tickets_status ON tickets(status) WHERE deleted_at IS NULL;

-- ============================================================
-- 11. ticket_kommentare — Verlauf/Historie pro Ticket
-- ============================================================
CREATE TABLE ticket_kommentare (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id           UUID NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES users(id),
    rolle               VARCHAR(20) NOT NULL,              -- Für Anzeige: 'vermieter'/'mieter'/'handwerker'
    text                TEXT NOT NULL,
    ist_ki_entwurf      BOOLEAN DEFAULT FALSE,            -- TRUE = KI-generierter Entwurf (vor Bestätigung)
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_kommentare_ticket ON ticket_kommentare(ticket_id);

-- ============================================================
-- 12. dokumente — Hochgeladene und generierte Dateien
-- ============================================================
CREATE TABLE dokumente (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vermieter_id        UUID NOT NULL REFERENCES vermieter_profile(id) ON DELETE CASCADE,

    -- Verknüpfungen (alle nullable, je nach Dokument-Typ)
    objekt_id           UUID REFERENCES objekte(id),
    einheit_id          UUID REFERENCES einheiten(id),
    mieter_id           UUID REFERENCES mieter(id),
    mietvertrag_id      UUID REFERENCES mietvertraege(id),

    -- Datei-Info
    dateiname           VARCHAR(255) NOT NULL,
    original_dateiname  VARCHAR(255),                    -- Originalname beim Upload
    file_path           TEXT NOT NULL,                    -- Pfad zur verschlüsselten Datei
    file_size           BIGINT,
    mime_type           VARCHAR(100),
    file_hash           VARCHAR(64),                     -- SHA-256 Prüfsumme (Integrität)

    -- Klassifikation
    typ                 VARCHAR(30) CHECK (typ IN
                        ('mietvertrag','ausweis','lohnabrechnung','schufa','versicherung',
                         'rechnung','beleg','uebergabeprotokoll','generiert','sonstiges')),
    sichtbarkeit        VARCHAR(20) DEFAULT 'vermieter' CHECK (sichtbarkeit IN
                        ('vermieter','mieter','beide','handwerker')),

    -- KI-Klassifikation
    ki_klassifiziert    BOOLEAN DEFAULT FALSE,

    -- Upload
    uploaded_by         UUID REFERENCES users(id),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ                      -- Soft-Delete (Datei wird auch physisch gelöscht)
);
CREATE INDEX idx_dokumente_vermieter ON dokumente(vermieter_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_dokumente_mieter ON dokumente(mieter_id) WHERE deleted_at IS NULL AND mieter_id IS NOT NULL;
CREATE INDEX idx_dokumente_objekt ON dokumente(objekt_id) WHERE deleted_at IS NULL AND objekt_id IS NOT NULL;

-- ============================================================
-- 13. dokument_freigaben — Gezielte Freigaben an Handwerker
-- ============================================================
CREATE TABLE dokument_freigaben (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dokument_id         UUID NOT NULL REFERENCES dokumente(id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES users(id), -- Der Handwerker
    freigegeben_von     UUID NOT NULL REFERENCES users(id), -- Der Vermieter
    freigegeben_am      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    widerrufen_am       TIMESTAMPTZ
);
CREATE INDEX idx_freigaben_dokument ON dokument_freigaben(dokument_id);
CREATE INDEX idx_freigaben_user ON dokument_freigaben(user_id);

-- ============================================================
-- 14. kostenkategorien — Pro Vermieter konfigurierbar (NEU)
-- ============================================================
-- Erlaubt Vermietern eigene Kategorien mit eigenen
-- Umlageschlüsseln und Steuerbehandlung zu definieren.
-- ============================================================
CREATE TABLE kostenkategorien (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vermieter_id        UUID NOT NULL REFERENCES vermieter_profile(id) ON DELETE CASCADE,
    name                VARCHAR(100) NOT NULL,             -- "Müllabfuhr", "Heizung", etc.
    standard_umlageart  VARCHAR(20) CHECK (standard_umlageart IN
                        ('nach_qm','nach_personen','nach_verbrauch','nicht_umlagefaehig')),
    ist_umlagefaehig    BOOLEAN NOT NULL DEFAULT TRUE,
    ist_standard        BOOLEAN DEFAULT FALSE,            -- TRUE = vom System vordefiniert
    farbe               VARCHAR(7),                      -- Für Dashboard-Charts
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_kategorien_vermieter ON kostenkategorien(vermieter_id);

-- ============================================================
-- 15. kosten — Betriebskosten erfassen
-- ============================================================
CREATE TABLE kosten (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    objekt_id           UUID NOT NULL REFERENCES objekte(id) ON DELETE CASCADE,
    einheit_id          UUID REFERENCES einheiten(id),    -- NULL = objekt-weite Kosten
    vermieter_id        UUID NOT NULL REFERENCES vermieter_profile(id) ON DELETE CASCADE,
    kategorie_id        UUID REFERENCES kostenkategorien(id),

    -- Bequemer: Kategorie auch als String (falls keine custom Kategorie)
    kategorie           VARCHAR(50) NOT NULL,             -- Fallback: 'hausgeld','versicherung', etc.
    betrag              NUMERIC(10,2) NOT NULL,
    datum               DATE NOT NULL,
    beschreibung        VARCHAR(500),
    umlagefaehig        BOOLEAN NOT NULL DEFAULT TRUE,
    umlageart           VARCHAR(20) CHECK (umlageart IN
                        ('nach_qm','nach_personen','nach_verbrauch','nicht_umlagefaehig')),

    -- Beleg-Verknüpfung
    beleg_id            UUID REFERENCES dokumente(id),     -- Gescannter Beleg

    -- Abrechnungs-Verknüpfung (NEU)
    abrechnung_id       UUID REFERENCES abrechnungen(id),  -- NULL = noch nicht abgerechnet
    abgerechnet_am      TIMESTAMPTZ,                      -- Wann in Abrechnung aufgenommen

    -- KI-Metadaten
    ki_kategorisiert    BOOLEAN DEFAULT FALSE,
    ki_umlage_geprueft  BOOLEAN DEFAULT FALSE,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ,
    created_by          UUID REFERENCES users(id)
);
CREATE INDEX idx_kosten_objekt ON kosten(objekt_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_kosten_einheit ON kosten(einheit_id) WHERE deleted_at IS NULL AND einheit_id IS NOT NULL;
CREATE INDEX idx_kosten_abrechnung ON kosten(abrechnung_id) WHERE abrechnung_id IS NOT NULL;

-- ============================================================
-- 16. mietzahlungen — Mieteinnahmen tracken
-- ============================================================
CREATE TABLE mietzahlungen (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mietvertrag_id      UUID NOT NULL REFERENCES mietvertraege(id) ON DELETE CASCADE,
    mieter_id           UUID NOT NULL REFERENCES mieter(id) ON DELETE CASCADE,
    vermieter_id        UUID NOT NULL REFERENCES vermieter_profile(id) ON DELETE CASCADE,

    -- Redundanz zu v1 entfernt: einheit_id via mietvertrag ableitbar

    monat               INTEGER NOT NULL CHECK (monat BETWEEN 1 AND 12),
    jahr                INTEGER NOT NULL,
    betrag_soll         NUMERIC(10,2) NOT NULL,           -- Erwartete Miete
    betrag_ist          NUMERIC(10,2),                    -- Tatsächlich gezahlt
    zahlungsdatum       DATE,                             -- Wann Geld eingegangen
    zahlungsreferenz    VARCHAR(100),                     -- Verwendungszweck (für Matching)
    status              VARCHAR(20) DEFAULT 'offen' CHECK (status IN
                        ('offen','teilbezahlt','bezahlt','ueberfaellig')),

    -- Mahnung
    mahnstufe           INTEGER DEFAULT 0,                -- 0=keine, 1/2/3
    mahnung_versendet_am TIMESTAMPTZ,
    mahnung_dokument_id UUID REFERENCES dokumente(id),

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ
);
CREATE INDEX idx_zahlungen_vertrag ON mietzahlungen(mietvertrag_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_zahlungen_status ON mietzahlungen(status) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX idx_zahlungen_eindeutig ON mietzahlungen(mietvertrag_id, monat, jahr) WHERE deleted_at IS NULL;

-- ============================================================
-- 17. abrechnungen — Nebenkostenabrechnung pro Einheit/Jahr
-- ============================================================
CREATE TABLE abrechnungen (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    einheit_id          UUID NOT NULL REFERENCES einheiten(id) ON DELETE CASCADE,
    mietvertrag_id      UUID NOT NULL REFERENCES mietvertraege(id) ON DELETE CASCADE,
    mieter_id           UUID NOT NULL REFERENCES mieter(id) ON DELETE CASCADE,
    objekt_id           UUID NOT NULL REFERENCES objekte(id) ON DELETE CASCADE,
    vermieter_id        UUID NOT NULL REFERENCES vermieter_profile(id) ON DELETE CASCADE,

    jahr                INTEGER NOT NULL,                 -- Abrechnungsjahr
    zeitraum_von        DATE NOT NULL,
    zeitraum_bis        DATE NOT NULL,

    -- Zusammenfassung
    gesamtkosten        NUMERIC(10,2) NOT NULL,           -- Summe aller umlagefähigen Kosten
    anteil_mieter       NUMERIC(10,2) NOT NULL,           -- Mieteranteil nach Umlageschlüssel
    vorauszahlung_total NUMERIC(10,2) NOT NULL,           -- Summe Vorauszahlungen im Zeitraum
    ergebnis            NUMERIC(10,2) NOT NULL,            -- + = Nachzahlung, - = Guthaben

    -- Status
    status              VARCHAR(20) DEFAULT 'entwurf' CHECK (status IN
                        ('entwurf','geprueft','versendet','rechtskraeftig','archiviert')),
    erstellt_am         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    versendet_am        TIMESTAMPTZ,
    pdf_dokument_id     UUID REFERENCES dokumente(id),

    -- Fristen
    einwendungsfrist_bis DATE,                            -- 12 Monate nach Versand (§556 Abs.3 BGB)
    rechtskraeftig_seit DATE,

    -- KI
    ki_text_generiert   BOOLEAN DEFAULT FALSE,
    ki_vollstaendigkeit_geprueft BOOLEAN DEFAULT FALSE,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ,
    created_by          UUID REFERENCES users(id)
);
CREATE UNIQUE INDEX idx_abrechnung_einheit_jahr ON abrechnungen(einheit_id, jahr) WHERE deleted_at IS NULL;
CREATE INDEX idx_abrechnungen_mieter ON abrechnungen(mieter_id) WHERE deleted_at IS NULL;

-- ============================================================
-- 18. abrechnung_positionen — Einzelne Positionen (NEU in v2)
-- ============================================================
-- Jede Kostenposition in der Abrechnung ist nachvollziehbar
-- zugeordnet. Rechtlich erforderlich für eine saubere
-- Nebenkostenabrechnung nach BetrKV.
-- ============================================================
CREATE TABLE abrechnung_positionen (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    abrechnung_id       UUID NOT NULL REFERENCES abrechnungen(id) ON DELETE CASCADE,
    kosten_id           UUID NOT NULL REFERENCES kosten(id),

    -- Position
    kategorie           VARCHAR(50) NOT NULL,             -- "Müllabfuhr", "Heizung", etc.
    gesamt_betrag       NUMERIC(10,2) NOT NULL,            -- Gesamtkosten dieser Position
    umlageart           VARCHAR(20) NOT NULL CHECK (umlageart IN
                        ('nach_qm','nach_personen','nach_verbrauch')),

    -- Verteilung
    verteilungs_basis   NUMERIC(10,2),                    -- z.B. Gesamt-qm des Objekts
    mieter_anteil       NUMERIC(10,2) NOT NULL,            -- Anteil des Mieters
    mieter_betrag       NUMERIC(10,2) NOT NULL,            -- = gesamt_betrag * (mieter_anteil / verteilungs_basis)

    -- Text (für PDF)
    beschreibung        VARCHAR(200),

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_positionen_abrechnung ON abrechnung_positionen(abrechnung_id);
CREATE INDEX idx_positionen_kosten ON abrechnung_positionen(kosten_id);

-- ============================================================
-- 19. events — Event-Queue für Automatisierungen (NEU)
-- ============================================================
-- Zentrale Tabelle für alle automatisierten Workflows.
-- Cron-Jobs und Trigger schreiben Events hier rein;
-- Worker verarbeiten sie.
-- ============================================================
CREATE TABLE events (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vermieter_id        UUID REFERENCES vermieter_profile(id),

    event_type          VARCHAR(50) NOT NULL,              -- 'ticket_neu', 'miete_ueberfaellig', 'frist_naht', etc.
    entity_type         VARCHAR(30),                      -- 'ticket', 'mietvertrag', 'abrechnung', etc.
    entity_id           UUID,                             -- ID des betroffenen Objekts

    -- Payload (als JSON, anonymisiert falls KI-relevant)
    payload             JSONB,

    -- Status
    status              VARCHAR(20) DEFAULT 'queued' CHECK (status IN
                        ('queued','processing','completed','failed')),
    processed_at        TIMESTAMPTZ,
    error_message       TEXT,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_events_status ON events(status) WHERE status IN ('queued','processing');
CREATE INDEX idx_events_vermieter ON events(vermieter_id);
CREATE INDEX idx_events_type ON events(event_type);

-- ============================================================
-- 20. notifications — Versendete Benachrichtigungen (NEU)
-- ============================================================
CREATE TABLE notifications (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_id            UUID REFERENCES events(id),

    -- Notification
    type                VARCHAR(30) NOT NULL,              -- 'email', 'in_app', 'push'
    subject             VARCHAR(200),
    body                TEXT,
    recipient_email     VARCHAR(255),

    -- Status
    status              VARCHAR(20) DEFAULT 'pending' CHECK (status IN
                        ('pending','sent','failed','read')),
    sent_at             TIMESTAMPTZ,
    read_at             TIMESTAMPTZ,
    error_message       TEXT,

    -- Meta
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_status ON notifications(status) WHERE status IN ('pending','failed');

-- ============================================================
-- 21. audit_logs — DSGVO-Audit-Log (NEU in v2)
-- ============================================================
-- Protokolliert ALLE sicherheitsrelevanten Aktionen.
-- Darf KEINE personenbezogenen Daten im Klartext enthalten.
-- ============================================================
CREATE TABLE audit_logs (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID REFERENCES users(id),         -- Wer hat die Aktion ausgeführt
    vermieter_id        UUID REFERENCES vermieter_profile(id),

    -- Aktion
    action              VARCHAR(50) NOT NULL,              -- 'login','logout','data_export','data_delete',
                                                          -- 'doc_upload','doc_download','ki_call','role_change'
    entity_type         VARCHAR(30),                      -- 'mieter','dokument','abrechnung', etc.
    entity_id           UUID,

    -- Details (keine Personendaten!)
    details             JSONB,                            -- Strukturierte Details (ohne Namen, IBAN etc.)
    ip_address          INET,
    user_agent          TEXT,

    -- Risiko
    risk_level          VARCHAR(10) DEFAULT 'low' CHECK (risk_level IN
                        ('low','medium','high','critical')),

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_created ON audit_logs(created_at);
-- Retention: 12 Monate (durch Cron-Job gelöscht)

-- ============================================================
-- 22. fristen — Fristen-Tracking (NEU)
-- ============================================================
-- Zentrale Tabelle für alle Fristen, die das System
-- überwachen muss.
-- ============================================================
CREATE TABLE fristen (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vermieter_id        UUID NOT NULL REFERENCES vermieter_profile(id) ON DELETE CASCADE,
    mietvertrag_id      UUID REFERENCES mietvertraege(id),

    frist_typ           VARCHAR(30) NOT NULL CHECK (frist_typ IN
                        ('mietende','kuendigungsfrist','abrechnungsfrist','einwendungsfrist',
                         'zinsbindung_ende','sonstiges')),
    frist_datum         DATE NOT NULL,
    beschreibung        VARCHAR(500),

    -- Warnstufen
    warn_in_monaten     INTEGER DEFAULT 6,                -- Standard: 6 Monate vorher warnen
    first_warn_sent     TIMESTAMPTZ,
    second_warn_sent    TIMESTAMPTZ,
    final_warn_sent     TIMESTAMPTZ,

    -- Status
    status              VARCHAR(20) DEFAULT 'aktiv' CHECK (status IN
                        ('aktiv','erledigt','verstrichen')),
    erledigt_am         TIMESTAMPTZ,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_fristen_vermieter ON fristen(vermieter_id) WHERE status = 'aktiv';
CREATE INDEX idx_fristen_datum ON fristen(frist_datum) WHERE status = 'aktiv';

-- ============================================================
-- ROW-LEVEL SECURITY POLICIES
-- ============================================================
-- Datenisolation auf Datenbankebene.
-- Vermieter sieht NUR eigene Daten, Mieter NUR eigene.

-- Aktiviere RLS
ALTER TABLE objekte ENABLE ROW LEVEL SECURITY;
ALTER TABLE einheiten ENABLE ROW LEVEL SECURITY;
ALTER TABLE mieter ENABLE ROW LEVEL SECURITY;
ALTER TABLE mietvertraege ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_kommentare ENABLE ROW LEVEL SECURITY;
ALTER TABLE dokumente ENABLE ROW LEVEL SECURITY;
ALTER TABLE kosten ENABLE ROW LEVEL SECURITY;
ALTER TABLE mietzahlungen ENABLE ROW LEVEL SECURITY;
ALTER TABLE abrechnungen ENABLE ROW LEVEL SECURITY;
ALTER TABLE abrechnung_positionen ENABLE ROW LEVEL SECURITY;
ALTER TABLE fristen ENABLE ROW LEVEL SECURITY;
ALTER TABLE kostenkategorien ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE einwilligungen ENABLE ROW LEVEL SECURITY;

-- Beispiel-Policies (vereinfacht):
-- In der App wird pro Request eine Session-Variable gesetzt:
--   SET app.current_user_id = '<uuid>';
--   SET app.current_role = 'vermieter';
--   SET app.current_vermieter_id = '<uuid>';

-- Policy: Vermieter sieht nur eigene Objekte
CREATE POLICY objekte_isolation ON objekte
    USING (vermieter_id = current_setting('app.current_vermieter_id')::uuid);

-- Policy: Mieter sieht nur eigene Tickets
CREATE POLICY tickets_mieter_isolation ON tickets
    FOR SELECT TO mieter_role
    USING (mieter_id = current_setting('app.current_mieter_id')::uuid);

-- (Weitere Policies analog für alle Tabellen)

-- ============================================================
-- INDIZES für Performance
-- ============================================================
CREATE INDEX idx_objekte_plz ON objekte(plz) WHERE deleted_at IS NULL;
CREATE INDEX idx_einheiten_vermietet ON einheiten(aktuell_vermietet) WHERE deleted_at IS NULL;
CREATE INDEX idx_mietvertraege_status ON mietvertraege(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_tickets_kategorie ON tickets(kategorie) WHERE deleted_at IS NULL;
CREATE INDEX idx_kosten_datum ON kosten(datum) WHERE deleted_at IS NULL;
CREATE INDEX idx_abrechnungen_jahr ON abrechnungen(jahr) WHERE deleted_at IS NULL;

-- ============================================================
-- ZUSAMMENFASSUNG: 22 Tabellen (v1: 13, v2: +9 neu)
-- ============================================================
-- NEU in v2:
--   1. mietvertraege           — Mietverträge separat von Mieter
--   2. mietvertrag_aenderungen — Vertragsänderungs-Historie
--   3. abrechnung_positionen   — Einzelne Kostenpositionen in Abrechnung
--   4. kostenkategorien        — Pro Vermieter konfigurierbare Kategorien
--   5. audit_logs              — DSGVO-Audit-Log (zwingend)
--   6. einwilligungen          — Versionierte DSGVO-Einwilligungen
--   7. user_sessions           — Session-Verwaltung (Geräte-Logout)
--   8. events                  — Event-Queue für Automatisierungen
--   9. notifications           — Versendete Benachrichtigungen
--  10. fristen                 — Zentrales Fristen-Tracking
--
-- ERWEITERT in v2:
--   - users: totp_secret, backup_codes, email_code, failed_login_count, locked_until,
--            password_changed_at, dsdvo_consent_at, dsdvo_consent_version
--   - alle Tabellen: deleted_at (Soft-Delete für DSGVO), updated_at, created_by
--   - dokumente: file_hash (SHA-256 Integrität), original_dateiname
--   - tickets: ki_kategorisiert, ki_prioritaet (KI-Metadaten)
--   - kosten: abrechnung_id, abgerechnet_am (Verknüpfung zur Abrechnung), ki_metadaten
--   - mietzahlungen: betrag_soll/ist, zahlungsreferenz, mahnstufe, mahnung_versendet_am
--   - abrechnungen: zeitraum_von/bis, einwendungsfrist_bis, rechtskraeftig_seit, ki_metadaten
--
-- BEHOBEN in v2:
--   - mieter.vermieter_id Redundanz entfernt (via mietvertraege ableitbar)
--   - mietzahlungen.einheit_id Redundanz entfernt (via mietvertraege ableitbar)
--   - Mietdaten aus mieter in mietvertraege verschoben
--   - kategorie in kosten hat nun FK auf kostenkategorien
-- ============================================================