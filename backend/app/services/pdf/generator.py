"""PDF-Generierung mit Jinja2 + WeasyPrint.

Baut Briefkopf-Dokumente aus DB-Daten. Zwei Klassen:
- Statische Vorlagen (Wohnungsgeberbestätigung, Übergabeprotokoll, ...)
- KI-generierte Texte (Mahnung, Mieterhöhung, Kündigung, ...)
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS

# Basis-Verzeichnis für Templates
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# Jinja2-Environment mit HTML-Escaping
_jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_template(template_name: str, context: dict[str, Any]) -> str:
    """Rendert ein Jinja2-Template zu HTML."""
    template = _jinja_env.get_template(template_name)
    return template.render(context)


def html_to_pdf(html_content: str) -> bytes:
    """Wandelt HTML in PDF-Bytes um."""
    html = HTML(string=html_content, base_url=str(TEMPLATES_DIR))
    return html.write_pdf()


def generate_pdf_from_template(template_name: str, context: dict[str, Any]) -> bytes:
    """Kombination: Template rendern + PDF erzeugen."""
    html = render_template(template_name, context)
    return html_to_pdf(html)


def build_base_context(
    vermieter: dict[str, Any],
    bankverbindung: dict[str, Any] | None = None,
    datum: date | None = None,
) -> dict[str, Any]:
    """Baut den Standard-Briefkopf-Kontext aus Vermieter-Stammdaten."""
    return {
        "datum": (datum or date.today()).strftime("%d.%m.%Y"),
        "vermieter": vermieter,
        "bankverbindung": bankverbindung or {},
        "logo_url": vermieter.get("logo_path") or None,
    }
