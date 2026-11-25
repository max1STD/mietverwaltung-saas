"""Admin-Konzept A1-A3: Richtlinien-Erweiterungen, Org-Rollen, Betroffenenanfragen.

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-11-25 14:00:00.000000+00:00
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Erweiterte OrgRichtlinien (A1/A3)
    op.execute("ALTER TABLE org_richtlinien ADD COLUMN IF NOT EXISTS sso_erlaubt BOOLEAN NOT NULL DEFAULT FALSE")
    op.execute("ALTER TABLE org_richtlinien ADD COLUMN IF NOT EXISTS sso_idp_metadata_url VARCHAR(500)")
    op.execute("ALTER TABLE org_richtlinien ADD COLUMN IF NOT EXISTS zwei_fa_erforderlich BOOLEAN NOT NULL DEFAULT TRUE")
    op.execute("ALTER TABLE org_richtlinien ADD COLUMN IF NOT EXISTS erweiterte_berichte BOOLEAN NOT NULL DEFAULT FALSE")
    op.execute("ALTER TABLE org_richtlinien ADD COLUMN IF NOT EXISTS compliance_center_aktiv BOOLEAN NOT NULL DEFAULT FALSE")

    # Benutzerdefinierte Org-Rollen (A2)
    op.execute("""
CREATE TABLE IF NOT EXISTS org_rollen (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    org_id              INT NOT NULL REFERENCES organisationen(id) ON DELETE CASCADE,
    name                VARCHAR(50) NOT NULL,
    berechtigungen      VARCHAR(2000),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
)
""")
    op.execute("CREATE INDEX IF NOT EXISTS idx_org_rollen_org ON org_rollen(org_id)")

    # Vertretungen: Objekt-Scope ergänzen (A1)
    op.execute("ALTER TABLE vertretungen ADD COLUMN IF NOT EXISTS objekt_ids VARCHAR(500)")

    # Sicherheitsereignisse erweitern (A1)
    op.execute("ALTER TABLE sicherheits_ereignisse ADD COLUMN IF NOT EXISTS admin_id INT REFERENCES plattform_admins(id) ON DELETE SET NULL")
    op.execute("ALTER TABLE sicherheits_ereignisse ADD COLUMN IF NOT EXISTS ernst VARCHAR(20) DEFAULT 'mittel'")
    op.execute("ALTER TABLE sicherheits_ereignisse ADD COLUMN IF NOT EXISTS gelesen_am TIMESTAMPTZ")
    op.execute("CREATE INDEX IF NOT EXISTS idx_sicherheits_ereignisse_admin ON sicherheits_ereignisse(admin_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_sicherheits_ereignisse_ernst ON sicherheits_ereignisse(ernst)")

    # Betroffenenanfragen (A1 Datenschutz-Center / A2 Compliance)
    op.execute("""
CREATE TABLE IF NOT EXISTS betroffenen_anfragen (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    org_id              INT NOT NULL REFERENCES organisationen(id) ON DELETE CASCADE,
    art                 VARCHAR(30) NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'offen'
                        CHECK (status IN ('offen','in_bearbeitung','erledigt','abgelehnt')),
    frist_bis           TIMESTAMPTZ NOT NULL,
    beschreibung        VARCHAR(2000),
    antwort             VARCHAR(4000),
    bearbeitet_von_id   INT REFERENCES users(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
)
""")
    op.execute("CREATE INDEX IF NOT EXISTS idx_betroffenen_anfragen_org ON betroffenen_anfragen(org_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_betroffenen_anfragen_frist ON betroffenen_anfragen(frist_bis)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_betroffenen_anfragen_status ON betroffenen_anfragen(status)")

    # RLS auf neuen Tabellen
    op.execute("ALTER TABLE org_rollen ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE betroffenen_anfragen ENABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS org_rollen_org_isolation ON org_rollen")
    op.execute("DROP POLICY IF EXISTS betroffenen_anfragen_org_isolation ON betroffenen_anfragen")
    op.execute("""
CREATE POLICY org_rollen_org_isolation ON org_rollen
FOR ALL TO app_user
USING (org_id = current_setting('app.org_id', TRUE)::int)
WITH CHECK (org_id = current_setting('app.org_id', TRUE)::int)
""")
    op.execute("""
CREATE POLICY betroffenen_anfragen_org_isolation ON betroffenen_anfragen
FOR ALL TO app_user
USING (org_id = current_setting('app.org_id', TRUE)::int)
WITH CHECK (org_id = current_setting('app.org_id', TRUE)::int)
""")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS betroffenen_anfragen CASCADE")
    op.execute("DROP TABLE IF EXISTS org_rollen CASCADE")
    op.execute("ALTER TABLE org_richtlinien DROP COLUMN IF EXISTS sso_erlaubt")
    op.execute("ALTER TABLE org_richtlinien DROP COLUMN IF EXISTS sso_idp_metadata_url")
    op.execute("ALTER TABLE org_richtlinien DROP COLUMN IF EXISTS zwei_fa_erforderlich")
    op.execute("ALTER TABLE org_richtlinien DROP COLUMN IF EXISTS erweiterte_berichte")
    op.execute("ALTER TABLE org_richtlinien DROP COLUMN IF EXISTS compliance_center_aktiv")
    op.execute("ALTER TABLE vertretungen DROP COLUMN IF EXISTS objekt_ids")
    op.execute("ALTER TABLE sicherheits_ereignisse DROP COLUMN IF EXISTS admin_id")
    op.execute("ALTER TABLE sicherheits_ereignisse DROP COLUMN IF EXISTS ernst")
    op.execute("ALTER TABLE sicherheits_ereignisse DROP COLUMN IF EXISTS gelesen_am")
