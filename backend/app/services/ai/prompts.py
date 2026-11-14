"""Prompt-Registry für KI-generierte Texte.

Alle Prompts erwarten anonymisierte Texte. Platzhalter werden lokal
wieder aufgelöst.
"""
from __future__ import annotations


def ticket_kategorie(description: str) -> str:
    return (
        "Du kategorisierst eine Mieter-Meldung für ein deutsches Mietverhältnis.\n"
        "Wähle genau eine Kategorie aus: heizung, wasser, elektrik, schimmel, sanitaer, schloss, sonstiges.\n"
        "Antworte nur mit dem Kategorie-Namen, ohne Erklärung.\n\n"
        f"Meldung: {description}\n\n"
        "Kategorie:"
    )


def ticket_prioritaet(description: str) -> str:
    return (
        "Du bewertest die Dringlichkeit einer Mieter-Meldung.\n"
        "Wähle genau eine Priorität: dringend, normal, niedrig.\n"
        "Antworte nur mit dem Wort, ohne Erklärung.\n\n"
        f"Meldung: {description}\n\n"
        "Priorität:"
    )


def antwort_entwurf(ticket_text: str, rolle: str = "vermieter") -> str:
    return (
        "Schreibe eine höfliche, professionelle deutsche Antwort auf folgende Mieter-Meldung.\n"
        f"Absenderrolle: {rolle}.\n"
        "Antworte in 2-3 Sätzen, sachlich und lösungsorientiert.\n\n"
        f"Meldung: {ticket_text}\n\n"
        "Antwort:"
    )


def beleg_scan_prompt(text: str) -> str:
    return (
        "Du analysierst einen Belegtext (Rechnung/Quittung) für eine Nebenkostenabrechnung.\n"
        "Extrahiere Betrag, Kategorie, Umlagefähigkeit und Verteilungsschlüssel.\n"
        "Antworte ausschließlich als JSON-Objekt mit diesen Feldern:\n"
        '{"betrag": number, "kategorie": "string", "umlagefaehig": boolean, "verteilungsschluessel": "qm|personen|verbrauch", "bemerkung": "string"}\n\n'
        f"Belegtext:\n{text}\n\n"
        "JSON:"
    )


def mahnung_text(stufe: int, betrag: float, faellig_seit: str, mieter_name: str) -> str:
    return (
        "Schreibe eine formelle deutsche Mahnung für ausstehende Miete.\n"
        f"Stufe: {stufe}\n"
        f"Mieter: {mieter_name}\n"
        f"Offener Betrag: {betrag} EUR\n"
        f"Fällig seit: {faellig_seit}\n\n"
        "Halte den Text sachlich, juristisch korrekt und höflich. Maximal 150 Wörter."
    )


def mieterhoehung_text(adresse: str, alte_miete: float, neue_miete: float, grund: str) -> str:
    return (
        "Schreibe einen deutschen Mieterhöhungsbrief nach § 558 BGB.\n"
        f"Adresse der Wohnung: {adresse}\n"
        f"Bisherige Kaltmiete: {alte_miete} EUR\n"
        f"Neue Kaltmiete: {neue_miete} EUR\n"
        f"Begründung: {grund}\n\n"
        "Formell, juristisch korrekt, maximal 200 Wörter."
    )


def abrechnungserklaerung(einheit: str, jahr: int, summe: float, hinweis: str) -> str:
    return (
        "Schreibe einen erklärenden Begleittext für eine Nebenkostenabrechnung.\n"
        f"Wohnung: {einheit}\n"
        f"Abrechnungsjahr: {jahr}\n"
        f"Summe Umlageanteil: {summe} EUR\n"
        f"Hinweis: {hinweis}\n\n"
        "Freundlich, verständlich, maximal 150 Wörter."
    )


def smart_insight(context: str) -> str:
    return (
        "Du bist ein KI-Assistent für deutsche Kleinvermieter.\n"
        "Analysiere folgende Daten und gib EINE konkrete, handlungsorientierte Empfehlung.\n"
        f"Kontext: {context}\n\n"
        "Empfehlung (1 Satz):"
    )
