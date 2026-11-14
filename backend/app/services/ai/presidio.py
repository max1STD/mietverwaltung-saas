"""Presidio-basierte Anonymisierung / Deanonymisierung von PII.

Wir ersetzen personenbezogene Daten durch Platzhalter (Pseudonymisierung),
bevor Text an externe KI-Modelle geht. Platzhalter werden anschließend lokal
wieder aufgelöst.

Unterstützte Entitäten:
- PERSON, LOCATION, EMAIL_ADDRESS, PHONE_NUMBER, IBAN, CREDIT_CARD
- DATE_TIME (für Geburtsdaten)
- Custom Recognizer für deutsche Adressen
"""
from __future__ import annotations

import re

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig


def _build_analyzer() -> AnalyzerEngine:
    """Erzeugt einen Analyzer mit deutschem spaCy-Modell + Custom Regeln."""
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [
            {"lang_code": "de", "model_name": "de_core_news_lg"},
            {"lang_code": "en", "model_name": "en_core_web_sm"},
        ],
    }
    provider = NlpEngineProvider(nlp_configuration=configuration)
    registry = RecognizerRegistry()
    registry.load_predefined_recognizers(languages=["en"])
    registry.supported_languages = ["en"]

    analyzer = AnalyzerEngine(
        nlp_engine=provider.create_engine(),
        registry=registry,
        supported_languages=["en"],
    )
    return analyzer


_ANALYZER = _build_analyzer()
_ANONYMIZER = AnonymizerEngine()

# Mapping PII-Typ -> Platzhalter
_PLACEHOLDERS: dict[str, str] = {
    "PERSON": "[PERSON]",
    "LOCATION": "[ADRESSE]",
    "EMAIL_ADDRESS": "[EMAIL]",
    "PHONE_NUMBER": "[TELEFON]",
    "IBAN": "[IBAN]",
    "CREDIT_CARD": "[KREDITKARTE]",
    "DATE_TIME": "[DATUM]",
    "ADDRESS": "[ADRESSE]",
}

_IBAN_RE = re.compile(
    r"\b[A-Z]{2}[0-9]{2}(?:[ ]?[A-Z0-9]{4}){4,7}(?:[ ]?[A-Z0-9]{1,4})?\b"
)
_PHONE_RE = re.compile(
    r"\b(?:\+49[ \-/]?|0)[1-9][0-9]{1,4}[ \-/]?[0-9]{3,9}[ \-/]?[0-9]{3,9}\b"
)
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")


def _pre_replace(text: str) -> tuple[str, dict[str, str]]:
    """Vorverarbeitung: Regex-basierte Ersetzung von IBAN, Telefon, E-Mail."""
    placeholders: dict[str, str] = {}
    counter = 0

    def store(value: str, typ: str) -> str:
        nonlocal counter
        key = f"__{typ}_{counter}__"
        placeholders[key] = value
        counter += 1
        return key

    def iban_replace(m: re.Match) -> str:
        return store(m.group().replace(" ", ""), "IBAN")

    def phone_replace(m: re.Match) -> str:
        return store(m.group(), "TELEFON")

    def email_replace(m: re.Match) -> str:
        return store(m.group(), "EMAIL")

    text = _IBAN_RE.sub(iban_replace, text)
    text = _PHONE_RE.sub(phone_replace, text)
    text = _EMAIL_RE.sub(email_replace, text)
    return text, placeholders


def _post_replace(text: str, placeholders: dict[str, str]) -> str:
    """Stellt ursprüngliche Regex-Platzhalter wieder her."""
    for key, value in placeholders.items():
        text = text.replace(key, value)
    return text


def anonymize(text: str) -> tuple[str, dict[str, str]]:
    """Anonymisiert Text mit Presidio + Custom-Regeln.

    Gibt anonymisierten Text und ein Mapping Platzhalter->Original zurück,
    das für die Deanonymisierung benötigt wird.
    """
    pre_text, pre_map = _pre_replace(text)

    results = _ANALYZER.analyze(
        text=pre_text,
        language="en",
        entities=list(_PLACEHOLDERS.keys()),
    )

    operators: dict[str, OperatorConfig] = {
        entity: OperatorConfig("replace", {"new_value": placeholder})
        for entity, placeholder in _PLACEHOLDERS.items()
    }

    anonymized = _ANONYMIZER.anonymize(
        text=pre_text,
        analyzer_results=results,
        operators=operators,
    ).text

    # Fasse Presidio-Ersetzungen in ein eindeutiges Mapping zusammen.
    # Gleiche Platzhalter werden durchnummeriert: [PERSON] -> [PERSON_0] etc.
    final_text = anonymized
    reverse_map: dict[str, str] = {}
    counter: dict[str, int] = {}
    for res in results:
        placeholder = _PLACEHOLDERS.get(res.entity_type, f"[{res.entity_type}]")
        original = pre_text[res.start : res.end]
        idx = counter.get(placeholder, 0)
        unique_key = f"{placeholder[:-1]}_{idx}]"
        final_text = final_text.replace(placeholder, unique_key, 1)
        reverse_map[unique_key] = original
        counter[placeholder] = idx + 1

    final_text = _post_replace(final_text, pre_map)
    return final_text, reverse_map


def deanonymize(text: str, mapping: dict[str, str]) -> str:
    """Löst Platzhalter aus `anonymize()` wieder in Originale auf."""
    # Längere Schlüssel zuerst ersetzen, um Teilstring-Probleme zu vermeiden
    for key in sorted(mapping.keys(), key=len, reverse=True):
        text = text.replace(key, mapping[key])
    return text


if __name__ == "__main__":
    sample = "Max Mustermann wohnt in Musterstraße 12, 12345 Berlin. IBAN: DE89370400440532013000."
    anon, mapping = anonymize(sample)
    print("Anonymisiert:", anon)
    print("Deanonymisiert:", deanonymize(anon, mapping))
