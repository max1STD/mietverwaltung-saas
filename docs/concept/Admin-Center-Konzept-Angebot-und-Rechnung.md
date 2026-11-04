# Admin-Center — Angebotserstellung und Rechnungsverwaltung

> **Status:** Konzept-Erweiterung v1.0  
> **Datum:** 2. November 2026  
> **Zweck:** Admin-Center erweitern um Angebote (Custom Pricing ≥ 50 WE), Rechnungen und E-Rechnungen  
> **Bezug:** Ergänzt `/root/mietverwaltung/Admin-Center-Konzept.md`  

---

## Kapitel A: Angebotserstellung und Rechnungsverwaltung im Admin-Center

### 1. Angebotserstellung (für ab 50 WE / Custom Pricing)

#### Ziel

Für Vermieter mit **≥ 50 Wohneinheiten** greift das Standard-Pro-WE-Preismodell (9,75 EUR Basis + Staffelrabatte) nicht mehr automatisch. Der Admin muss im Admin-Center ein **individuelles Angebot** erstellen, als PDF versenden und online zur Annahme freigeben.

#### Ablauf

1. Admin öffnet **„Neues Angebot“** im Admin-Center.
2. System zieht automatisch **Stammdaten aus der DB**:
   - Vermieter-Name, -Adresse, -E-Mail, -Telefon
   - Aktuelle WE-Anzahl (`plan_usage.wohnungen_count`)
   - Aktueller Plan (`subscriptions.plan`)
3. Admin gibt ein:
   - **Preis pro WE** (individuell)
   - **Laufzeit**: monatlich / jährlich / 2-jährlich
   - **Rabatt** (% oder absolut)
   - **Sonderbedingungen** (Freitext)
4. System berechnet **live**:
   - monatlicher Betrag
   - jährlicher Betrag
   - Ersparnis gegenüber Standardpreis
5. Admin generiert **PDF** (WeasyPrint + Jinja2).
6. System sendet E-Mail mit **Accept-Link** an Vermieter.
7. Vermieter klickt Accept-Link → Stripe-Subscription wird automatisch erstellt.
8. Status wechselt zu `angenommen`.

#### DB: Tabelle `angebots`

```sql
-- ============================================================
-- angebots — Angebotserstellung für Custom Pricing (≥ 50 WE)
-- ============================================================
CREATE TABLE angebots (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    admin_id            INT NOT NULL REFERENCES users(id),
    preis_pro_we        DECIMAL(10,2) NOT NULL,          -- individueller Preis pro WE
    we_bereich          INT NOT NULL,                    -- Anzahl WE zum Zeitpunkt des Angebots
    laufzeit            VARCHAR(20) NOT NULL
                        CHECK (laufzeit IN ('monatlich','jaehrlich','2-jaehrlich')),
    rabatt_prozent      DECIMAL(5,2) DEFAULT 0.00,     -- optionaler Rabatt in %
    rabatt_betrag       DECIMAL(10,2) DEFAULT 0.00,     -- optionaler absoluter Rabatt
    sonderbedingungen   TEXT,
    monatlicher_betrag  DECIMAL(10,2) NOT NULL,
    jaehrlicher_betrag  DECIMAL(10,2) NOT NULL,
    ersparnis           DECIMAL(10,2) DEFAULT 0.00,
    status              VARCHAR(20) NOT NULL DEFAULT 'entwurf'
                        CHECK (status IN ('entwurf','versendet','angenommen','abgelehnt','abgelaufen')),
    gueltig_bis         DATE NOT NULL,                 -- z. B. NOW() + 30 Tage
    accept_token        UUID DEFAULT gen_random_uuid(),  -- geheimer Annahme-Token
    pdf_path            VARCHAR(255),
    sent_at             TIMESTAMPTZ,
    accepted_at         TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_angebots_vermieter   ON angebots(vermieter_id);
CREATE INDEX idx_angebots_status      ON angebots(status);
CREATE INDEX idx_angebots_created     ON angebots(created_at);
CREATE INDEX idx_angebots_accept_token ON angebots(accept_token);

ALTER TABLE angebots ENABLE ROW LEVEL SECURITY;
CREATE POLICY angebots_admin_only ON angebots
    FOR ALL USING (current_setting('app.current_user_role') = 'admin');
```

#### FastAPI Endpoints

