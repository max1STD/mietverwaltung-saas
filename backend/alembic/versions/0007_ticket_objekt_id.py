"""Objekt-Verknüpfung für Tickets.

Revision ID: 0007
Revises: 0006_dokumente
Create Date: 2026-11-16 13:10:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = '0007_ticket_objekt_id'
down_revision = '0006_dokumente'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Fügt der tickets-Tabelle eine objekt_id-Spalte hinzu."""
    conn = op.get_bind()
    result = conn.execute(
        sa.text("""
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'tickets' AND column_name = 'objekt_id'
        """)
    )
    if result.scalar() is None:
        op.add_column(
            'tickets',
            sa.Column('objekt_id', sa.Integer(), sa.ForeignKey('objekte.id', ondelete='SET NULL'), nullable=True),
        )


def downgrade() -> None:
    """Entfernt die objekt_id-Spalte wieder."""
    conn = op.get_bind()
    result = conn.execute(
        sa.text("""
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'tickets' AND column_name = 'objekt_id'
        """)
    )
    if result.scalar() is not None:
        op.drop_column('tickets', 'objekt_id')
