"""Dokumente-Tabelle und Paperless-User-Spalten für DMS-Integration."""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = '0006_dokumente'
down_revision = '0005_mieter_addresses_guarantors'
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
    """Add dokumente table and paperless columns to users."""
    # ── Paperless-Spalten am Vermieter (User) ──
    if not _column_exists('users', 'paperless_user_id'):
        op.add_column(
            'users',
            sa.Column('paperless_user_id', sa.Integer(), nullable=True),
        )
    if not _column_exists('users', 'paperless_token_enc'):
        op.add_column(
            'users',
            sa.Column('paperless_token_enc', sa.dialects.postgresql.BYTEA(), nullable=True),
        )

    # ── Dokumente-Tabelle ──
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
    """Remove dokumente table and paperless columns."""
    if _table_exists('dokumente'):
        op.drop_table('dokumente')

    if _column_exists('users', 'paperless_user_id'):
        op.drop_column('users', 'paperless_user_id')
    if _column_exists('users', 'paperless_token_enc'):
        op.drop_column('users', 'paperless_token_enc')