```python
# backend/app/routers/admin/angebots.py
# Präfix: /api/admin/angebots
# Endpunkte: POST /, GET /, GET /{id}, POST /{id}/senden, POST /angebot/{id}/accept/{token} (public)
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db, require_admin, client_ip, log_admin_action
from app.services import angebot_service, email_service, stripe_service
from app.schemas.admin import AngebotCreate, AngebotOut, AngebotSenden

router = APIRouter(prefix="/api/admin/angebots", tags=["admin-angebots"])

# POST /api/admin/angebots
@router.post("/", response_model=AngebotOut, status_code=201)
async def create_angebot(
    payload: AngebotCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin),
    ip = Depends(client_ip),
):
    """
    Erstellt ein neues Angebot (Entwurf).
    Berechnet monatlichen/jährlichen Betrag und Ersparnis vs. Standardpreis.
    """
    angebot = await angebot_service.create(db, payload, admin_id=admin.id)
    await log_admin_action(
        db, admin.id, "angebot_created", "angebots", angebot.id,
        payload.model_dump(), ip, risk_level="mittel"
    )
    return angebot

# GET /api/admin/angebots
@router.get("/", response_model=list[AngebotOut])
async def list_angebots(
    status: str | None = None,
    vermieter_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin),
):
    """Liste aller Angebote (optional gefiltert)."""
    return await angebot_service.list(db, status=status, vermieter_id=vermieter_id)

# GET /api/admin/angebots/{id}
@router.get("/{angebot_id}", response_model=AngebotOut)
async def get_angebot(
    angebot_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin),
):
    angebot = await db.get(Angebot, angebot_id)
    if not angebot:
        raise HTTPException(404, "Angebot nicht gefunden")
    return angebot

# POST /api/admin/angebots/{id}/senden
@router.post("/{angebot_id}/senden", response_model=AngebotOut)
async def send_angebot(
    angebot_id: int,
    payload: AngebotSenden,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin),
    ip = Depends(client_ip),
):
    """
    Generiert PDF, sendet E-Mail mit Accept-Link und setzt Status auf 'versendet'.
    """
    angebot = await angebot_service.get(db, angebot_id)
    pdf_path = await angebot_service.generate_pdf(db, angebot)

    background_tasks.add_task(
        email_service.send_angebot_email,
        angebot.vermieter.email,
        angebot_id=angebot.id,
        accept_token=str(angebot.accept_token),
        pdf_path=pdf_path,
    )

    angebot.status = "versendet"
    angebot.sent_at = datetime.utcnow()
    angebot.pdf_path = pdf_path
    await db.commit()

    await log_admin_action(
        db, admin.id, "angebot_sent", "angebots", angebot.id,
        {"recipient": angebot.vermieter.email}, ip, risk_level="mittel"
    )
    return angebot


# Öffentlicher Accept-Endpunkt (nicht admin-geschützt, nur Token)
# backend/app/routers/public/angebot_accept.py
from fastapi import APIRouter, HTTPException
from app.services import stripe_service, angebot_service

router = APIRouter(prefix="/angebot", tags=["angebot-accept"])

@router.post("/{angebot_id}/accept/{token}")
async def accept_angebot(
    angebot_id: int,
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Vermieter nimmt Angebot online an.
    Erstellt automatisch Stripe-Subscription mit individuellem Preis.
    """
    angebot = await angebot_service.get_by_token(db, angebot_id, token)
    if angebot.status != "versendet":
        raise HTTPException(400, "Angebot nicht mehr gültig")
    if angebot.gueltig_bis < date.today():
        angebot.status = "abgelaufen"
        await db.commit()
        raise HTTPException(410, "Angebot ist abgelaufen")

    subscription = await stripe_service.create_custom_subscription(
        vermieter_id=angebot.vermieter_id,
        preis_pro_we=float(angebot.preis_pro_we),
        we_count=angebot.we_bereich,
        laufzeit=angebot.laufzeit,
    )

    # Subscription in DB speichern
    await subscription_service.activate_custom(
        db,
        vermieter_id=angebot.vermieter_id,
        stripe_subscription_id=subscription.id,
        preis_pro_we=angebot.preis_pro_we,
        laufzeit=angebot.laufzeit,
    )

    angebot.status = "angenommen"
    angebot.accepted_at = datetime.utcnow()
    await db.commit()

    await email_service.send_angebot_accepted_confirmation(angebot.vermieter.email)
    return {"status": "angenommen", "stripe_subscription_id": subscription.id}
```

#### Service: Angebot berechnen & PDF generieren

```python
# backend/app/services/admin/angebot_service.py
from decimal import Decimal
from datetime import date, timedelta
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

STANDARD_PREIS_PRO_WE = Decimal("9.75")

def berechne_angebot(
    preis_pro_we: Decimal,
    we_count: int,
    laufzeit: str,
    rabatt_prozent: Decimal = Decimal("0.00"),
    rabatt_betrag: Decimal = Decimal("0.00"),
) -> dict:
    monatlich_netto = preis_pro_we * Decimal(we_count)
    if laufzeit == "jaehrlich":
        monatlich_netto *= Decimal("0.90")  # 10% Jahresrabatt
    elif laufzeit == "2-jaehrlich":
        monatlich_netto *= Decimal("0.85")  # 15% Zweijahresrabatt

    rabatt = monatlich_netto * (rabatt_prozent / Decimal("100")) + rabatt_betrag
    monatlicher_betrag = max(Decimal("0"), monatlich_netto - rabatt).quantize(Decimal("0.01"))
    jaehrlicher_betrag = (monatlicher_betrag * Decimal("12")).quantize(Decimal("0.01"))

    standard_monatlich = (STANDARD_PREIS_PRO_WE * Decimal(we_count)).quantize(Decimal("0.01"))
    ersparnis = (standard_monatlich - monatlicher_betrag).quantize(Decimal("0.01"))

    return {
        "monatlicher_betrag": monatlicher_betrag,
        "jaehrlicher_betrag": jaehrlicher_betrag,
        "ersparnis": ersparnis,
    }

async def generate_pdf(db: AsyncSession, angebot: Angebot) -> str:
    vermieter = await db.get(User, angebot.vermieter_id)
    env = Environment(loader=FileSystemLoader("templates/angebote"))
    template = env.get_template("angebot.html")
    html_out = template.render(
        angebot=angebot,
        vermieter=vermieter,
        heute=date.today().strftime("%d.%m.%Y"),
    )
    pdf_path = f"storage/angebote/angebot-{angebot.id}.pdf"
    HTML(string=html_out).write_pdf(pdf_path)
    return pdf_path
```

#### Pydantic Schemas

```python
# backend/app/schemas/admin.py
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date
from typing import Literal

class AngebotCreate(BaseModel):
    vermieter_id: int
    preis_pro_we: Decimal = Field(..., gt=0)
    laufzeit: Literal["monatlich", "jaehrlich", "2-jaehrlich"]
    rabatt_prozent: Decimal = Field(0, ge=0, le=100)
    rabatt_betrag: Decimal = Field(0, ge=0)
    sonderbedingungen: str | None = None
    gueltig_bis: date | None = None  # default 30 Tage

class AngebotOut(BaseModel):
    id: int
    vermieter_id: int
    vermieter_name: str
    admin_id: int
    preis_pro_we: Decimal
    we_bereich: int
    laufzeit: str
    rabatt_prozent: Decimal
    monatlicher_betrag: Decimal
    jaehrlicher_betrag: Decimal
    ersparnis: Decimal
    status: str
    gueltig_bis: date
    pdf_path: str | None
    created_at: datetime

class AngebotSenden(BaseModel):
    subject: str = "Ihr individuelles Angebot — MietVerwaltung"
    message: str | None = None
```

#### Vue.js Komponenten-Struktur

