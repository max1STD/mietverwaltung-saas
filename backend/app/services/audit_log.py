"""Audit-Log-Hilfsfunktion für Geschäftslogik-Services."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


async def audit_log(
    db: AsyncSession,
    user_id: int | None,
    vermieter_id: int | None,
    action: str,
    entity: str,
    entity_id: int | None = None,
    details: dict[str, Any] | None = None,
    ip: str | None = None,
    risk_level: str = "niedrig",
) -> None:
    """Schreibt einen Audit-Log-Eintrag für Geschäfts-CRUD-Operationen."""
    log = AuditLog(
        user_id=user_id,
        vermieter_id=vermieter_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        risk_level=risk_level,
        details=details or {},
        ip_address=ip,
        created_at=datetime.now(UTC),
    )
    db.add(log)
