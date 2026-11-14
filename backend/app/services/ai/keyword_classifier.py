"""Keyword-Classifier für Tickets und Kosten.

Vorgeschaltet vor der teuren KI, um ~60 % der Fälle ohne API-Call zu lösen.
"""
from __future__ import annotations

import re
from typing import Any


# ── Ticket-Kategorie ────────────────────────────────────────────────
_TICKET_KEYWORDS: dict[str, list[str]] = {
    "heizung": ["heiz", "kalt", "warmwasser", "thermostat", "heizkörper", "heizung"],
    "wasser": ["wasser", "tropf", " tropft", "leck", "rohrbruch", "abfluss", "toilette", "wc"],
    "elektrik": ["strom", "licht", "steckdose", "sicherung", "lampe", "elektro", "klingel"],
    "schimmel": ["schimmel", "feucht", "nass", "lüften", "schimmelpilz"],
    "schloss": ["schlüssel", "schloss", "tür", "ausgesperrt", "zugesperrt"],
    "sanitaer": ["bad", "dusche", "waschbecken", "armatur", "spüle", "küche"],
}

_TICKET_PRIORITY_KEYWORDS: list[tuple[str, list[str]]] = [
    ("dringend", ["stromausfall", "wasserrohrbruch", "heizungsausfall", "schimmel", "ausgesperrt", "keller voll wasser", "gasgeruch", "heizung ist", "heizung ausgefallen"]),
    ("niedrig", ["kosmetisch", "farbe abgeblättert", "kleiner fleck", "lampenwechsel"]),
]


def classify_ticket(description: str) -> tuple[str | None, float]:
    """Ordnet eine Ticket-Beschreibung einer Kategorie zu.

    Returns:
        (kategorie, confidence) — confidence 0.0–1.0. None wenn kein Match.
    """
    text = description.lower()
    scores: dict[str, int] = {}
    for category, keywords in _TICKET_KEYWORDS.items():
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}", text):
                scores[category] = scores.get(category, 0) + 1

    if not scores:
        return None, 0.0

    best = max(scores, key=lambda k: scores[k])
    total = sum(scores.values())
    confidence = scores[best] / total
    return best, round(confidence, 2)


def classify_ticket_priority(description: str) -> tuple[str, float]:
    """Bestimmt Ticket-Priorität anhand dringender Keywords."""
    text = description.lower()
    for priority, keywords in _TICKET_PRIORITY_KEYWORDS:
        for kw in keywords:
            if kw in text:
                return priority, 0.9

    # Wenn kein dringendes Keyword: normal
    return "normal", 0.0


# ── Kosten-Kategorie ────────────────────────────────────────────────
_KOSTEN_KEYWORDS: dict[str, list[str]] = {
    "heizkosten": ["heiz", "öl", "gas", "fernwärme", "wärmepumpe", "heizungswartung"],
    "wasserkosten": ["wasser", "abwasser", "kanal", "wasserzähler"],
    "stromkosten": ["strom", "elektrizität", "stromzähler", "energie"],
    "versicherung": ["versicherung", "gebäudeversicherung", "haftpflicht"],
    "muellgebuehren": ["müll", "abfall", "entsorgung", "restmüll"],
    "grundsteuer": ["grundsteuer", "steuer", "gemeinde"],
    "garten": ["garten", "rasen", "grünfläche", "hausmeister"],
    "verschleißreparaturen": ["reparatur", "wartung", "schornsteinfeger", "aufzug", "klingel"],
}


def suggest_cost_category(description: str) -> tuple[str | None, float]:
    """Schlägt eine Kostenkategorie anhand der Beschreibung vor."""
    text = description.lower()
    scores: dict[str, int] = {}
    for category, keywords in _KOSTEN_KEYWORDS.items():
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}", text):
                scores[category] = scores.get(category, 0) + 1

    if not scores:
        return None, 0.0

    best = max(scores, key=lambda k: scores[k])
    total = sum(scores.values())
    confidence = scores[best] / total
    return best, round(confidence, 2)


def suggest_cost_umlagefaehig(category_name: str) -> bool:
    """Heuristische Einschätzung Umlagefähigkeit nach BetrKV."""
    name = category_name.lower()
    if any(x in name for x in ["versicherung", "muell", "grundsteuer", "garten", "schornstein", "wartung", "reparatur"]):
        return True
    if any(x in name for x in ["heizkosten", "wasserkosten", "stromkosten", "abwasser"]):
        return True
    return False
