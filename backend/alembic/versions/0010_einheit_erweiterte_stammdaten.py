"""Migration: Erweiterte Wohneinheit-Stammdaten und Ausstattung.

Fuegt zusaetzliche Felder fuer Flaechen, Ausstattung, Zustand,
Heizung, Energie, Sanitaer und Bauweise zur einheiten-Tabelle hinzu.
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = '0010_einheit_stammdaten'
# 0010_einheit_erweiterte_stammdaten ist zu lang fuer alembic_version varchar(32)
down_revision = '0009_public_ids_mieter_mv'
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
        # Zaehler (Anzahl)
        ("schlafzimmer", sa.Integer(), True),
        ("badezimmer", sa.Integer(), True),
        ("wohnzimmer", sa.Integer(), True),
        # Flaechen
        ("nutzflaeche_qm", sa.DECIMAL(8, 2), True),
        ("balkon_flaeche_qm", sa.DECIMAL(6, 2), True),
        ("terrasse_flaeche_qm", sa.DECIMAL(6, 2), True),
        ("garten_flaeche_qm", sa.DECIMAL(8, 2), True),
        ("gewerbeflaeche_qm", sa.DECIMAL(8, 2), True),
        # Ausstattung (Boolean)
        ("balkon", sa.Boolean(), True),
        ("terrasse", sa.Boolean(), True),
        ("garten", sa.Boolean(), True),
        ("garage", sa.Boolean(), True),
        ("stellplatz", sa.Boolean(), True),
        ("keller", sa.Boolean(), True),
        ("aufzug", sa.Boolean(), True),
        ("barrierefrei", sa.Boolean(), True),
        ("moebliert", sa.Boolean(), True),
        # Energie / Bau
        ("baujahr_einheit", sa.Integer(), True),
        ("heizungsart", sa.String(50), True),
        ("warmwasserbereitung", sa.String(50), True),
        ("fenster", sa.String(50), True),
        ("boden", sa.String(50), True),
        ("sanitaer", sa.String(50), True),
        ("kueche", sa.String(50), True),
        ("energieausweis_art", sa.String(50), True),
        ("energieverbrauch_kennwert", sa.DECIMAL(6, 2), True),
        ("energieverbrauch_klasse", sa.String(10), True),
        ("bauweise", sa.String(50), True),
        ("denkmalschutz", sa.Boolean(), True),
        ("denkmalschutz_bis", sa.Date(), True),
        # Verwaltung / Vermietung
        ("renovierungsstatus", sa.String(50), True),
        ("zustand", sa.String(50), True),
        ("bewohnbar_ab", sa.Date(), True),
        ("anmerkungen", sa.Text(), True),
    ]

    for name, col_type, nullable in new_columns:
        if not _column_exists("einheiten", name):
            op.add_column("einheiten", sa.Column(name, col_type, nullable=nullable))


new_column_names = [
    "schlafzimmer",
    "badezimmer",
    "wohnzimmer",
    "nutzflaeche_qm",
    "balkon_flaeche_qm",
    "terrasse_flaeche_qm",
    "garten_flaeche_qm",
    "gewerbeflaeche_qm",
    "balkon",
    "terrasse",
    "garten",
    "garage",
    "stellplatz",
    "keller",
    "aufzug",
    "barrierefrei",
    "moebliert",
    "baujahr_einheit",
    "heizungsart",
    "warmwasserbereitung",
    "fenster",
    "boden",
    "sanitaer",
    "kueche",
    "energieausweis_art",
    "energieverbrauch_kennwert",
    "energieverbrauch_klasse",
    "bauweise",
    "denkmalschutz",
    "denkmalschutz_bis",
    "renovierungsstatus",
    "zustand",
    "bewohnbar_ab",
    "anmerkungen",
]


def downgrade() -> None:
    for name in new_column_names:
        if _column_exists("einheiten", name):
            op.drop_column("einheiten", name)
