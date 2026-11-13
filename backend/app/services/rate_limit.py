"""Redis-basiertes Rate-Limiting für öffentliche Auth-Endpunkte."""
from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta
from typing import Any

import redis.asyncio as aioredis

from app.config import settings

WINDOW_SECONDS = 15 * 60  # 15 Minuten
MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 15 * 60


class RateLimitExceeded(Exception):
    """Wird geworfen, wenn ein Client das Limit überschreitet."""

    def __init__(self, retry_after: int, message: str = "Rate limit exceeded"):
        self.retry_after = retry_after
        super().__init__(message)


async def _get_redis() -> aioredis.Redis:
    return aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)


def _key(action: str, ip: str) -> str:
    return f"rl:{action}:{ip}"


def _lockout_key(action: str, ip: str) -> str:
    return f"rl:lockout:{action}:{ip}"


async def check_rate_limit(action: str, ip: str) -> None:
    """Prüft, ob ein IP-basiertes Rate-Limit überschritten ist.

    Erlaubt 5 Versuche pro 15 Minuten; nach Überschreitung 15 Minuten Sperre.
    """
    redis = await _get_redis()
    try:
        lockout_key = _lockout_key(action, ip)
        lockout_ttl = await redis.ttl(lockout_key)
        if lockout_ttl > 0:
            raise RateLimitExceeded(retry_after=lockout_ttl)

        key = _key(action, ip)
        current = int(await redis.incr(key))
        if current == 1:
            await redis.expire(key, WINDOW_SECONDS)

        ttl = await redis.ttl(key)
        ttl = max(ttl, 1)

        if current > MAX_ATTEMPTS:
            await redis.set(_lockout_key(action, ip), "1", ex=LOCKOUT_SECONDS)
            raise RateLimitExceeded(retry_after=LOCKOUT_SECONDS)
    finally:
        await redis.aclose()


async def record_failed_attempt(action: str, ip: str) -> None:
    """Zählt einen fehlgeschlagenen Versuch zusätzlich (z. B. falsches Passwort)."""
    redis = await _get_redis()
    try:
        key = _key(action, ip)
        current = int(await redis.incr(key))
        if current == 1:
            await redis.expire(key, WINDOW_SECONDS)
        if current > MAX_ATTEMPTS:
            await redis.set(_lockout_key(action, ip), "1", ex=LOCKOUT_SECONDS)
    finally:
        await redis.aclose()


async def reset_rate_limit(action: str, ip: str) -> None:
    """Löscht das Limit nach erfolgreicher Aktion."""
    redis = await _get_redis()
    try:
        await redis.delete(_key(action, ip), _lockout_key(action, ip))
    finally:
        await redis.aclose()
