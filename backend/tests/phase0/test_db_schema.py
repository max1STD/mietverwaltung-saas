"""Phase 0: Datenbank-Schema-Validierung."""
from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


REQUIRED_TABLES = {
    "users",
    "user_sessions",
    "einwilligungen",
    "audit_logs",
    "subscriptions",
    "plan_usage",
    "bankverbindungen",
    "objekte",
    "einheiten",
    "einheit_ausstattung",
    "mieter_historie",
    "bewerbungen",
    "mieter",
    "mietvertraege",
    "mietvertrag_aenderungen",
    "kostenkategorien",
    "handwerker",
    "ticket_sla",
    "ticket_trigger",
    "abrechnungen",
    "kosten",
    "abrechnung_positionen",
    "dokumente",
    "dokument_freigaben",
    "tickets",
    "ticket_kommentare",
    "mietzahlungen",
    "events",
    "notifications",
    "fristen",
    "onboarding_progress",
    "ai_stored_results",
    "referrals",
}

USERS_KEY_COLUMNS = {
    "id",
    "email",
    "password_hash",
    "full_name",
    "role",
    "phone",
    "vermieter_id",
    "totp_secret",
    "backup_codes",
    "email_code",
    "email_code_expires",
    "failed_login_count",
    "locked_until",
    "is_active",
    "email_verified",
    "dsgvo_consent_at",
    "firma",
    "steuernr_enc",
    "rechnungs_strasse",
    "rechnungs_hausnr",
    "rechnungs_plz",
    "rechnungs_ort",
    "ust_id",
    "created_at",
    "updated_at",
    "deleted_at",
}

SUBSCRIPTION_PRICING_COLUMNS = {"price_per_we", "billing_cycle"}

SOFT_DELETE_TABLES = {
    "users",
    "objekte",
    "einheiten",
    "mieter",
    "mietvertraege",
    "bewerbungen",
    "bankverbindungen",
    "abrechnungen",
    "kosten",
    "abrechnung_positionen",
    "dokumente",
}


@pytest.mark.phase0
@pytest.mark.integration
@pytest.mark.asyncio
async def test_all_required_tables_exist(db_session: AsyncSession) -> None:
    """Alle erforderlichen Tabellen des v4.1-Schemas sind vorhanden."""
    result = await db_session.execute(
        text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
        """)
    )
    tables = {row[0] for row in result.all()}
    missing = REQUIRED_TABLES - tables
    assert not missing, f"Fehlende Tabellen: {missing}"


@pytest.mark.phase0
@pytest.mark.integration
@pytest.mark.asyncio
async def test_alembic_version_is_expected(db_session: AsyncSession) -> None:
    """alembic_version enthält eine erwartete Revision."""
    result = await db_session.execute(
        text("SELECT version_num FROM alembic_version")
    )
    version = result.scalar_one_or_none()
    assert version in {
        "0001", "0002", "0003_frontend_aligned_fields", "0004_public_ids",
        "0005_mieter_addresses_guarantors", "0006_dokumente", "0007_ticket_objekt_id",
        "0008_dokumente_neue_struktur", "0009_public_ids_mieter_mv", "0010_einheit_stammdaten",
        "0011_objekt_stammdaten", "0012_dokumente_ocr",
        "f715d10be63c", "b30dda0e71ec", "c3a9f8e21b4d", "d2c4a7e89b1f", "e5b1c2d3a4f6",
        "f2f81c52b352", "1a2b3c4d5e6f",
    }, f"Unerwartete Alembic-Version: {version}"


@pytest.mark.phase0
@pytest.mark.integration
@pytest.mark.asyncio
async def test_users_key_columns_exist(db_session: AsyncSession) -> None:
    """Die users-Tabelle enthält alle Schlüsselspalten."""
    result = await db_session.execute(
        text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'users'
        """)
    )
    columns = {row[0] for row in result.all()}
    missing = USERS_KEY_COLUMNS - columns
    assert not missing, f"Fehlende users-Spalten: {missing}"


@pytest.mark.phase0
@pytest.mark.integration
@pytest.mark.asyncio
async def test_subscriptions_we_pricing_columns(db_session: AsyncSession) -> None:
    """Die subscriptions-Tabelle verwendet WE-basierte Preisgestaltung."""
    result = await db_session.execute(
        text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'subscriptions'
        """)
    )
    columns = {row[0] for row in result.all()}
    assert SUBSCRIPTION_PRICING_COLUMNS.issubset(columns)


@pytest.mark.phase0
@pytest.mark.integration
@pytest.mark.asyncio
async def test_soft_delete_columns_exist(db_session: AsyncSession) -> None:
    """deleted_at existiert auf den erwarteten Tabellen."""
    result = await db_session.execute(
        text("""
            SELECT table_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND column_name = 'deleted_at'
        """)
    )
    tables_with_soft_delete = {row[0] for row in result.all()}
    missing = SOFT_DELETE_TABLES - tables_with_soft_delete
    assert not missing, f"Fehlende Soft-Delete-Spalten auf: {missing}"
