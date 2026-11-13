"""Initial schema v4.1 — 33 tables, 34 RLS policies, 92 indexes

Manuelle Alembic-Migration fuer das MietVerwaltung SaaS DB-Schema v4.1.
Erstellt alle Tabellen, Views, RLS-Policies, Indizes und Constraints.
Die Migration verwendet rohe SQL-Befehle via op.execute(), da zum Zeitpunkt
der Erstellung noch keine SQLAlchemy-Modelle existieren.
"""

from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================================
    # 1. Extension
    # ============================================================
    op.execute("""
CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- AES-256-GCM Feld-Verschlüsselung
""")

    # ============================================================
    # 2. Tabellen und View (in Abhaengigkeits-Reihenfolge)
    # ============================================================
    op.execute("""
CREATE TABLE users (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email               VARCHAR(255) NOT NULL,
    password_hash       VARCHAR(255) NOT NULL,
    full_name           VARCHAR(100) NOT NULL,
    role                VARCHAR(20) NOT NULL DEFAULT 'vermieter'
                        CHECK (role IN ('vermieter','mieter','admin')),
    vermieter_id        INT REFERENCES users(id),
    totp_secret         VARCHAR(64),
    backup_codes        JSONB,
    email_code          VARCHAR(6),
    email_code_expires  TIMESTAMPTZ,
    failed_login_count  INT DEFAULT 0,
    locked_until        TIMESTAMPTZ,
    dsgvo_consent_at    TIMESTAMPTZ,
    firma               VARCHAR(200),
    steuernr_enc        BYTEA,                 -- AES-256 verschlüsselt
    rechnungs_strasse   VARCHAR(255),
    rechnungs_hausnr    VARCHAR(20),
    rechnungs_plz       VARCHAR(10),
    rechnungs_ort       VARCHAR(100),
    ust_id              VARCHAR(20),            -- optional, z. B. für B2B-E-Rechnung
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ
)
""")

    op.execute("""
ALTER TABLE users ADD CONSTRAINT chk_mieter_vermieter_id
    CHECK (
        (role = 'mieter' AND vermieter_id IS NOT NULL)
        OR (role != 'mieter' AND vermieter_id IS NULL)
    )
""")

    op.execute("""
CREATE VIEW vermieter_public_view WITH (security_invoker = false) AS
SELECT id, full_name, email
FROM users
WHERE role = 'vermieter'
  AND deleted_at IS NULL
  AND id = current_setting('app.current_vermieter_id', true)::INT
""")

    op.execute("""
CREATE TABLE user_sessions (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id             INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token       VARCHAR(255) NOT NULL,
    device_info         VARCHAR(255),
    ip_address          INET,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    expires_at          TIMESTAMPTZ NOT NULL,
    revoked_at          TIMESTAMPTZ
)
""")

    op.execute("""
CREATE TABLE einwilligungen (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id             INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    version             INT NOT NULL DEFAULT 1,
    purpose             VARCHAR(50) NOT NULL, -- ki_anonymisierung, ki_dokumente, marketing
    consent_text        TEXT NOT NULL,
    consented_at        TIMESTAMPTZ NOT NULL,
    withdrawn_at        TIMESTAMPTZ,
    ip_address          INET,
    created_at          TIMESTAMPTZ DEFAULT NOW()
)
""")

    op.execute("""
CREATE TABLE audit_logs (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id             INT REFERENCES users(id),
    vermieter_id        INT REFERENCES users(id),
    action              VARCHAR(100) NOT NULL,
    entity              VARCHAR(50),
    entity_id           INT,
    risk_level          VARCHAR(10) NOT NULL DEFAULT 'niedrig'
                        CHECK (risk_level IN ('niedrig','mittel','hoch')),
    details             JSONB,
    ip_address          INET,
    created_at          TIMESTAMPTZ DEFAULT NOW()
)
""")

    op.execute("""
CREATE TABLE subscriptions (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id             INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id),
    price_per_we        DECIMAL(10,2) NOT NULL,      -- z. B. 9.75
    billing_cycle       VARCHAR(10) NOT NULL
                        CHECK (billing_cycle IN ('monthly','yearly')),
    trial_ends_at       TIMESTAMPTZ,
    stripe_subscription_id VARCHAR(255),
    stripe_customer_id  VARCHAR(255),
    status              VARCHAR(20) NOT NULL DEFAULT 'trial'
                        CHECK (status IN ('trial','active','past_due','cancelled')),
    current_period_start TIMESTAMPTZ,
    current_period_end  TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
)
""")

    op.execute("""
CREATE TABLE plan_usage (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id             INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id),
    wohnungen_count     INT NOT NULL DEFAULT 0,
    last_checked_at     TIMESTAMPTZ DEFAULT NOW()
)
""")

    op.execute("""
CREATE TABLE objekte (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name                VARCHAR(100) NOT NULL,
    address             VARCHAR(255) NOT NULL,
    typ                 VARCHAR(20) NOT NULL, -- mehrfamilienhaus, einfamilienhaus, etc.
    baujahr             INT,
    foto_url            VARCHAR(500),          -- Pfad im Upload-Verzeichnis
    kaufpreis           DECIMAL(12,2),
    kaufdatum           DATE,
    eigenkapital        DECIMAL(12,2),
    darlehen_betrag     DECIMAL(12,2),
    zinssatz            DECIMAL(5,2),          -- z.B. 3.50
    tilgung             DECIMAL(5,2),          -- z.B. 2.00
    monatliche_rate     DECIMAL(10,2),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ
)
""")

    op.execute("""
CREATE TABLE einheiten (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    objekt_id           INT NOT NULL REFERENCES objekte(id) ON DELETE CASCADE,
    name                VARCHAR(100) NOT NULL, -- 'Wohnung 1.OG links'
    size_qm             DECIMAL(6,2) NOT NULL,
    rooms               INT NOT NULL,
    rent_cold           DECIMAL(10,2) NOT NULL,
    floor               VARCHAR(20), -- EG, 1.OG, 2.OG, Souterrain
    energy_class        VARCHAR(2), -- A+, A, B, C, D, E, F, G, H
    last_renovation     DATE,
    available_from      DATE,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ
)
""")

    op.execute("""
CREATE TABLE mieter (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    first_name          VARCHAR(50) NOT NULL,
    last_name           VARCHAR(50) NOT NULL,
    email               VARCHAR(255),
    phone               VARCHAR(30),
    birth_date_enc      BYTEA, -- AES-256 verschlüsselt
    status              VARCHAR(20) DEFAULT 'aktiv'
                        CHECK (status IN ('aktiv','ehemalig','bewerber')),
    since               DATE,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ
)
""")

    op.execute("""
CREATE TABLE mieter_historie (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    einheit_id          INT NOT NULL REFERENCES einheiten(id) ON DELETE CASCADE,
    mieter_id           INT REFERENCES mieter(id) ON DELETE SET NULL,
    mieter_name         VARCHAR(100) NOT NULL,
    mietbeginn          DATE NOT NULL,
    mietende            DATE NOT NULL,
    last_rent           DECIMAL(10,2),
    move_out_reason     VARCHAR(100),
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
)
""")

    op.execute("""
CREATE TABLE einheit_ausstattung (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    einheit_id          INT NOT NULL REFERENCES einheiten(id) ON DELETE CASCADE,
    feature             VARCHAR(50) NOT NULL, -- bad_wanne, bad_dusche, einbaukueche, etc.
    value               VARCHAR(100),
    created_at          TIMESTAMPTZ DEFAULT NOW()
)
""")

    op.execute("""
CREATE TABLE bewerbungen (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    einheit_id          INT NOT NULL REFERENCES einheiten(id) ON DELETE CASCADE,
    first_name          VARCHAR(50) NOT NULL,
    last_name           VARCHAR(50) NOT NULL,
    email               VARCHAR(255),
    phone               VARCHAR(30),
    income_monthly      DECIMAL(10,2),
    schufa_score        INT,
    documents           JSONB,
    status              VARCHAR(20) DEFAULT 'offen'
                        CHECK (status IN ('offen','angenommen','abgelehnt')),
    applied_at          TIMESTAMPTZ DEFAULT NOW(),
    decided_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ
)
""")

    op.execute("""
CREATE TABLE mietvertraege (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mieter_id           INT NOT NULL REFERENCES mieter(id) ON DELETE CASCADE,
    einheit_id          INT NOT NULL REFERENCES einheiten(id),
    mietbeginn          DATE NOT NULL,
    mietende            DATE,
    miete_cold          DECIMAL(10,2) NOT NULL,
    nebenkosten_voraus  DECIMAL(10,2) NOT NULL,
    kaution             DECIMAL(10,2),
    kaution_hinterlegt  BOOLEAN DEFAULT FALSE,
    status              VARCHAR(20) DEFAULT 'aktiv'
                        CHECK (status IN ('aktiv','gekuendigt','beendet')),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ
)
""")

    op.execute("""
CREATE TABLE mietvertrag_aenderungen (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vertrag_id          INT NOT NULL REFERENCES mietvertraege(id) ON DELETE CASCADE,
    field               VARCHAR(50) NOT NULL,
    old_value           TEXT,
    new_value           TEXT,
    changed_at          TIMESTAMPTZ DEFAULT NOW(),
    reason              TEXT
)
""")

    op.execute("""
CREATE TABLE kostenkategorien (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name                VARCHAR(50) NOT NULL,
    betrvk_key          VARCHAR(20),
    umlagefaehig        BOOLEAN DEFAULT TRUE,
    verteilungsschluessel VARCHAR(20) DEFAULT 'qm'
                        CHECK (verteilungsschluessel IN ('qm','personen','verbrauch')),
    is_default          BOOLEAN DEFAULT FALSE
)
""")

    op.execute("""
CREATE TABLE handwerker (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name                VARCHAR(100) NOT NULL,
    gewerk              VARCHAR(50),
    email               VARCHAR(255),
    phone               VARCHAR(30),
    rating              INT,
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ DEFAULT NOW()
)
""")

    op.execute("""
CREATE TABLE ticket_sla (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name                VARCHAR(50) NOT NULL,
    response_time_hours INT NOT NULL DEFAULT 48,
    resolution_time_hours INT NOT NULL DEFAULT 168,
    biz_hours_only      BOOLEAN DEFAULT TRUE,
    biz_start           TIME DEFAULT '09:00',
    biz_end             TIME DEFAULT '17:00',
    biz_days            VARCHAR(7) DEFAULT 'mtwtf',
    escalation_levels   JSONB,
    is_active           BOOLEAN DEFAULT TRUE
)
""")

    op.execute("""
CREATE TABLE ticket_trigger (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name                VARCHAR(100) NOT NULL,
    trigger_type        VARCHAR(20) NOT NULL,
    condition           JSONB NOT NULL,
    perform             JSONB NOT NULL,
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ DEFAULT NOW()
)
""")

    op.execute("""
CREATE TABLE abrechnungen (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    einheit_id          INT NOT NULL REFERENCES einheiten(id),
    objekt_id           INT REFERENCES objekte(id),
    jahr                INT NOT NULL,
    zeitraum_von        DATE NOT NULL,
    zeitraum_bis        DATE NOT NULL,
    einwendungsfrist_bis DATE,
    rechtskraeftig_seit DATE,
    status              VARCHAR(20) DEFAULT 'entwurf'
                        CHECK (status IN ('entwurf','versendet','rechtskraeftig','angefochten')),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ
)
""")

    op.execute("""
CREATE TABLE kosten (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    objekt_id           INT REFERENCES objekte(id),
    einheit_id          INT REFERENCES einheiten(id),
    kategorie_id        INT REFERENCES kostenkategorien(id),
    betrag              DECIMAL(10,2) NOT NULL,
    datum               DATE NOT NULL,
    umlagefaehig        BOOLEAN DEFAULT TRUE,
    abrechnung_id       INT REFERENCES abrechnungen(id),
    abgerechnet_am      DATE,
    ki_kategorisiert    BOOLEAN DEFAULT FALSE,
    datev_konto         VARCHAR(10),
    datev_buchungstext  VARCHAR(100),
    deleted_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW()
)
""")

    op.execute("""
CREATE TABLE abrechnung_positionen (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    abrechnung_id       INT NOT NULL REFERENCES abrechnungen(id) ON DELETE CASCADE,
    kategorie_id        INT REFERENCES kostenkategorien(id),
    kosten_id           INT REFERENCES kosten(id),
    betrag_total        DECIMAL(10,2) NOT NULL,
    umlageanteil        DECIMAL(10,2) NOT NULL,
    verteilungsschluessel VARCHAR(20) NOT NULL
                        CHECK (verteilungsschluessel IN ('qm','personen','verbrauch')),
    datev_betrag        DECIMAL(10,2),
    deleted_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW()
)
""")

    op.execute("""
CREATE TABLE dokumente (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    objekt_id           INT REFERENCES objekte(id),
    einheit_id          INT REFERENCES einheiten(id),
    mieter_id           INT REFERENCES mieter(id),
    name                VARCHAR(255) NOT NULL,
    type                VARCHAR(20) NOT NULL, -- vertrag, protokoll, bewerbung, rechnung, foto, sonstiges
    sichtbarkeit        VARCHAR(20) NOT NULL DEFAULT 'vermieter'
                        CHECK (sichtbarkeit IN ('vermieter','mieter','beide','handwerker')),
    file_path           VARCHAR(500) NOT NULL,
    file_hash           VARCHAR(64) NOT NULL, -- SHA-256
    file_size           INT,
    mime_type           VARCHAR(50),
    encrypted           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ
)
""")

    op.execute("""
CREATE TABLE dokument_freigaben (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dokument_id         INT NOT NULL REFERENCES dokumente(id) ON DELETE CASCADE,
    user_id             INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    freigegeben_von     INT REFERENCES users(id),
    freigegeben_am      TIMESTAMPTZ DEFAULT NOW(),
    created_at          TIMESTAMPTZ DEFAULT NOW()
)
""")

    op.execute("""
CREATE TABLE tickets (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mieter_id           INT REFERENCES mieter(id),
    einheit_id          INT REFERENCES einheiten(id),
    ticket_number       VARCHAR(20) UNIQUE NOT NULL,
    title               VARCHAR(200) NOT NULL,
    description         TEXT,
    category            VARCHAR(50),
    priority            VARCHAR(10) DEFAULT 'normal',
    status              VARCHAR(20) DEFAULT 'offen',
    ki_kategorisiert    BOOLEAN DEFAULT FALSE,
    ki_prioritaet       BOOLEAN DEFAULT FALSE,
    assigned_to         INT REFERENCES users(id),
    handwerker_id       INT REFERENCES handwerker(id),
    sla_id              INT REFERENCES ticket_sla(id),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    closed_at           TIMESTAMPTZ
)
""")

    op.execute("""
CREATE TABLE ticket_kommentare (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ticket_id           INT NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    author_id           INT REFERENCES users(id),
    author_role         VARCHAR(20) NOT NULL, -- vermieter, mieter, handwerker, system
    content             TEXT NOT NULL,
    ist_ki_entwurf      BOOLEAN DEFAULT FALSE,
    is_internal         BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMPTZ DEFAULT NOW()
)
""")

    op.execute("""
CREATE TABLE mietzahlungen (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mieter_id           INT REFERENCES mieter(id),
    vertrag_id          INT REFERENCES mietvertraege(id),
    betrag_soll         DECIMAL(10,2) NOT NULL,
    betrag_ist          DECIMAL(10,2),
    zahlungsdatum       DATE,
    mahnstufe           INT DEFAULT 0,
    zahlungsreferenz    VARCHAR(50),
    created_at          TIMESTAMPTZ DEFAULT NOW()
)
""")

    op.execute("""
CREATE TABLE events (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type          VARCHAR(50) NOT NULL,
    entity              VARCHAR(50),
    entity_id           INT,
    payload             JSONB,
    processed_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW()
)
""")

    op.execute("""
CREATE TABLE notifications (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_id             INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_id            INT REFERENCES events(id),
    type                VARCHAR(20) NOT NULL, -- email, in_app, push
    title               VARCHAR(200) NOT NULL,
    body                TEXT,
    status              VARCHAR(20) DEFAULT 'pending',
    sent_at             TIMESTAMPTZ
)
""")

    op.execute("""
CREATE TABLE fristen (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entity              VARCHAR(50),
    entity_id           INT,
    deadline            DATE NOT NULL,
    warn_level          VARCHAR(10) DEFAULT 'green',
    description         TEXT,
    is_done             BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
)
""")

    op.execute("""
CREATE TABLE onboarding_progress (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id             INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    step                VARCHAR(50) NOT NULL,
    is_done             BOOLEAN DEFAULT FALSE,
    done_at             TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW()
)
""")

    op.execute("""
CREATE TABLE ai_stored_results (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    use_case            VARCHAR(50) NOT NULL,
    model               VARCHAR(50) NOT NULL,
    prompt_hash         VARCHAR(64) NOT NULL,
    result              JSONB NOT NULL,
    confidence          VARCHAR(20),
    tokens_used         INT,
    duration_ms         INT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
)
""")

    op.execute("""
CREATE TABLE referrals (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    referrer_id         INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    referred_email      VARCHAR(255) NOT NULL,
    referred_user_id    INT REFERENCES users(id),
    status              VARCHAR(20) DEFAULT 'pending',
    reward_type         VARCHAR(20),
    reward_amount       DECIMAL(10,2),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    rewarded_at         TIMESTAMPTZ
)
""")

    op.execute("""
CREATE TABLE bankverbindungen (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mieter_id           INT REFERENCES mieter(id) ON DELETE SET NULL,
    iban_enc            BYTEA NOT NULL,          -- AES-256 verschlüsselt
    bic                 VARCHAR(11),
    kontoinhaber        VARCHAR(100) NOT NULL,
    bankname            VARCHAR(100),
    is_default          BOOLEAN DEFAULT FALSE,
    deleted_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW()
)
""")

    # ============================================================
    # 3. Row-Level Security aktivieren und Policies anlegen
    # ============================================================
    op.execute("""
ALTER TABLE users                ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE bankverbindungen     ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE subscriptions        ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE plan_usage           ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE objekte              ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE einheiten            ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE einheit_ausstattung  ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE mieter               ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE mieter_historie      ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE bewerbungen          ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE mietvertraege        ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE mietvertrag_aenderungen ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE kostenkategorien     ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE kosten               ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE dokumente            ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE dokument_freigaben   ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE tickets              ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE ticket_kommentare    ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE ticket_sla           ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE ticket_trigger       ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE mietzahlungen        ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE abrechnungen         ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE abrechnung_positionen ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE events               ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE notifications        ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE fristen              ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE ai_stored_results    ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE referrals            ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE handwerker           ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE audit_logs           ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE user_sessions        ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE einwilligungen       ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
ALTER TABLE onboarding_progress  ENABLE ROW LEVEL SECURITY
""")

    op.execute("""
DROP POLICY IF EXISTS users_isolation ON users
""")

    op.execute("""
CREATE POLICY users_isolation ON users
    FOR ALL
    USING (
        id = current_setting('app.current_user_id')::INT
        OR (
            current_setting('app.current_user_role') IN ('vermieter','admin')
            AND role = 'mieter'
            AND vermieter_id = current_setting('app.current_user_id')::INT
        )
        OR current_setting('app.current_user_role') = 'admin'
    )
""")

    op.execute("""
CREATE POLICY bankverbindungen_isolation ON bankverbindungen
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY subscriptions_isolation ON subscriptions
    FOR ALL USING (user_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY plan_usage_isolation ON plan_usage
    FOR ALL USING (user_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY objekte_isolation ON objekte
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY einheiten_isolation ON einheiten
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY einheit_ausstattung_isolation ON einheit_ausstattung
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY mieter_isolation ON mieter
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY mieter_historie_isolation ON mieter_historie
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY bewerbungen_isolation ON bewerbungen
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY mietvertraege_isolation ON mietvertraege
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY mietvertrag_aenderungen_isolation ON mietvertrag_aenderungen
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY kostenkategorien_isolation ON kostenkategorien
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY kosten_isolation ON kosten
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY dokumente_isolation ON dokumente
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY dokument_freigaben_isolation ON dokument_freigaben
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY tickets_isolation ON tickets
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY ticket_kommentare_isolation ON ticket_kommentare
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY ticket_sla_isolation ON ticket_sla
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY ticket_trigger_isolation ON ticket_trigger
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY mietzahlungen_isolation ON mietzahlungen
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY abrechnungen_isolation ON abrechnungen
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY abrechnung_positionen_isolation ON abrechnung_positionen
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY events_isolation ON events
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY notifications_isolation ON notifications
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY fristen_isolation ON fristen
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY ai_stored_results_isolation ON ai_stored_results
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY referrals_isolation ON referrals
    FOR ALL USING (referrer_id = current_setting('app.current_user_id')::INT)
""")

    op.execute("""
CREATE POLICY handwerker_isolation ON handwerker
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY audit_logs_isolation ON audit_logs
    FOR ALL USING (vermieter_id = current_setting('app.current_vermieter_id')::INT)
""")

    op.execute("""
CREATE POLICY user_sessions_isolation ON user_sessions
    FOR ALL USING (user_id = current_setting('app.current_user_id')::INT)
""")

    op.execute("""
CREATE POLICY einwilligungen_isolation ON einwilligungen
    FOR ALL USING (user_id = current_setting('app.current_user_id')::INT)
""")

    op.execute("""
CREATE POLICY onboarding_progress_isolation ON onboarding_progress
    FOR ALL USING (user_id = current_setting('app.current_user_id')::INT)
""")

    # ============================================================
    # 4. Indizes
    # ============================================================
    op.execute("""
CREATE UNIQUE INDEX idx_users_email_active    ON users(email) WHERE deleted_at IS NULL;  -- v4.1
""")

    op.execute("""
CREATE INDEX idx_users_vermieter_id           ON users(vermieter_id) WHERE role = 'mieter'
""")

    op.execute("""
CREATE INDEX idx_user_sessions_user           ON user_sessions(user_id)
""")

    op.execute("""
CREATE INDEX idx_user_sessions_expires        ON user_sessions(expires_at)
""")

    op.execute("""
CREATE INDEX idx_einwilligungen_user          ON einwilligungen(user_id)
""")

    op.execute("""
CREATE INDEX idx_einwilligungen_purpose       ON einwilligungen(purpose)
""")

    op.execute("""
CREATE INDEX idx_audit_logs_user              ON audit_logs(user_id)
""")

    op.execute("""
CREATE INDEX idx_audit_logs_vermieter         ON audit_logs(vermieter_id)
""")

    op.execute("""
CREATE INDEX idx_audit_logs_created           ON audit_logs(created_at)
""")

    op.execute("""
CREATE INDEX idx_bankverbindungen_vermieter   ON bankverbindungen(vermieter_id) WHERE deleted_at IS NULL;  -- v4.1
""")

    op.execute("""
CREATE INDEX idx_bankverbindungen_mieter      ON bankverbindungen(mieter_id) WHERE mieter_id IS NOT NULL AND deleted_at IS NULL;  -- v4.1
""")

    op.execute("""
CREATE INDEX idx_subscriptions_user           ON subscriptions(user_id)
""")

    op.execute("""
CREATE INDEX idx_plan_usage_user              ON plan_usage(user_id)
""")

    op.execute("""
CREATE INDEX idx_objekte_vermieter            ON objekte(vermieter_id) WHERE deleted_at IS NULL
""")

    op.execute("""
CREATE INDEX idx_einheiten_objekt             ON einheiten(objekt_id) WHERE deleted_at IS NULL
""")

    op.execute("""
CREATE INDEX idx_einheiten_vermieter          ON einheiten(vermieter_id) WHERE deleted_at IS NULL
""")

    op.execute("""
CREATE INDEX idx_einheit_ausstattung_einheit  ON einheit_ausstattung(einheit_id)
""")

    op.execute("""
CREATE INDEX idx_mieter_vermieter             ON mieter(vermieter_id) WHERE deleted_at IS NULL
""")

    op.execute("""
CREATE INDEX idx_mieter_historie_einheit      ON mieter_historie(einheit_id)
""")

    op.execute("""
CREATE INDEX idx_bewerbungen_einheit          ON bewerbungen(einheit_id, status) WHERE deleted_at IS NULL
""")

    op.execute("""
CREATE INDEX idx_mietvertraege_vermieter      ON mietvertraege(vermieter_id) WHERE deleted_at IS NULL
""")

    op.execute("""
CREATE INDEX idx_mietvertraege_einheit        ON mietvertraege(einheit_id) WHERE deleted_at IS NULL
""")

    op.execute("""
CREATE INDEX idx_mietvertraege_mieter       ON mietvertraege(mieter_id) WHERE deleted_at IS NULL
""")

    op.execute("""
CREATE INDEX idx_mietvertraege_status         ON mietvertraege(status) WHERE deleted_at IS NULL
""")

    op.execute("""
CREATE INDEX idx_mietvertrag_aenderungen_vertrag ON mietvertrag_aenderungen(vertrag_id)
""")

    op.execute("""
CREATE INDEX idx_kostenkategorien_vermieter   ON kostenkategorien(vermieter_id)
""")

    op.execute("""
CREATE INDEX idx_kosten_objekt                ON kosten(objekt_id, datum) WHERE deleted_at IS NULL;  -- v4.1
""")

    op.execute("""
CREATE INDEX idx_kosten_einheit               ON kosten(einheit_id) WHERE einheit_id IS NOT NULL AND deleted_at IS NULL;  -- v4.1
""")

    op.execute("""
CREATE INDEX idx_kosten_abrechnung            ON kosten(abrechnung_id) WHERE abrechnung_id IS NOT NULL AND deleted_at IS NULL;  -- v4.1
""")

    op.execute("""
CREATE INDEX idx_mietzahlungen_vertrag        ON mietzahlungen(vertrag_id)
""")

    op.execute("""
CREATE INDEX idx_mietzahlungen_vermieter      ON mietzahlungen(vermieter_id)
""")

    op.execute("""
CREATE UNIQUE INDEX uq_abrechnungen_einheit_jahr_active
    ON abrechnungen(einheit_id, jahr) WHERE deleted_at IS NULL;  -- v4.1
""")

    op.execute("""
CREATE INDEX idx_abrechnungen_vermieter       ON abrechnungen(vermieter_id) WHERE deleted_at IS NULL
""")

    op.execute("""
CREATE INDEX idx_abrechnung_positionen_abrechnung ON abrechnung_positionen(abrechnung_id) WHERE deleted_at IS NULL;  -- v4.1
""")

    op.execute("""
CREATE INDEX idx_abrechnung_positionen_kosten     ON abrechnung_positionen(kosten_id) WHERE deleted_at IS NULL;  -- v4.1
""")

    op.execute("""
CREATE INDEX idx_dokumente_vermieter          ON dokumente(vermieter_id) WHERE deleted_at IS NULL
""")

    op.execute("""
CREATE INDEX idx_dokumente_mieter             ON dokumente(mieter_id) WHERE deleted_at IS NULL AND mieter_id IS NOT NULL
""")

    op.execute("""
CREATE INDEX idx_dokumente_objekt             ON dokumente(objekt_id) WHERE deleted_at IS NULL AND objekt_id IS NOT NULL
""")

    op.execute("""
CREATE INDEX idx_dokumente_einheit            ON dokumente(einheit_id) WHERE deleted_at IS NULL AND einheit_id IS NOT NULL
""")

    op.execute("""
CREATE INDEX idx_dokument_freigaben_dokument  ON dokument_freigaben(dokument_id)
""")

    op.execute("""
CREATE INDEX idx_tickets_vermieter_status     ON tickets(vermieter_id, status)
""")

    op.execute("""
CREATE INDEX idx_tickets_einheit                ON tickets(einheit_id)
""")

    op.execute("""
CREATE INDEX idx_tickets_mieter               ON tickets(mieter_id)
""")

    op.execute("""
CREATE INDEX idx_ticket_kommentare_ticket     ON ticket_kommentare(ticket_id)
""")

    op.execute("""
CREATE INDEX idx_ticket_sla_vermieter         ON ticket_sla(vermieter_id)
""")

    op.execute("""
CREATE INDEX idx_ticket_trigger_vermieter     ON ticket_trigger(vermieter_id)
""")

    op.execute("""
CREATE INDEX idx_events_pending               ON events(processed_at) WHERE processed_at IS NULL
""")

    op.execute("""
CREATE INDEX idx_events_vermieter             ON events(vermieter_id)
""")

    op.execute("""
CREATE INDEX idx_notifications_user           ON notifications(user_id)
""")

    op.execute("""
CREATE INDEX idx_notifications_status         ON notifications(status) WHERE status IN ('pending','failed')
""")

    op.execute("""
CREATE INDEX idx_fristen_deadline             ON fristen(deadline, warn_level)
""")

    op.execute("""
CREATE INDEX idx_fristen_vermieter            ON fristen(vermieter_id)
""")

    op.execute("""
CREATE INDEX idx_onboarding_user              ON onboarding_progress(user_id, is_done)
""")

    op.execute("""
CREATE INDEX idx_ai_stored_results_usecase    ON ai_stored_results(vermieter_id, use_case)
""")

    op.execute("""
CREATE INDEX idx_referrals_referrer           ON referrals(referrer_id)
""")

    op.execute("""
CREATE INDEX idx_handwerker_vermieter         ON handwerker(vermieter_id)
""")



