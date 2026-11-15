"""Add public_id columns and sequences for objekte and einheiten."""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = '0004_public_ids'
down_revision = '0003_frontend_aligned_fields'
branch_labels = None
depends_on = None


def _column_exists(table: str, column: str) -> bool:
    """Check whether a column exists in the current database."""
    conn = op.get_bind()
    result = conn.execute(
        sa.text("""
            SELECT 1 FROM information_schema.columns
            WHERE table_name = :table AND column_name = :column
        """),
        {"table": table, "column": column},
    )
    return result.scalar() is not None


def _sequence_exists(name: str) -> bool:
    """Check whether a sequence exists in the current database."""
    conn = op.get_bind()
    result = conn.execute(
        sa.text("""
            SELECT 1 FROM pg_sequences WHERE sequencename = :name
        """),
        {"name": name},
    )
    return result.scalar() is not None


def upgrade() -> None:
    """Add public_id columns and sequences."""
    # ── sequences ──
    if not _sequence_exists('objekte_public_id_seq'):
        op.execute("CREATE SEQUENCE objekte_public_id_seq START 1001")
    if not _sequence_exists('einheiten_public_id_seq'):
        op.execute("CREATE SEQUENCE einheiten_public_id_seq START 1001")

    # ── columns ──
    if not _column_exists('objekte', 'public_id'):
        op.add_column(
            'objekte',
            sa.Column('public_id', sa.BigInteger(), nullable=False, server_default=sa.text("nextval('objekte_public_id_seq')"), unique=True),
        )
    else:
        op.alter_column('objekte', 'public_id', nullable=False, server_default=sa.text("nextval('objekte_public_id_seq')"))

    if not _column_exists('einheiten', 'public_id'):
        op.add_column(
            'einheiten',
            sa.Column('public_id', sa.BigInteger(), nullable=False, server_default=sa.text("nextval('einheiten_public_id_seq')"), unique=True),
        )
    else:
        op.alter_column('einheiten', 'public_id', nullable=False, server_default=sa.text("nextval('einheiten_public_id_seq')"))


def downgrade() -> None:
    """Remove public_id columns and sequences."""
    op.drop_column('objekte', 'public_id')
    op.drop_column('einheiten', 'public_id')
    op.execute("DROP SEQUENCE IF EXISTS objekte_public_id_seq")
    op.execute("DROP SEQUENCE IF EXISTS einheiten_public_id_seq")
