"""bankverbindungen bic_enc

Revision ID: d2c4a7e89b1f
Revises: c3a9f8e21b4d
Create Date: 2026-11-18 12:45:00.000000+00:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d2c4a7e89b1f"
down_revision = "c3a9f8e21b4d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "bankverbindungen",
        sa.Column("bic_enc", sa.dialects.postgresql.BYTEA(), nullable=True),
    )
    # Alte Klartext-BIC-Spalte wird nicht mehr beschrieben, aber vorerst
    # nicht gelöscht, damit ein eventueller Rollback ohne Datenverlust möglich ist.


def downgrade() -> None:
    op.drop_column("bankverbindungen", "bic_enc")
