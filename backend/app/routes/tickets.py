"""Ticket-System REST API: Tickets, Kommentare, SLA und Trigger."""
from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import csrf_protect, get_current_user
from app.models.mieter import Mieter
from app.models.tickets import Ticket, TicketComment, TicketSLA, TicketTrigger
from app.models.user import User
from app.schemas.tickets import (
    MessageResponse,
    TicketCommentCreate,
    TicketCommentResponse,
    TicketCreate,
    TicketListResponse,
    TicketResponse,
    TicketSLACreate,
    TicketSLAResponse,
    TicketSLAUpdate,
    TicketTriggerCreate,
    TicketTriggerResponse,
    TicketTriggerUpdate,
    TicketUpdate,
)

router = APIRouter()

TICKET_FINAL_STATES = {"erledigt", "geschlossen", "abgelehnt"}


def _is_final_status(status_value: str | None) -> bool:
    return status_value in TICKET_FINAL_STATES


def _format_dt(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _to_comment_response(comment: TicketComment) -> TicketCommentResponse:
    return TicketCommentResponse(
        id=comment.id,
        ticket_id=comment.ticket_id,
        author_id=comment.author_id,
        author_role=comment.author_role,
        content=comment.content,
        ist_ki_entwurf=comment.ist_ki_entwurf,
        is_internal=comment.is_internal,
        created_at=_format_dt(comment.created_at),
    )


def _to_ticket_response(ticket: Ticket, include_comments: bool = True) -> TicketResponse:
    comments = (
        [_to_comment_response(c) for c in ticket.comments]
        if include_comments
        else []
    )
    return TicketResponse(
        id=ticket.id,
        vermieter_id=ticket.vermieter_id,
        mieter_id=ticket.mieter_id,
        einheit_id=ticket.einheit_id,
        ticket_number=ticket.ticket_number,
        title=ticket.title,
        description=ticket.description,
        category=ticket.category,
        priority=ticket.priority,
        status=ticket.status,
        ki_kategorisiert=ticket.ki_kategorisiert,
        ki_prioritaet=ticket.ki_prioritaet,
        assigned_to=ticket.assigned_to,
        handwerker_id=ticket.handwerker_id,
        sla_id=ticket.sla_id,
        created_at=_format_dt(ticket.created_at),
        updated_at=_format_dt(ticket.updated_at),
        closed_at=_format_dt(ticket.closed_at),
        comments=comments,
    )


def _to_sla_response(sla: TicketSLA) -> TicketSLAResponse:
    return TicketSLAResponse(
        id=sla.id,
        vermieter_id=sla.vermieter_id,
        name=sla.name,
        response_time_hours=sla.response_time_hours,
        resolution_time_hours=sla.resolution_time_hours,
        biz_hours_only=sla.biz_hours_only,
        biz_start=sla.biz_start.strftime("%H:%M") if sla.biz_start else None,
        biz_end=sla.biz_end.strftime("%H:%M") if sla.biz_end else None,
        biz_days=sla.biz_days,
        escalation_levels=sla.escalation_levels,
        is_active=sla.is_active,
    )


def _to_trigger_response(trigger: TicketTrigger) -> TicketTriggerResponse:
    return TicketTriggerResponse(
        id=trigger.id,
        vermieter_id=trigger.vermieter_id,
        name=trigger.name,
        trigger_type=trigger.trigger_type,
        condition=trigger.condition,
        perform=trigger.perform,
        is_active=trigger.is_active,
        created_at=_format_dt(trigger.created_at),
    )


def _require_vermieter(user: User) -> None:
    """Wirft 403, wenn der User kein Vermieter ist."""
    if user.role not in {"vermieter", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur Vermieter dürfen diese Aktion ausführen",
        )


async def _get_mieter_for_user(db: AsyncSession, user: User) -> Mieter:
    """Ermittelt den Mieter-Datensatz zum eingeloggten Mieter-Account."""
    result = await db.execute(
        select(Mieter)
        .where(
            Mieter.email == user.email,
            Mieter.vermieter_id == user.vermieter_id,
        )
        .limit(1)
    )
    mieter = result.scalar_one_or_none()
    if mieter is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mieterprofil nicht gefunden",
        )
    return mieter