```
frontend/src/views/admin/
├── AngeboteListe.vue
└── AngebotEditor.vue

frontend/src/components/admin/angebote/
├── AngebotForm.vue          # Formular + Live-Berechnung
├── AngebotPreview.vue       # PDF-Vorschau / Download
├── AngebotStatusBadge.vue
└── AngebotEmailModal.vue
```

```vue
<!-- AngebotForm.vue -->
<template>
  <form @submit.prevent="submit" class="angebot-form">
    <div class="form-row">
      <label>Preis pro WE (€)</label>
      <input v-model.number="form.preis_pro_we" type="number" step="0.01" min="0" />
    </div>
    <div class="form-row">
      <label>Laufzeit</label>
      <select v-model="form.laufzeit">
        <option value="monatlich">Monatlich</option>
        <option value="jaehrlich">Jährlich (10% Rabatt)</option>
        <option value="2-jaehrlich">2-jährlich (15% Rabatt)</option>
      </select>
    </div>
    <div class="form-row">
      <label>Rabatt (%)</label>
      <input v-model.number="form.rabatt_prozent" type="number" min="0" max="100" />
    </div>
    <div class="form-row">
      <label>Sonderbedingungen</label>
      <textarea v-model="form.sonderbedingungen" rows="3" />
    </div>

    <div class="live-calculation card">
      <div class="calc-row"><span>WE-Anzahl:</span><strong>{{ stammdaten.we_count }}</strong></div>
      <div class="calc-row"><span>Monatlich:</span><strong>{{ formatEUR(calculated.monatlicher_betrag) }}</strong></div>
      <div class="calc-row"><span>Jährlich:</span><strong>{{ formatEUR(calculated.jaehrlicher_betrag) }}</strong></div>
      <div class="calc-row"><span>Ersparnis vs. Standard:</span><strong class="green">{{ formatEUR(calculated.ersparnis) }}</strong></div>
    </div>
  </form>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps(['form', 'stammdaten'])

const calculated = computed(() => {
  const p = Number(props.form.preis_pro_we) || 0
  const we = Number(props.stammdaten.we_count) || 0
  const rabattPct = Number(props.form.rabatt_prozent) || 0
  let monthly = p * we
  if (props.form.laufzeit === 'jaehrlich') monthly *= 0.90
  if (props.form.laufzeit === '2-jaehrlich') monthly *= 0.85
  monthly -= monthly * (rabattPct / 100)
  const yearly = monthly * 12
  const standard = 9.75 * we
  return {
    monatlicher_betrag: monthly,
    jaehrlicher_betrag: yearly,
    ersparnis: standard - monthly,
  }
})
</script>
```

---

### 2. Rechnungserstellung

#### Automatische Rechnungen

Stripe generiert bei jeder erfolgreichen Zahlung automatisch eine Rechnung (`Invoice`). Unser System holt diese über Webhook oder Stripe-Sync ab und speichert sie in der `rechnungen`-Tabelle (Caching + lokale Rechnungsnummer).

#### Manuelle Rechnungen

Admin kann manuelle Rechnungen erstellen für:
- Custom Pricing (z. B. abweichender Zyklus)
- Einmalige Setup-Gebühr
- Zusatzleistungen (Migration, Schulung, Custom-Entwicklung)

#### Rechnungsdaten aus DB

| Feld | Quelle |
|------|--------|
| Vermieter-Name | `users.full_name` |
| Vermieter-Adresse | `users.adresse` (wenn vorhanden) oder Hauptobjekt (`objekte.adresse`) |
| Vermieter-E-Mail | `users.email` |
| Vermieter-Telefon | `users.phone` |
| USt-Id | `users.ust_id` (NEU) |
| Steuerbefreit | `users.steuerbefreit` (NEU, z. B. private GbR) |
| WE-Anzahl | `plan_usage.wohnungen_count` |
| Plan | `subscriptions.plan` |

#### Rechnungsnummer-Format

```
MV-2026-0001
MV-2026-0002
...
MV-2027-0001  (neues Jahr, Zähler reset)
```

Fortlaufend pro Kalenderjahr. Sperrung über `SELECT FOR UPDATE` auf `rechnungsnummer_zaehler`.

#### DB: Tabelle `rechnungen`

```sql
-- ============================================================
-- rechnungen — Rechnungen (Stripe + manuell)
-- ============================================================
CREATE TABLE rechnungen (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rechnungs_nr        VARCHAR(20) UNIQUE NOT NULL,     -- MV-YYYY-NNNN
    rechnungs_datum     DATE NOT NULL DEFAULT CURRENT_DATE,
    leistungszeitraum_von DATE,
    leistungszeitraum_bis DATE,
    betrag              DECIMAL(10,2) NOT NULL,          -- Netto
    ust_betrag          DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    gesamt_betrag       DECIMAL(10,2) NOT NULL,
    ust_satz            DECIMAL(5,2) NOT NULL DEFAULT 19.00,
    ust_befreit         BOOLEAN DEFAULT FALSE,
    status              VARCHAR(20) NOT NULL DEFAULT 'entwurf'
                        CHECK (status IN ('entwurf','versendet','bezahlt','storniert')),
    stripe_invoice_id   VARCHAR(255),                  -- falls aus Stripe
    pdf_path            VARCHAR(255),
    xrechnung_xml       TEXT,                           -- XML für E-Rechnung
    zugferd_pdf_path    VARCHAR(255),                   -- ZUGFeRD-PDF
    paid_at             TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_rechnungen_vermieter      ON rechnungen(vermieter_id);
CREATE INDEX idx_rechnungen_nr             ON rechnungen(rechnungs_nr);
CREATE INDEX idx_rechnungen_status         ON rechnungen(status);
CREATE INDEX idx_rechnungen_stripe         ON rechnungen(stripe_invoice_id);
CREATE INDEX idx_rechnungen_created        ON rechnungen(rechnungs_datum);

ALTER TABLE rechnungen ENABLE ROW LEVEL SECURITY;
CREATE POLICY rechnungen_admin_only ON rechnungen
    FOR ALL USING (current_setting('app.current_user_role') = 'admin');
```

