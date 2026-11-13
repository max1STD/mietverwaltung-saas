"""Auth-Routen: Registrierung, Login, 2FA, Refresh, Logout, Passwort-Reset, Profil."""
from __future__ import annotations

import secrets
from typing import Any

import pyotp
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import (
    _get_client_ip,
    csrf_protect,
    get_current_user,
    require_role,
    set_rls_context,
    to_user_response,
)
from app.models.session import UserSession
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    PasswordResetResponse,
    Pre2FAResponse,
    RegisterRequest,
    SessionResponse,
    TokenResponse,
    TwoFactorSetupRequest,
    TwoFactorSetupResponse,
    TwoFactorVerifyRequest,
    UserPasswordChangeRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.services.auth import (
    AuthError,
    change_password,
    confirm_password_reset,
    create_refresh_session,
    login_step,
    register,
    request_password_reset,
    revoke_session,
    rotate_refresh_token,
    setup_2fa,
    update_user_profile,
    verify_2fa,
)
from app.services.jwt import (
    REFRESH_COOKIE,
    TEMP_COOKIE,
    clear_auth_cookies,
    create_access_token,
    create_temp_token,
    get_cookie_token,
    get_csrf_token,
    set_auth_cookies,
    set_temp_cookie,
    verify_temp_token,
)
from app.services.rate_limit import RateLimitExceeded, check_rate_limit, reset_rate_limit

router = APIRouter()


def _generate_csrf() -> str:
    return secrets.token_urlsafe(32)


def _ensure_temp_payload(request: Request) -> dict[str, Any]:
    token = get_cookie_token(request, TEMP_COOKIE)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="2FA-Setup erfordert vorherigen Login",
        )
    payload = verify_temp_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Temporäres Token abgelaufen",
        )
    return payload


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_route(
    request: Request,
    data: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Registriert einen neuen Vermieter-Account."""
    try:
        await check_rate_limit("register", _get_client_ip(request))
        user = await register(
            db,
            data.email,
            data.password,
            data.full_name,
            data.consent_text,
            request=request,
        )
        await db.commit()
        # CSRF-Cookie für nachfolgende Login-Anfragen setzen.
        response.set_cookie(
            key="csrf_token",
            value=_generate_csrf(),
            httponly=False,
            secure=False,
            samesite="lax",
            max_age=60 * 60 * 24 * 7,
            path="/",
        )
        return await to_user_response(user)
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Zu viele Versuche. Bitte in {exc.retry_after} Sekunden erneut versuchen.",
            headers={"Retry-After": str(exc.retry_after)},
        ) from exc
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post("/login")
async def login_route(
    request: Request,
    data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse | Pre2FAResponse:
    """Login-Schritt 1: Passwort prüfen, ggf. 2FA anfordern."""
    ip = _get_client_ip(request)
    try:
        user, requires_2fa = await login_step(db, data.email, data.password, ip)
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Zu viele Login-Versuche",
            headers={"Retry-After": str(exc.retry_after)},
        ) from exc
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    temp_token = create_temp_token(user.id)
    set_temp_cookie(response, temp_token)

    if not requires_2fa:
        # Noch kein TOTP eingerichtet → Setup erzwingen.
        return Pre2FAResponse(requires_2fa=True, temp_token=temp_token)

    return Pre2FAResponse(requires_2fa=True, temp_token=temp_token)


@router.post("/2fa/setup", dependencies=[Depends(csrf_protect)])
async def two_fa_setup(
    request: Request,
    response: Response,
    _body: TwoFactorSetupRequest = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TwoFactorSetupResponse:
    """TOTP-Secret und Backup-Codes generieren (benötigt temp Token)."""
    payload = _ensure_temp_payload(request)
    try:
        user, secret, backup_codes, otpauth_uri = await setup_2fa(db, payload)
        await db.commit()
        return TwoFactorSetupResponse(
            secret=secret,
            backup_codes=backup_codes,
            otpauth_uri=otpauth_uri,
        )
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


@router.post("/2fa/verify", dependencies=[Depends(csrf_protect)])
async def two_fa_verify(
    request: Request,
    data: TwoFactorVerifyRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """TOTP oder Backup-Code validieren und finale Tokens ausstellen."""
    payload = _ensure_temp_payload(request)
    ip = _get_client_ip(request)
    try:
        user = await verify_2fa(db, payload, code=data.code, ip=ip)
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    # Finale Session anlegen.
    refresh_plain = secrets.token_urlsafe(48)
    session = await create_refresh_session(
        db,
        user,
        refresh_plain,
        ip,
        request.headers.get("user-agent"),
    )
    access_token = create_access_token(
        user.id,
        user.role,
        user.vermieter_id if user.role == "mieter" else user.id,
    )
    csrf_token = _generate_csrf()
    set_auth_cookies(response, access_token, refresh_plain, csrf_token)
    await reset_rate_limit("login", ip)
    await db.commit()
    return TokenResponse(access_token=access_token, user=await to_user_response(user))


@router.post("/refresh", dependencies=[Depends(csrf_protect)])
async def refresh_route(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Refresh-Token rotieren und neue Access/Refresh-Cookies ausstellen."""
    old_token = get_cookie_token(request, REFRESH_COOKIE)
    if not old_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kein Refresh-Token vorhanden",
        )
    try:
        user, new_refresh, _session_id = await rotate_refresh_token(
            db,
            old_token,
            _get_client_ip(request),
            request.headers.get("user-agent"),
        )
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    access_token = create_access_token(
        user.id,
        user.role,
        user.vermieter_id if user.role == "mieter" else user.id,
    )
    csrf_token = _generate_csrf()
    set_auth_cookies(response, access_token, new_refresh, csrf_token)
    await db.commit()
    return TokenResponse(access_token=access_token, user=await to_user_response(user))


