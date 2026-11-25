import pytest
import pytest_asyncio
from datetime import datetime, timedelta, UTC
from sqlalchemy import select

from app.services.auth import hash_password
from app.models.user import User
from app.models.mieter import Mieter
from app.models.organisation import Organisation, OrganisationsMitglied
from app.models.loeschregel import Loeschregel
from app.services.retention import RetentionService, LoeschStatus


@pytest_asyncio.fixture
async def retention_setup(db_session):
    owner = User(
        email="r-owner@example.com",
        password_hash=hash_password("password"),
        full_name="Retention Owner",
        is_active=True,
    )
    db_session.add(owner)
    await db_session.flush()
    await db_session.refresh(owner)
    org = Organisation(name="Retention-Org")
    db_session.add(org)
    await db_session.flush()
    await db_session.refresh(org)
    db_session.add(OrganisationsMitglied(user_id=owner.id, org_id=org.id, rolle="org_admin"))
    await db_session.flush()
    return db_session, org, owner


async def test_seed_default_rules(retention_setup):
    db_session, org, owner = retention_setup
    rs = RetentionService(db_session)
    await rs.seed_default_rules()
    rules = [r for r in (await db_session.execute(select(Loeschregel))).scalars().all() if r.org_id is None]
    assert len(rules) == 12
    assert any(r.klasse == "K1" for r in rules)


async def test_block_and_lifecycle_flow(retention_setup):
    db_session, org, owner = retention_setup
    rs = RetentionService(db_session)
    await rs.seed_default_rules()

    mieter = Mieter(
        first_name="Max",
        last_name="Mustermann",
        email="max@example.com",
        vermieter_id=owner.id,
        org_id=org.id,
    )
    db_session.add(mieter)
    await db_session.flush()
    await db_session.refresh(mieter)

    await rs.sperren(Mieter, mieter.id, "K1", org_id=org.id)
    assert mieter.lifecycle_status == LoeschStatus.GESPERRT.value
    assert mieter.gesperrt_am is not None
    assert mieter.loeschklasse == "K1"
    assert mieter.loeschen_fruehestens_am is not None


async def test_run_warns_only(retention_setup):
    db_session, org, owner = retention_setup
    rs = RetentionService(db_session)
    await rs.seed_default_rules()
    mieter = Mieter(
        first_name="Max",
        last_name="Mustermann",
        email="max2@example.com",
        vermieter_id=owner.id,
        org_id=org.id,
        lifecycle_status=LoeschStatus.GESPERRT.value,
        loeschklasse="K1",
        loeschen_fruehestens_am=datetime.now(UTC) + timedelta(days=10),
    )
    db_session.add(mieter)
    await db_session.flush()
    await db_session.refresh(mieter)

    protocol = await rs.run_dry()
    assert any(p.aktion == "WARNUNG_30_TAGE" for p in protocol)
