"""Auth-Service: Registrierung, Login, 2FA, Refresh, Logout, Passwort-Reset."""
from __future__ import annotations

import random
import secrets
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import pyotp
from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.middleware.auth import set_rls_context
from app.models.audit import AuditLog
from app.models.einwilligung import Einwilligung
from app.models.session import UserSession
from app.models.user import User
from app.services.billing import is_subscription_expired
from app.services.crypto import encrypt_value
from app.services.rate_limit import check_rate_limit, record_failed_attempt

if TYPE_CHECKING:
    from fastapi import Request

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
    type=Type.ID,
)


class AuthError(Exception):
    """Generischer Auth-Fehler ohne interne Details preiszugeben."""

    pass


def hash_password(password: str) -> str:
    """Hasht ein Passwort mit Argon2id."""
    return ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Prüft ein Passwort gegen einen Argon2id-Hash."""
    try:
        ph.verify(password_hash, password)
    except VerifyMismatchError:
        return False
    # Rehashen falls Parameter aktualisiert wurden.
    if ph.check_needs_rehash(password_hash):
        # In echter Anwendung: Hash in DB aktualisieren.
        pass
    return True


def generate_backup_codes(count: int = 8) -> list[str]:
    """Erzeugt 8 alphanumerische Einmal-Backup-Codes."""
    return [secrets.token_hex(4).upper() for _ in range(count)]


def generate_email_code() -> str:
    """Erzeugt einen 6-stelligen numerischen E-Mail-Code."""
    return f"{random.randint(0, 999_999):06d}"


def verify_totp(secret: str, code: str) -> bool:
    """Validiert einen TOTP-Code mit Zeit-Toleranz."""
    if not secret or not code:
        return False
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


def generate_totp_secret() -> str:
    """Erzeugt ein neues TOTP-Geheimnis."""
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str, issuer: str = "MietVerwaltung") -> str:
    """Gibt den otpauth:// URI für Authenticator-Apps zurück."""
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)