#### Hilfstabelle: Rechnungsnummer-Zähler

```sql
CREATE TABLE rechnungsnummer_zaehler (
    jahr    INT PRIMARY KEY,
    zaehler INT NOT NULL DEFAULT 0
);
```

#### FastAPI Endpoints

```python
# backend/app/routers/admin/rechnungen.py
# Präfix: /api/admin/rechnungen
# Endpunkte: POST /, GET /, GET /{id}, POST /{id}/senden, POST /{id}/stornieren
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, require_admin, client_ip, log_admin_action
from app.services import rechnung_service, email_service
from app.schemas.admin import RechnungCreate, RechnungOut, RechnungPosition

router = APIRouter(prefix="/api/admin/rechnungen", tags=["admin-rechnungen"])

# POST /api/admin/rechnungen
@router.post("/", response_model=RechnungOut, status_code=201)
async def create_rechnung(
    payload: RechnungCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin),
    ip = Depends(client_ip),
):
    """
    Erstellt eine manuelle Rechnung (Entwurf).
    Rechnungsnummer wird fortlaufend pro Jahr vergeben.
    """
    rechnung = await rechnung_service.create_manual(db, payload, admin_id=admin.id)
    await log_admin_action(
        db, admin.id, "rechnung_created", "rechnungen", rechnung.id,
        payload.model_dump(), ip, risk_level="mittel"
    )
    return rechnung

# GET /api/admin/rechnungen
@router.get("/", response_model=list[RechnungOut])
async def list_rechnungen(
    status: str | None = None,
    vermieter_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin),
):
    return await rechnung_service.list(db, status=status, vermieter_id=vermieter_id)

# GET /api/admin/rechnungen/{id}
@router.get("/{rechnung_id}", response_model=RechnungOut)
async def get_rechnung(
    rechnung_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin),
):
    rechnung = await db.get(Rechnung, rechnung_id)
    if not rechnung:
        raise HTTPException(404, "Rechnung nicht gefunden")
    return rechnung

# POST /api/admin/rechnungen/{id}/senden
@router.post("/{rechnung_id}/senden", response_model=RechnungOut)
async def send_rechnung(
    rechnung_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin),
    ip = Depends(client_ip),
):
    """Generiert PDF, sendet E-Mail und setzt Status auf 'versendet'."""
    rechnung = await rechnung_service.get(db, rechnung_id)
    pdf_path = await rechnung_service.generate_pdf(db, rechnung)

    background_tasks.add_task(
        email_service.send_rechnung_email,
        to=rechnung.vermieter.email,
        rechnung_id=rechnung.id,
        pdf_path=pdf_path,
    )

    rechnung.status = "versendet"
    rechnung.pdf_path = pdf_path
    await db.commit()

    await log_admin_action(
        db, admin.id, "rechnung_sent", "rechnungen", rechnung.id,
        {"recipient": rechnung.vermieter.email}, ip, risk_level="mittel"
    )
    return rechnung

# POST /api/admin/rechnungen/{id}/stornieren
@router.post("/{rechnung_id}/stornieren", response_model=RechnungOut)
async def storniere_rechnung(
    rechnung_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin),
    ip = Depends(client_ip),
):
    rechnung = await rechnung_service.stornieren(db, rechnung_id)
    await log_admin_action(
        db, admin.id, "rechnung_storniert", "rechnungen", rechnung.id,
        {}, ip, risk_level="hoch"
    )
    return rechnung
```

#### Service: Rechnung erstellen + PDF

```python
# backend/app/services/admin/rechnung_service.py
from decimal import Decimal
from datetime import date
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def next_rechnungsnummer(db: AsyncSession, jahr: int = None) -> str:
    jahr = jahr or date.today().year
    # Atomic increment
    row = await db.execute(
        select(RechnungsnummerZaehler).where(RechnungsnummerZaehler.jahr == jahr).with_for_update()
    )
    zaehler = row.scalar_one_or_none()
    if not zaehler:
        zaehler = RechnungsnummerZaehler(jahr=jahr, zaehler=0)
        db.add(zaehler)
    zaehler.zaehler += 1
    await db.flush()
    return f"MV-{jahr}-{zaehler.zaehler:04d}"

async def create_manual(db: AsyncSession, payload: RechnungCreate, admin_id: int):
    vermieter = await db.get(User, payload.vermieter_id)
    ust_satz = Decimal("0.00") if vermieter.ust_befreit else Decimal("19.00")

    netto = sum(p.betrag for p in payload.positionen)
    ust = (netto * ust_satz / Decimal("100")).quantize(Decimal("0.01"))
    gesamt = (netto + ust).quantize(Decimal("0.01"))

    rechnung = Rechnung(
        vermieter_id=payload.vermieter_id,
        rechnungs_nr=await next_rechnungsnummer(db),
        rechnungs_datum=payload.rechnungs_datum or date.today(),
        leistungszeitraum_von=payload.leistungszeitraum_von,
        leistungszeitraum_bis=payload.leistungszeitraum_bis,
        betrag=netto,
        ust_betrag=ust,
        gesamt_betrag=gesamt,
        ust_satz=ust_satz,
        ust_befreit=vermieter.ust_befreit,
        status="entwurf",
    )
    db.add(rechnung)
    await db.commit()
    await db.refresh(rechnung)
    return rechnung

async def generate_pdf(db: AsyncSession, rechnung: Rechnung) -> str:
    vermieter = await db.get(User, rechnung.vermieter_id)
    env = Environment(loader=FileSystemLoader("templates/rechnungen"))
    template = env.get_template("rechnung.html")
    html_out = template.render(
        rechnung=rechnung,
        vermieter=vermieter,
        positionen=rechnung.positionen,
    )
    pdf_path = f"storage/rechnungen/{rechnung.rechnungs_nr}.pdf"
    HTML(string=html_out).write_pdf(pdf_path)
    return pdf_path
```

#### Rechnungs-Template (Jinja2 → WeasyPrint)

