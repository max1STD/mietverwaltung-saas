"""Geo-Hilfsrouten für Adress-Autovervollständigung.

Datenquellen:
- OpenPLZ API (PLZ → Ort)
- OpenStreetMap Nominatim (Straßen-Autocomplete)

Alle Anfragen werden serverseitig ausgeführt, damit keine externen
API-Keys oder URLs im Frontend sichtbar sind.
"""
from __future__ import annotations

import asyncio
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.middleware.auth import require_role

router = APIRouter()

# OpenPLZ API liefert für eine deutsche PLZ alle zugehörigen Orte.
OPENPLZ_URL = "https://openplzapi.org/de/Localities"

# Nominatim erfordert einen validen User-Agent.
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_USER_AGENT = "MietVerwaltung-SaaS/0.1.0"


async def _fetch_openplz(plz: str) -> list[dict[str, Any]]:
    """Holt Orte für eine Postleitzahl von der OpenPLZ API."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            OPENPLZ_URL,
            params={"postalCode": plz},
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json()


async def _fetch_nominatim_strassen(
    plz: str | None,
    ort: str | None,
    q: str | None,
) -> list[dict[str, Any]]:
    """Holt Straßenvorschläge von Nominatim (strukturierte Suche)."""
    params: dict[str, Any] = {
        "format": "json",
        "addressdetails": 1,
        "limit": 10,
        "countrycodes": "de",
        "dedupe": 1,
    }
    if plz:
        params["postalcode"] = plz
    if ort:
        params["city"] = ort
    # Nominatim akzeptiert 'street' für Straßenpräfixe.
    if q:
        params["street"] = q

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            NOMINATIM_URL,
            params=params,
            headers={"User-Agent": NOMINATIM_USER_AGENT, "Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json()


@router.get(
    "/plz/{plz}",
    dependencies=[Depends(require_role("vermieter"))],
)
async def plz_to_ort(plz: str) -> dict[str, Any]:
    """Liefert zu einer deutschen PLZ den/die zugehörigen Orte.

    Beispiel: `/api/v1/geo/plz/21635` → `{ "plz": "21635", "orte": ["Jork", ...] }`
    """
    if not plz.isdigit() or len(plz) != 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ungültige PLZ. Erwartet werden 5 Ziffern.",
        )

    try:
        data = await _fetch_openplz(plz)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Fehler bei der PLZ-Suche: {exc}",
        ) from exc

    orte = sorted({item.get("name") for item in data if item.get("name")})
    return {"plz": plz, "orte": orte}


@router.get(
    "/strassen",
    dependencies=[Depends(require_role("vermieter"))],
)
async def strassen_autocomplete(
    plz: str | None = None,
    ort: str | None = None,
    q: str | None = None,
) -> dict[str, Any]:
    """Liefert Straßenvorschläge basierend auf PLZ, Ort und/oder Präfix.

    Beispiel: `/api/v1/geo/strassen?plz=21635&q=Kurze` → Straßen in Jork mit 'Kurze'.
    """
    if not any([plz, ort, q]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mindestens einer der Parameter plz, ort oder q ist erforderlich.",
        )

    try:
        data = await _fetch_nominatim_strassen(plz, ort, q)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Fehler bei der Straßensuche: {exc}",
        ) from exc

    strassen: list[str] = []
    seen = set()
    for item in data:
        addr = item.get("address", {})
        # Nominatim liefert Straßen unter unterschiedlichen Schlüsseln.
        street = addr.get("road") or addr.get("street") or addr.get("pedestrian") or addr.get("square")
        if street:
            key = street.lower()
            if key not in seen:
                seen.add(key)
                strassen.append(street)

    return {"plz": plz, "ort": ort, "q": q, "strassen": strassen}
