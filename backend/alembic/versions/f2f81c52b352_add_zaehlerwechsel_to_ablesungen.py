"""add_zaehlerwechsel_to_ablesungen

Revision ID: f2f81c52b352
Revises: e5b1c2d3a4f6
Create Date: 2026-11-18 20:24:29.793672

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2f81c52b352'
down_revision = 'e5b1c2d3a4f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('zaehlerablesungen', sa.Column('zaehlerwechsel', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.alter_column('zaehlerablesungen', 'zaehlerwechsel', server_default=None)


def downgrade() -> None:
    op.drop_column('zaehlerablesungen', 'zaehlerwechsel')
