"""Schemas fuer Bankverbindungen."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BankverbindungBase(BaseModel):
    """Gemeinsame Felder fuer Bankverbindungen."""

    iban: str = Field(..., min_length=15, max_length=34, description="IBAN im Klartext (wird verschlüsselt gespeichert)")
    bic: str | None = Field(None, max_length=11, description="BIC (optional)")
    kontoinhaber: str = Field(..., max_length=100, description="Name des Kontoinhabers")
    bankname: str | None = Field(None, max_length=100, description="Name der Bank (optional)")
    is_default: bool = Field(False, description="Standard-Bankverbindung des Vermieters")
    mieter_id: int | None = Field(None, description="Optional: Bankverbindung einem Mieter zuordnen")

    @field_validator("iban")
    @classmethod
    def iban_uppercase(cls, value: str) -> str:
        return value.upper().replace(" ", "")


class BankverbindungCreate(BankverbindungBase):
    """Schema zum Anlegen einer Bankverbindung."""

    pass


class BankverbindungUpdate(BaseModel):
    """Schema zum Aktualisieren einer Bankverbindung."""

    iban: str | None = Field(None, min_length=15, max_length=34)
    bic: str | None = Field(None, max_length=11)
    kontoinhaber: str | None = Field(None, max_length=100)
    bankname: str | None = Field(None, max_length=100)
    is_default: bool | None = None
    mieter_id: int | None = None

    @field_validator("iban")
    @classmethod
    def iban_uppercase(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.upper().replace(" ", "")


class BankverbindungResponse(BankverbindungBase):
    """Schema fuer Rueckgabe einer Bankverbindung."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vermieter_id: int
