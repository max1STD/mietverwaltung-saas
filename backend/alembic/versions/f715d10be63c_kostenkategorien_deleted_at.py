"""kostenkategorien_deleted_at

Revision ID: f715d10be63c
Revises: 0012_dokumente_ocr
Create Date: 2026-11-17 17:21:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f715d10be63c'
down_revision = '0012_dokumente_ocr'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'kostenkategorien',
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('kostenkategorien', 'deleted_at')
