"""KI-Endpunkte — Ticket-Kategorisierung, Beleg-Scan, Text-Generierung."""
from __future__ import annotations

import json
import tempfile
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import _get_client_ip, csrf_protect, get_current_user, require_role
from app.models.user import User
from app.schemas.ki import (
    KIMahnungRequest,
    KIReceiptResponse,
    KISimpleRequest,
    KISimpleResponse,
    KISmartInsightRequest,
    KITicketCategorizeRequest,
    KITicketCategorizeResponse,
)
from app.services.ai.keyword_classifier import (
    classify_ticket,
    classify_ticket_priority,
    suggest_cost_category,
    suggest_cost_umlagefaehig,
)
from app.services.ai.ollama_client import KIResult, generate_text
from app.services.ai.presidio import anonymize, deanonymize
from app.services.ai import prompts
from app.services.audit_log import audit_log
from app.services.ocr.tesseract import extract_text

router = APIRouter()


@router.post(
    "/ticket-kategorie",
    response_model=KITicketCategorizeResponse,
    dependencies=[Depends(csrf_protect)],
)
async def ki_ticket_kategorie(
    data: KITicketCategorizeRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> KITicketCategorizeResponse:
    """Schlägt Kategorie + Priorität für ein Ticket vor."""
    text = data.text
    cat, cat_conf = classify_ticket(text)
    prio, prio_conf = classify_ticket_priority(text)

    # Falls Keyword-Classifier unsicher ist, frage KI
    if cat is None or cat_conf < 0.6:
        anon, mapping = anonymize(text)
        prompt = prompts.ticket_kategorie(anon)
        result: KIResult = await generate_text(prompt, model="glm-5.2")
        cat = deanonymize(result.text.strip().lower(), mapping)
        cat_conf = 0.7

    if prio == "normal" or prio_conf < 0.6:
        anon, mapping = anonymize(text)
        prompt = prompts.ticket_prioritaet(anon)
        result = await generate_text(prompt, model="glm-5.2")
        raw = deanonymize(result.text.strip().lower(), mapping)
        if raw in {"dringend", "normal", "niedrig"}:
            prio = raw
            prio_conf = 0.7

    await audit_log(
        db,
        user_id=user.id,
        vermieter_id=user.id,
        action="ki_ticket_kategorie",
        entity="ki",
        entity_id=0,
        details={"input_length": len(text), "kategorie": cat, "prioritaet": prio},
        ip=_get_client_ip(request),
    )

    return KITicketCategorizeResponse(
        kategorie=cat or "sonstiges",
        kategorie_confidence=cat_conf,
        prioritaet=prio,
        prioritaet_confidence=prio_conf,
    )


@router.post(
    "/antwort-entwurf",
    response_model=KISimpleResponse,
    dependencies=[Depends(csrf_protect)],
)
async def ki_antwort_entwurf(
    data: KISimpleRequest,
    request: Request,
    rolle: str = "vermieter",
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> KISimpleResponse:
    """Erzeugt einen Antwort-Entwurf auf eine Mieter-Meldung."""
    text = data.text
    anon, mapping = anonymize(text)
    prompt = prompts.antwort_entwurf(anon, rolle=rolle)
    result = await generate_text(prompt, model="glm-5.2")
    answer = deanonymize(result.text.strip(), mapping)

    await audit_log(
        db,
        user_id=user.id,
        vermieter_id=user.id,
        action="ki_antwort_entwurf",
        entity="ki",
        entity_id=0,
        details={"input_length": len(text)},
        ip=_get_client_ip(request),
    )

    return KISimpleResponse(text=answer)


@router.post(
    "/beleg-scan",
    response_model=KIReceiptResponse,
    dependencies=[Depends(csrf_protect)],
)
async def ki_beleg_scan(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> KIReceiptResponse:
    """Lädt einen Beleg hoch, führt OCR aus und schlägt Kosten-Details vor."""
    suffix = ".pdf" if file.content_type and "pdf" in file.content_type else ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        raw_text = extract_text(tmp_path, mime_type=file.content_type)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"OCR fehlgeschlagen: {exc}",
        ) from exc

    # Keyword-Classifier als schnelle Heuristik
    cat, cat_conf = suggest_cost_category(raw_text)
    umlagefaehig = suggest_cost_umlagefaehig(cat or "")
    schluessel = "qm"

    # KI-Fallback für Betrag + Kategorie
    if cat is None or cat_conf < 0.6:
        anon, mapping = anonymize(raw_text[:2000])
        prompt = prompts.beleg_scan_prompt(anon)
        result = await generate_text(prompt, model="glm-5.2")
        try:
            parsed = json.loads(result.text.strip())
            cat = parsed.get("kategorie", cat or "sonstiges")
            betrag = float(parsed.get("betrag", 0.0))
            umlagefaehig = bool(parsed.get("umlagefaehig", umlagefaehig))
            schluessel = parsed.get("verteilungsschluessel", schluessel)
        except (json.JSONDecodeError, ValueError):
            betrag = 0.0
    else:
        betrag = 0.0

    await audit_log(
        db,
        user_id=user.id,
        vermieter_id=user.id,
        action="ki_beleg_scan",
        entity="ki",
        entity_id=0,
        details={
            "filename": file.filename,
            "ocr_chars": len(raw_text),
            "kategorie": cat,
        },
        ip=_get_client_ip(request),
    )

    return KIReceiptResponse(
        rohtext=raw_text[:500],
        betrag=betrag,
        kategorie=cat or "sonstiges",
        umlagefaehig=umlagefaehig,
        verteilungsschluessel=schluessel,
    )


@router.post(
    "/mahnung",
    response_model=KISimpleResponse,
    dependencies=[Depends(csrf_protect)],
)
async def ki_mahnung(
    data: KIMahnungRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> KISimpleResponse:
    """Erzeugt einen Mahnungstext."""
    text = data.text
    stufe = data.stufe
    betrag = data.betrag
    faellig_seit = data.faellig_seit
    mieter_name = data.mieter_name
    anon, mapping = anonymize(text)
    prompt = prompts.mahnung_text(stufe, betrag, faellig_seit, mieter_name)
    result = await generate_text(prompt, model="kimi-k2.6")
    answer = deanonymize(result.text.strip(), mapping)

    await audit_log(
        db,
        user_id=user.id,
        vermieter_id=user.id,
        action="ki_mahnung",
        entity="ki",
        entity_id=0,
        details={"stufe": stufe, "betrag": betrag},
        ip=_get_client_ip(request),
    )

    return KISimpleResponse(text=answer)


@router.post(
    "/smart-insight",
    response_model=KISimpleResponse,
    dependencies=[Depends(csrf_protect)],
)
async def ki_smart_insight(
    data: KISmartInsightRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> KISimpleResponse:
    """Erzeugt eine Smart-Insight-Empfehlung."""
    context = data.context
    anon, mapping = anonymize(context)
    prompt = prompts.smart_insight(anon)
    result = await generate_text(prompt, model="glm-5.2")
    answer = deanonymize(result.text.strip(), mapping)

    await audit_log(
        db,
        user_id=user.id,
        vermieter_id=user.id,
        action="ki_smart_insight",
        entity="ki",
        entity_id=0,
        details={"context_length": len(context)},
        ip=_get_client_ip(request),
    )

    return KISimpleResponse(text=answer)