def downgrade() -> None:
    # ============================================================
    # Downgrade: alles in umgekehrter Reihenfolge entfernen
    # ============================================================

    # 1. Indizes droppen
    # --------------------------------------------------------
    op.execute('DROP INDEX IF EXISTS "idx_handwerker_vermieter"')
    op.execute('DROP INDEX IF EXISTS "idx_referrals_referrer"')
    op.execute('DROP INDEX IF EXISTS "idx_ai_stored_results_usecase"')
    op.execute('DROP INDEX IF EXISTS "idx_onboarding_user"')
    op.execute('DROP INDEX IF EXISTS "idx_fristen_vermieter"')
    op.execute('DROP INDEX IF EXISTS "idx_fristen_deadline"')
    op.execute('DROP INDEX IF EXISTS "idx_notifications_status"')
    op.execute('DROP INDEX IF EXISTS "idx_notifications_user"')
    op.execute('DROP INDEX IF EXISTS "idx_events_vermieter"')
    op.execute('DROP INDEX IF EXISTS "idx_events_pending"')
    op.execute('DROP INDEX IF EXISTS "idx_ticket_trigger_vermieter"')
    op.execute('DROP INDEX IF EXISTS "idx_ticket_sla_vermieter"')
    op.execute('DROP INDEX IF EXISTS "idx_ticket_kommentare_ticket"')
    op.execute('DROP INDEX IF EXISTS "idx_tickets_mieter"')
    op.execute('DROP INDEX IF EXISTS "idx_tickets_einheit"')
    op.execute('DROP INDEX IF EXISTS "idx_tickets_vermieter_status"')
    op.execute('DROP INDEX IF EXISTS "idx_dokument_freigaben_dokument"')
    op.execute('DROP INDEX IF EXISTS "idx_dokumente_einheit"')
    op.execute('DROP INDEX IF EXISTS "idx_dokumente_objekt"')
    op.execute('DROP INDEX IF EXISTS "idx_dokumente_mieter"')
    op.execute('DROP INDEX IF EXISTS "idx_dokumente_vermieter"')
    op.execute('DROP INDEX IF EXISTS "idx_abrechnung_positionen_kosten"')
    op.execute('DROP INDEX IF EXISTS "idx_abrechnung_positionen_abrechnung"')
    op.execute('DROP INDEX IF EXISTS "idx_abrechnungen_vermieter"')
    op.execute('DROP INDEX IF EXISTS "uq_abrechnungen_einheit_jahr_active"')
    op.execute('DROP INDEX IF EXISTS "idx_mietzahlungen_vermieter"')
    op.execute('DROP INDEX IF EXISTS "idx_mietzahlungen_vertrag"')
    op.execute('DROP INDEX IF EXISTS "idx_kosten_abrechnung"')
    op.execute('DROP INDEX IF EXISTS "idx_kosten_einheit"')
    op.execute('DROP INDEX IF EXISTS "idx_kosten_objekt"')
    op.execute('DROP INDEX IF EXISTS "idx_kostenkategorien_vermieter"')
    op.execute('DROP INDEX IF EXISTS "idx_mietvertrag_aenderungen_vertrag"')
    op.execute('DROP INDEX IF EXISTS "idx_mietvertraege_status"')
    op.execute('DROP INDEX IF EXISTS "idx_mietvertraege_mieter"')
    op.execute('DROP INDEX IF EXISTS "idx_mietvertraege_einheit"')
    op.execute('DROP INDEX IF EXISTS "idx_mietvertraege_vermieter"')
    op.execute('DROP INDEX IF EXISTS "idx_bewerbungen_einheit"')
    op.execute('DROP INDEX IF EXISTS "idx_mieter_historie_einheit"')
    op.execute('DROP INDEX IF EXISTS "idx_mieter_vermieter"')
    op.execute('DROP INDEX IF EXISTS "idx_einheit_ausstattung_einheit"')
    op.execute('DROP INDEX IF EXISTS "idx_einheiten_vermieter"')
    op.execute('DROP INDEX IF EXISTS "idx_einheiten_objekt"')
    op.execute('DROP INDEX IF EXISTS "idx_objekte_vermieter"')
    op.execute('DROP INDEX IF EXISTS "idx_plan_usage_user"')
    op.execute('DROP INDEX IF EXISTS "idx_subscriptions_user"')
    op.execute('DROP INDEX IF EXISTS "idx_bankverbindungen_mieter"')
    op.execute('DROP INDEX IF EXISTS "idx_bankverbindungen_vermieter"')
    op.execute('DROP INDEX IF EXISTS "idx_audit_logs_created"')
    op.execute('DROP INDEX IF EXISTS "idx_audit_logs_vermieter"')
    op.execute('DROP INDEX IF EXISTS "idx_audit_logs_user"')
    op.execute('DROP INDEX IF EXISTS "idx_einwilligungen_purpose"')
    op.execute('DROP INDEX IF EXISTS "idx_einwilligungen_user"')
    op.execute('DROP INDEX IF EXISTS "idx_user_sessions_expires"')
    op.execute('DROP INDEX IF EXISTS "idx_user_sessions_user"')
    op.execute('DROP INDEX IF EXISTS "idx_users_vermieter_id"')
    op.execute('DROP INDEX IF EXISTS "idx_users_email_active"')

    # 2. RLS-Policies droppen
    # --------------------------------------------------------
    op.execute('DROP POLICY IF EXISTS "onboarding_progress_isolation" ON "onboarding_progress"')
    op.execute('DROP POLICY IF EXISTS "einwilligungen_isolation" ON "einwilligungen"')
    op.execute('DROP POLICY IF EXISTS "user_sessions_isolation" ON "user_sessions"')
    op.execute('DROP POLICY IF EXISTS "audit_logs_isolation" ON "audit_logs"')
    op.execute('DROP POLICY IF EXISTS "handwerker_isolation" ON "handwerker"')
    op.execute('DROP POLICY IF EXISTS "referrals_isolation" ON "referrals"')
    op.execute('DROP POLICY IF EXISTS "ai_stored_results_isolation" ON "ai_stored_results"')
    op.execute('DROP POLICY IF EXISTS "fristen_isolation" ON "fristen"')
    op.execute('DROP POLICY IF EXISTS "notifications_isolation" ON "notifications"')
    op.execute('DROP POLICY IF EXISTS "events_isolation" ON "events"')
    op.execute('DROP POLICY IF EXISTS "abrechnung_positionen_isolation" ON "abrechnung_positionen"')
    op.execute('DROP POLICY IF EXISTS "abrechnungen_isolation" ON "abrechnungen"')
    op.execute('DROP POLICY IF EXISTS "mietzahlungen_isolation" ON "mietzahlungen"')
    op.execute('DROP POLICY IF EXISTS "ticket_trigger_isolation" ON "ticket_trigger"')
    op.execute('DROP POLICY IF EXISTS "ticket_sla_isolation" ON "ticket_sla"')
    op.execute('DROP POLICY IF EXISTS "ticket_kommentare_isolation" ON "ticket_kommentare"')
    op.execute('DROP POLICY IF EXISTS "tickets_isolation" ON "tickets"')
    op.execute('DROP POLICY IF EXISTS "dokument_freigaben_isolation" ON "dokument_freigaben"')
    op.execute('DROP POLICY IF EXISTS "dokumente_isolation" ON "dokumente"')
    op.execute('DROP POLICY IF EXISTS "kosten_isolation" ON "kosten"')
    op.execute('DROP POLICY IF EXISTS "kostenkategorien_isolation" ON "kostenkategorien"')
    op.execute('DROP POLICY IF EXISTS "mietvertrag_aenderungen_isolation" ON "mietvertrag_aenderungen"')
    op.execute('DROP POLICY IF EXISTS "mietvertraege_isolation" ON "mietvertraege"')
    op.execute('DROP POLICY IF EXISTS "bewerbungen_isolation" ON "bewerbungen"')
    op.execute('DROP POLICY IF EXISTS "mieter_historie_isolation" ON "mieter_historie"')
    op.execute('DROP POLICY IF EXISTS "mieter_isolation" ON "mieter"')
    op.execute('DROP POLICY IF EXISTS "einheit_ausstattung_isolation" ON "einheit_ausstattung"')
    op.execute('DROP POLICY IF EXISTS "einheiten_isolation" ON "einheiten"')
    op.execute('DROP POLICY IF EXISTS "objekte_isolation" ON "objekte"')
    op.execute('DROP POLICY IF EXISTS "plan_usage_isolation" ON "plan_usage"')
    op.execute('DROP POLICY IF EXISTS "subscriptions_isolation" ON "subscriptions"')
    op.execute('DROP POLICY IF EXISTS "bankverbindungen_isolation" ON "bankverbindungen"')
    op.execute('DROP POLICY IF EXISTS "users_isolation" ON "users"')

    # 3. Tabellen droppen (in umgekehrter Abhaengigkeits-Reihenfolge)
    # --------------------------------------------------------
    op.execute('DROP TABLE IF EXISTS "bankverbindungen" CASCADE')
    op.execute('DROP TABLE IF EXISTS "referrals" CASCADE')
    op.execute('DROP TABLE IF EXISTS "ai_stored_results" CASCADE')
    op.execute('DROP TABLE IF EXISTS "onboarding_progress" CASCADE')
    op.execute('DROP TABLE IF EXISTS "fristen" CASCADE')
    op.execute('DROP TABLE IF EXISTS "notifications" CASCADE')
    op.execute('DROP TABLE IF EXISTS "events" CASCADE')
    op.execute('DROP TABLE IF EXISTS "mietzahlungen" CASCADE')
    op.execute('DROP TABLE IF EXISTS "ticket_kommentare" CASCADE')
    op.execute('DROP TABLE IF EXISTS "tickets" CASCADE')
    op.execute('DROP TABLE IF EXISTS "dokument_freigaben" CASCADE')
    op.execute('DROP TABLE IF EXISTS "dokumente" CASCADE')
    op.execute('DROP TABLE IF EXISTS "abrechnung_positionen" CASCADE')
    op.execute('DROP TABLE IF EXISTS "kosten" CASCADE')
    op.execute('DROP TABLE IF EXISTS "abrechnungen" CASCADE')
    op.execute('DROP TABLE IF EXISTS "ticket_trigger" CASCADE')
    op.execute('DROP TABLE IF EXISTS "ticket_sla" CASCADE')
    op.execute('DROP TABLE IF EXISTS "handwerker" CASCADE')
    op.execute('DROP TABLE IF EXISTS "kostenkategorien" CASCADE')
    op.execute('DROP TABLE IF EXISTS "mietvertrag_aenderungen" CASCADE')
    op.execute('DROP TABLE IF EXISTS "mietvertraege" CASCADE')
    op.execute('DROP TABLE IF EXISTS "bewerbungen" CASCADE')
    op.execute('DROP TABLE IF EXISTS "einheit_ausstattung" CASCADE')
    op.execute('DROP TABLE IF EXISTS "mieter_historie" CASCADE')
    op.execute('DROP TABLE IF EXISTS "mieter" CASCADE')
    op.execute('DROP TABLE IF EXISTS "einheiten" CASCADE')
    op.execute('DROP TABLE IF EXISTS "objekte" CASCADE')
    op.execute('DROP TABLE IF EXISTS "plan_usage" CASCADE')
    op.execute('DROP TABLE IF EXISTS "subscriptions" CASCADE')
    op.execute('DROP TABLE IF EXISTS "audit_logs" CASCADE')
    op.execute('DROP TABLE IF EXISTS "einwilligungen" CASCADE')
    op.execute('DROP TABLE IF EXISTS "user_sessions" CASCADE')
    op.execute('DROP TABLE IF EXISTS "users" CASCADE')

    op.execute('DROP VIEW IF EXISTS "vermieter_public_view"')
    # pgcrypto wird nicht gedroppt, weil es vom DB-Superuser vorinstalliert ist
    # und der mv-User keine Owner-Rechte dafuer hat.