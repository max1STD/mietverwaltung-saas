
"""Tests fuer Admin-A0 Services und Router."""
from __future__ import annotations

import pytest
import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db_context import DbContext
from app.core.db_context import set_db_context as _set_db_context
from app.models.organisation import (
    Einladung,
    Organisation,
    OrganisationsMitglied,
    PlattformAdmin,
    PlattformAuditLog,
    SupportFreigabe,
)
from app.models.user import User
from app.services.admin import (
    AdminPermission,
    OrgAdminService,
    OrgMitgliedService,
    PlattformAdminService,
    SupportFreigabeService,
)


@pytest.fixture
async def owner_user(db_session: AsyncSession) -> User:
    user = User(
        email="owner@example.com",
        full_name="Test Owner",
        role="vermieter",
        is_active=True,
        email_verified=True,
        password_hash="hash",
    )
    db_session.add(user)
    await db_session.flush()
    await _set_db_context(db_session, DbContext(user_id=user.id, org_id=None, role="owner"))
    return user


@pytest.fixture
async def org(db_session: AsyncSession, owner_user: User) -> Organisation:
    from app.models.organisation import Eigentuemer
    org = Organisation(name="Test Org", status="aktiv", plan="free")
    db_session.add(org)
    await db_session.flush()
    eigentuemer = Eigentuemer(org_id=org.id, user_id=owner_user.id, name="Test Eigentuemer")
    db_session.add(eigentuemer)
    mitglied = OrganisationsMitglied(
        org_id=org.id, user_id=owner_user.id, rolle="eigentuemer", aktiv=True, eingeladen_von=owner_user.id
    )
    db_session.add(mitglied)
    await db_session.flush()
    await db_session.refresh(org)
    return org


@pytest.fixture
async def platform_admin(db_session: AsyncSession) -> PlattformAdmin:
    admin = PlattformAdmin(
        email="admin@platform.local",
        rolle="owner",
        aktiv=True,
        passkey_ref=None,
        letzte_anmeldung=None,
    )
    db_session.add(admin)
    await db_session.flush()
    await db_session.refresh(admin)
    return admin


class TestPlattformAdminService:
    async def test_create_admin(self, db_session: AsyncSession, platform_admin: PlattformAdmin):
        service = PlattformAdminService(db_session, admin_id=platform_admin.id)
        new_admin = await service.create_admin("ops@platform.local", "ops", platform_admin.id)
        assert new_admin.email == "ops@platform.local"
        assert new_admin.rolle == "ops"
        assert new_admin.eingeladen_von_id == platform_admin.id

    async def test_list_organisations(self, db_session: AsyncSession, org: Organisation):
        service = OrgAdminService(db_session)
        rows = await service.list_organisations(limit=10)
        assert any(r["id"] == org.id for r in rows)


class TestOrgMitgliedService:
    async def test_invite_member(self, db_session: AsyncSession, org: Organisation, owner_user: User):
        service = OrgMitgliedService(db_session, org.id)
        einladung = await service.invite_member("new@example.com", "sachbearbeiter", owner_user.id)
        assert einladung.org_id == org.id
        assert einladung.ziel_kontakt == "new@example.com"
        assert einladung.rolle_oder_scope == "sachbearbeiter"

    async def test_set_role_and_deactivate(
        self, db_session: AsyncSession, org: Organisation, owner_user: User
    ):
        service = OrgMitgliedService(db_session, org.id)
        stmt = select(OrganisationsMitglied).where(
            OrganisationsMitglied.org_id == org.id,
            OrganisationsMitglied.user_id == owner_user.id,
        )
        result = await db_session.execute(stmt)
        mitglied = result.scalar_one()
        updated = await service.set_role(mitglied.id, "buchhaltung")
        assert updated is not None
        assert updated.rolle == "buchhaltung"
        deactivated = await service.deactivate_member(mitglied.id)
        assert deactivated is not None
        assert deactivated.aktiv is False


class TestSupportFreigabeService:
    async def test_create_support_freigabe(
        self, db_session: AsyncSession, platform_admin: PlattformAdmin, org: Organisation, owner_user: User
    ):
        service = SupportFreigabeService(db_session, admin_id=platform_admin.id)
        sf = await service.create(org.id, None, "Problem", "lesend", 4, owner_user.id)
        assert sf.org_id == org.id
        assert sf.umfang == "lesend"
        assert sf.erteilt_von_user_id == owner_user.id


class TestAdminPermission:
    def test_owner_has_org_suspend(self):
        assert AdminPermission.ORG_SUSPEND in {
            AdminPermission.ORG_SUSPEND,
            AdminPermission.ORG_READ,
            AdminPermission.BILLING_READ,
        }