async def _generate_ticket_number(
    db: AsyncSession,
    vermieter_id: int,
) -> str:
    """Erzeugt eine fortlaufende Ticketnummer pro Vermieter und Jahr.

    Format: TKT-YYYY-NNNN. Bei Konflikt (race condition) wird einmalig neu
    ermittelt, da UNIQUE-Constraint auf DB-Ebene greift.
    """
    year = datetime.now(UTC).year
    prefix = f"TKT-{year}-"

    result = await db.execute(
        select(Ticket.ticket_number)
        .where(
            Ticket.vermieter_id == vermieter_id,
            Ticket.ticket_number.like(f"{prefix}%"),
        )
        .order_by(Ticket.ticket_number.desc())
        .limit(1)
    )
    last = result.scalar_one_or_none()
    next_seq = 1
    if last:
        try:
            next_seq = int(last.split("-")[-1]) + 1
        except ValueError:
            next_seq = 1
    return f"{prefix}{next_seq:04d}"


async def _get_ticket_or_404(
    db: AsyncSession,
    ticket_id: int,
    user: User,
) -> Ticket:
    """Lädt ein Ticket mit Berechtigungsprüfung."""
    ticket = await db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket nicht gefunden",
        )

    # Sicherstellen, dass das Ticket zum aktuellen Vermieter gehört.
    expected_vermieter_id = (
        user.vermieter_id if user.role == "mieter" else user.id
    )
    if ticket.vermieter_id != expected_vermieter_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Zugriff auf dieses Ticket nicht erlaubt",
        )

    # Mieter dürfen nur eigene Tickets sehen (über Mieter-Datensatz).
    if user.role == "mieter":
        mieter = await _get_mieter_for_user(db, user)
        if ticket.mieter_id is None or ticket.mieter_id != mieter.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Zugriff auf dieses Ticket nicht erlaubt",
            )

    return ticket


# ---------------------------------------------------------------------------
# Tickets
# ---------------------------------------------------------------------------
@router.get("", response_model=TicketListResponse)
async def list_tickets(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    status_filter: str | None = Query(None, alias="status"),
    priority: str | None = Query(None),
    category: str | None = Query(None),
    mieter_id: int | None = Query(None),
    einheit_id: int | None = Query(None),
    assigned_to: int | None = Query(None),
    open_only: bool = Query(False),
) -> TicketListResponse:
    """Liste aller Tickets des Vermieters (oder eigene Tickets für Mieter)."""
    query = select(Ticket)

    if user.role == "mieter":
        mieter_profile = await _get_mieter_for_user(db, user)
        query = query.where(
            Ticket.vermieter_id == user.vermieter_id,
            Ticket.mieter_id == mieter_profile.id,
        )
    else:
        query = query.where(Ticket.vermieter_id == user.id)

    if status_filter:
        query = query.where(Ticket.status == status_filter)
    if priority:
        query = query.where(Ticket.priority == priority)
    if category:
        query = query.where(Ticket.category == category)
    if mieter_id is not None:
        query = query.where(Ticket.mieter_id == mieter_id)
    if einheit_id is not None:
        query = query.where(Ticket.einheit_id == einheit_id)
    if assigned_to is not None:
        query = query.where(Ticket.assigned_to == assigned_to)
    if open_only:
        query = query.where(Ticket.status.notin_(TICKET_FINAL_STATES))

    query = query.order_by(Ticket.created_at.desc())

    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar_one()

    result = await db.execute(query)
    items = [_to_ticket_response(t, include_comments=False) for t in result.scalars().all()]
    return TicketListResponse(items=items, total=total)


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
async def create_ticket(
    request: Request,
    data: TicketCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TicketResponse:
    """Erstellt ein neues Ticket."""
    if user.role == "mieter":
        if user.vermieter_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vermieter-Zuordnung fehlt",
            )
        vermieter_id = user.vermieter_id
        mieter_profile = await _get_mieter_for_user(db, user)
        mieter_id = mieter_profile.id
        # Mieter dürfen keine fremden Mieter-IDs übergeben.
        if data.mieter_id is not None and data.mieter_id != mieter_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Ungültige Mieter-Zuordnung",
            )
    else:
        vermieter_id = user.id
        mieter_id = data.mieter_id

    ticket_number = await _generate_ticket_number(db, vermieter_id)

    ticket = Ticket(
        vermieter_id=vermieter_id,
        mieter_id=mieter_id,
        einheit_id=data.einheit_id,
        ticket_number=ticket_number,
        title=data.title,
        description=data.description,
        category=data.category,
        priority=data.priority,
        status="offen",
        assigned_to=data.assigned_to,
        handwerker_id=data.handwerker_id,
        sla_id=data.sla_id,
    )
    db.add(ticket)
    await db.flush()
    await db.refresh(ticket)
    return _to_ticket_response(ticket)