async def _get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User)
        .options(selectinload(User.subscription))
        .where(
            User.email.ilike(email),
            User.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def _is_account_locked(user: User) -> bool:
    return bool(user.locked_until and user.locked_until > datetime.now(UTC))


async def _audit(
    db: AsyncSession,
    user_id: int | None,
    action: str,
    vermieter_id: int | None = None,
    details: dict | None = None,
    ip: str | None = None,
    risk_level: str = "niedrig",
    entity: str | None = None,
    entity_id: int | None = None,
) -> None:
    """Schreibt einen Audit-Log-Eintrag."""
    log = AuditLog(
        user_id=user_id,
        vermieter_id=vermieter_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        risk_level=risk_level,
        details=details or {},
        ip_address=ip,
    )
    db.add(log)


async def register(
    db: AsyncSession,
    email: str,
    password: str,
    full_name: str,
    consent_text: str,
    request: Request | None = None,
) -> User:
    """Registriert einen neuen Vermieter-Account."""
    # RLS deaktivieren für System-Operation (kein eingeloggter User vorhanden).
    from app.middleware.auth import set_system_rls_context
    await set_system_rls_context(db)

    existing = await _get_user_by_email(db, email)
    if existing:
        raise AuthError("E-Mail-Adresse bereits registriert")

    user = User(
        email=email.lower().strip(),
        password_hash=hash_password(password),
        full_name=full_name.strip(),
        role="vermieter",
        is_active=True,
        email_verified=False,
        dsgvo_consent_at=datetime.now(UTC),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # RLS-Kontext für nachfolgende Inserts setzen.
    await set_rls_context(db, user)

    # DSGVO-Einwilligung versioniert speichern.
    einwilligung = Einwilligung(
        user_id=user.id,
        purpose="dsgvo_terms",
        consent_text=consent_text,
        consented_at=datetime.now(UTC),
        ip_address=request.client.host if request and request.client else None,
    )
    db.add(einwilligung)

    # Standard-Kostenkategorien für den neuen Vermieter anlegen.
    from app.services.kosten import get_or_create_default_kategorien
    await get_or_create_default_kategorien(db, vermieter_id=user.id)

    await _audit(
        db,
        user_id=user.id,
        action="register",
        vermieter_id=user.id,
        details={"email": email},
        ip=request.client.host if request and request.client else None,
        risk_level="mittel",
        entity="users",
        entity_id=user.id,
    )
    return user


async def login_step(
    db: AsyncSession,
    email: str,
    password: str,
    ip: str | None = None,
) -> tuple[User, bool]:
    """Erster Login-Schritt: Passwort prüfen, ggf. 2FA anfordern.

    Returns:
        (user, requires_2fa): Wenn requires_2fa True, muss /2fa/verify folgen.
    """
    # RLS deaktivieren für System-Operation (kein eingeloggter User vorhanden).
    from app.middleware.auth import set_system_rls_context
    await set_system_rls_context(db)

    await check_rate_limit("login", ip or "unknown")

    user = await _get_user_by_email(db, email)
    if user is None:
        # Gleiche Zeit verschwenden wie bei korrektem User (Timing).
        ph.hash("dummy")
        raise AuthError("Ungültige Anmeldedaten")

    if not user.is_active:
        raise AuthError("Account ist deaktiviert")

    if await _is_account_locked(user):
        raise AuthError("Account vorübergehend gesperrt")

    if user.role == "vermieter" and is_subscription_expired(user.subscription):
        raise AuthError("Abonnement abgelaufen. Bitte erneuere dein Abo, um fortzufahren.")

    # RLS-Kontext setzen, bevor User-Zeile verändert oder Audit geschrieben wird.
    await set_rls_context(db, user)

    if not verify_password(password, user.password_hash):
        user.failed_login_count += 1
        if user.failed_login_count >= 5:
            user.locked_until = datetime.now(UTC) + timedelta(minutes=15)
        raise AuthError("Ungültige Anmeldedaten")

    # Erfolgreicher Passwort-Check: Zähler zurücksetzen.
    user.failed_login_count = 0
    user.locked_until = None

    # 2FA erforderlich, wenn TOTP-Secret hinterlegt ist.
    requires_2fa = bool(user.totp_secret)

    await _audit(
        db,
        user_id=user.id,
        action="login_step_password",
        vermieter_id=user.vermieter_id if user.role == "mieter" else user.id,
        details={"requires_2fa": requires_2fa, "ip": ip},
        ip=ip,
        risk_level="mittel" if requires_2fa else "niedrig",
        entity="users",
        entity_id=user.id,
    )
    return user, requires_2fa


async def setup_2fa(
    db: AsyncSession,
    temp_payload: dict,
) -> tuple[User, str, list[str], str]:
    """Richtet TOTP für einen frisch authentifizierten User ein.

    Returns:
        (user, secret, backup_codes, otpauth_uri)
    """
    user_id = int(temp_payload["sub"])
    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise AuthError("Ungültige Sitzung")

    secret = generate_totp_secret()
    backup_codes = generate_backup_codes()
    user.totp_secret = secret
    user.backup_codes = backup_codes

    await set_rls_context(db, user)
    await _audit(
        db,
        user_id=user.id,
        action="2fa_setup",
        vermieter_id=user.vermieter_id if user.role == "mieter" else user.id,
        entity="users",
        entity_id=user.id,
        risk_level="hoch",
    )
    await db.flush()
    return user, secret, backup_codes, get_totp_uri(secret, user.email)


async def verify_2fa(
    db: AsyncSession,
    temp_payload: dict,
    code: str | None = None,
    email_fallback: bool = False,
    ip: str | None = None,
) -> User:
    """Validiert TOTP oder E-Mail-Code und schließt Login ab."""
    user_id = int(temp_payload["sub"])
    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise AuthError("Ungültige Sitzung")

    verified = False
    method: str | None = None

    if code and user.totp_secret and verify_totp(user.totp_secret, code):
        verified = True
        method = "totp"
    elif code and user.email_code and user.email_code_expires_at and (
        user.email_code == code
        and user.email_code_expires_at > datetime.now(UTC)
    ):
        verified = True
        method = "email_code"

    if not verified:
        await record_failed_attempt("2fa", ip or "unknown")
        raise AuthError("Ungültiger oder abgelaufener 2FA-Code")

    # E-Mail-Code nach erfolgreicher Verwendung invalidieren.
    if method == "email_code":
        user.email_code = None
        user.email_code_expires_at = None

    await set_rls_context(db, user)
    await _audit(
        db,
        user_id=user.id,
        action="2fa_verify",
        vermieter_id=user.vermieter_id if user.role == "mieter" else user.id,
        details={"method": method, "ip": ip},
        ip=ip,
        risk_level="niedrig",
        entity="users",
        entity_id=user.id,
    )
    return user


async def create_refresh_session(
    db: AsyncSession,
    user: User,
    refresh_token_plain: str,
    ip: str | None,
    device_info: str | None,
) -> UserSession:
    """Legt eine neue Refresh-Session in der Datenbank an."""
    session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token_plain,
        ip_address=ip,
        device_info=device_info,
        expires_at=datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS),
    )
    db.add(session)
    await db.flush()
    return session


