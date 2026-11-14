"""Health check route — prüft DB, Redis und App-Status.

Gibt detaillierten Status zurück für Monitoring und Deploy-Health-Checks.
"""
from datetime import UTC, datetime

import redis.asyncio as aioredis
from fastapi import APIRouter
from sqlalchemy import text

from app.config import settings
from app.database import async_session

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Health-Check: App + Datenbank + Redis.

    Returns:
        dict mit Status je Komponente und Timestamp.
    """
    checks: dict[str, str] = {}
    overall = "ok"

    # ── Datenbank ──
    try:
        async with async_session() as session:
            result = await session.execute(text("SELECT 1"))
            result.fetchone()
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e!s}"
        overall = "degraded"

    # ── Redis ──
    try:
        r = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        await r.ping()
        await r.aclose()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e!s}"
        overall = "degraded"

    return {
        "status": overall,
        "checks": checks,
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(UTC).isoformat(),
    }
