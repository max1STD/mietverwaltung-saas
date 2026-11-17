"""Migration: Erweiterte Objekt-Stammdaten.

Fuegt zusaetzliche Felder fuer Flaechen, Energie, Heizung, Bau,
Denkmalschutz und Zustand zur objekte-Tabelle hinzu.
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = '0011_objekt_stammdaten'
down_revision = '0010_einheit_stammdaten'
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
        # Flaechen
        ("grundstuecksflaeche_qm", sa.DECIMAL(10, 2), True),
        ("wohnflaeche_gesamt_qm", sa.DECIMAL(10, 2), True),
        ("nutzflaeche_gesamt_qm", sa.DECIMAL(10, 2), True),
        ("vermietbare_flaeche_qm", sa.DECIMAL(10, 2), True),
        # Verwaltung
        ("anzahl_einheiten", sa.Integer(), True),
        ("baujahr_objekt", sa.Integer(), True),
        ("bauweise", sa.String(50), True),
        ("zustand", sa.String(50), True),
        ("denkmalschutz", sa.Boolean(), True),
        ("denkmalschutz_bis", sa.Date(), True),
        # Energie
        ("energieausweis_art", sa.String(50), True),
        ("energieausweis_gueltig_bis", sa.Date(), True),
        ("energieverbrauch_kennwert", sa.DECIMAL(6, 2), True),
        ("energieverbrauch_klasse", sa.String(10), True),
        ("heizungsart", sa.String(50), True),
        ("warmwasserbereitung", sa.String(50), True),
        ("solaranlage", sa.Boolean(), True),
        # Adresse / Lage
        ("land", sa.String(2), True),
        ("adresszusatz", sa.String(100), True),
        ("lagebeschreibung", sa.Text(), True),
        # Finanzen
        ("kaufpreis_pro_qm", sa.DECIMAL(10, 2), True),
        ("gesamtmiete_ist", sa.DECIMAL(10, 2), True),
        ("gesamtmiete_soll", sa.DECIMAL(10, 2), True),
        # Sonstiges
        ("barrierefrei", sa.Boolean(), True),
        ("aufzug", sa.Boolean(), True),
        ("gartennutzung", sa.Boolean(), True),
        ("anmerkungen", sa.Text(), True),
    ]

    for name, col_type, nullable in new_columns:
        if not _column_exists("objekte", name):
            op.add_column("objekte", sa.Column(name, col_type, nullable=nullable))


new_column_names = [
    "grundstuecksflaeche_qm",
    "wohnflaeche_gesamt_qm",
    "nutzflaeche_gesamt_qm",
    "vermietbare_flaeche_qm",
    "anzahl_einheiten",
    "baujahr_objekt",
    "bauweise",
    "zustand",
    "denkmalschutz",
    "denkmalschutz_bis",
    "energieausweis_art",
    "energieausweis_gueltig_bis",
    "energieverbrauch_kennwert",
    "energieverbrauch_klasse",
    "heizungsart",
    "warmwasserbereitung",
    "solaranlage",
    "land",
    "adresszusatz",
    "lagebeschreibung",
    "kaufpreis_pro_qm",
    "gesamtmiete_ist",
    "gesamtmiete_soll",
    "barrierefrei",
    "aufzug",
    "gartennutzung",
    "anmerkungen",
]


def downgrade() -> None:
    for name in new_column_names:
        if _column_exists("objekte", name):
            op.drop_column("objekte", name)