```html
<!-- templates/rechnungen/rechnung.html -->
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #1d1d1f; padding: 48px; }
    .header { display: flex; justify-content: space-between; border-bottom: 2px solid #0D3B70; padding-bottom: 24px; margin-bottom: 32px; }
    .logo { font-size: 24px; font-weight: 700; color: #0D3B70; }
    .meta { text-align: right; font-size: 14px; }
    .address { margin-bottom: 32px; font-size: 14px; line-height: 1.6; }
    table { width: 100%; border-collapse: collapse; margin-top: 24px; }
    th { background: #f5f5f7; text-align: left; padding: 10px; font-size: 13px; }
    td { padding: 10px; border-bottom: 1px solid #e2e2e7; font-size: 14px; }
    .totals { margin-top: 24px; width: 40%; margin-left: auto; }
    .totals td { border: none; text-align: right; }
    .totals .grand { font-size: 18px; font-weight: 700; color: #0D3B70; }
  </style>
</head>
<body>
  <div class="header">
    <div class="logo">MietVerwaltung</div>
    <div class="meta">
      <div>Rechnungsnummer: {{ rechnung.rechnungs_nr }}</div>
      <div>Datum: {{ rechnung.rechnungs_datum.strftime('%d.%m.%Y') }}</div>
    </div>
  </div>

  <div class="address">
    <strong>{{ vermieter.full_name }}</strong><br>
    {{ vermieter.adresse|nl2br }}<br>
    {% if vermieter.ust_id %}USt-Id: {{ vermieter.ust_id }}<br>{% endif %}
  </div>

  <h2>Rechnung</h2>
  <p>Leistungszeitraum: {{ rechnung.leistungszeitraum_von }} – {{ rechnung.leistungszeitraum_bis }}</p>

  <table>
    <thead>
      <tr><th>Pos.</th><th>Bezeichnung</th><th>Menge</th><th>Einzelpreis</th><th>Gesamt</th></tr>
    </thead>
    <tbody>
      {% for p in positionen %}
      <tr>
        <td>{{ loop.index }}</td>
        <td>{{ p.bezeichnung }}</td>
        <td>{{ p.menge }}</td>
        <td>{{ "%0.2f"|format(p.einzelpreis) }} €</td>
        <td>{{ "%0.2f"|format(p.betrag) }} €</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <table class="totals">
    <tr><td>Zwischensumme (netto)</td><td>{{ "%0.2f"|format(rechnung.betrag) }} €</td></tr>
    <tr>
      <td>
        {% if rechnung.ust_befreit %}USt.-befreit (privater Verkäufer){% else %}USt. {{ rechnung.ust_satz }}%{% endif %}
      </td>
      <td>{{ "%0.2f"|format(rechnung.ust_betrag) }} €</td>
    </tr>
    <tr class="grand"><td>Gesamtbetrag</td><td>{{ "%0.2f"|format(rechnung.gesamt_betrag) }} €</td></tr>
  </table>
</body>
</html>
```

---

### 3. E-Rechnung (elektronische Rechnung)

#### Was ist eine E-Rechnung?

Eine **E-Rechnung** ist ein strukturiertes, maschinenlesbares Rechnungsformat. In Deutschland sind zwei Varianten relevant:

- **XRechnung**: XML-basiertes Format nach EN 16931, verpflichtend für **B2G** (Behörden) und ab 2025/2026 zunehmend für **B2B**.
- **ZUGFeRD**: PDF/A mit eingebetteter XML-Datei (EN 16931-konform), besser für B2B geeignet.

#### Rechtsgrundlage

- **EU-Richtlinie 2014/55/EU** verpflichtet öffentliche Auftraggeber, elektronische Rechnungen anzunehmen.
- Ab 2025/2026 wird die **E-Rechnung-Pflicht für B2B** in Deutschland schrittweise eingeführt.
- Als SaaS-Anbieter müssen wir E-Rechnungen ausstellen können, wenn ein gewerblicher Kunde eine USt-Id hat und explizit danach fragt (z. B. öffentliche Auftraggeber, größere Wohnungsgesellschaften).

#### Wann erzeugen wir E-Rechnungen?

| Kunde | USt-Id | E-Rechnung |
|-------|--------|------------|
| Privater Vermieter / GbR | nein / steuerbefreit | nein |
| Gewerblicher Vermieter (z. B. GmbH) | ja | ja (XRechnung oder ZUGFeRD) |
| Öffentlicher Auftraggeber | ja | ja (XRechnung empfohlen) |

#### Tools

| Tool | Sprache | Zweck |
|------|---------|-------|
| `python-xrechnung` | Python | XRechnung-XML erzeugen |
| `mustanglibrary` | Java | ZUGFeRD validieren + erzeugen |
| `stingray` / `drafthorse` | Python | ZUGFeRD PDF erzeugen |

Wir empfehlen:
- **XRechnung**: `python-xrechnung` oder selbstgebautes XML-Template (EN 16931).
- **ZUGFeRD**: `drafthorse` oder `mustanglibrary` als externes Tool.

