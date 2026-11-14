"""Dokumenten-Endpunkte — PDF-Generierung und Download."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import _get_client_ip, csrf_protect, require_role
from app.models.user import User
from app.schemas.dokument import DokumentGenerateRequest, DokumentGenerateResponse
from app.services.audit_log import audit_log
from app.services.pdf.documents import (
    generate_mahnung,
    generate_wohnungsgeberbestaetigung,
)

router = APIRouter()


@router.post(
    "/generate",
    response_model=DokumentGenerateResponse,
    dependencies=[Depends(csrf_protect)],
)
async def generate_document(
    data: DokumentGenerateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> DokumentGenerateResponse:
    """Generiert ein Dokument und gibt Download-URL zurück."""
    template = data.template
    if template not in {"wohnungsgeberbestaetigung", "mahnung"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vorlage '{template}' wird nicht unterstützt",
        )

    await audit_log(
        db,
        user_id=user.id,
        vermieter_id=user.id,
        action="dokument_generiert",
        entity="dokument",
        entity_id=0,
        details={"template": template, "mieter_id": data.mieter_id},
        ip=_get_client_ip(request),
    )

    return DokumentGenerateResponse(
        dokument_id=0,
        download_url=f"/api/v1/dokumente/download/{template}?mieter_id={data.mieter_id}",
        template=template,
    )


@router.get("/download/wohnungsgeberbestaetigung")
async def download_wohnungsgeberbestaetigung(
    mieter_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> Response:
    """Liefert Wohnungsgeberbestätigung als PDF-Download."""
    try:
        pdf_bytes = await generate_wohnungsgeberbestaetigung(db, user.id, mieter_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=wohnungsgeberbestaetigung.pdf",
        },
    )


@router.get("/download/mahnung")
async def download_mahnung(
    mieter_id: int,
    stufe: int = 1,
    betrag: float = 0.0,
    faellig_seit: str = "",
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> Response:
    """Liefert Mahnung als PDF-Download."""
    try:
        pdf_bytes = await generate_mahnung(
            db,
            user.id,
            mieter_id,
            stufe=stufe,
            betrag=betrag,
            faellig_seit=faellig_seit,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=mahnung_stufe_{stufe}.pdf",
        },
    )
