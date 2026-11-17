"""Dokumenten-Endpunkte — PDF-Generierung, Upload, Liste, Download, Vorschau."""
from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import _get_client_ip, csrf_protect, require_role
from app.models.user import User
from app.schemas.dokument import (
    DokumentDeleteResponse,
    DokumentGenerateRequest,
    DokumentGenerateResponse,
    DokumentListResponse,
    DokumentUploadResponse,
)
from app.services.audit_log import audit_log
from app.services.dokumente import DokumentService, DokumentValidationError
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


@router.post("/upload", response_model=DokumentUploadResponse, dependencies=[Depends(csrf_protect)])
async def upload_document(
    entity_type: str = Form(...),
    entity_id: int = Form(...),
    titel: str = Form(...),
    typ: str = Form("sonstiges"),
    jahr: int | None = Form(None),
    file: UploadFile = File(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> DokumentUploadResponse:
    """Ladet ein Dokument für eine Entität hoch."""
    service = DokumentService(db)
    try:
        dokument = await service.upload(
            vermieter_id=user.id,
            entity_type=entity_type,
            entity_id=entity_id,
            upload=file,
            titel=titel,
            typ=typ,
            jahr=jahr,
        )
    except DokumentValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={exc.field: [exc.message]},
        ) from exc

    await audit_log(
        db,
        user_id=user.id,
        vermieter_id=user.id,
        action="dokument_hochgeladen",
        entity="dokument",
        entity_id=dokument.id,
        details={"entity_type": entity_type, "entity_id": entity_id, "titel": titel},
        ip=_get_client_ip(request),
    )

    return _map_dokument(dokument)


@router.get("/", response_model=DokumentListResponse)
async def list_documents(
    entity_type: str | None = None,
    entity_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> DokumentListResponse:
    """Listet Dokumente des Vermieters, optional gefiltert nach Entität."""
    service = DokumentService(db)
    docs = await service.list_documents(
        vermieter_id=user.id,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    return DokumentListResponse(items=[_map_dokument(d) for d in docs])


@router.get("/{dokument_id}/download")
async def download_uploaded_document(
    dokument_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> Response:
    """Lädt ein hochgeladenes Dokument herunter."""
    service = DokumentService(db)
    dokument = await service.get_document(user.id, dokument_id)
    if not dokument:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dokument nicht gefunden")

    try:
        content, content_type = await service.download(dokument)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return Response(
        content=content,
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={dokument.file_name}",
        },
    )


@router.get("/{dokument_id}/preview")
async def preview_uploaded_document(
    dokument_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> Response:
    """Zeigt eine Vorschau des Dokuments (PDF/PNG)."""
    service = DokumentService(db)
    dokument = await service.get_document(user.id, dokument_id)
    if not dokument:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dokument nicht gefunden")

    try:
        content, content_type = await service.preview(dokument)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return Response(
        content=content,
        media_type=content_type,
    )


@router.delete("/{dokument_id}", response_model=DokumentDeleteResponse, dependencies=[Depends(csrf_protect)])
async def delete_uploaded_document(
    dokument_id: int,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("vermieter")),
) -> DokumentDeleteResponse:
    """Löscht ein hochgeladenes Dokument."""
    service = DokumentService(db)
    dokument = await service.get_document(user.id, dokument_id)
    if not dokument:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dokument nicht gefunden")

    await service.delete(dokument)

    await audit_log(
        db,
        user_id=user.id,
        vermieter_id=user.id,
        action="dokument_geloescht",
        entity="dokument",
        entity_id=dokument_id,
        details={"file_name": dokument.file_name},
        ip=_get_client_ip(request),
    )

    return DokumentDeleteResponse(id=dokument_id)


def _map_dokument(dokument) -> DokumentUploadResponse:
    return DokumentUploadResponse(
        id=dokument.id,
        entity_type=dokument.entity_type,
        entity_id=dokument.entity_id,
        titel=dokument.titel,
        typ=dokument.typ,
        jahr=dokument.jahr,
        file_name=dokument.file_name,
        file_size=dokument.file_size,
        content_type=dokument.content_type,
        status=dokument.status,
        storage_path=dokument.storage_path,
        created_at=dokument.created_at,
        upload_error=dokument.upload_error,
    )