#### Konkretes XRechnung-XML-Beispiel

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
         xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
         xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
         xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
  <rsm:ExchangedDocumentContext>
    <ram:BusinessProcessSpecifiedDocumentContextParameter>
      <ram:ID>urn:fdc:peppol.eu:2017:poacc:billing:01:1.0</ram:ID>
    </ram:BusinessProcessSpecifiedDocumentContextParameter>
    <ram:GuidelineSpecifiedDocumentContextParameter>
      <ram:ID>urn:cen.eu:en16931:2017</ram:ID>
    </ram:GuidelineSpecifiedDocumentContextParameter>
  </rsm:ExchangedDocumentContext>

  <rsm:ExchangedDocument>
    <ram:ID>MV-2026-0001</ram:ID>
    <ram:TypeCode>380</ram:TypeCode>  <!-- Rechnung -->
    <ram:IssueDateTime>
      <udt:DateTimeString format="102">20261102</udt:DateTimeString>
    </ram:IssueDateTime>
  </rsm:ExchangedDocument>

  <rsm:SupplyChainTradeTransaction>
    <!-- Verkäufer (MietVerwaltung SaaS) -->
    <ram:ApplicableHeaderTradeAgreement>
      <ram:SellerTradeParty>
        <ram:Name>MietVerwaltung GmbH</ram:Name>
        <ram:PostalTradeAddress>
          <ram:PostcodeCode>12345</ram:PostcodeCode>
          <ram:LineOne>Musterstraße 1</ram:LineOne>
          <ram:CityName>Berlin</ram:CityName>
          <ram:CountryID>DE</ram:CountryID>
        </ram:PostalTradeAddress>
        <ram:SpecifiedTaxRegistration>
          <ram:ID schemeID="VA">DE123456789</ram:ID>
        </ram:SpecifiedTaxRegistration>
      </ram:SellerTradeParty>

      <!-- Käufer (Vermieter) -->
      <ram:BuyerTradeParty>
        <ram:Name>Immobilien Müller GmbH</ram:Name>
        <ram:PostalTradeAddress>
          <ram:PostcodeCode>10115</ram:PostcodeCode>
          <ram:LineOne>Friedrichstraße 100</ram:LineOne>
          <ram:CityName>Berlin</ram:CityName>
          <ram:CountryID>DE</ram:CountryID>
        </ram:PostalTradeAddress>
        <ram:SpecifiedTaxRegistration>
          <ram:ID schemeID="VA">DE987654321</ram:ID>
        </ram:SpecifiedTaxRegistration>
      </ram:BuyerTradeParty>
    </ram:ApplicableHeaderTradeAgreement>

    <!-- Leistungszeitraum + Zahlungsbedingungen -->
    <ram:ApplicableHeaderTradeDelivery>
      <ram:ActualDeliverySupplyChainEvent>
        <ram:OccurrenceDateTime>
          <udt:DateTimeString format="102">20261102</udt:DateTimeString>
        </ram:OccurrenceDateTime>
      </ram:ActualDeliverySupplyChainEvent>
    </ram:ApplicableHeaderTradeDelivery>

    <ram:ApplicableHeaderTradeSettlement>
      <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
      <ram:SpecifiedTradeSettlementPaymentMeans>
        <ram:TypeCode>58</ram:TypeCode>  <!-- SEPA-Lastschrift -->
        <ram:PayeePartyCreditorFinancialAccount>
          <ram:IBANID>DE89370400440532013000</ram:IBANID>
        </ram:PayeePartyCreditorFinancialAccount>
      </ram:SpecifiedTradeSettlementPaymentMeans>

      <!-- Steuer -->
      <ram:ApplicableTradeTax>
        <ram:CalculatedAmount>113.05</ram:CalculatedAmount>
        <ram:TypeCode>VAT</ram:TypeCode>
        <ram:BasisAmount>595.00</ram:BasisAmount>
        <ram:CategoryCode>S</ram:CategoryCode>
        <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
      </ram:ApplicableTradeTax>

      <!-- Summen -->
      <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        <ram:LineTotalAmount>595.00</ram:LineTotalAmount>
        <ram:ChargeTotalAmount>0.00</ram:ChargeTotalAmount>
        <ram:AllowanceTotalAmount>0.00</ram:AllowanceTotalAmount>
        <ram:TaxBasisTotalAmount>595.00</ram:TaxBasisTotalAmount>
        <ram:TaxTotalAmount currencyID="EUR">113.05</ram:TaxTotalAmount>
        <ram:GrandTotalAmount>708.05</ram:GrandTotalAmount>
        <ram:DuePayableAmount>708.05</ram:DuePayableAmount>
      </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
    </ram:ApplicableHeaderTradeSettlement>

    <!-- Rechnungsposition -->
    <ram:IncludedSupplyChainTradeLineItem>
      <ram:AssociatedDocumentLineDocument>
        <ram:LineID>1</ram:LineID>
      </ram:AssociatedDocumentLineDocument>
      <ram:SpecifiedTradeProduct>
        <ram:Name>MietVerwaltung Pro — 67 WE (Custom Pricing)</ram:Name>
      </ram:SpecifiedTradeProduct>
      <ram:SpecifiedLineTradeAgreement>
        <ram:NetPriceProductTradePrice>
          <ram:ChargeAmount>8.88</ram:ChargeAmount>
        </ram:NetPriceProductTradePrice>
      </ram:SpecifiedLineTradeAgreement>
      <ram:SpecifiedLineTradeDelivery>
        <ram:BilledQuantity unitCode="C62">67</ram:BilledQuantity>  <!-- Stück -->
      </ram:SpecifiedLineTradeDelivery>
      <ram:SpecifiedLineTradeSettlement>
        <ram:ApplicableTradeTax>
          <ram:TypeCode>VAT</ram:TypeCode>
          <ram:CategoryCode>S</ram:CategoryCode>
          <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
        </ram:ApplicableTradeTax>
        <ram:SpecifiedTradeSettlementLineMonetarySummation>
          <ram:LineTotalAmount>595.00</ram:LineTotalAmount>
        </ram:SpecifiedTradeSettlementLineMonetarySummation>
      </ram:SpecifiedLineTradeSettlement>
    </ram:IncludedSupplyChainTradeLineItem>
  </rsm:SupplyChainTradeTransaction>
</Invoice>
```

Hier im Beispiel:
- **Rechnungsnummer**: `MV-2026-0001`
- **Leistung**: MietVerwaltung Pro, 67 WE, individueller Preis 8,88 €/WE
- **Netto**: 595,00 €
- **USt. 19%**: 113,05 €
- **Brutto**: 708,05 €

#### FastAPI Endpoints

```python
# backend/app/routers/admin/erechnung.py
# Präfix: /api/admin/rechnungen
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, require_admin
from app.services import erechnung_service

router = APIRouter(prefix="/api/admin/rechnungen", tags=["admin-erechnung"])

# GET /api/admin/rechnungen/{id}/xrechnung.xml
@router.get("/{rechnung_id}/xrechnung.xml")
async def get_xrechnung_xml(
    rechnung_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin),
):
    """Liefert XRechnung-XML (EN 16931) für eine Rechnung."""
    rechnung = await erechnung_service.get(db, rechnung_id)
    xml = await erechnung_service.generate_xrechnung_xml(db, rechnung)

    # Cachen in DB
    rechnung.xrechnung_xml = xml
    await db.commit()

    return Response(
        content=xml,
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename={rechnung.rechnungs_nr}.xml"
        }
    )

