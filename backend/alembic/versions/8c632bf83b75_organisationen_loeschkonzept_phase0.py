"""organisationen_loeschkonzept_phase0

Revision ID: 8c632bf83b75
Revises: 1a2b3c4d5e6f
Create Date: 2026-11-25 10:12:46.218545

Manuelle Migration fuer:
- Organisationen (organisationen, organisations_mitglieder, eigentuemer,
  mitglied_objekt_scope, org_features, einladungen)
- Löschkonzept (loeschregeln, loeschprotokoll)
- org_id auf allen fachlichen Tabellen (nullable +
  Backfill pro Vermieter -> Organisation)
- RetentionMixin-Felder (lifecycle_status, gesperrt_am, loeschklasse,
  loeschen_fruehestens_am, legal_hold) auf Tabellen mit personenbezogenen Daten
- RLS-Policies fuer neue Tabellen
"""
from alembic import op
import sqlalchemy as sa

revision = '8c632bf83b75'
down_revision = '1a2b3c4d5e6f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================================
    # 0. Pruefen, ob app_user existiert
    # ============================================================
    result = op.get_bind().execute(sa.text("SELECT 1 FROM pg_roles WHERE rolname = 'app_user'"))
    app_user_exists = result.scalar() is not None

    if not app_user_exists:
        # In Production muss der DBA/Superuser app_user anlegen.
        # Siehe docs/ops/database-roles.md
        raise RuntimeError(
            "Datenbank-Rolle 'app_user' fehlt. "
            "Bitte als Superuser ausfuehren: CREATE ROLE app_user WITH LOGIN NOINHERIT;"
        )

    # ============================================================
    # 1. Sequenzen
    # ============================================================
    op.execute("CREATE SEQUENCE IF NOT EXISTS organisationen_public_id_seq START 100000")

    # ============================================================
    # 2. Neue Tabellen
    # ============================================================
    op.execute("""
CREATE TABLE organisationen (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    public_id           BIGINT NOT NULL UNIQUE DEFAULT nextval('organisationen_public_id_seq'),
    typ                 VARCHAR(30) NOT NULL DEFAULT 'selbstverwalter'
                        CHECK (typ IN ('selbstverwalter','hausverwaltung','partner')),
    name                VARCHAR(150) NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'aktiv'
                        CHECK (status IN ('aktiv','gesperrt','geloescht')),
    plan                VARCHAR(30) NOT NULL DEFAULT 'basis',
    stripe_customer_id  VARCHAR(100),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
)
""")

    op.execute("""
CREATE TABLE organisations_mitglieder (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    org_id              INT NOT NULL REFERENCES organisationen(id) ON DELETE CASCADE,
    user_id             INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rolle               VARCHAR(30) NOT NULL DEFAULT 'sachbearbeiter'
                        CHECK (rolle IN ('org_admin','sachbearbeiter','buchhaltung','eigentuemer')),
    aktiv               BOOLEAN NOT NULL DEFAULT TRUE,
    eingeladen_von      INT REFERENCES users(id) ON DELETE SET NULL,
    letzter_org_switch  TIMESTAMPTZ DEFAULT NOW(),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_organisations_mitglieder_org_user UNIQUE (org_id, user_id)
)
""")
    op.execute("CREATE INDEX idx_organisations_mitglieder_org ON organisations_mitglieder(org_id)")
    op.execute("CREATE INDEX idx_organisations_mitglieder_user ON organisations_mitglieder(user_id)")

    op.execute("""
CREATE TABLE eigentuemer (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    org_id              INT NOT NULL REFERENCES organisationen(id) ON DELETE CASCADE,
    name                VARCHAR(150) NOT NULL,
    kontakt_email       VARCHAR(255),
    kontakt_telefon     VARCHAR(30),
    user_id             INT REFERENCES users(id) ON DELETE SET NULL,
    notizen             VARCHAR(2000),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
)
""")
    op.execute("CREATE INDEX idx_eigentuemer_org ON eigentuemer(org_id)")
    op.execute("CREATE INDEX idx_eigentuemer_user ON eigentuemer(user_id)")

    op.execute("""
CREATE TABLE mitglied_objekt_scope (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    org_id              INT NOT NULL REFERENCES organisationen(id) ON DELETE CASCADE,
    mitglied_id         INT NOT NULL REFERENCES organisations_mitglieder(id) ON DELETE CASCADE,
    objekt_id           INT NOT NULL REFERENCES objekte(id) ON DELETE CASCADE,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_mitglied_objekt_scope UNIQUE (mitglied_id, objekt_id)
)
""")
    op.execute("CREATE INDEX idx_mitglied_objekt_scope_org ON mitglied_objekt_scope(org_id)")
    op.execute("CREATE INDEX idx_mitglied_objekt_scope_mitglied ON mitglied_objekt_scope(mitglied_id)")
    op.execute("CREATE INDEX idx_mitglied_objekt_scope_objekt ON mitglied_objekt_scope(objekt_id)")

    op.execute("""
CREATE TABLE org_features (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    org_id              INT NOT NULL REFERENCES organisationen(id) ON DELETE CASCADE,
    feature             VARCHAR(50) NOT NULL,
    aktiv_ab            TIMESTAMPTZ DEFAULT NOW(),
    aktiv_bis           TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_org_features_org_feature UNIQUE (org_id, feature)
)
""")
    op.execute("CREATE INDEX idx_org_features_org ON org_features(org_id)")

    op.execute("""
CREATE TABLE einladungen (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    art                 VARCHAR(30) NOT NULL
                        CHECK (art IN ('mitglied','eigentuemer','handwerker','partner')),
    org_id              INT NOT NULL REFERENCES organisationen(id) ON DELETE CASCADE,
    ziel_kontakt        VARCHAR(255) NOT NULL,
    rolle_oder_scope    VARCHAR(50),
    token_hash          VARCHAR(255) NOT NULL UNIQUE,
    gueltig_bis         TIMESTAMPTZ NOT NULL,
    angenommen_am       TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
)
""")
    op.execute("CREATE INDEX idx_einladungen_org ON einladungen(org_id)")

    op.execute("""
CREATE TABLE loeschregeln (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    org_id              INT REFERENCES organisationen(id) ON DELETE CASCADE,
    klasse              VARCHAR(20) NOT NULL,
    datenart            VARCHAR(100) NOT NULL,
    frist_monate        INT NOT NULL,
    startpunkt          VARCHAR(200) NOT NULL,
    rechtsgrundlage     VARCHAR(255) NOT NULL,
    mindestfrist_monate INT NOT NULL,
    vom_vermieter_aenderbar BOOLEAN NOT NULL DEFAULT TRUE,
    version             INT NOT NULL DEFAULT 1,
    gueltig_ab          TIMESTAMPTZ DEFAULT NOW(),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_loeschregeln_org_klasse_version UNIQUE (org_id, klasse, version)
)
""")
    op.execute("CREATE INDEX idx_loeschregeln_org ON loeschregeln(org_id)")
    op.execute("CREATE INDEX idx_loeschregeln_klasse ON loeschregeln(klasse)")

    op.execute("""
CREATE TABLE loeschprotokoll (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    org_id              INT REFERENCES organisationen(id) ON DELETE SET NULL,
    tabelle             VARCHAR(50) NOT NULL,
    datensatz_id        INT NOT NULL,
    public_id           INT,
    klasse              VARCHAR(20),
    aktion              VARCHAR(20) NOT NULL
                        CHECK (aktion IN ('gesperrt','vorwarnung','geloescht','anonymisiert')),
    zeitpunkt           TIMESTAMPTZ DEFAULT NOW(),
    ausloeser           VARCHAR(50) NOT NULL,
    grund               TEXT,
    details             TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
)
""")
    op.execute("CREATE INDEX idx_loeschprotokoll_lookup ON loeschprotokoll(tabelle, datensatz_id)")
    op.execute("CREATE INDEX idx_loeschprotokoll_org ON loeschprotokoll(org_id)")

    # ============================================================
    # 3. org_id auf Fachtabellen (nullable zuerst)
    # ============================================================
    tables_with_vermieter = [
        "objekte", "einheiten", "einheit_ausstattung", "mieter", "mieter_historie",
        "mietvertraege", "mietvertrag_aenderungen", "bewerbungen",
        "kosten", "kostenkategorien", "abrechnungen", "abrechnung_positionen",
        "mietzahlungen", "dokumente", "dokument_freigaben",
        "tickets", "ticket_kommentare", "ticket_sla", "ticket_trigger",
        "zaehler", "zaehlerablesungen", "bankverbindungen",
        "handwerker", "fristen", "notifications", "events",
        "plan_usage", "subscriptions",
    ]
    for table in tables_with_vermieter:
        op.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS org_id INT REFERENCES organisationen(id) ON DELETE CASCADE")
        op.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_org ON {table}(org_id)")

    # ============================================================
    # 4. Backfill: pro Vermieter eine Organisation anlegen
    # ============================================================
    op.execute("""
INSERT INTO organisationen (name, typ, status, plan)
SELECT DISTINCT u.full_name || ' (Import)', 'selbstverwalter', 'aktiv', 'basis'
FROM users u
WHERE u.role = 'vermieter'
  AND u.deleted_at IS NULL
  AND NOT EXISTS (
      SELECT 1 FROM organisations_mitglieder om
      JOIN users u2 ON om.user_id = u2.id
      WHERE u2.role = 'vermieter' AND u2.id = u.id
  )
""")

    op.execute("""
INSERT INTO organisations_mitglieder (org_id, user_id, rolle, aktiv)
SELECT o.id, u.id, 'org_admin', TRUE
FROM users u
JOIN organisationen o ON o.name = u.full_name || ' (Import)'
WHERE u.role = 'vermieter'
  AND u.deleted_at IS NULL
""")

    backfill_configs = [
        ("objekte", "vermieter_id"),
        ("einheiten", "vermieter_id"),
        ("einheit_ausstattung", "vermieter_id"),
        ("mieter", "vermieter_id"),
        ("mieter_historie", "vermieter_id"),
        ("mietvertraege", "vermieter_id"),
        ("mietvertrag_aenderungen", "vermieter_id"),
        ("bewerbungen", "vermieter_id"),
        ("kosten", "vermieter_id"),
        ("kostenkategorien", "vermieter_id"),
        ("abrechnungen", "vermieter_id"),
        ("abrechnung_positionen", "vermieter_id"),
        ("mietzahlungen", "vermieter_id"),
        ("dokumente", "vermieter_id"),
        ("dokument_freigaben", "vermieter_id"),
        ("tickets", "vermieter_id"),
        ("ticket_kommentare", "vermieter_id"),
        ("ticket_sla", "vermieter_id"),
        ("ticket_trigger", "vermieter_id"),
        ("zaehler", "vermieter_id"),
        ("zaehlerablesungen", "vermieter_id"),
        ("bankverbindungen", "vermieter_id"),
        ("handwerker", "vermieter_id"),
        ("fristen", "vermieter_id"),
        ("notifications", "vermieter_id"),
        ("events", "vermieter_id"),
        ("plan_usage", "user_id"),
        ("subscriptions", "user_id"),
    ]

    for table, fk_col in backfill_configs:
        op.execute(f"""
UPDATE {table} t
SET org_id = o.id
FROM users u
JOIN organisations_mitglieder om ON om.user_id = u.id
JOIN organisationen o ON o.id = om.org_id
WHERE t.{fk_col} = u.id
""")

    # ============================================================
    # 5. RetentionMixin-Felder auf Tabellen mit personenbezogenen Daten
    # ============================================================
    retention_tables = [
        "users", "mieter", "mietvertraege", "bewerbungen", "dokumente",
        "abrechnungen", "kosten", "tickets", "bankverbindungen",
        "zaehler", "zaehlerablesungen", "organisationen",
    ]
    for table in retention_tables:
        op.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS lifecycle_status VARCHAR(20) NOT NULL DEFAULT 'aktiv' CHECK (lifecycle_status IN ('aktiv','gesperrt','geloescht'))")
        op.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS gesperrt_am TIMESTAMPTZ")
        op.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS loeschklasse VARCHAR(20)")
        op.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS loeschen_fruehestens_am TIMESTAMPTZ")
        op.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS legal_hold BOOLEAN NOT NULL DEFAULT FALSE")

    # ============================================================
    # 6. RLS-Policies fuer neue Tabellen
    # ============================================================
    for table in ["organisationen", "organisations_mitglieder", "eigentuemer",
                  "mitglied_objekt_scope", "org_features", "einladungen"]:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(f'DROP POLICY IF EXISTS "{table}_isolation" ON "{table}"')
        if table == "organisationen":
            op.execute(f"""
CREATE POLICY "{table}_isolation" ON "{table}"
    FOR ALL
    TO app_user
    USING (
        id = current_setting('app.org_id', true)::INT
        OR EXISTS (
            SELECT 1 FROM organisations_mitglieder om
            WHERE om.org_id = {table}.id
              AND om.user_id = current_setting('app.user_id', true)::INT
        )
    )
""")
        else:
            op.execute(f"""
CREATE POLICY "{table}_isolation" ON "{table}"
    FOR ALL
    TO app_user
    USING (
        org_id = current_setting('app.org_id', true)::INT
    )
""")

    # Loeschregeln/Loeschprotokoll: RLS aktiv, aber fuer Migration nicht FORCED
    for table in ["loeschregeln", "loeschprotokoll"]:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f'DROP POLICY IF EXISTS "{table}_isolation" ON "{table}"')
        if table == "loeschregeln":
            op.execute(f"""
CREATE POLICY "{table}_isolation" ON "{table}"
    FOR ALL
    TO app_user
    USING (
        org_id = current_setting('app.org_id', true)::INT
        OR org_id IS NULL
    )
""")
        else:
            op.execute(f"""
CREATE POLICY "{table}_isolation" ON "{table}"
    FOR ALL
    TO app_user
    USING (
        org_id = current_setting('app.org_id', true)::INT
    )
""")

    # ============================================================
    # 7. Bestehende RLS-Policies auf org_id erweitern
    # ============================================================
    for table in tables_with_vermieter:
        op.execute(f'DROP POLICY IF EXISTS "{table}_isolation" ON "{table}"')
        if table in ("plan_usage", "subscriptions"):
            op.execute(f"""
CREATE POLICY "{table}_isolation" ON "{table}"
    FOR ALL
    TO app_user
    USING (
        org_id = current_setting('app.org_id', true)::INT
        OR user_id = current_setting('app.user_id', true)::INT
    )
""")
        else:
            op.execute(f"""
CREATE POLICY "{table}_isolation" ON "{table}"
    FOR ALL
    TO app_user
    USING (
        org_id = current_setting('app.org_id', true)::INT
        OR vermieter_id = current_setting('app.user_id', true)::INT
    )
""")

    # ============================================================
    # 8. Default-Löschregeln anlegen
    # ============================================================
    op.execute("""
INSERT INTO loeschregeln (klasse, datenart, frist_monate, startpunkt, rechtsgrundlage, mindestfrist_monate)
VALUES
('K1','Mietinteressenten und Bewerber, kein Vertrag',3,'Absage oder Vergabe der Wohnung','DSGVO Art. 5 und 6',3),
('K2','Selbstauskunft und Bonitaetsdaten des Mieters',24,'Mietvertragsschluss','Datenminimierung',24),
('K3','Mietvertrag und Mieterstammdaten',36,'Ende des Jahres, in dem die Forderungen faellig wurden','§§ 195, 199 BGB',36),
('K4','Nebenkostenabrechnung und Belege gegenueber dem Mieter',36,'Ende des Jahres, in dem die Abrechnung zuging','§ 556 Abs. 3 BGB, §§ 195, 199 BGB',36),
('K5','Kaution und Kautionsabrechnung',36,'Ende des Jahres der Kautionsabrechnung','§§ 195, 199 BGB',36),
('K6','Buchungsbelege, Rechnungen, Zahlungsnachweise',96,'Ende des Kalenderjahres der Entstehung','§ 147 Abs. 3 AO, § 257 Abs. 4 HGB, § 14b UStG',96),
('K7','Handels- und Geschaeftsbriefe',72,'Ende des Kalenderjahres','§ 147 AO, § 257 HGB',72),
('K8','Anschaffungs- und Herstellungskosten der Immobilie',0,'Verkauf bzw. Ende der Nutzung','steuerliche Nachweise',0),
('K9','Tickets, Handwerkerauftraege, Kommunikation',36,'Ticket geschlossen','§§ 195, 199 BGB',36),
('K10','Zugriffs- und Audit-Protokolle',12,'Erzeugung','Art. 5 Abs. 2 DSGVO, Art. 32',12),
('K11','Eigene Nutzerkonten und Abrechnung',96,'Vertragsende','§ 147 AO',96),
('K12','Datenraum-Pakete und Freigaben',1,'Freigabe','Zweckbindung',1)
""")


