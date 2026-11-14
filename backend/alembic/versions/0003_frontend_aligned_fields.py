"""Add frontend-aligned fields to objekte and einheiten (idempotent)."""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = '0003_frontend_aligned_fields'
down_revision = '0002'
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


def upgrade() -> None:
    """Align objekte/einheiten columns with frontend form fields."""
    # ── objekte ──
    if not _column_exists('objekte', 'plz'):
        op.add_column('objekte', sa.Column('plz', sa.String(10), nullable=True))
    if not _column_exists('objekte', 'ort'):
        op.add_column('objekte', sa.Column('ort', sa.String(100), nullable=True))
    if not _column_exists('objekte', 'notizen'):
        op.add_column('objekte', sa.Column('notizen', sa.String(2000), nullable=True))

    op.alter_column('objekte', 'address', nullable=True)
    op.alter_column('objekte', 'typ', nullable=True)

    # ── einheiten ──
    # Rename old columns to frontend field names
    if _column_exists('einheiten', 'size_qm') and not _column_exists('einheiten', 'wohnflaeche_qm'):
        op.alter_column('einheiten', 'size_qm', new_column_name='wohnflaeche_qm')
    if _column_exists('einheiten', 'rent_cold') and not _column_exists('einheiten', 'kaltmiete'):
        op.alter_column('einheiten', 'rent_cold', new_column_name='kaltmiete')

    # 'rooms' becomes 'etage'. To keep the model flexible we copy data,
    # then add a new nullable 'rooms' column for future use.
    if _column_exists('einheiten', 'rooms') and not _column_exists('einheiten', 'etage'):
        op.add_column('einheiten', sa.Column('etage', sa.Integer(), nullable=True))
        op.execute("UPDATE einheiten SET etage = rooms")
        op.drop_column('einheiten', 'rooms')

    if not _column_exists('einheiten', 'rooms'):
        op.add_column('einheiten', sa.Column('rooms', sa.Integer(), nullable=True))

    if not _column_exists('einheiten', 'nebenkosten_vorschuss'):
        op.add_column('einheiten', sa.Column('nebenkosten_vorschuss', sa.DECIMAL(10, 2), nullable=True))

    op.alter_column('einheiten', 'wohnflaeche_qm', nullable=False)
    op.alter_column('einheiten', 'kaltmiete', nullable=False)


def downgrade() -> None:
    """Revert to old column names."""
    op.alter_column('einheiten', 'wohnflaeche_qm', nullable=True)
    op.alter_column('einheiten', 'kaltmiete', nullable=True)

    if _column_exists('einheiten', 'nebenkosten_vorschuss'):
        op.drop_column('einheiten', 'nebenkosten_vorschuss')

    if _column_exists('einheiten', 'rooms'):
        op.drop_column('einheiten', 'rooms')

    if _column_exists('einheiten', 'etage') and not _column_exists('einheiten', 'rooms'):
        op.add_column('einheiten', sa.Column('rooms', sa.Integer(), nullable=False))
        op.execute("UPDATE einheiten SET rooms = etage WHERE etage IS NOT NULL")
        op.drop_column('einheiten', 'etage')

    if _column_exists('einheiten', 'kaltmiete') and not _column_exists('einheiten', 'rent_cold'):
        op.alter_column('einheiten', 'kaltmiete', new_column_name='rent_cold')
    if _column_exists('einheiten', 'wohnflaeche_qm') and not _column_exists('einheiten', 'size_qm'):
        op.alter_column('einheiten', 'wohnflaeche_qm', new_column_name='size_qm')

    op.alter_column('objekte', 'address', nullable=False)
    op.alter_column('objekte', 'typ', nullable=False)

    if _column_exists('objekte', 'notizen'):
        op.drop_column('objekte', 'notizen')
    if _column_exists('objekte', 'ort'):
        op.drop_column('objekte', 'ort')
    if _column_exists('objekte', 'plz'):
        op.drop_column('objekte', 'plz')