# GET /api/admin/rechnungen/{id}/zugferd.pdf
@router.get("/{rechnung_id}/zugferd.pdf")
async def get_zugferd_pdf(
    rechnung_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin),
):
    """Liefert ZUGFeRD-PDF/A (PDF + eingebettetes XML)."""
    rechnung = await erechnung_service.get(db, rechnung_id)
    pdf_bytes = await erechnung_service.generate_zugferd_pdf(db, rechnung)

    rechnung.zugferd_pdf_path = f"storage/zugferd/{rechnung.rechnungs_nr}.pdf"
    await db.commit()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={rechnung.rechnungs_nr}-zugferd.pdf"
        }
    )
```

#### Service: XRechnung + ZUGFeRD

```python
# backend/app/services/admin/erechnung_service.py
from lxml import etree
from decimal import Decimal
from datetime import date

# Simpler EN 16931 XML-Builder (alternativ: python-xrechnung)
def build_xrechnung_xml(rechnung, vermieter, seller) -> str:
    NS = {
        None: "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
        "ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
        "udt": "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100",
    }
    root = etree.Element("{%s}CrossIndustryInvoice" % NS[None], nsmap=NS)
    # ... XML-Builder wie im Beispiel oben ...
    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode()

async def generate_xrechnung_xml(db: AsyncSession, rechnung: Rechnung) -> str:
    vermieter = await db.get(User, rechnung.vermieter_id)
    seller = {
        "name": "MietVerwaltung GmbH",
        "strasse": "Musterstraße 1",
        "plz": "12345",
        "stadt": "Berlin",
        "ust_id": "DE123456789",
        "iban": "DE89370400440532013000",
    }
    return build_xrechnung_xml(rechnung, vermieter, seller)

async def generate_zugferd_pdf(db: AsyncSession, rechnung: Rechnung) -> bytes:
    """
    Erzeugt ZUGFeRD-PDF/A.
    Option A: drafthorse (Python) einbetten.
    Option B: mustanglibrary als externes CLI-Tool aufrufen.
    """
    xml = await generate_xrechnung_xml(db, rechnung)
    pdf_visual = await rechnung_service.generate_pdf_bytes(db, rechnung)

    # Pseudocode für drafthorse:
    # from drafthorse import pdf
    # return pdf.attach_xml(pdf_visual, xml, level="ZUGFeRD-Comfort")
    return pdf_visual  # Platzhalter: in Produktion drafthorse einsetzen
```

---

### 4. Stammdaten aus DB für Angebote/Rechnungen

#### Quellen

| Stammdatum | DB-Tabelle / Feld | Verwendung |
|------------|-------------------|------------|
| Vermieter-Name | `users.full_name` | Angebot, Rechnung, E-Mail |
| Vermieter-Adresse | `users.adresse` (bevorzugt) oder `objekte.adresse` (Hauptobjekt) | Rechnungsanschrift, Briefkopf |
| Vermieter-E-Mail | `users.email` | Angebot-Versand, Rechnungs-E-Mail |
| Vermieter-Telefon | `users.phone` | Detail-Screen, Support |
| USt-Id | `users.ust_id` (NEU) | E-Rechnung, Steuerberechnung |
| Steuerbefreit | `users.ust_befreit` (NEU) | USt. 0% oder 19% |
| Aktuelle WE-Anzahl | `plan_usage.wohnungen_count` (live) | Angebot, Preisberechnung |
| Aktueller Plan | `subscriptions.plan` | Angebot, Rechnungsposition |
| Zahlungshistorie | `payment_history` | Detail-Screen, Mahnwesen |

#### NEUE Felder in `users`

```sql
ALTER TABLE users ADD COLUMN ust_id VARCHAR(30);
ALTER TABLE users ADD COLUMN ust_befreit BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN adresse TEXT;  -- falls noch nicht vorhanden
ALTER TABLE users ADD COLUMN phone VARCHAR(30);  -- falls noch nicht vorhanden
```

#### Admin-Endpoint: Vermieter-Stammdaten

```python
# backend/app/routers/admin/vermieter.py
@router.get("/{vermieter_id}/stammdaten")
async def get_vermieter_stammdaten(
    vermieter_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin),
):
    """Liefert alle Stammdaten eines Vermieters für Angebot/Rechnung."""
    return await vermieter_service.get_stammdaten(db, vermieter_id)
```

```python
# backend/app/services/admin/vermieter_service.py
async def get_stammdaten(db: AsyncSession, vermieter_id: int) -> dict:
    user = await db.get(User, vermieter_id)
    if not user:
        raise HTTPException(404, "Vermieter nicht gefunden")

    plan_usage = await db.execute(
        select(PlanUsage).where(PlanUsage.vermieter_id == vermieter_id)
    )
    plan_usage = plan_usage.scalar_one_or_none()

    subscription = await db.execute(
        select(Subscription).where(Subscription.vermieter_id == vermieter_id)
    )
    subscription = subscription.scalar_one_or_none()

    # Adresse: users.adresse > objekte.adresse (Hauptobjekt)
    adresse = user.adresse
    if not adresse:
        objekt = await db.execute(
            select(Objekt).where(Objekt.vermieter_id == vermieter_id).limit(1)
        )
        objekt = objekt.scalar_one_or_none()
        adresse = objekt.adresse if objekt else None

    payments = await db.execute(
        select(PaymentHistory)
        .where(PaymentHistory.vermieter_id == vermieter_id)
        .order_by(PaymentHistory.created_at.desc())
        .limit(10)
    )

    return {
        "vermieter_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "adresse": adresse,
        "ust_id": user.ust_id,
        "ust_befreit": user.ust_befreit,
        "we_count": plan_usage.wohnungen_count if plan_usage else 0,
        "plan": subscription.plan if subscription else None,
        "subscription_status": subscription.status if subscription else None,
        "zahlungshistorie": [p.to_dict() for p in payments.scalars().all()],
    }
