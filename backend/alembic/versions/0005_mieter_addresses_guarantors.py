"""Mieter addresses, guarantors and separate first/last name support."""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = '0005_mieter_addresses_guarantors'
down_revision = '0004_public_ids'
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


def _table_exists(table: str) -> bool:
    """Check whether a table exists in the current database."""
    conn = op.get_bind()
    result = conn.execute(
        sa.text("""
            SELECT 1 FROM information_schema.tables
            WHERE table_name = :table
        """),
        {"table": table},
    )
    return result.scalar() is not None


def upgrade() -> None:
    """Add address table, guarantor table and optional separate name fields."""
    # ── Adress-Tabelle ──
    if not _table_exists('adressen'):
        op.create_table(
            'adressen',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('mieter_id', sa.Integer(), sa.ForeignKey('mieter.id', ondelete='CASCADE'), nullable=False),
            sa.Column('typ', sa.String(20), nullable=False),  # postal | residential | rental_object | guarantor
            sa.Column('strasse', sa.String(255), nullable=False),
            sa.Column('hausnummer', sa.String(20), nullable=True),
            sa.Column('plz', sa.String(10), nullable=False),
            sa.Column('ort', sa.String(100), nullable=False),
            sa.Column('land', sa.String(2), nullable=False, server_default='DE'),
            sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        )

    # ── Bürgschaften-Tabelle ──
    if not _table_exists('buergschaften'):
        op.create_table(
            'buergschaften',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('mieter_id', sa.Integer(), sa.ForeignKey('mieter.id', ondelete='CASCADE'), nullable=False),
            sa.Column('vermieter_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('buerge_first_name', sa.String(50), nullable=False),
            sa.Column('buerge_last_name', sa.String(50), nullable=False),
            sa.Column('buerge_geburtsdatum', sa.Date(), nullable=True),
            sa.Column('buerge_adresse_id', sa.Integer(), sa.ForeignKey('adressen.id', ondelete='SET NULL'), nullable=True),
            sa.Column('buerge_phone', sa.String(30), nullable=True),
            sa.Column('buerge_email', sa.String(255), nullable=True),
            sa.Column('hoechstbetrag', sa.Numeric(12, 2), nullable=True),
            sa.Column('gueltig_bis', sa.Date(), nullable=True),
            sa.Column('status', sa.String(20), nullable=False, server_default='aktiv'),
            sa.Column('notizen', sa.String(2000), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        )

    # ── Mieter: index für Adress-Lookups ──
    op.create_index('idx_adressen_mieter', 'adressen', ['mieter_id'])
    op.create_index('idx_buergschaften_mieter', 'buergschaften', ['mieter_id'])


def downgrade() -> None:
    """Remove address/guarantor tables."""
    if _table_exists('buergschaften'):
        op.drop_table('buergschaften')
    if _table_exists('adressen'):
        op.drop_table('adressen')
