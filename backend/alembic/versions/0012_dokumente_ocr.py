"""Migration: OCR-Felder fuer Dokumente.

Ermoeglicht Speicherung von OCR-Text, Status und Confidence fuer hochgeladene
Dokumente. OCR laeuft lokal ueber Tesseract + PyMuPDF (Schicht 1).
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = '0012_dokumente_ocr'
down_revision = '0011_objekt_stammdaten'
branch_labels = None
depends_on = None


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
    new_columns = [
        ("ocr_status", sa.String(20), True),
        ("ocr_text", sa.Text(), True),
        ("ocr_confidence", sa.DECIMAL(5, 2), True),
        ("ocr_engine", sa.String(50), True),
        ("ocr_finished_at", sa.DateTime(timezone=True), True),
    ]

    for name, col_type, nullable in new_columns:
        if not _column_exists("dokumente", name):
            op.add_column("dokumente", sa.Column(name, col_type, nullable=nullable))


def downgrade() -> None:
    for name in ["ocr_status", "ocr_text", "ocr_confidence", "ocr_engine", "ocr_finished_at"]:
        if _column_exists("dokumente", name):
            op.drop_column("dokumente", name)