```

#### Frontend: Vermieter-Detail mit Stammdaten

```vue
<!-- VermieterDetail.vue -->
<template>
  <div class="vermieter-detail">
    <div class="card">
      <div class="card-title">Stammdaten</div>
      <div class="stamm-grid">
        <div><span>Name</span><strong>{{ stammdaten.full_name }}</strong></div>
        <div><span>E-Mail</span><strong>{{ stammdaten.email }}</strong></div>
        <div><span>Telefon</span><strong>{{ stammdaten.phone || '—' }}</strong></div>
        <div><span>Adresse</span><strong>{{ stammdaten.adresse || '—' }}</strong></div>
        <div><span>USt-Id</span><strong>{{ stammdaten.ust_id || '—' }}</strong></div>
        <div><span>Steuerbefreit</span><strong>{{ stammdaten.ust_befreit ? 'Ja' : 'Nein' }}</strong></div>
        <div><span>WE-Anzahl</span><strong>{{ stammdaten.we_count }}</strong></div>
        <div><span>Plan</span><strong>{{ stammdaten.plan }}</strong></div>
      </div>
      <div class="actions" style="margin-top: 16px;">
        <button class="btn btn-primary" @click="createAngebot">+ Angebot erstellen</button>
        <button class="btn btn-secondary" @click="createRechnung">+ Rechnung erstellen</button>
      </div>
    </div>
  </div>
</template>
```

---

### 5. Mockup-Erweiterung admin.html

Das Mockup unter `/root/mietverwaltung/mockup/admin.html` wird um folgende Screens erweitert:

| Screen | Inhalt |
|--------|--------|
| **Angebote** | Liste aller Angebote, Status-Badge, „Neues Angebot“-Button, Formular mit Live-Berechnung, PDF-Vorschau |
| **Rechnungen** | Liste aller Rechnungen, Rechnungsnummer, Betrag, Status, PDF-Vorschau, XRechnung/ZUGFeRD-Download |
| **Vermieter-Detail** | Alle Stammdaten für Angebot/Rechnung, Schnellaktionen „Angebot erstellen“ / „Rechnung erstellen“ |

Design bleibt identisch:
- Navy `#0D3B70`
- Apple-Style Cards
- Dark-Mode
- Mobile-First
- Single-File HTML, inline CSS+JS

Die konkrete Implementierung liegt in `/root/mietverwaltung/mockup/admin.html`.

---

## Kapitel B: Zusammenfassung und nächste Schritte

### Was wurde definiert?

| Bereich | Umsetzung |
|---------|-----------|
| **Angebote** | Tabelle `angebots`, FastAPI-CRUD + Senden + Accept, PDF via WeasyPrint, Stripe-Subscription-Automatisierung |
| **Rechnungen** | Tabelle `rechnungen`, fortlaufende Rechnungsnummer, Stripe-Caching, manuelle Rechnungen, PDF-Template |
| **E-Rechnung** | XRechnung-XML (EN 16931), ZUGFeRD-PDF, Endpoints `/xrechnung.xml` und `/zugferd.pdf`, USt-Id-Handling |
| **Stammdaten** | Quellen dokumentiert, neues Felder `ust_id`/`ust_befreit` in `users`, Admin-Endpoint `/stammdaten` |
| **Mockup** | `Angebote`, `Rechnungen`, `Vermieter-Detail` ergänzt im bestehenden Design-System |

### Nächste Schritte

1. **DB-Migration**: `angebots`, `rechnungen`, `rechnungsnummer_zaehler` anlegen; `users.ust_id` und `users.ust_befreit` hinzufügen.
2. **Backend**: Router `admin/angebots.py`, `admin/rechnungen.py`, `admin/erechnung.py` implementieren.
3. **PDF-Templates**: `templates/angebote/angebot.html` und `templates/rechnungen/rechnung.html` erstellen.
4. **E-Rechnung**: Entscheidung XRechnung-Builder vs. `python-xrechnung`; ZUGFeRD mit `drafthorse` / `mustanglibrary`.
5. **Stripe-Integration**: Custom-Price + Subscription für angenommene Angebote.
6. **Frontend**: Vue-Views `AngeboteListe`, `AngebotEditor`, `RechnungenListe`, `RechnungDetail`, `VermieterDetail` bauen.
7. **Sicherheit**: Admin-Audit-Log für jeden Endpunkt, 2FA/IP-Whitelist beibehalten.
8. **GoBD/DSGVO**: Rechnungen 10 Jahre aufbewahren, E-Rechnung-XML als Nachweis speichern.

---

## Anhang: API-Übersicht Angebot & Rechnung

| Methode | Path | Auth | Beschreibung |
|---------|------|------|--------------|
| POST | `/api/admin/angebots` | Admin | Angebot erstellen |
| GET | `/api/admin/angebots` | Admin | Angebote auflisten |
| GET | `/api/admin/angebots/{id}` | Admin | Angebot-Details |
| POST | `/api/admin/angebots/{id}/senden` | Admin | PDF + E-Mail senden |
| POST | `/angebot/{id}/accept/{token}` | Öffentlich | Vermieter nimmt Angebot an |
| POST | `/api/admin/rechnungen` | Admin | Manuelle Rechnung erstellen |
| GET | `/api/admin/rechnungen` | Admin | Rechnungen auflisten |
| GET | `/api/admin/rechnungen/{id}` | Admin | Rechnung-Details |
| POST | `/api/admin/rechnungen/{id}/senden` | Admin | Rechnung per E-Mail senden |
| POST | `/api/admin/rechnungen/{id}/stornieren` | Admin | Rechnung stornieren |
| GET | `/api/admin/rechnungen/{id}/xrechnung.xml` | Admin | XRechnung-XML download |
| GET | `/api/admin/rechnungen/{id}/zugferd.pdf` | Admin | ZUGFeRD-PDF download |
| GET | `/api/admin/vermieter/{id}/stammdaten` | Admin | Stammdaten für Angebot/Rechnung |
