"""Admin-Konzept A0: Plattform-Admin, Audit, Support-Freigabe, Org-Richtlinien.

Revision ID: a1b2c3d4e5f6
Revises: 8c632bf83b75
Create Date: 2026-11-25 12:00:00.000000+00:00
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "8c632bf83b75"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
CREATE TABLE plattform_admins (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email               VARCHAR(255) NOT NULL UNIQUE,
    rolle               VARCHAR(30) NOT NULL DEFAULT 'support'
                        CHECK (rolle IN ('owner','support','billing','compliance','ops','partner')),
    aktiv               BOOLEAN NOT NULL DEFAULT TRUE,
    passkey_ref         VARCHAR(255),
    letzte_anmeldung    TIMESTAMPTZ,
    eingeladen_von_id   INT REFERENCES plattform_admins(id) ON DELETE SET NULL,
    eingeladen_am       TIMESTAMPTZ DEFAULT NOW(),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
)
""")
    op.execute("CREATE INDEX idx_plattform_admins_rolle ON plattform_admins(rolle)")
    op.execute("CREATE INDEX idx_plattform_admins_aktiv ON plattform_admins(aktiv)")
    op.execute("CREATE INDEX idx_plattform_admins_eingeladen_von ON plattform_admins(eingeladen_von_id)")

    op.execute("""
CREATE TABLE plattform_audit_log (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    admin_id            INT REFERENCES plattform_admins(id) ON DELETE SET NULL,
    aktion              VARCHAR(100) NOT NULL,
    ziel_typ            VARCHAR(50),
    ziel_id             INT,
    begruendung         VARCHAR(1000),
    ergebnis            VARCHAR(50),
    zeitpunkt           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ip_adresse          VARCHAR(45)
)
""")
    op.execute("CREATE INDEX idx_plattform_audit_log_admin ON plattform_audit_log(admin_id)")
    op.execute("CREATE INDEX idx_plattform_audit_log_zeitpunkt ON plattform_audit_log(zeitpunkt)")
    op.execute("CREATE INDEX idx_plattform_audit_log_ziel ON plattform_audit_log(ziel_typ, ziel_id)")

    op.execute("""
CREATE TABLE support_freigaben (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    org_id              INT NOT NULL REFERENCES organisationen(id) ON DELETE CASCADE,
    ticket_ref          VARCHAR(100),
    grund               VARCHAR(1000) NOT NULL,
    umfang              VARCHAR(500) NOT NULL,
    gueltig_bis         TIMESTAMPTZ NOT NULL,
    widerrufen_am       TIMESTAMPTZ,
    erteilt_von_user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
)
""")
    op.execute("CREATE INDEX idx_support_freigaben_org ON support_freigaben(org_id)")
    op.execute("CREATE INDEX idx_support_freigaben_gueltig ON support_freigaben(gueltig_bis)")

    op.execute("""
CREATE TABLE support_zugriffe (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    freigabe_id         INT NOT NULL REFERENCES support_freigaben(id) ON DELETE CASCADE,
    admin_id            INT REFERENCES plattform_admins(id) ON DELETE SET NULL,
    aktion              VARCHAR(100) NOT NULL,
    ziel                VARCHAR(500),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
)
""")
    op.execute("CREATE INDEX idx_support_zugriffe_freigabe ON support_zugriffe(freigabe_id)")

    op.execute("""
CREATE TABLE freigabe_anfragen (
    id                          INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    org_id                      INT REFERENCES organisationen(id) ON DELETE CASCADE,
    aktion                      VARCHAR(100) NOT NULL,
    angefordert_von_admin_id    INT NOT NULL REFERENCES plattform_admins(id) ON DELETE CASCADE,
    bestaetigt_von_admin_id     INT REFERENCES plattform_admins(id) ON DELETE SET NULL,
    status                      VARCHAR(20) NOT NULL DEFAULT 'ausstehend'
                                CHECK (status IN ('ausstehend','bestaetigt','abgelehnt','abgelaufen')),
    ausfuehren_ab               TIMESTAMPTZ NOT NULL,
    ablauf                      TIMESTAMPTZ NOT NULL,
    created_at                  TIMESTAMPTZ DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ DEFAULT NOW()
)
""")
    op.execute("CREATE INDEX idx_freigabe_anfragen_status ON freigabe_anfragen(status)")
    op.execute("CREATE INDEX idx_freigabe_anfragen_org ON freigabe_anfragen(org_id)")

    op.execute("""
CREATE TABLE org_richtlinien (
    org_id                      INT PRIMARY KEY REFERENCES organisationen(id) ON DELETE CASCADE,
    mfa_pflicht                 BOOLEAN NOT NULL DEFAULT TRUE,
    mfa_pflicht_rollen          VARCHAR(200) DEFAULT 'org_admin,admin,buchhaltung',
    session_dauer_stunden       INT NOT NULL DEFAULT 12,
    inaktivitaet_minuten        INT NOT NULL DEFAULT 60,
    vier_augen_aktionen         VARCHAR(500) DEFAULT '',
    massenexport_benachrichtigt BOOLEAN NOT NULL DEFAULT TRUE,
    ip_freigabe                 VARCHAR(500),
    created_at                  TIMESTAMPTZ DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ DEFAULT NOW()
)
""")

    op.execute("""
CREATE TABLE vertretungen (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    org_id              INT NOT NULL REFERENCES organisationen(id) ON DELETE CASCADE,
    von_mitglied_id     INT NOT NULL REFERENCES organisations_mitglieder(id) ON DELETE CASCADE,
    an_mitglied_id      INT NOT NULL REFERENCES organisations_mitglieder(id) ON DELETE CASCADE,
    rolle               VARCHAR(30),
    von                 TIMESTAMPTZ NOT NULL,
    bis                 TIMESTAMPTZ NOT NULL,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_vertretung_verschieden CHECK (von_mitglied_id != an_mitglied_id)
)
""")
    op.execute("CREATE INDEX idx_vertretungen_org ON vertretungen(org_id)")
    op.execute("CREATE INDEX idx_vertretungen_aktiv ON vertretungen(von, bis)")

    op.execute("""
CREATE TABLE sicherheits_ereignisse (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    org_id              INT REFERENCES organisationen(id) ON DELETE CASCADE,
    user_id             INT REFERENCES users(id) ON DELETE SET NULL,
    art                 VARCHAR(50) NOT NULL,
    details             VARCHAR(1000),
    zeitpunkt           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
)
""")
    op.execute("CREATE INDEX idx_sicherheits_ereignisse_org ON sicherheits_ereignisse(org_id)")
    op.execute("CREATE INDEX idx_sicherheits_ereignisse_zeitpunkt ON sicherheits_ereignisse(zeitpunkt)")

    # RLS fuer neue Admin-Tabellen: app_user darf nichts sehen
    for table in ["plattform_admins", "plattform_audit_log", "support_freigaben",
                  "support_zugriffe", "freigabe_anfragen", "org_richtlinien",
                  "vertretungen", "sicherheits_ereignisse"]:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f'DROP POLICY IF EXISTS "{table}_deny_app_user" ON "{table}"')
        op.execute(f"""
CREATE POLICY "{table}_deny_app_user" ON "{table}"
    FOR ALL
    TO app_user
    USING (FALSE)
""")


def downgrade() -> None:
    for table in ["sicherheits_ereignisse", "vertretungen", "org_richtlinien",
                  "freigabe_anfragen", "support_zugriffe", "support_freigaben",
                  "plattform_audit_log", "plattform_admins"]:
        op.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
