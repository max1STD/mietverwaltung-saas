"""Phase 1: Auth-Spalten zu users hinzufügen und RLS für App-User erzwingen.

Fügt fehlende Spalten hinzu, die im Build-Plan v3 für Phase 1 vorgesehen,
aber noch nicht in der initialen v4.1-Migration enthalten waren:
  - phone
  - is_active
  - email_verified
"""

from alembic import op

# Revision identifiers
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS phone VARCHAR(30),
        ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE,
        ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE
    """)

    # Bestehende Zeilen erhalten konsistente Defaults.
    op.execute("""
        UPDATE users
        SET is_active = TRUE,
            email_verified = FALSE
        WHERE is_active IS NULL
    """)

    # Nicht-NULL-Constraint, sobald alle Zeilen gefüllt sind.
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN is_active SET NOT NULL,
        ALTER COLUMN is_active SET DEFAULT TRUE,
        ALTER COLUMN email_verified SET NOT NULL,
        ALTER COLUMN email_verified SET DEFAULT FALSE
    """)

    # FORCE ROW LEVEL SECURITY: App-User (Table-Owner) muss RLS ebenfalls befolgen.
    op.execute("ALTER TABLE users FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE user_sessions FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE einwilligungen FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE audit_logs FORCE ROW LEVEL SECURITY")


def downgrade() -> None:
    op.execute("""
        ALTER TABLE users
        DROP COLUMN IF EXISTS phone,
        DROP COLUMN IF EXISTS is_active,
        DROP COLUMN IF EXISTS email_verified
    """)

    op.execute("""
        ALTER TABLE users NO FORCE ROW LEVEL SECURITY;
        ALTER TABLE user_sessions NO FORCE ROW LEVEL SECURITY;
        ALTER TABLE einwilligungen NO FORCE ROW LEVEL SECURITY;
        ALTER TABLE audit_logs NO FORCE ROW LEVEL SECURITY
    """)
