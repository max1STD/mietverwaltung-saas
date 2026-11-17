"""bankverbindungen_updated_at

Revision ID: b30dda0e71ec
Revises: f715d10be63c
Create Date: 2026-11-17 17:41:22.241092

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b30dda0e71ec'
down_revision = 'f715d10be63c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'bankverbindungen',
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('bankverbindungen', 'updated_at')