async def rotate_refresh_token(
    db: AsyncSession,
    old_token: str,
    ip: str | None,
    device_info: str | None,
) -> tuple[User, str, int]:
    """Rotiert ein Refresh-Token: altes widerrufen, neues ausstellen."""
    result = await db.execute(
        select(UserSession).where(
            UserSession.refresh_token == old_token,
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > datetime.now(UTC),
        )
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise AuthError("Ungültiges oder abgelaufenes Refresh-Token")

    user = await db.get(User, session.user_id)
    if user is None or not user.is_active:
        raise AuthError("Account ungültig")

    # Altes Token widerrufen.
    session.revoked_at = datetime.now(UTC)

    new_token = secrets.token_urlsafe(48)
    new_session = await create_refresh_session(db, user, new_token, ip, device_info)

    await set_rls_context(db, user)
    await _audit(
        db,
        user_id=user.id,
        action="refresh_token_rotate",
        vermieter_id=user.vermieter_id if user.role == "mieter" else user.id,
        details={"session_id": new_session.id, "old_session_id": session.id},
        ip=ip,
        risk_level="niedrig",
        entity="user_sessions",
        entity_id=new_session.id,
    )
    return user, new_token, new_session.id


async def revoke_session(db: AsyncSession, user: User, session_id: int) -> None:
    """Widerruft eine einzelne Session eines Users."""
    result = await db.execute(
        select(UserSession).where(
            UserSession.id == session_id,
            UserSession.user_id == user.id,
            UserSession.revoked_at.is_(None),
        )
    )
    session = result.scalar_one_or_none()
    if session:
        session.revoked_at = datetime.now(UTC)


async def logout_all_sessions(db: AsyncSession, user: User) -> None:
    """Widerruft alle offenen Sessions eines Users."""
    await db.execute(
        select(UserSession).where(
            UserSession.user_id == user.id,
            UserSession.revoked_at.is_(None),
        )
    )
    # Batch-Update via SQL.
    from sqlalchemy import update

    await db.execute(
        update(UserSession)
        .where(
            UserSession.user_id == user.id,
            UserSession.revoked_at.is_(None),
        )
        .values(revoked_at=datetime.now(UTC))
    )


async def request_password_reset(
    db: AsyncSession,
    email: str,
    ip: str | None = None,
) -> str | None:
    """Erzeugt einen 15-minütigen E-Mail-Code für Passwort-Reset.

    Gibt den Code nur bei existierendem User zurück (keine Offenlegung).
    """
    # RLS deaktivieren für System-Operation (kein eingeloggter User vorhanden).
    from app.middleware.auth import set_system_rls_context
    await set_system_rls_context(db)

    await check_rate_limit("password_reset", ip or "unknown")

    user = await _get_user_by_email(db, email)
    if user is None or not user.is_active:
        return None

    code = generate_email_code()
    user.email_code = code
    user.email_code_expires_at = datetime.now(UTC) + timedelta(minutes=15)

    await set_rls_context(db, user)
    await _audit(
        db,
        user_id=user.id,
        action="password_reset_request",
        vermieter_id=user.vermieter_id if user.role == "mieter" else user.id,
        ip=ip,
        risk_level="mittel",
        entity="users",
        entity_id=user.id,
    )
    return code


async def confirm_password_reset(
    db: AsyncSession,
    email: str,
    code: str,
    new_password: str,
    ip: str | None = None,
) -> bool:
    """Setzt das Passwort zurück, wenn der Code gültig ist."""
    # RLS deaktivieren für System-Operation.
    from app.middleware.auth import set_system_rls_context
    await set_system_rls_context(db)

    user = await _get_user_by_email(db, email)
    if user is None or not user.is_active:
        return False

    if (
        not user.email_code
        or user.email_code != code
        or not user.email_code_expires_at
        or user.email_code_expires_at <= datetime.now(UTC)
    ):
        return False

    user.password_hash = hash_password(new_password)
    user.email_code = None
    user.email_code_expires_at = None
    user.failed_login_count = 0
    user.locked_until = None

    # Alle bestehenden Sessions invalidieren = sicher.
    await logout_all_sessions(db, user)

    await set_rls_context(db, user)
    await _audit(
        db,
        user_id=user.id,
        action="password_reset_confirm",
        vermieter_id=user.vermieter_id if user.role == "mieter" else user.id,
        ip=ip,
        risk_level="hoch",
        entity="users",
        entity_id=user.id,
    )
    return True


async def update_user_profile(
    db: AsyncSession,
    user: User,
    data: dict,
    ip: str | None = None,
) -> User:
    """Aktualisiert das eigene Profil (Name, Telefon, Vermieter-Stammdaten)."""
    allowed_fields = {
        "full_name",
        "phone",
        "firma",
        "rechnungs_strasse",
        "rechnungs_hausnr",
        "rechnungs_plz",
        "rechnungs_ort",
        "ust_id",
    }
    changed: dict[str, str | None] = {}
    for field in allowed_fields:
        if field in data:
            old = getattr(user, field)
            new = data[field]
            setattr(user, field, new)
            if old != new:
                changed[field] = "changed"

    # Steuernummer separat verschlüsseln.
    if "steuernr" in data:
        old_enc = user.steuernr_enc
        user.steuernr_enc = encrypt_value(data["steuernr"], context="users:steuernr")
        changed["steuernr"] = "changed" if old_enc != user.steuernr_enc else None

    await set_rls_context(db, user)
    await _audit(
        db,
        user_id=user.id,
        action="profile_update",
        vermieter_id=user.vermieter_id if user.role == "mieter" else user.id,
        details={"changed": changed, "ip": ip},
        ip=ip,
        risk_level="niedrig",
        entity="users",
        entity_id=user.id,
    )
    return user


async def change_password(
    db: AsyncSession,
    user: User,
    old_password: str,
    new_password: str,
    ip: str | None = None,
) -> bool:
    """Ändert das Passwort nach Prüfung des alten Passworts."""
    if not verify_password(old_password, user.password_hash):
        return False
    user.password_hash = hash_password(new_password)
    await logout_all_sessions(db, user)
    await set_rls_context(db, user)
    await _audit(
        db,
        user_id=user.id,
        action="password_change",
        vermieter_id=user.vermieter_id if user.role == "mieter" else user.id,
        ip=ip,
        risk_level="hoch",
        entity="users",
        entity_id=user.id,
    )
    return True
