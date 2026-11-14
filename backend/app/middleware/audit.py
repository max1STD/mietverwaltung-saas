"""Audit-Logging Middleware: protokolliert sicherheitsrelevante Auth-Aktionen."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import Request, Response
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.database import async_session
from app.middleware.auth import _get_client_ip, decode_access_cookie
from app.models.audit import AuditLog


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware, die Auth-Aktionen asynchron ins audit_logs schreibt."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
        response = await call_next(request)

        action = self._classify_action(request, response)
        if action:
            # Synchrones Logging, damit Audit-Einträge vor der Response persistiert sind.
            await self._log(request, response, action)

        return response

    def _classify_action(self, request: Request, response: Response) -> str | None:
        path = request.url.path
        method = request.method
        status_code = response.status_code

        if path == "/api/v1/auth/register" and method == "POST" and status_code < 400:
            return "register"
        if path == "/api/v1/auth/login" and method == "POST":
            return "login" if status_code < 400 else "login_failed"
        if path == "/api/v1/auth/2fa/setup" and method == "POST" and status_code < 400:
            return "2fa_setup"
        if path == "/api/v1/auth/2fa/verify" and method == "POST" and status_code < 400:
            return "2fa_verify"
        if path == "/api/v1/auth/refresh" and method == "POST":
            return "refresh" if status_code < 400 else "refresh_failed"
        if path == "/api/v1/auth/logout" and method == "POST" and status_code < 400:
            return "logout"
        if path == "/api/v1/auth/password-reset" and method == "POST":
            if status_code < 400:
                body = getattr(request.state, "password_reset_action", "password_reset")
                return body
            return "password_reset_failed"
        if path == "/api/v1/einwilligungen" and method == "POST" and status_code < 400:
            return "consent_change"
        if path == "/api/v1/users/me" and method == "PATCH" and status_code < 400:
            return "profile_update"
        if path.startswith("/api/v1/dsgvo/delete") and method == "DELETE" and status_code < 400:
            return "deletion_request"
        return None

    async def _log(
        self,
        request: Request,
        response: Response,
        action: str,
    ) -> None:
        try:
            payload = decode_access_cookie(request)
            user_id = int(payload.get("sub")) if payload else None
            role = payload.get("role") if payload else None
            vermieter_id_raw = payload.get("vermieter_id") if payload else None
            vermieter_id = int(vermieter_id_raw) if vermieter_id_raw is not None else None

            details: dict[str, Any] = {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
            }
            risk_level = "niedrig"
            if action in ("login_failed", "password_reset_failed", "2fa_setup"):
                risk_level = "mittel"
            if action in ("deletion_request", "password_reset_confirm"):
                risk_level = "hoch"

            async with async_session() as db:
                # RLS-Kontext für das Audit-Log setzen.
                user_id = int(payload.get("sub")) if payload else None
                role = payload.get("role") if payload else "anonymous"
                vermieter_id_raw = payload.get("vermieter_id") if payload else None
                vermieter_id = int(vermieter_id_raw) if vermieter_id_raw is not None else None
                if user_id is not None:
                    await db.execute(text(f"SET LOCAL app.current_user_id = '{user_id}'"))
                    await db.execute(text(f"SET LOCAL app.current_user_role = '{role}'"))
                    await db.execute(text(f"SET LOCAL app.current_vermieter_id = '{vermieter_id or user_id}'"))

                log = AuditLog(
                    user_id=user_id,
                    vermieter_id=vermieter_id,
                    action=action,
                    risk_level=risk_level,
                    details=details,
                    ip_address=_get_client_ip(request),
                )
                db.add(log)
                await db.commit()
        except Exception:
            # Audit-Logging darf den Request nicht zum Scheitern bringen.
            pass
