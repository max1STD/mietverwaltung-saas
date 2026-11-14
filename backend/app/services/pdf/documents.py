"""Dokumenten-Generierungs-Service — PDF aus Vorlagen + DB-Daten."""
from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.einheit import Einheit
from app.models.mieter import Mieter
from app.models.mietvertraege import Mietvertrag
from app.models.objekt import Objekt
from app.models.user import User
from app.services.pdf.generator import build_base_context, generate_pdf_from_template


async def _load_mieter_context(
    db: AsyncSession,
    vermieter_id: int,
    mieter_id: int,
) -> dict[str, Any]:
    """Lädt Mieter, aktiven Vertrag, Einheit und Objekt für Dokumente."""
    mieter = await db.execute(
        select(Mieter).where(Mieter.id == mieter_id, Mieter.vermieter_id == vermieter_id)
    )
    mieter_obj = mieter.scalar_one_or_none()
    if not mieter_obj:
        raise ValueError("Mieter nicht gefunden")

    vertrag_result = await db.execute(
        select(Mietvertrag)
        .where(
            Mietvertrag.mieter_id == mieter_id,
            Mietvertrag.vermieter_id == vermieter_id,
            Mietvertrag.status == "aktiv",
        )
        .order_by(Mietvertrag.mietbeginn.desc())
    )
    vertrag = vertrag_result.scalar_one_or_none()
    einheit = None
    objekt = None
    if vertrag:
        einheit = await db.get(Einheit, vertrag.einheit_id)
        if einheit:
            objekt = await db.get(Objekt, einheit.objekt_id)

    return {
        "mieter": {
            "id": mieter_obj.id,
            "full_name": f"{mieter_obj.first_name} {mieter_obj.last_name}",
            "first_name": mieter_obj.first_name,
            "last_name": mieter_obj.last_name,
            "email": mieter_obj.email,
            "phone": mieter_obj.phone,
            "anrede": "Sehr geehrte/r",
        },
        "vertrag": {
            "mietbeginn": vertrag.mietbeginn.strftime("%d.%m.%Y") if vertrag else "",
            "miete_cold": vertrag.miete_cold if vertrag else 0.0,
            "nebenkosten_voraus": vertrag.nebenkosten_voraus if vertrag else 0.0,
        },
        "einheit": {
            "id": einheit.id if einheit else None,
            "name": einheit.name if einheit else "",
            "size_qm": einheit.size_qm if einheit else 0.0,
            "floor": einheit.floor if einheit else "",
        },
        "objekt": {
            "id": objekt.id if objekt else None,
            "bezeichnung": objekt.bezeichnung if objekt else "",
            "adresse": f"{objekt.strasse} {objekt.hausnr}" if objekt else "",
            "plz": objekt.plz if objekt else "",
            "ort": objekt.ort if objekt else "",
        },
    }


async def _vermieter_dict(db: AsyncSession, vermieter_id: int) -> dict[str, Any]:
    """Lädt Vermieter-Stammdaten für Briefkopf."""
    user = await db.get(User, vermieter_id)
    if not user:
        raise ValueError("Vermieter nicht gefunden")

    return {
        "id": user.id,
        "full_name": user.full_name,
        "company": user.company or user.full_name,
        "email": user.email,
        "phone": user.phone,
        "street": getattr(user, "street", ""),
        "house_number": getattr(user, "house_number", ""),
        "zip": getattr(user, "zip", ""),
        "city": getattr(user, "city", ""),
        "logo_path": getattr(user, "logo_path", None),
    }


async def generate_wohnungsgeberbestaetigung(
    db: AsyncSession,
    vermieter_id: int,
    mieter_id: int,
) -> bytes:
    """Erzeugt Wohnungsgeberbestätigung als PDF."""
    vermieter = await _vermieter_dict(db, vermieter_id)
    ctx = await _load_mieter_context(db, vermieter_id, mieter_id)
    base = build_base_context(vermieter, datum=date.today())

    context = {
        "title": "Wohnungsgeberbestätigung",
        **base,
        **ctx,
    }
    return generate_pdf_from_template("wohnungsgeberbestaetigung.html", context)


async def generate_mahnung(
    db: AsyncSession,
    vermieter_id: int,
    mieter_id: int,
    stufe: int,
    betrag: float,
    faellig_seit: str,
) -> bytes:
    """Erzeugt Mahnung als PDF."""
    vermieter = await _vermieter_dict(db, vermieter_id)
    ctx = await _load_mieter_context(db, vermieter_id, mieter_id)
    base = build_base_context(vermieter, datum=date.today())

    context = {
        "title": f"Mahnung Stufe {stufe}",
        **base,
        **ctx,
        "stufe": stufe,
        "betrag": betrag,
        "faellig_seit": faellig_seit,
    }
    return generate_pdf_from_template("mahnung.html", context)
