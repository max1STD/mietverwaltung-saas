
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
    BetroffenenAnfragenService,
    OrgAdminService,
    OrgMitgliedService,
    OrgRichtlinienService,
    OrgRolleService,
    PlattformAdminService,
    SicherheitsService,
    SupportFreigabeService,
    VertretungsService,
    VierAugenService,
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


class TestOrgRichtlinienService:
    async def test_get_or_create(self, db_session: AsyncSession, org: Organisation):
        service = OrgRichtlinienService(db_session, org.id)
        r = await service.get_or_create()
        assert r.org_id == org.id
        assert r.mfa_pflicht is True

    async def test_update_richtlinie(self, db_session: AsyncSession, org: Organisation):
        service = OrgRichtlinienService(db_session, org.id)
        r = await service.update(session_dauer_stunden=8, sso_erlaubt=True, compliance_center_aktiv=True)
        assert r.session_dauer_stunden == 8
        assert r.sso_erlaubt is True
        assert r.compliance_center_aktiv is True


class TestVertretungsService:
    async def test_create_and_list(self, db_session: AsyncSession, org: Organisation, owner_user: User):
        from app.models.organisation import OrganisationsMitglied
        from datetime import datetime, timedelta, UTC
        # create two members
        stmt = select(OrganisationsMitglied).where(OrganisationsMitglied.org_id == org.id)
        result = await db_session.execute(stmt)
        m1 = result.scalar_one()
        u2 = User(email="v2@example.com", full_name="Vertretung", role="vermieter", is_active=True, email_verified=True, password_hash="hash")
        db_session.add(u2)
        await db_session.flush()
        m2 = OrganisationsMitglied(org_id=org.id, user_id=u2.id, rolle="sachbearbeiter", aktiv=True, eingeladen_von=owner_user.id)
        db_session.add(m2)
        await db_session.flush()

        service = VertretungsService(db_session, org.id)
        now = datetime.now(UTC)
        v = await service.create(m1.id, m2.id, "admin", None, now, now + timedelta(days=7))
        assert v.an_mitglied_id == m2.id
        rows = await service.list_active()
        assert any(r.id == v.id for r in rows)


class TestVierAugenService:
    async def test_request_confirm_and_execute(self, db_session: AsyncSession, platform_admin: PlattformAdmin):
        from app.models.organisation import FreigabeAnfrage
        from datetime import datetime, timedelta, UTC
        service = VierAugenService(db_session, admin_id=platform_admin.id)
        now = datetime.now(UTC)
        fa = await service.request("org_delete", None, now + timedelta(hours=24), now + timedelta(days=2))
        assert fa.status == "ausstehend"

        # create second admin for confirmation
        a2 = await PlattformAdminService(db_session, admin_id=platform_admin.id).create_admin("a2@platform.local", "owner", platform_admin.id)
        confirmed = await service.confirm(fa.id, a2.id)
        assert confirmed is not None
        assert confirmed.status == "bestaetigt"

        executable = await service.is_executable(fa.id, now + timedelta(hours=25))
        assert executable is not None


class TestSicherheitsService:
    async def test_log_and_read(self, db_session: AsyncSession, org: Organisation):
        service = SicherheitsService(db_session, org.id)
        e = await service.log("viele_downloads", "100 downloads in 5 min", ernst="hoch")
        assert e.org_id == org.id
        assert e.ernst == "hoch"
        unread = await service.list_unread()
        assert any(x.id == e.id for x in unread)
        await service.mark_read(e.id)
        unread2 = await service.list_unread()
        assert not any(x.id == e.id for x in unread2)


class TestBetroffenenAnfragenService:
    async def test_create_and_close(self, db_session: AsyncSession, org: Organisation, owner_user: User):
        from datetime import datetime, timedelta, UTC
        service = BetroffenenAnfragenService(db_session, org.id)
        frist = datetime.now(UTC) + timedelta(days=30)
        a = await service.create("loeschung", frist, "Bitte loeschen")
        assert a.status == "offen"
        updated = await service.update_status(a.id, "erledigt", "erledigt", owner_user.id)
        assert updated is not None
        assert updated.status == "erledigt"


class TestOrgRolleService:
    async def test_custom_role(self, db_session: AsyncSession, org: Organisation):
        service = OrgRolleService(db_session, org.id)
        rolle = await service.create("Hausmeister-Plus", ["objekt:read", "tickets:write"])
        assert rolle.org_id == org.id
        assert "tickets:write" in rolle.berechtigungen
        rows = await service.list()
        assert any(r.id == rolle.id for r in rows)
