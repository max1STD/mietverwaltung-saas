"""Integrationstests für das Ticket-System."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pyotp
import pytest
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tickets import Ticket, TicketComment, TicketSLA, TicketTrigger
from app.models.user import User
from app.services.auth import hash_password


CONSENT_TEXT = (
    "Ich stimme der Verarbeitung meiner Daten gemäß DSGVO und den AGB zu. "
    "Einwilligungen können jederzeit widerrufen werden."
)

PASSWORD = "SicheresPasswort123!"


async def _register_vermieter(client: AsyncClient) -> dict:
    """Registriert einen neuen Vermieter über die API."""
    email = f"v-{uuid.uuid4().hex[:8]}@example.com"
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": PASSWORD,
            "full_name": "Test Vermieter",
            "consent_text": CONSENT_TEXT,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


async def _login(client: AsyncClient, email: str, password: str) -> dict:
    """Login inkl. 2FA-Setup/Verify, gibt Token-Response zurück."""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200, resp.text

    csrf = client.cookies.get("csrf_token") or ""
    setup = await client.post(
        "/api/v1/auth/2fa/setup",
        json={},
        headers={"X-CSRF-Token": csrf},
    )
    assert setup.status_code == 200, setup.text
    secret = setup.json()["secret"]

    code = pyotp.TOTP(secret).now()
    verify = await client.post(
        "/api/v1/auth/2fa/verify",
        json={"code": code},
        headers={"X-CSRF-Token": csrf},
    )
    assert verify.status_code == 200, verify.text
    return verify.json()


def _csrf(client: AsyncClient) -> str:
    return client.cookies.get("csrf_token") or ""


async def _seed_mieter_einheit(db: AsyncSession, vermieter_id: int) -> tuple[int, int]:
    """Legt Objekt, Einheit und Mieter für Ticket-Tests an."""
    result = await db.execute(
        text(
            """
            INSERT INTO objekte (vermieter_id, name, address, typ)
            VALUES (:vid, 'Testobjekt', 'Musterstraße 1, 12345 Musterstadt', 'mehrfamilienhaus')
            RETURNING id
            """
        ),
        {"vid": vermieter_id},
    )
    objekt_id = result.scalar_one()

    result = await db.execute(
        text(
            """
            INSERT INTO einheiten (vermieter_id, objekt_id, name, size_qm, rooms, rent_cold)
            VALUES (:vid, :oid, 'Wohnung 1', 75.0, 3, 850.00)
            RETURNING id
            """
        ),
        {"vid": vermieter_id, "oid": objekt_id},
    )
    einheit_id = result.scalar_one()

    result = await db.execute(
        text(
            """
            INSERT INTO mieter (vermieter_id, first_name, last_name, email, status, since)
            VALUES (:vid, 'Max', 'Mustermann', 'mieter@example.com', 'aktiv', NOW())
            RETURNING id
            """
        ),
        {"vid": vermieter_id},
    )
    mieter_id = result.scalar_one()

    return einheit_id, mieter_id


async def _create_mieter_user(
    db: AsyncSession,
    vermieter_id: int,
    mieter_id: int,
    suffix: str = "mieter1",
) -> str:
    """Legt einen Login-Account für einen bestehenden Mieter an."""
    email = f"{suffix}-{vermieter_id}@example.com"
    user = User(
        email=email,
        password_hash=hash_password(PASSWORD),
        full_name=f"Mieter {suffix}",
        role="mieter",
        vermieter_id=vermieter_id,
        is_active=True,
        email_verified=True,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    # Mieter-Zeile mit Account verknüpfen (über eindeutige E-Mail).
    await db.execute(
        text("UPDATE mieter SET email = :email WHERE id = :mid"),
        {"email": email, "mid": mieter_id},
    )
    return email


@pytest.mark.asyncio
async def test_create_ticket(async_client: AsyncClient) -> None:
    """Vermieter kann ein Ticket erstellen und bekommt fortlaufende Nummer."""
    db = async_client.db_session
    vermieter = await _register_vermieter(async_client)
    await _login(async_client, vermieter["email"], PASSWORD)

    einheit_id, mieter_id = await _seed_mieter_einheit(db, vermieter["id"])

    resp = await async_client.post(
        "/api/v1/tickets",
        json={
            "title": "Heizung defekt",
            "description": "Die Heizung im Wohnzimmer bleibt kalt.",
            "category": "heizung",
            "priority": "dringend",
            "mieter_id": mieter_id,
            "einheit_id": einheit_id,
        },
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["title"] == "Heizung defekt"
    assert data["category"] == "heizung"
    assert data["priority"] == "dringend"
    assert data["status"] == "offen"
    assert data["ticket_number"].startswith(f"TKT-{datetime.now(UTC).year}-")
    assert data["mieter_id"] == mieter_id
    assert data["einheit_id"] == einheit_id


@pytest.mark.asyncio
async def test_list_and_filter_tickets(async_client: AsyncClient) -> None:
    """Tickets können aufgelistet und gefiltert werden."""
    db = async_client.db_session
    vermieter = await _register_vermieter(async_client)
    await _login(async_client, vermieter["email"], PASSWORD)

    einheit_id, mieter_id = await _seed_mieter_einheit(db, vermieter["id"])

    # Zwei Tickets anlegen.
    for title, category, priority in [
        ("Wasserhahn tropft", "wasser", "normal"),
        ("Schimmel im Bad", "schimmel", "dringend"),
    ]:
        resp = await async_client.post(
            "/api/v1/tickets",
            json={
                "title": title,
                "category": category,
                "priority": priority,
                "mieter_id": mieter_id,
                "einheit_id": einheit_id,
            },
            headers={"X-CSRF-Token": _csrf(async_client)},
        )
        assert resp.status_code == 201

    # Ohne Filter: 2 Tickets.
    resp = await async_client.get("/api/v1/tickets")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2

    # Filter nach Priorität.
    resp = await async_client.get("/api/v1/tickets?priority=dringend")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Schimmel im Bad"

    # Nur offene Tickets.
    resp = await async_client.get("/api/v1/tickets?open_only=true")
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


@pytest.mark.asyncio
async def test_update_ticket_status(async_client: AsyncClient) -> None:
    """Status-Updates setzen closed_at bei Endstatus."""
    db = async_client.db_session
    vermieter = await _register_vermieter(async_client)
    await _login(async_client, vermieter["email"], PASSWORD)

    einheit_id, mieter_id = await _seed_mieter_einheit(db, vermieter["id"])

    resp = await async_client.post(
        "/api/v1/tickets",
        json={
            "title": "Lampe kaputt",
            "category": "elektrik",
            "mieter_id": mieter_id,
            "einheit_id": einheit_id,
        },
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    ticket = resp.json()

    # Status auf erledigt setzen.
    resp = await async_client.patch(
        f"/api/v1/tickets/{ticket['id']}",
        json={"status": "erledigt"},
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "erledigt"
    assert data["closed_at"] is not None

    # Status zurück auf offen.
    resp = await async_client.patch(
        f"/api/v1/tickets/{ticket['id']}",
        json={"status": "offen"},
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "offen"
    assert data["closed_at"] is None


@pytest.mark.asyncio
async def test_ticket_comments(async_client: AsyncClient) -> None:
    """Kommentare können erstellt und aufgelistet werden."""
    db = async_client.db_session
    vermieter = await _register_vermieter(async_client)
    await _login(async_client, vermieter["email"], PASSWORD)

    einheit_id, mieter_id = await _seed_mieter_einheit(db, vermieter["id"])

    resp = await async_client.post(
        "/api/v1/tickets",
        json={
            "title": "Fenster defekt",
            "mieter_id": mieter_id,
            "einheit_id": einheit_id,
        },
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    ticket_id = resp.json()["id"]

    resp = await async_client.post(
        f"/api/v1/tickets/{ticket_id}/comments",
        json={"content": "Handwerker wurde informiert.", "is_internal": True},
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    assert resp.status_code == 201
    comment = resp.json()
    assert comment["content"] == "Handwerker wurde informiert."
    assert comment["author_role"] == "vermieter"
    assert comment["is_internal"] is True

    resp = await async_client.get(f"/api/v1/tickets/{ticket_id}/comments")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # Ticket-Detail liefert Kommentare mit.
    resp = await async_client.get(f"/api/v1/tickets/{ticket_id}")
    assert resp.status_code == 200
    assert len(resp.json()["comments"]) == 1


@pytest.mark.asyncio
async def test_delete_ticket(async_client: AsyncClient) -> None:
    """Vermieter kann ein Ticket löschen."""
    db = async_client.db_session
    vermieter = await _register_vermieter(async_client)
    await _login(async_client, vermieter["email"], PASSWORD)

    einheit_id, mieter_id = await _seed_mieter_einheit(db, vermieter["id"])

    resp = await async_client.post(
        "/api/v1/tickets",
        json={"title": "Löschen Test", "mieter_id": mieter_id, "einheit_id": einheit_id},
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    ticket_id = resp.json()["id"]

    resp = await async_client.delete(
        f"/api/v1/tickets/{ticket_id}",
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    assert resp.status_code == 200

    resp = await async_client.get(f"/api/v1/tickets/{ticket_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_sla_crud(async_client: AsyncClient) -> None:
    """SLA-Konfiguration CRUD."""
    vermieter = await _register_vermieter(async_client)
    await _login(async_client, vermieter["email"], PASSWORD)

    resp = await async_client.post(
        "/api/v1/tickets/sla",
        json={
            "name": "Standard SLA",
            "response_time_hours": 24,
            "resolution_time_hours": 72,
            "biz_hours_only": True,
            "biz_start": "08:00",
            "biz_end": "18:00",
            "biz_days": "mtwtf",
            "escalation_levels": {"level1": "manager"},
        },
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    assert resp.status_code == 201
    sla = resp.json()
    assert sla["name"] == "Standard SLA"
    assert sla["response_time_hours"] == 24
    assert sla["biz_start"] == "08:00"

    sla_id = sla["id"]

    resp = await async_client.get("/api/v1/tickets/sla")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = await async_client.patch(
        f"/api/v1/tickets/sla/{sla_id}",
        json={"response_time_hours": 12},
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    assert resp.status_code == 200
    assert resp.json()["response_time_hours"] == 12

    resp = await async_client.delete(
        f"/api/v1/tickets/sla/{sla_id}",
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    assert resp.status_code == 200

    resp = await async_client.get("/api/v1/tickets/sla")
    assert len(resp.json()) == 0


@pytest.mark.asyncio
async def test_trigger_crud(async_client: AsyncClient) -> None:
    """Trigger/Automatisierungsregeln CRUD."""
    vermieter = await _register_vermieter(async_client)
    await _login(async_client, vermieter["email"], PASSWORD)

    resp = await async_client.post(
        "/api/v1/tickets/triggers",
        json={
            "name": "Dringend -> Benachrichtigung",
            "trigger_type": "event",
            "condition": {"priority": "dringend"},
            "perform": {"notify": "vermieter"},
        },
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    assert resp.status_code == 201
    trigger = resp.json()
    assert trigger["condition"]["priority"] == "dringend"

    trigger_id = trigger["id"]

    resp = await async_client.get("/api/v1/tickets/triggers")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = await async_client.patch(
        f"/api/v1/tickets/triggers/{trigger_id}",
        json={"is_active": False},
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False

    resp = await async_client.delete(
        f"/api/v1/tickets/triggers/{trigger_id}",
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_mieter_ticket_isolation(async_client: AsyncClient) -> None:
    """Mieter sieht nur eigene Tickets und kann nur eigene erstellen."""
    db = async_client.db_session
    vermieter = await _register_vermieter(async_client)
    await _login(async_client, vermieter["email"], PASSWORD)

    einheit_id, mieter_id = await _seed_mieter_einheit(db, vermieter["id"])

    # Vermieter legt ein Ticket für den Mieter an.
    resp = await async_client.post(
        "/api/v1/tickets",
        json={
            "title": "Mieter-Ticket",
            "mieter_id": mieter_id,
            "einheit_id": einheit_id,
        },
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    assert resp.status_code == 201
    ticket_id = resp.json()["id"]

    # Mieter-Login-Account anlegen.
    mieter_email = await _create_mieter_user(db, vermieter["id"], mieter_id, "mieter_e2e")
    await db.commit()

    # Als Mieter einloggen (Cookies werden ersetzt).
    await _login(async_client, mieter_email, PASSWORD)

    # Eigenes Ticket lesen.
    resp = await async_client.get(f"/api/v1/tickets/{ticket_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Mieter-Ticket"

    # Eigenes Ticket erstellen.
    resp = await async_client.post(
        "/api/v1/tickets",
        json={"title": "Mieter selbst erstellt", "einheit_id": einheit_id},
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["mieter_id"] is not None

    # SLA/Trigger für Mieter blockiert.
    resp = await async_client.get("/api/v1/tickets/sla")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_ticket_number_sequence(async_client: AsyncClient) -> None:
    """Ticketnummern sind fortlaufend pro Vermieter und Jahr."""
    db = async_client.db_session
    vermieter = await _register_vermieter(async_client)
    await _login(async_client, vermieter["email"], PASSWORD)

    einheit_id, mieter_id = await _seed_mieter_einheit(db, vermieter["id"])

    numbers = []
    for i in range(3):
        resp = await async_client.post(
            "/api/v1/tickets",
            json={"title": f"Ticket {i}", "mieter_id": mieter_id, "einheit_id": einheit_id},
            headers={"X-CSRF-Token": _csrf(async_client)},
        )
        assert resp.status_code == 201
        numbers.append(resp.json()["ticket_number"])

    # Sortierte Nummern müssen aufsteigend sein.
    assert numbers == sorted(numbers)
    seqs = [int(n.split("-")[-1]) for n in numbers]
    assert seqs == list(range(1, 4))


@pytest.mark.asyncio
async def test_mieter_cannot_access_other_tickets(async_client: AsyncClient) -> None:
    """Mieter kann fremde Tickets weder lesen noch kommentieren."""
    db = async_client.db_session
    vermieter = await _register_vermieter(async_client)
    await _login(async_client, vermieter["email"], PASSWORD)

    einheit_id, mieter_id = await _seed_mieter_einheit(db, vermieter["id"])

    # Zweiten Mieter anlegen.
    result = await db.execute(
        text(
            """
            INSERT INTO mieter (vermieter_id, first_name, last_name, email, status)
            VALUES (:vid, 'Anders', 'Mensch', 'anders@example.com', 'aktiv')
            RETURNING id
            """
        ),
        {"vid": vermieter["id"]},
    )
    other_mieter_id = result.scalar_one()

    resp = await async_client.post(
        "/api/v1/tickets",
        json={
            "title": "Fremdes Ticket",
            "mieter_id": other_mieter_id,
            "einheit_id": einheit_id,
        },
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    other_ticket_id = resp.json()["id"]

    # Mieter-Login.
    mieter_email = await _create_mieter_user(db, vermieter["id"], mieter_id, "isolated")
    await db.commit()
    await _login(async_client, mieter_email, PASSWORD)

    resp = await async_client.get(f"/api/v1/tickets/{other_ticket_id}")
    assert resp.status_code == 403

    resp = await async_client.post(
        f"/api/v1/tickets/{other_ticket_id}/comments",
        json={"content": "Unbefugter Kommentar"},
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_mieter_cannot_see_internal_comments(async_client: AsyncClient) -> None:
    """Interne Vermieter-Kommentare bleiben vor Mietern verborgen."""
    db = async_client.db_session
    vermieter = await _register_vermieter(async_client)
    await _login(async_client, vermieter["email"], PASSWORD)

    einheit_id, mieter_id = await _seed_mieter_einheit(db, vermieter["id"])

    resp = await async_client.post(
        "/api/v1/tickets",
        json={"title": "Öffentlich + Intern", "mieter_id": mieter_id, "einheit_id": einheit_id},
        headers={"X-CSRF-Token": _csrf(async_client)},
    )
    ticket_id = resp.json()["id"]

    # Interner Vermieter-Kommentar.
    await async_client.post(
        f"/api/v1/tickets/{ticket_id}/comments",
        json={"content": "Interne Notiz", "is_internal": True},
        headers={"X-CSRF-Token": _csrf(async_client)},
    )

    # Öffentlicher Kommentar.
    await async_client.post(
        f"/api/v1/tickets/{ticket_id}/comments",
        json={"content": "Hallo Mieter"},
        headers={"X-CSRF-Token": _csrf(async_client)},
    )

    # Als Mieter einloggen und prüfen.
    mieter_email = await _create_mieter_user(db, vermieter["id"], mieter_id, "public_only")
    await db.commit()
    await _login(async_client, mieter_email, PASSWORD)

    resp = await async_client.get(f"/api/v1/tickets/{ticket_id}/comments")
    assert resp.status_code == 200
    comments = resp.json()
    assert len(comments) == 1
    assert comments[0]["content"] == "Hallo Mieter"


@pytest.mark.asyncio
async def test_models_import_and_table_names() -> None:
    """Sanity-Check: Modelle sind importierbar und Tabellennamen korrekt."""
    assert Ticket.__tablename__ == "tickets"
    assert TicketComment.__tablename__ == "ticket_kommentare"
    assert TicketSLA.__tablename__ == "ticket_sla"
    assert TicketTrigger.__tablename__ == "ticket_trigger"
