"""Service fuer Bankverbindungen — CRUD mit IBAN- und BIC-Verschluesselung."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bankverbindung import Bankverbindung
from app.schemas.bankverbindung import BankverbindungCreate, BankverbindungUpdate
from app.services.audit_log import audit_log
from app.services.crypto import decrypt_value, encrypt_value


_IBAN_CONTEXT = "bankverbindungen:iban"
_BIC_CONTEXT = "bankverbindungen:bic"


async def create_bankverbindung(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    data: BankverbindungCreate,
    ip: str | None = None,
) -> Bankverbindung:
    """Erstellt eine neue Bankverbindung fuer den Vermieter (optional: Mieter-Zuordnung)."""
    if data.is_default:
        await _clear_default_bankverbindungen(db, vermieter_id)

    bankverbindung = Bankverbindung(
        vermieter_id=vermieter_id,
        mieter_id=data.mieter_id,
        iban_enc=encrypt_value(data.iban, context=_IBAN_CONTEXT),
        bic_enc=encrypt_value(data.bic, context=_BIC_CONTEXT),
        kontoinhaber=data.kontoinhaber,
        bankname=data.bankname,
        is_default=data.is_default,
    )
    db.add(bankverbindung)
    await db.flush()
    await db.refresh(bankverbindung)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="bankverbindung_create",
        entity="bankverbindungen",
        entity_id=bankverbindung.id,
        details={"kontoinhaber": data.kontoinhaber, "has_mieter": data.mieter_id is not None},
        ip=ip,
        risk_level="hoch",
    )
    return bankverbindung


async def list_bankverbindungen(
    db: AsyncSession,
    vermieter_id: int,
) -> list[Bankverbindung]:
    """Listet alle aktiven Bankverbindungen eines Vermieters."""
    result = await db.execute(
        select(Bankverbindung).where(
            Bankverbindung.vermieter_id == vermieter_id,
            Bankverbindung.deleted_at.is_(None),
        ).order_by(Bankverbindung.is_default.desc(), Bankverbindung.created_at.desc())
    )
    return list(result.scalars().all())


async def get_bankverbindung(
    db: AsyncSession,
    vermieter_id: int,
    bankverbindung_id: int,
) -> Bankverbindung | None:
    """Gibt eine einzelne Bankverbindung zurueck."""
    result = await db.execute(
        select(Bankverbindung).where(
            Bankverbindung.id == bankverbindung_id,
            Bankverbindung.vermieter_id == vermieter_id,
            Bankverbindung.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def update_bankverbindung(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    bankverbindung: Bankverbindung,
    data: BankverbindungUpdate,
    ip: str | None = None,
) -> Bankverbindung:
    """Aktualisiert eine Bankverbindung."""
    update_fields = data.model_dump(exclude_unset=True)

    if "iban" in update_fields and update_fields["iban"] is not None:
        bankverbindung.iban_enc = encrypt_value(update_fields.pop("iban"), context=_IBAN_CONTEXT)

    if "bic" in update_fields and update_fields["bic"] is not None:
        bankverbindung.bic_enc = encrypt_value(update_fields.pop("bic"), context=_BIC_CONTEXT)
        bankverbindung.bic = None

    if "is_default" in update_fields and update_fields["is_default"]:
        await _clear_default_bankverbindungen(db, vermieter_id)

    for field, value in update_fields.items():
        setattr(bankverbindung, field, value)

    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="bankverbindung_update",
        entity="bankverbindungen",
        entity_id=bankverbindung.id,
        details={"updated_fields": list(update_fields.keys())},
        ip=ip,
        risk_level="hoch",
    )
    await db.flush()
    await db.refresh(bankverbindung)
    return bankverbindung


async def delete_bankverbindung(
    db: AsyncSession,
    vermieter_id: int,
    user_id: int,
    bankverbindung: Bankverbindung,
    ip: str | None = None,
) -> None:
    """Soft-Delete einer Bankverbindung."""
    from datetime import UTC, datetime

    bankverbindung.deleted_at = datetime.now(UTC)
    await audit_log(
        db,
        user_id=user_id,
        vermieter_id=vermieter_id,
        action="bankverbindung_delete",
        entity="bankverbindungen",
        entity_id=bankverbindung.id,
        details={"kontoinhaber": bankverbindung.kontoinhaber},
        ip=ip,
        risk_level="hoch",
    )
    await db.flush()


async def _clear_default_bankverbindungen(
    db: AsyncSession,
    vermieter_id: int,
) -> None:
    """Setzt is_default bei allen anderen Bankverbindungen eines Vermieters zurueck."""
    result = await db.execute(
        select(Bankverbindung).where(
            Bankverbindung.vermieter_id == vermieter_id,
            Bankverbindung.is_default.is_(True),
            Bankverbindung.deleted_at.is_(None),
        )
    )
    for bv in result.scalars().all():
        bv.is_default = False
    await db.flush()


def get_iban(bankverbindung: Bankverbindung) -> str | None:
    """Hilfsfunktion zum Entschluesseln der IBAN."""
    return decrypt_value(bankverbindung.iban_enc, context=_IBAN_CONTEXT)


def get_bic(bankverbindung: Bankverbindung) -> str | None:
    """Hilfsfunktion zum Entschluesseln der BIC."""
    return decrypt_value(bankverbindung.bic_enc, context=_BIC_CONTEXT)