@router.get("/{ticket_id:int}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TicketResponse:
    """Gibt ein einzelnes Ticket inklusive Kommentare zurück."""
    ticket = await _get_ticket_or_404(db, ticket_id, user)
    return _to_ticket_response(ticket)


@router.patch(
    "/{ticket_id:int}",
    response_model=TicketResponse,
    dependencies=[Depends(csrf_protect)],
)
async def update_ticket(
    request: Request,
    ticket_id: int,
    data: TicketUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TicketResponse:
    """Aktualisiert ein Ticket (Status, Priorität, Zuordnung, ...)."""
    ticket = await _get_ticket_or_404(db, ticket_id, user)

    # Mieter dürfen nur bestimmte Felder ändern.
    if user.role == "mieter":
        allowed = {"description", "priority"}
        update_data = data.model_dump(exclude_unset=True)
        for key in list(update_data.keys()):
            if key not in allowed:
                del update_data[key]
    else:
        update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(ticket, key, value)

    # closed_at automatisch bei Endstatus setzen/entfernen.
    new_status = update_data.get("status")
    if new_status is not None:
        if _is_final_status(new_status):
            ticket.closed_at = datetime.now(UTC)
        else:
            ticket.closed_at = None

    await db.flush()
    await db.refresh(ticket)
    return _to_ticket_response(ticket)


@router.delete(
    "/{ticket_id:int}",
    response_model=MessageResponse,
    dependencies=[Depends(csrf_protect)],
)
async def delete_ticket(
    request: Request,
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MessageResponse:
    """Löscht ein Ticket inklusive Kommentare (physisch, da kein Soft-Delete)."""
    _require_vermieter(user)
    ticket = await _get_ticket_or_404(db, ticket_id, user)
    await db.delete(ticket)
    await db.flush()
    return MessageResponse(message="Ticket gelöscht")


# ---------------------------------------------------------------------------
# Kommentare
# ---------------------------------------------------------------------------
@router.get("/{ticket_id:int}/comments", response_model=list[TicketCommentResponse])
async def list_comments(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[TicketCommentResponse]:
    """Liste aller Kommentare zu einem Ticket."""
    ticket = await _get_ticket_or_404(db, ticket_id, user)
    visible = [
        c for c in ticket.comments if not c.is_internal or user.role != "mieter"
    ]
    return [_to_comment_response(c) for c in visible]


@router.post(
    "/{ticket_id:int}/comments",
    response_model=TicketCommentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
async def create_comment(
    request: Request,
    ticket_id: int,
    data: TicketCommentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TicketCommentResponse:
    """Fügt einem Ticket einen Kommentar hinzu."""
    ticket = await _get_ticket_or_404(db, ticket_id, user)

    # Mieter dürfen keine internen Notizen schreiben.
    is_internal = data.is_internal if user.role != "mieter" else False

    comment = TicketComment(
        vermieter_id=ticket.vermieter_id,
        ticket_id=ticket.id,
        author_id=user.id,
        author_role=user.role,
        content=data.content,
        is_internal=is_internal,
    )
    db.add(comment)
    await db.flush()
    await db.refresh(comment)
    return _to_comment_response(comment)


@router.delete(
    "/{ticket_id:int}/comments/{comment_id:int}",
    response_model=MessageResponse,
    dependencies=[Depends(csrf_protect)],
)
async def delete_comment(
    request: Request,
    ticket_id: int,
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MessageResponse:
    """Löscht einen Kommentar (nur Vermieter/Admin)."""
    _require_vermieter(user)
    ticket = await _get_ticket_or_404(db, ticket_id, user)
    comment = await db.get(TicketComment, comment_id)
    if comment is None or comment.ticket_id != ticket.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kommentar nicht gefunden",
        )
    await db.delete(comment)
    await db.flush()
    return MessageResponse(message="Kommentar gelöscht")


# ---------------------------------------------------------------------------
# SLA-Konfiguration
# ---------------------------------------------------------------------------
@router.get("/sla", response_model=list[TicketSLAResponse])
async def list_sla_configs(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[TicketSLAResponse]:
    """Liste aller SLA-Konfigurationen des Vermieters."""
    _require_vermieter(user)
    result = await db.execute(
        select(TicketSLA)
        .where(TicketSLA.vermieter_id == user.id)
        .order_by(TicketSLA.id.desc())
    )
    return [_to_sla_response(s) for s in result.scalars().all()]


@router.post(
    "/sla",
    response_model=TicketSLAResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
async def create_sla_config(
    request: Request,
    data: TicketSLACreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TicketSLAResponse:
    """Erstellt eine neue SLA-Konfiguration."""
    _require_vermieter(user)
    sla = TicketSLA(
        vermieter_id=user.id,
        name=data.name,
        response_time_hours=data.response_time_hours,
        resolution_time_hours=data.resolution_time_hours,
        biz_hours_only=data.biz_hours_only,
        biz_start=datetime.strptime(data.biz_start or "09:00", "%H:%M").time(),
        biz_end=datetime.strptime(data.biz_end or "17:00", "%H:%M").time(),
        biz_days=data.biz_days,
        escalation_levels=data.escalation_levels,
        is_active=data.is_active,
    )
    db.add(sla)
    await db.flush()
    await db.refresh(sla)
    return _to_sla_response(sla)


@router.patch(
    "/sla/{sla_id}",
    response_model=TicketSLAResponse,
    dependencies=[Depends(csrf_protect)],
)
async def update_sla_config(
    request: Request,
    sla_id: int,
    data: TicketSLAUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TicketSLAResponse:
    """Aktualisiert eine SLA-Konfiguration."""
    _require_vermieter(user)
    sla = await db.get(TicketSLA, sla_id)
    if sla is None or sla.vermieter_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SLA-Konfiguration nicht gefunden",
        )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key in ("biz_start", "biz_end") and value is not None:
            value = datetime.strptime(value, "%H:%M").time()
        setattr(sla, key, value)

    await db.flush()
    await db.refresh(sla)
    return _to_sla_response(sla)


@router.delete(
    "/sla/{sla_id}",
    response_model=MessageResponse,
    dependencies=[Depends(csrf_protect)],
)
async def delete_sla_config(
    request: Request,
    sla_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MessageResponse:
    """Löscht eine SLA-Konfiguration."""
    _require_vermieter(user)
    sla = await db.get(TicketSLA, sla_id)
    if sla is None or sla.vermieter_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SLA-Konfiguration nicht gefunden",
        )
    await db.delete(sla)
    await db.flush()
    return MessageResponse(message="SLA-Konfiguration gelöscht")


# ---------------------------------------------------------------------------
# Trigger / Automatisierungsregeln
# ---------------------------------------------------------------------------
@router.get("/triggers", response_model=list[TicketTriggerResponse])
async def list_triggers(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[TicketTriggerResponse]:
    """Liste aller Ticket-Trigger des Vermieters."""
    _require_vermieter(user)
    result = await db.execute(
        select(TicketTrigger)
        .where(TicketTrigger.vermieter_id == user.id)
        .order_by(TicketTrigger.created_at.desc())
    )
    return [_to_trigger_response(t) for t in result.scalars().all()]


@router.post(
    "/triggers",
    response_model=TicketTriggerResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
async def create_trigger(
    request: Request,
    data: TicketTriggerCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TicketTriggerResponse:
    """Erstellt eine neue Automatisierungsregel."""
    _require_vermieter(user)
    trigger = TicketTrigger(
        vermieter_id=user.id,
        name=data.name,
        trigger_type=data.trigger_type,
        condition=data.condition,
        perform=data.perform,
        is_active=data.is_active,
    )
    db.add(trigger)
    await db.flush()
    await db.refresh(trigger)
    return _to_trigger_response(trigger)


@router.patch(
    "/triggers/{trigger_id}",
    response_model=TicketTriggerResponse,
    dependencies=[Depends(csrf_protect)],
)
async def update_trigger(
    request: Request,
    trigger_id: int,
    data: TicketTriggerUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TicketTriggerResponse:
    """Aktualisiert eine Automatisierungsregel."""
    _require_vermieter(user)
    trigger = await db.get(TicketTrigger, trigger_id)
    if trigger is None or trigger.vermieter_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trigger nicht gefunden",
        )

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(trigger, key, value)

    await db.flush()
    await db.refresh(trigger)
    return _to_trigger_response(trigger)


@router.delete(
    "/triggers/{trigger_id}",
    response_model=MessageResponse,
    dependencies=[Depends(csrf_protect)],
)
async def delete_trigger(
    request: Request,
    trigger_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MessageResponse:
    """Löscht eine Automatisierungsregel."""
    _require_vermieter(user)
    trigger = await db.get(TicketTrigger, trigger_id)
    if trigger is None or trigger.vermieter_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trigger nicht gefunden",
        )
    await db.delete(trigger)
    await db.flush()
    return MessageResponse(message="Trigger gelöscht")
