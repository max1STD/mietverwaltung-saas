"""mietzahlungen updated_at deleted_at

Revision ID: e5b1c2d3a4f6
Revises: d2c4a7e89b1f
Create Date: 2026-11-18 14:00:00.000000+00:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e5b1c2d3a4f6"
down_revision = "d2c4a7e89b1f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "mietzahlungen",
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "mietzahlungen",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("mietzahlungen", "deleted_at")
    op.drop_column("mietzahlungen", "updated_at")
