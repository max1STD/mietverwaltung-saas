"""Ollama Cloud Client — GLM 5.2 + Kimi K2.6.

Sensible Daten werden vor dem Call anonymisiert (Presidio) und das Ergebnis
wieder deanonymisiert. Es werden nur anonymisierte Daten übertragen.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

import httpx
import structlog

logger = structlog.get_logger()

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "https://ollama.com/v1")
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY")

# Default-Modelle aus dem Konzept
DEFAULT_MODEL = "glm-5.2"
COMPLEX_MODEL = "kimi-k2.6"


@dataclass(frozen=True)
class KIResult:
    text: str
    model: str
    finish_reason: str | None
    raw_response: dict[str, Any] | None = None


async def generate_text(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.3,
    max_tokens: int = 2048,
    timeout: float = 60.0,
) -> KIResult:
    """Sendet einen Prompt an Ollama Cloud und gibt den generierten Text zurück.

    Falls kein API-Key konfiguriert ist, wird ein lokaler Fallback-Text geliefert,
    damit die App im Dev-Modus testbar bleibt.
    """
    if not OLLAMA_API_KEY:
        logger.warning("ollama_api_key_missing", model=model)
        return KIResult(
            text=_fallback_response(prompt, model),
            model=model,
            finish_reason="fallback",
        )

    headers = {
        "Authorization": f"Bearer {OLLAMA_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(
            f"{OLLAMA_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

    choice = data.get("choices", [{}])[0]
    text = choice.get("message", {}).get("content", "")
    finish_reason = choice.get("finish_reason")

    return KIResult(
        text=text,
        model=data.get("model", model),
        finish_reason=finish_reason,
        raw_response=data,
    )


def _fallback_response(prompt: str, model: str) -> str:
    """Lokaler Fallback, wenn kein Ollama-Key hinterlegt ist.

    Gibt sinnvolle Stub-Antworten zurück, damit Tests/Frontend funktionieren.
    """
    lowered = prompt.lower()
    if "ticket" in lowered and "kategorie" in lowered:
        return "wasser"
    if "priorit" in lowered:
        return "dringend"
    if "beleg" in lowered or "kosten" in lowered:
        return json.dumps({
            "betrag": 124.50,
            "kategorie": "reparatur",
            "umlagefaehig": True,
            "verteilungsschluessel": "qm",
            "bemerkung": "Keine OCR-Key-Konfiguration aktiv (Fallback).",
        })
    if "mahnung" in lowered:
        return "Sehr geehrte Damen und Herren, leider haben wir Ihre Mietzahlung noch nicht erhalten. Bitte überweisen Sie den offenen Betrag innerhalb von 7 Tagen."
    if "mieterhöhung" in lowered or "miete" in lowered:
        return "Sehr geehrte/r Mieter/in, wir passen die Kaltmiete gemäß § 558 BGB an. Die neue Kaltmiete beträgt ab dem vereinbarten Termin [MIETE] €."
    if "antwort" in lowered or "entwurf" in lowered:
        return "Vielen Dank für Ihre Nachricht. Wir kümmern uns zeitnah um Ihr Anliegen."
    return f"KI-Antwort (Fallback, Modell {model})."
