"""DB-Kontext für Mandantentrennung via SET LOCAL.

Statt session-weit `row_security = off` zu setzen, wird pro Transaktion
`SET LOCAL app.org_id`, `app.user_id`, `app.rolle` gesetzt. So leakt der
Kontext nicht bei gepoolten Connections in den nächsten Request.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    pass


class DbContext:
    """Hält den aktuellen Sicherheitskontext für RLS."""

    def __init__(
        self,
        org_id: int | None = None,
        user_id: int | None = None,
        role: str | None = None,
        mitglied_id: int | None = None,
        mieter_id: int | None = None,
        handwerker_firma_id: int | None = None,
    ):
        self.org_id = org_id
        self.user_id = user_id
        self.role = role
        self.mitglied_id = mitglied_id
        self.mieter_id = mieter_id
        self.handwerker_firma_id = handwerker_firma_id


async def set_db_context(
    session: AsyncSession,
    context: DbContext,
) -> None:
    """Setzt den RLS-Kontext LOCAL in der aktuellen Transaktion."""
    values = [
        ("app.org_id", context.org_id),
        ("app.user_id", context.user_id),
        ("app.rolle", context.role),
        ("app.mitglied_id", context.mitglied_id),
        ("app.mieter_id", context.mieter_id),
        ("app.handwerker_firma_id", context.handwerker_firma_id),
    ]
    for name, value in values:
        if value is None:
            await session.execute(text(f"SET LOCAL {name} = ''"))
        else:
            await session.execute(text(f"SET LOCAL {name} = '{str(value).replace(chr(39), chr(39)+chr(39))}'"))


@asynccontextmanager
async def db_context_scope(
    session: AsyncSession,
    context: DbContext,
):
    """Kontextmanager, der den RLS-Kontext setzt und am Ende zurücksetzt."""
    await set_db_context(session, context)
    try:
        yield session
    finally:
        await session.execute(text("SET LOCAL app.org_id = ''"))
        await session.execute(text("SET LOCAL app.user_id = ''"))
        await session.execute(text("SET LOCAL app.rolle = ''"))
        await session.execute(text("SET LOCAL app.mitglied_id = ''"))
        await session.execute(text("SET LOCAL app.mieter_id = ''"))
        await session.execute(text("SET LOCAL app.handwerker_firma_id = ''"))
