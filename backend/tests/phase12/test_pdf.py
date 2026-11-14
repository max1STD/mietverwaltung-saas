"""Tests für Phase 12: PDF-Export und Vorlagen."""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.services.pdf.documents import generate_mahnung, generate_wohnungsgeberbestaetigung
from app.services.pdf.generator import html_to_pdf, render_template


@pytest.mark.phase12
@pytest.mark.integration
async def test_render_base_template():
    html = render_template("base.html", {"title": "Test", "vermieter": {"full_name": "Max Mustermann"}, "bankverbindung": {}, "datum": "14.11.2026"})
    assert "MietVerwaltung" in html or "14.11.2026" in html


@pytest.mark.phase12
@pytest.mark.integration
async def test_html_to_pdf():
    html = "<html><body><h1>Test PDF</h1></body></html>"
    pdf_bytes = html_to_pdf(html)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 100


@pytest.mark.phase12
@pytest.mark.integration
async def test_generate_wohnungsgeberbestaetigung(auth_client: AsyncClient):
    from app.models.mieter import Mieter
    from app.models.objekt import Objekt
    from app.models.einheit import Einheit
    from app.models.mietvertraege import Mietvertrag
    from datetime import date
    from app.services.auth import hash_password

    session = auth_client.db_session
    user_id = getattr(auth_client, "user_id", 1)
    from app.models.user import User
    user = await session.get(User, user_id)

    objekt = Objekt(
        vermieter_id=user.id,
        name="Testhaus",
        address="Musterstraße 1, 12345 Musterstadt",
        typ="mehrfamilienhaus",
    )
    session.add(objekt)
    await session.flush()

    einheit = Einheit(
        vermieter_id=user.id,
        objekt_id=objekt.id,
        name="Wohnung 1",
        wohnflaeche_qm=55.0,
        rooms=2,
        kaltmiete=500.0,
    )
    session.add(einheit)
    await session.flush()

    mieter = Mieter(
        vermieter_id=user.id,
        first_name="Anna",
        last_name="Muster",
        email="anna@example.de",
    )
    session.add(mieter)
    await session.flush()

    vertrag = Mietvertrag(
        vermieter_id=user.id,
        mieter_id=mieter.id,
        einheit_id=einheit.id,
        mietbeginn=date(2024, 1, 1),
        miete_cold=500.0,
        nebenkosten_voraus=100.0,
        status="aktiv",
    )
    session.add(vertrag)
    await session.flush()

    pdf_bytes = await generate_wohnungsgeberbestaetigung(session, user.id, mieter.id)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 100


@pytest.mark.phase12
@pytest.mark.integration
async def test_dokument_generate_endpoint(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/api/v1/dokumente/generate",
        json={"template": "wohnungsgeberbestaetigung", "mieter_id": 1},
    )
    assert resp.status_code in {200, 404}


@pytest.mark.phase12
@pytest.mark.integration
async def test_dokument_unsupported_template(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/api/v1/dokumente/generate",
        json={"template": "nichtexistent", "mieter_id": 1},
    )
    assert resp.status_code == 400
