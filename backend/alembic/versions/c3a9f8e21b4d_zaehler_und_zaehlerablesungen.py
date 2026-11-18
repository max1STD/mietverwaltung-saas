"""Zähler und Zählerablesungen.

Revision ID: c3a9f8e21b4d
Revises: b30dda0e71ec
Create Date: 2026-11-18 07:36:00.000000+00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "c3a9f8e21b4d"
down_revision = "b30dda0e71ec"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "zaehler",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "vermieter_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "einheit_id",
            sa.Integer(),
            sa.ForeignKey("einheiten.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("bezeichnung", sa.String(100), nullable=False, default=""),
        sa.Column("zaehlernummer", sa.String(100), nullable=True),
        sa.Column("typ", sa.String(20), nullable=False),
        sa.Column("einheit", sa.String(20), nullable=False, default="kwh"),
        sa.Column("ist_hauptzaehler", sa.Boolean(), nullable=False, default=False),
        sa.Column("ablesedatum", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_zaehler_vermieter_id", "zaehler", ["vermieter_id"])
    op.create_index("ix_zaehler_einheit_id", "zaehler", ["einheit_id"])
    op.create_index("ix_zaehler_typ", "zaehler", ["typ"])

    op.create_table(
        "zaehlerablesungen",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "vermieter_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "zaehler_id",
            sa.Integer(),
            sa.ForeignKey("zaehler.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ablesedatum", sa.Date(), nullable=False),
        sa.Column("zaehlerstand", sa.Numeric(15, 3), nullable=False),
        sa.Column("verbrauch", sa.Numeric(15, 3), nullable=True),
        sa.Column("ableser", sa.String(50), nullable=True),
        sa.Column("notizen", sa.String(500), nullable=True),
        sa.Column("ist_schaetzung", sa.Boolean(), nullable=False, default=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_zaehlerablesungen_vermieter_id", "zaehlerablesungen", ["vermieter_id"])
    op.create_index("ix_zaehlerablesungen_zaehler_id", "zaehlerablesungen", ["zaehler_id"])
    op.create_index("ix_zaehlerablesungen_ablesedatum", "zaehlerablesungen", ["ablesedatum"])


def downgrade() -> None:
    op.drop_index("ix_zaehlerablesungen_ablesedatum", table_name="zaehlerablesungen")
    op.drop_index("ix_zaehlerablesungen_zaehler_id", table_name="zaehlerablesungen")
    op.drop_index("ix_zaehlerablesungen_vermieter_id", table_name="zaehlerablesungen")
    op.drop_table("zaehlerablesungen")

    op.drop_index("ix_zaehler_typ", table_name="zaehler")
    op.drop_index("ix_zaehler_einheit_id", table_name="zaehler")
    op.drop_index("ix_zaehler_vermieter_id", table_name="zaehler")
    op.drop_table("zaehler")
