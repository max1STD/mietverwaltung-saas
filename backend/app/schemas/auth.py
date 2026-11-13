"""Pydantic-Schemas für Auth-Endpunkte."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """Registrierung eines neuen Vermieter-Accounts."""

    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)
    consent_text: str = Field(..., min_length=20)


class LoginRequest(BaseModel):
    """Login mit E-Mail und Passwort."""

    email: EmailStr
    password: str


class TwoFactorSetupRequest(BaseModel):
    """Startet TOTP-Setup (benötigt temporäres Post-Login-Token)."""

    # Der temporäre Token wird via Cookie übermittelt; Body ist leer.
    pass


class TwoFactorVerifyRequest(BaseModel):
    """Abschluss des Logins via TOTP oder E-Mail-Code."""

    code: str = Field(..., min_length=6, max_length=10)


class PasswordResetRequest(BaseModel):
    """Anforderung eines Passwort-Reset-Codes."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Bestätigung des Passwort-Resets mit Code und neuem Passwort."""

    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=12, max_length=128)


class UserResponse(BaseModel):
    """Öffentliche User-Daten."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str
    phone: str | None = None
    email_verified: bool
    is_active: bool
    dsgvo_consent_at: str | None = None
    firma: str | None = None
    rechnungs_strasse: str | None = None
    rechnungs_hausnr: str | None = None
    rechnungs_plz: str | None = None
    rechnungs_ort: str | None = None
    ust_id: str | None = None


class TwoFactorSetupResponse(BaseModel):
    """TOTP-Secret und Backup-Codes für die Einrichtung."""

    secret: str
    backup_codes: list[str]
    otpauth_uri: str


class TokenResponse(BaseModel):
    """Antwort nach erfolgreichem Login/Refresh."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordResetResponse(BaseModel):
    """Status einer Passwort-Reset-Anforderung."""

    message: str


class UserUpdateRequest(BaseModel):
    """Erlaubte Felder für PATCH /users/me."""

    full_name: str | None = Field(None, min_length=2, max_length=100)
    phone: str | None = Field(None, max_length=30)
    firma: str | None = Field(None, max_length=200)
    rechnungs_strasse: str | None = Field(None, max_length=255)
    rechnungs_hausnr: str | None = Field(None, max_length=20)
    rechnungs_plz: str | None = Field(None, max_length=10)
    rechnungs_ort: str | None = Field(None, max_length=100)
    ust_id: str | None = Field(None, max_length=20)
    steuernr: str | None = Field(None, max_length=30)


class UserPasswordChangeRequest(BaseModel):
    """Passwort-Änderung im eingeloggten Zustand."""

    old_password: str
    new_password: str = Field(..., min_length=12, max_length=128)


class SessionResponse(BaseModel):
    """Eine aktive Session."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    device_info: str | None
    ip_address: str | None
    created_at: str
    expires_at: str


class ConsentRequest(BaseModel):
    """Neue oder aktualisierte Einwilligung."""

    purpose: str = Field(..., min_length=1, max_length=50)
    consent_text: str = Field(..., min_length=20)
    version: int = Field(default=1, ge=1)


class ConsentResponse(BaseModel):
    """Gespeicherte Einwilligung."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    purpose: str
    version: int
    consent_text: str
    consented_at: str
    withdrawn_at: str | None


class DsgvoOverviewResponse(BaseModel):
    """Zusammenfassung der gespeicherten Personendaten."""

    user: dict
    sessions_count: int
    einwilligungen_count: int
    audit_logs_count: int
    mietvertraege_count: int
    abrechnungen_count: int


class DsgvoExportResponse(BaseModel):
    """Datenexport nach Art. 15/20 DSGVO."""

    export_format: str = "json"
    exported_at: str
    data: dict


class DsgvoDeletionResponse(BaseModel):
    """Ergebnis eines Löschantrags."""

    deleted: bool
    message: str
    retained: list[dict] | None = None


class MessageResponse(BaseModel):
    """Generische Statusnachricht."""

    message: str


class Pre2FAResponse(BaseModel):
    """Zwischenantwort, wenn 2FA erforderlich ist."""

    requires_2fa: bool = True
    temp_token: str
