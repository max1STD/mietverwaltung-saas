"""Migration: Alte dokumente-Tabelle auf neue DMS-Struktur umbauen.

Die alte Tabelle hatte feste Fremdschlüssel zu objekte/einheiten/mieter.
Die neue Tabelle verwendet generische entity_type/entity_id, damit auch
Mietverträge und Tickets Dokumente haben können.
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = '0008_dokumente_neue_struktur'
down_revision = '0007_ticket_objekt_id'
branch_labels = None
depends_on = None


def _table_exists(table: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(
        sa.text("""
            SELECT 1 FROM information_schema.tables
            WHERE table_name = :table AND table_schema = 'public'
        """),
        {"table": table},
    )
    return result.scalar() is not None


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


def upgrade() -> None:
    # Altes Fremdschlüssel-Constraint zu dokument_freigaben entfernen, falls vorhanden.
    conn = op.get_bind()
    fk_result = conn.execute(
        sa.text("""
            SELECT constraint_name FROM information_schema.table_constraints
            WHERE constraint_type = 'FOREIGN KEY'
              AND table_name = 'dokument_freigaben'
              AND constraint_name LIKE '%%dokument%%'
        """)
    )
    for row in fk_result.fetchall():
        op.drop_constraint(row[0], 'dokument_freigaben', type_='foreignkey')

    # Wenn alte Tabelle mit altem Schema existiert, löschen und neu anlegen.
    if _table_exists('dokumente') and _column_exists('dokumente', 'objekt_id'):
        op.drop_table('dokumente')

    if not _table_exists('dokumente'):
        op.create_table(
            'dokumente',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('vermieter_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('entity_type', sa.String(20), nullable=False),
            sa.Column('entity_id', sa.Integer(), nullable=False),
            sa.Column('paperless_document_id', sa.Integer(), nullable=True),
            sa.Column('paperless_user_id', sa.Integer(), nullable=True),
            sa.Column('status', sa.String(20), nullable=False, server_default='bereit'),
            sa.Column('typ', sa.String(30), nullable=False, server_default='sonstiges'),
            sa.Column('titel', sa.String(255), nullable=False),
            sa.Column('jahr', sa.Integer(), nullable=True),
            sa.Column('file_name', sa.String(255), nullable=False),
            sa.Column('file_size', sa.Integer(), nullable=False),
            sa.Column('content_type', sa.String(100), nullable=False),
            sa.Column('storage_path', sa.String(500), nullable=True),
            sa.Column('upload_error', sa.String(1000), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
            sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        )
        op.create_index('idx_dokumente_vermieter', 'dokumente', ['vermieter_id'])
        op.create_index('idx_dokumente_entity', 'dokumente', ['entity_type', 'entity_id'])
        op.create_index('idx_dokumente_paperless_id', 'dokumente', ['paperless_document_id'])


def downgrade() -> None:
    if _table_exists('dokumente'):
        op.drop_table('dokumente')
