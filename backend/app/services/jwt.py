"""JWT-Erzeugung, -Validierung und Cookie-Handling."""
from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt as pyjwt
from fastapi import Request, Response

from app.config import settings

ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"
TEMP_COOKIE = "temp_token"  # Pre-2FA
CSRF_COOKIE = "csrf_token"


def _now() -> datetime:
    return datetime.now(UTC)


def _encode(payload: dict[str, Any], expires: datetime) -> str:
    payload["exp"] = int(expires.timestamp())
    payload["iat"] = int(_now().timestamp())
    payload["jti"] = secrets.token_urlsafe(16)
    # PyJWT erwartet 'sub' als String.
    if "sub" in payload:
        payload["sub"] = str(payload["sub"])
    if "vermieter_id" in payload and payload["vermieter_id"] is not None:
        payload["vermieter_id"] = str(payload["vermieter_id"])
    return pyjwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def _decode(token: str) -> dict[str, Any]:
    return pyjwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
        options={"require": ["exp", "iat"]},
    )


def create_access_token(user_id: int, role: str, vermieter_id: int | None) -> str:
    """Erstellt ein 15-minütiges Access-Token."""
    expires = _now() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    return _encode(
        {
            "sub": user_id,
            "role": role,
            "vermieter_id": vermieter_id,
            "type": "access",
        },
        expires,
    )


def create_temp_token(user_id: int) -> str:
    """Erstellt ein kurzlebiges Token für den 2FA-Setup/Verify-Schritt."""
    expires = _now() + timedelta(minutes=10)
    return _encode(
        {
            "sub": user_id,
            "type": "temp",
        },
        expires,
    )


def verify_access_token(token: str) -> dict[str, Any] | None:
    """Validiert ein Access-Token und gibt Payload zurück oder None."""
    try:
        payload = _decode(token)
    except pyjwt.PyJWTError:
        return None
    if payload.get("type") != "access":
        return None
    return payload


def verify_temp_token(token: str) -> dict[str, Any] | None:
    """Validiert ein temporäres 2FA-Token."""
    try:
        payload = _decode(token)
    except pyjwt.PyJWTError:
        return None
    if payload.get("type") != "temp":
        return None
    return payload


def _cookie_secure(request: Request | None = None) -> bool:
    """Gibt zurück, ob Cookies das Secure-Flag gesetzt bekommen sollen.

    - Wenn X-Forwarded-Proto == https, setzen wir Secure (Cloudflare-Tunnel etc.).
    - In Produktion immer True.
    - Lokal bei HTTP bleibt es False.
    """
    if request is not None:
        forwarded_proto = request.headers.get("x-forwarded-proto")
        if forwarded_proto and forwarded_proto.lower() == "https":
            return True
    return settings.ENVIRONMENT.lower() == "production"


def _cookie_host(request: Request | None = None) -> str | None:
    """Bestimmt den Domain-/Host-Wert für Cookies."""
    return None  # Default: Cookie gilt für die aktuelle Domain


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
    csrf_token: str,
    remember_me: bool = True,
    request: Request | None = None,
) -> None:
    """Setzt HTTP-only Secure SameSite=Lax Cookies für Tokens und CSRF.

    Args:
        remember_me: Wenn True (Default), wird das Refresh-Cookie mit 30 Tagen
            Lebensdauer gesetzt, damit der Nutzer auch nach Browser-Neustart
            eingeloggt bleibt.
    """
    secure = _cookie_secure(request)
    access_max_age = int(timedelta(hours=24).total_seconds())
    refresh_max_age = int(timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS).total_seconds())
    response.set_cookie(
        key=ACCESS_COOKIE,
        value=access_token,
        httponly=True,
        secure=secure,
        samesite="Lax",
        max_age=access_max_age,
        path="/",
    )
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=secure,
        samesite="Lax",
        max_age=refresh_max_age,
        path="/api/v1/auth/refresh",
    )
    # CSRF-Cookie darf nicht HTTP-only sein, damit JS es lesen kann.
    response.set_cookie(
        key=CSRF_COOKIE,
        value=csrf_token,
        httponly=False,
        secure=secure,
        samesite="Lax",
        max_age=refresh_max_age,
        path="/",
    )


def set_temp_cookie(response: Response, temp_token: str) -> None:
    """Setzt das kurzlebige Pre-2FA Cookie."""
    response.set_cookie(
        key=TEMP_COOKIE,
        value=temp_token,
        httponly=True,
        secure=_cookie_secure(),
        samesite="Lax",
        max_age=60 * 10,
        path="/api/v1/auth/2fa",
    )


def clear_auth_cookies(response: Response) -> None:
    """Entfernt alle Auth-Cookies."""
    secure = _cookie_secure()
    response.delete_cookie(key=ACCESS_COOKIE, path="/", secure=secure, samesite="lax", httponly=True)
    response.delete_cookie(key=REFRESH_COOKIE, path="/api/v1/auth/refresh", secure=secure, samesite="lax", httponly=True)
    response.delete_cookie(key=TEMP_COOKIE, path="/api/v1/auth/2fa", secure=secure, samesite="lax", httponly=True)
    response.delete_cookie(key=CSRF_COOKIE, path="/", secure=secure, samesite="lax", httponly=False)


def get_cookie_token(request: Request, name: str) -> str | None:
    return request.cookies.get(name)


def get_csrf_token(request: Request) -> str | None:
    return request.cookies.get(CSRF_COOKIE)
