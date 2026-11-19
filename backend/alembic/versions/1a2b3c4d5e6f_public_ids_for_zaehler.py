"""public_ids_for_zaehler

Revision ID: 1a2b3c4d5e6f
Revises: f2f81c52b352
Create Date: 2026-11-19 11:30:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = 'f2f81c52b352'
branch_labels = None
depends_on = None


def _column_exists(table: str, column: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(
        sa.text("""
            SELECT 1 FROM information_schema.columns
            WHERE table_name = :table AND column_name = :column AND table_schema = 'public'
        """),
        {"table": table, "column": column},
    )
    return result.scalar() is not None


def _sequence_exists(name: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(
        sa.text("""
            SELECT 1 FROM information_schema.sequences
            WHERE sequence_name = :name AND sequence_schema = 'public'
        """),
        {"name": name},
    )
    return result.scalar() is not None


def _backfill_public_id(table: str, sequence: str) -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(f"""
            UPDATE {table}
            SET public_id = nextval(:sequence)
            WHERE public_id IS NULL
        """),
        {"sequence": sequence},
    )


def upgrade() -> None:
    """Add public_id column and sequence for zaehler."""
    if not _sequence_exists('zaehler_public_id_seq'):
        op.execute("CREATE SEQUENCE zaehler_public_id_seq START 1001")

    if not _column_exists('zaehler', 'public_id'):
        op.add_column(
            'zaehler',
            sa.Column(
                'public_id',
                sa.BigInteger,
                nullable=True,
                server_default=sa.text("nextval('zaehler_public_id_seq')"),
            ),
        )

    _backfill_public_id('zaehler', 'zaehler_public_id_seq')
    op.alter_column('zaehler', 'public_id', nullable=False)
    op.create_unique_constraint('uq_zaehler_public_id', 'zaehler', ['public_id'])


def downgrade() -> None:
    if _column_exists('zaehler', 'public_id'):
        op.drop_constraint('uq_zaehler_public_id', 'zaehler', type_='unique')
        op.drop_column('zaehler', 'public_id')
    if _sequence_exists('zaehler_public_id_seq'):
        op.execute(sa.text("DROP SEQUENCE zaehler_public_id_seq"))
