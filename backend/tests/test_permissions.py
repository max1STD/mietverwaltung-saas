import pytest
import pytest_asyncio

from app.services.auth import hash_password
from app.core.db_context import DbContext
from app.models.user import User
from app.models.organisation import Organisation, OrganisationsMitglied
from app.services.permissions import Permission, PermissionService


@pytest_asyncio.fixture
async def owner_user(db_session):
    user = User(
        email="owner@example.com",
        password_hash=hash_password("password"),
        full_name="Owner",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    org = Organisation(name="Test-Org")
    db_session.add(org)
    await db_session.flush()
    await db_session.refresh(org)
    Mitglied = OrganisationsMitglied(user_id=user.id, org_id=org.id, rolle="org_admin")
    db_session.add(Mitglied)
    await db_session.flush()
    return user, org, Mitglied


async def test_owner_can_mieter_list(db_session, owner_user):
    user, org, Mitglied = owner_user
    ctx = DbContext(user_id=user.id, org_id=org.id, role="org_admin")
    ps = PermissionService(db_session, ctx)
    await ps.require(Permission.MIETER_READ)


async def test_sachbearbeiter_cannot_delete_abrechnung(db_session, owner_user):
    user, org, _ = owner_user
    sach = User(
        email="sach@example.com",
        password_hash=hash_password("password"),
        full_name="Sach",
        is_active=True,
    )
    db_session.add(sach)
    await db_session.flush()
    await db_session.refresh(sach)
    db_session.add(OrganisationsMitglied(user_id=sach.id, org_id=org.id, rolle="sachbearbeiter"))
    await db_session.flush()
    ctx = DbContext(user_id=sach.id, org_id=org.id, role="sachbearbeiter")
    ps = PermissionService(db_session, ctx)
    assert await ps.may(Permission.ABRECHNUNG_WRITE) is False
    with pytest.raises(PermissionError):
        await ps.require(Permission.ABRECHNUNG_WRITE)


async def test_cross_org_denied(db_session, owner_user):
    user1, org1, _ = owner_user
    user2 = User(
        email="other@example.com",
        password_hash=hash_password("password"),
        full_name="Other",
        is_active=True,
    )
    db_session.add(user2)
    await db_session.flush()
    await db_session.refresh(user2)
    org2 = Organisation(name="Other-Org")
    db_session.add(org2)
    await db_session.flush()
    await db_session.refresh(org2)
    db_session.add(OrganisationsMitglied(user_id=user2.id, org_id=org2.id, rolle="org_admin"))
    await db_session.flush()

    ctx = DbContext(user_id=user1.id, org_id=org2.id, role="org_admin")
    ps = PermissionService(db_session, ctx)
    assert await ps.may(Permission.MIETER_READ) is False
