"""Migration: Öffentliche IDs fuer Mieter und Mietvertraege.

Fuegt public_id-Spalten mit PostgreSQL-Sequenzen hinzu und befuellt
bestehende Datensaetze. URLs/Responses koennen danach public_id nutzen.
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = '0009_public_ids_mieter_mv'
down_revision = '0008_dokumente_neue_struktur'
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


def upgrade() -> None:
    conn = op.get_bind()

    # --- Mieter ---
    if not _sequence_exists('mieter_public_id_seq'):
        op.execute(sa.text("CREATE SEQUENCE mieter_public_id_seq START 1001"))

    if not _column_exists('mieter', 'public_id'):
        op.add_column(
            'mieter',
            sa.Column(
                'public_id',
                sa.BigInteger,
                nullable=True,
                server_default=sa.text("nextval('mieter_public_id_seq')"),
            ),
        )
        # Backfill bestehende Zeilen
        op.execute(sa.text("""
            UPDATE mieter
            SET public_id = nextval('mieter_public_id_seq')
            WHERE public_id IS NULL
        """))
        op.alter_column('mieter', 'public_id', nullable=False)
        op.create_unique_constraint('uq_mieter_public_id', 'mieter', ['public_id'])

    # --- Mietvertraege ---
    if not _sequence_exists('mietvertraege_public_id_seq'):
        op.execute(sa.text("CREATE SEQUENCE mietvertraege_public_id_seq START 1001"))

    if not _column_exists('mietvertraege', 'public_id'):
        op.add_column(
            'mietvertraege',
            sa.Column(
                'public_id',
                sa.BigInteger,
                nullable=True,
                server_default=sa.text("nextval('mietvertraege_public_id_seq')"),
            ),
        )
        op.execute(sa.text("""
            UPDATE mietvertraege
            SET public_id = nextval('mietvertraege_public_id_seq')
            WHERE public_id IS NULL
        """))
        op.alter_column('mietvertraege', 'public_id', nullable=False)
        op.create_unique_constraint('uq_mietvertraege_public_id', 'mietvertraege', ['public_id'])


def downgrade() -> None:
    if _column_exists('mietvertraege', 'public_id'):
        op.drop_constraint('uq_mietvertraege_public_id', 'mietvertraege', type_='unique')
        op.drop_column('mietvertraege', 'public_id')
    if _sequence_exists('mietvertraege_public_id_seq'):
        op.execute(sa.text("DROP SEQUENCE mietvertraege_public_id_seq"))

    if _column_exists('mieter', 'public_id'):
        op.drop_constraint('uq_mieter_public_id', 'mieter', type_='unique')
        op.drop_column('mieter', 'public_id')
    if _sequence_exists('mieter_public_id_seq'):
        op.execute(sa.text("DROP SEQUENCE mieter_public_id_seq"))