@router.post("/logout", dependencies=[Depends(csrf_protect)])
async def logout_route(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MessageResponse:
    """Aktuelle Session widerrufen und Cookies löschen."""
    refresh_token = get_cookie_token(request, REFRESH_COOKIE)
    if refresh_token:
        result = await db.execute(
            select(UserSession).where(
                UserSession.refresh_token == refresh_token,
                UserSession.user_id == user.id,
                UserSession.revoked_at.is_(None),
            )
        )
        session = result.scalar_one_or_none()
        if session:
            from datetime import UTC, datetime

            session.revoked_at = datetime.now(UTC)
    else:
        # Refresh-Cookie hat path=/api/v1/auth/refresh und wird nicht
        # an /logout gesendet. Alle aktiven Sessions des Users widerrufen.
        from datetime import UTC, datetime

        result = await db.execute(
            select(UserSession).where(
                UserSession.user_id == user.id,
                UserSession.revoked_at.is_(None),
            )
        )
        for session in result.scalars().all():
            session.revoked_at = datetime.now(UTC)
    clear_auth_cookies(response)
    await db.commit()
    return MessageResponse(message="Ausgeloggt")


@router.post("/password-reset", dependencies=[Depends(csrf_protect)])
async def password_reset_route(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> PasswordResetResponse:
    """Passwort-Reset: Anforderung oder Bestätigung (zweistufig)."""
    body = await request.json()
    ip = _get_client_ip(request)

    if "new_password" in body and "code" in body:
        # Bestätigungs-Schritt
        data = PasswordResetConfirm(**body)
        request.state.password_reset_action = "password_reset_confirm"
        success = await confirm_password_reset(
            db,
            data.email,
            data.code,
            data.new_password,
            ip,
        )
        await db.commit()
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ungültiger Code oder abgelaufen",
            )
        return PasswordResetResponse(message="Passwort zurückgesetzt")

    # Anforderungs-Schritt
    data = PasswordResetRequest(**body)
    request.state.password_reset_action = "password_reset_request"
    try:
        await check_rate_limit("password_reset", ip)
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Zu viele Versuche",
            headers={"Retry-After": str(exc.retry_after)},
        ) from exc

    # Code wird nur intern zurückgegeben (in echter App per E-Mail versenden).
    code = await request_password_reset(db, data.email, ip)
    await db.commit()
    # Demo/Tests: Code in Response zurückgeben, in Produktion entfernen.
    detail = {"code": code} if code else {}
    return PasswordResetResponse(message="Wenn die E-Mail existiert, wurde ein Code versandt.")


@router.get("/sessions")
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[SessionResponse]:
    """Liste aller aktiven Sessions des eingeloggten Users."""
    result = await db.execute(
        select(UserSession).where(
            UserSession.user_id == user.id,
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        )
    )
    sessions = result.scalars().all()
    return [
        SessionResponse(
            id=s.id,
            device_info=s.device_info,
            ip_address=s.ip_address,
            created_at=s.created_at.isoformat() if s.created_at else None,
            expires_at=s.expires_at.isoformat() if s.expires_at else None,
        )
        for s in sessions
    ]


@router.delete("/sessions/{session_id}", dependencies=[Depends(csrf_protect)])
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MessageResponse:
    """Widerruft eine bestimmte Session (Geräte-Logout)."""
    await revoke_session(db, user, session_id)
    await db.commit()
    return MessageResponse(message="Session widerrufen")


@router.get("/users/me")
async def get_me(user: User = Depends(get_current_user)) -> UserResponse:
    """Gibt das eigene Profil zurück."""
    return await to_user_response(user)


@router.patch("/users/me", dependencies=[Depends(csrf_protect)])
async def update_me(
    data: UserUpdateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> UserResponse:
    """Aktualisiert das eigene Profil."""
    update_data = data.model_dump(exclude_unset=True)
    updated = await update_user_profile(
        db,
        user,
        update_data,
        _get_client_ip(request),
    )
    await db.commit()
    return await to_user_response(updated)


@router.post("/users/me/password", dependencies=[Depends(csrf_protect)])
async def change_password_route(
    data: UserPasswordChangeRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MessageResponse:
    """Passwort ändern (alle Sessions werden ausgeloggt)."""
    ok = await change_password(
        db,
        user,
        data.old_password,
        data.new_password,
        _get_client_ip(request),
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Altes Passwort ist falsch",
        )
    clear_auth_cookies(response)
    await db.commit()
    return MessageResponse(message="Passwort geändert. Bitte erneut einloggen.")


# Vermieter-Account anlegen (nur Admins).
@router.post("/admin/users", dependencies=[Depends(require_role("admin"))])
async def create_user_admin() -> dict:
    return {"message": "Nur Platzhalter für Admin-Center"}