def downgrade() -> None:
    # Nur die neuen Tabellen droppen; org_id + Retention-Felder bleiben
    # zunaechst, da ein Downgrade sonst Datenverluste riskiert.
    for table in ["loeschprotokoll", "loeschregeln", "einladungen", "org_features",
                  "mitglied_objekt_scope", "eigentuemer", "organisations_mitglieder",
                  "organisationen"]:
        op.execute(f'DROP POLICY IF EXISTS "{table}_isolation" ON "{table}"')
        op.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
    op.execute("DROP SEQUENCE IF EXISTS organisationen_public_id_seq")

    tables_with_vermieter = [
        "objekte", "einheiten", "einheit_ausstattung", "mieter", "mieter_historie",
        "mietvertraege", "mietvertrag_aenderungen", "bewerbungen",
        "kosten", "kostenkategorien", "abrechnungen", "abrechnung_positionen",
        "mietzahlungen", "dokumente", "dokument_freigaben",
        "tickets", "ticket_kommentare", "ticket_sla", "ticket_trigger",
        "zaehler", "zaehlerablesungen", "bankverbindungen",
        "handwerker", "fristen", "notifications", "events",
        "plan_usage", "subscriptions",
    ]
    for table in tables_with_vermieter:
        op.execute(f'DROP POLICY IF EXISTS "{table}_isolation" ON "{table}"')
        op.execute(f"""
CREATE POLICY "{table}_isolation" ON "{table}"
    FOR ALL
    TO app_user
    USING (
        vermieter_id = current_setting('app.user_id', true)::INT
    )
""")
