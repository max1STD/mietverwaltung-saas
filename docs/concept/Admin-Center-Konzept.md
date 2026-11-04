# MietVerwaltung — Admin-Center Konzept

> **Status:** Konzept v1.0  
> **Datum:** 2. November 2026  
> **Zweck:** Internes Verwaltungs-Tool für uns als SaaS-Hersteller (Max + ggf. Mitarbeiter)  
> **Trennung:** Vollständig getrennt vom öffentlichen Vermieter- und Mieter-Portal  

---

## 1. Übersicht und Zweck

Das **Admin-Center** ist das interne Verwaltungs-Tool für uns als Hersteller der MietVerwaltung-SaaS. Es dient ausschließlich dazu, die gesamte Plattform zu überwachen, Kunden zu supporten, Zahlungen zu verwalten und Systemeinstellungen zu steuern.

### Kernanforderungen

| Aspekt | Spezifikation |
|--------|--------------|
| **Zielgruppe** | Max + autorisierte Mitarbeiter (intern) |
| **URL** | `admin.mietverwaltung.de` (später) oder `/admin` Route im selben Deployment mit separatem Router |
| **Zugriff** | Nur `users.role = 'admin'` |
| **Authentifizierung** | Separater Login-Bereich, nicht im öffentlichen Portal |
| **2FA** | Pflicht (TOTP oder E-Mail-Code-Fallback) |
| **IP-Whitelist** | Nur bekannte IPs (Büro, VPN, Home-Office) |
| **Audit-Log** | Jede Aktion wird protokolliert: wer, was, wann, IP |
| **Datenzugriff** | Admin ist technischer Superuser — kann alle Vermieter/Mieter-Daten lesen, aber nur im Support-Kontext |

### Warum getrennt?

- **Sicherheit:** Admin-Funktionen dürfen niemals über das gleiche UI wie Vermieter erreichbar sein.
- **Klarheit:** Interne KPIs, Zahlungsdaten und Kundendetails haben im Kundenportal nichts zu suchen.
- **Compliance:** DSGVO, GoBD und Stripe-Compliance erfordern getrennte Admin-Audit-Spuren.

---

## 2. Dashboard / KPI-Center

Das Admin-Dashboard zeigt vollständige, nicht-anonymisierte Plattform-Statistiken. Es ist die ehrliche Version der "Live-Stats", die wir auf der Website zeigen.

### KPI-Kategorien

| Bereich | Metrik | Datenquelle |
|---------|--------|-------------|
| **Vermieter** | Gesamt, aktiv, gesperrt, neu diese Woche/Monat | `users WHERE role = 'vermieter'` |
| **Mieter** | Gesamt, aktiv | `mieter` + `users WHERE role = 'mieter'` |
| **Wohnungen** | Gesamt verwaltet, vermietet, leer | `einheiten` + `mietvertraege` |
| **Revenue** | MRR, ARR, pro Plan | `subscriptions` + Stripe |
| **Churn** | Monat, Quartal, Jahr | `subscriptions.status = 'cancelled'` + Events |
| **Aktivität** | DAU/MAU aktiver Vermieter | `user_sessions` + `audit_logs` |
| **Registrierungen** | Pro Tag/Woche | `users.created_at` |
| **KI** | Aufrufe gesamt, Kosten, pro Vermieter | `ai_stored_results` |
| **E-Mail** | Gesendet, Bounce-Rate | `email_logs` |
| **Stripe** | Ausstehend, fehlgeschlagen, Rückbuchungen | Stripe API |

### Dashboard-Karten (Apple-Style)

```vue
<!-- AdminDashboard.vue -->
<template>
  <div class="admin-dashboard">
    <div class="kpi-grid">
      <KpiCard
        v-for="kpi in kpis"
        :key="kpi.id"
        :title="kpi.title"
        :value="kpi.value"
        :change="kpi.change"
        :trend="kpi.trend"
        :icon="kpi.icon"
      />
    </div>

    <div class="charts-row">
      <MrrChart :data="mrrSeries" />
      <VermieterChart :data="registrationSeries" />
    </div>

    <div class="recent-tables">
      <RecentRegistrations />
      <FailedPayments />
      <OpenSupportTickets />
    </div>
  </div>
</template>
```

### FastAPI Endpoint: Dashboard-KPIs

```python
# backend/app/routers/admin/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, require_admin
from app.services.admin import kpi_service

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/dashboard", response_model=AdminDashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    Liefert aggregierte KPIs für das Admin-Center.
    Caching via Redis (TTL 5 Min), da Aggregationen teuer sind.
    """
    return await kpi_service.get_dashboard(db)


# app/services/admin/kpi_service.py
async def get_dashboard(db: AsyncSession) -> AdminDashboardResponse:
    return AdminDashboardResponse(
        vermieter=await _vermieter_stats(db),
        mieter=await _mieter_stats(db),
        wohnungen=await _wohnungen_stats(db),
        revenue=await _revenue_stats(db),
        churn=await _churn_stats(db),
        aktivitaet=await _activity_stats(db),
        ki=await _ki_stats(db),
        email=await _email_stats(db),
        stripe=await _stripe_stats(db),
    )
```

### SQL-Abfragen für KPIs

```sql
-- Anzahl Vermieter gesamt / aktiv / neu diese Woche
SELECT
    COUNT(*) FILTER (WHERE role = 'vermieter' AND deleted_at IS NULL) AS vermieter_gesamt,
    COUNT(*) FILTER (WHERE role = 'vermieter' AND deleted_at IS NULL AND locked_until IS NULL) AS vermieter_aktiv,
    COUNT(*) FILTER (WHERE role = 'vermieter' AND created_at >= NOW() - INTERVAL '7 days') AS neu_diese_woche
FROM users;

-- MRR gesamt und pro Plan
SELECT
    s.plan,
    SUM(CASE
        WHEN s.plan = 'basis' THEN 14.90
        WHEN s.plan = 'pro' THEN 29.90
        WHEN s.plan = 'business' THEN 49.90
        ELSE 0
    END) AS mrr
FROM subscriptions s
WHERE s.status = 'active'
GROUP BY s.plan;

-- Aktive / vermietete Wohnungen
SELECT
    COUNT(*) AS wohnungen_gesamt,
    COUNT(*) FILTER (WHERE EXISTS (
        SELECT 1 FROM mietvertraege mv
        WHERE mv.einheit_id = e.id AND mv.status = 'aktiv' AND mv.deleted_at IS NULL
    )) AS wohnungen_vermietet
FROM einheiten e
WHERE e.deleted_at IS NULL;
```

---

## 3. Vermieter-Verwaltung

### Funktionsumfang

| Funktion | Beschreibung |
|----------|--------------|
| **Liste** | Alle Vermieter mit Name, E-Mail, Plan, WE-Anzahl, Status, MRR, Registriert am, Letzte Aktivität |
| **Suche** | Nach Name/E-Mail |
| **Filter** | Plan, Status, Registrierungsdatum, Letzte Aktivität |
| **Sperren** | Account suspendieren: Grund eingeben, E-Mail geht raus, Daten bleiben erhalten |
| **Entsperren** | Wieder aktivieren |
| **Details** | Alle Objekte, Einheiten, Mieter, Abrechnungen, Tickets einsehen (read-only) |
| **Abo bearbeiten** | Plan ändern, Upgrades/Downgrades als Admin |
| **Löschen** | DSGVO-Löschung mit Bestätigung, Export vorher, Audit-Log |
| **Passwort-Reset** | Admin löst Reset aus, Link an Vermieter-E-Mail |
| **Impersonate** | Als Vermieter einloggen (Support, Zeitlimit, Audit-Log) |

### FastAPI Endpoints

```python
# backend/app/routers/admin/vermieter.py
from fastapi import APIRouter, Depends, Query, Path, Body
from app.dependencies import get_db, require_admin, log_admin_action

router = APIRouter(prefix="/api/admin/vermieter", tags=["admin-vermieter"])

@router.get("/", response_model=PaginatedVermieterList)
async def list_vermieter(
    q: str | None = Query(None, description="Suche nach Name/E-Mail"),
    plan: str | None = Query(None),
    status: str | None = Query(None),
    registered_from: date | None = Query(None),
    registered_to: date | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Liste aller Vermieter mit Filter und Pagination."""
    return await vermieter_service.list(db, q, plan, status, registered_from, registered_to, limit, offset)

@router.get("/{vermieter_id}", response_model=VermieterAdminDetail)
async def get_vermieter(
    vermieter_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Vollständige Details eines Vermieters inkl. Objekte, Einheiten, Mieter, Abrechnungen."""
    return await vermieter_service.get_detail(db, vermieter_id)

@router.patch("/{vermieter_id}/suspend")
async def suspend_vermieter(
    vermieter_id: int,
    payload: SuspendRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    ip: str = Depends(client_ip),
):
    """Vermieter sperren. Grund wird per E-Mail an Vermieter geschickt."""
    result = await vermieter_service.suspend(db, vermieter_id, payload.reason)
    await log_admin_action(
        db, admin.id, "suspend_vermieter", "users", vermieter_id,
        {"reason": payload.reason}, ip, risk_level="hoch"
    )
    return result

@router.patch("/{vermieter_id}/unsuspend")
async def unsuspend_vermieter(
    vermieter_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    ip: str = Depends(client_ip),
):
    result = await vermieter_service.unsuspend(db, vermieter_id)
    await log_admin_action(db, admin.id, "unsuspend_vermieter", "users", vermieter_id, {}, ip, risk_level="mittel")
    return result

@router.patch("/{vermieter_id}/subscription")
async def update_subscription(
    vermieter_id: int,
    payload: AdminSubscriptionUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    ip: str = Depends(client_ip),
):
    """Plan ändern, Trial setzen, Limits anpassen. Sync mit Stripe."""
    result = await subscription_service.admin_update(db, vermieter_id, payload)
    await log_admin_action(
        db, admin.id, "subscription_update", "subscriptions", result.subscription_id,
        payload.model_dump(), ip, risk_level="hoch"
    )
    return result

@router.post("/{vermieter_id}/password-reset")
async def trigger_password_reset(
    vermieter_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    ip: str = Depends(client_ip),
):
    """Admin löst Passwort-Reset aus. Link wird an Vermieter-E-Mail gesendet."""
    token = await auth_service.create_password_reset_token(db, vermieter_id)
    await email_service.send_admin_password_reset(vermieter_id, token)
    await log_admin_action(db, admin.id, "password_reset", "users", vermieter_id, {}, ip, risk_level="hoch")
    return {"ok": True}

@router.post("/{vermieter_id}/impersonate")
async def impersonate_vermieter(
    vermieter_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    ip: str = Depends(client_ip),
):
    """
    Admin loggt sich als Vermieter ein (Support).
    Zeitlimit: 30 Min. Audit-Log. Vermieter bekommt E-Mail danach.
    """
    token = await auth_service.create_impersonation_token(db, admin.id, vermieter_id, ttl_minutes=30)
    await log_admin_action(db, admin.id, "impersonate_start", "users", vermieter_id, {}, ip, risk_level="hoch")
    return {"impersonation_token": token, "expires_in": 1800}

@router.delete("/{vermieter_id}")
async def delete_vermieter(
    vermieter_id: int,
    payload: DeleteVermieterRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    ip: str = Depends(client_ip),
):
    """
    DSGVO-Löschung eines Vermieters.
    Vorbedingung: Bestätigung via Checkbox + Daten-Export.
    """
    if not payload.confirm:
        raise HTTPException(400, "Löschung muss bestätigt werden")
    export_url = await dsgvo_service.export_vermieter_data(db, vermieter_id)
    await vermieter_service.schedule_deletion(db, vermieter_id, days=30)
    await log_admin_action(
        db, admin.id, "vermieter_delete", "users", vermieter_id,
        {"export_url": export_url, "delete_after_days": 30}, ip, risk_level="hoch"
    )
    return {"export_url": export_url, "scheduled_deletion": "+30d"}
```

### Sperren/E-Mail

```python
async def suspend(db: AsyncSession, vermieter_id: int, reason: str):
    user = await db.get(User, vermieter_id)
    user.locked_until = datetime.max  # gesperrt bis manuell entsperrt
    user.failed_login_count = 999
    await db.commit()

    await email_service.send(
        to=user.email,
        template="admin/account_suspended",
        context={"reason": reason, "support_email": "support@mietverwaltung.de"}
    )
    return {"status": "suspended"}
```

---

## 4. Mieter-Verwaltung

| Funktion | Beschreibung |
|----------|--------------|
| **Liste** | Alle Mieter aller Vermieter: Name, E-Mail, Vermieter, Status |
| **Suche/Filter** | Name, E-Mail, Vermieter, Status |
| **Sperren/Entsperren** | Bei Missbrauch |
| **Passwort-Reset** | Admin löst aus |
| **Details** | Tickets, Abrechnungen, Dokumente einsehen |
| **Löschen** | DSGVO-Löschung |

```python
# backend/app/routers/admin/mieter.py
router = APIRouter(prefix="/api/admin/mieter", tags=["admin-mieter"])

@router.get("/", response_model=PaginatedMieterList)
async def list_mieter(
    q: str | None = Query(None),
    vermieter_id: int | None = Query(None),
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return await mieter_service.list_all(db, q, vermieter_id, status)

@router.get("/{mieter_id}", response_model=MieterAdminDetail)
async def get_mieter(
    mieter_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return await mieter_service.get_detail(db, mieter_id)

@router.patch("/{mieter_id}/suspend")
async def suspend_mieter(...):
    ...

@router.delete("/{mieter_id}")
async def delete_mieter(...):
    ...
```

---

## 5. Zahlungs-Verwaltung (Stripe)

### Funktionsumfang

| Funktion | Beschreibung |
|----------|--------------|
| **Subscriptions** | Alle aktiven Subscriptions mit Status, Plan, Betrag, nächste Abbuchung |
| **Fehlgeschlagene Zahlungen** | Liste mit Retry-Status, manueller Retry |
| **Chargebacks** | Rückbuchungen anzeigen, Kunde markieren |
| **Manuelle Rechnung** | Für Custom Pricing großer Kunden |
| **Refund** | Rückerstattung auslösen |
| **Stripe-Sync** | DB mit Stripe abgleichen (manuell + Cron) |
| **Umsatz-Report** | Monat/Quartal/Jahr mit CSV-Export |
| **MRR-Chart** | Entwicklung grafisch |

### FastAPI Endpoints

```python
# backend/app/routers/admin/payments.py
router = APIRouter(prefix="/api/admin/payments", tags=["admin-payments"])

@router.get("/", response_model=PaginatedPaymentList)
async def list_payments(
    status: str | None = Query(None),
    plan: str | None = Query(None),
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return await payment_service.list_all(db, status, plan, from_date, to_date)

@router.get("/failed")
async def list_failed_payments(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return await stripe_service.list_failed_invoices()

@router.post("/{payment_id}/retry")
async def retry_payment(
    payment_id: str,
    admin: User = Depends(require_admin),
    ip: str = Depends(client_ip),
):
    result = await stripe_service.retry_invoice(payment_id)
    await log_admin_action(db, admin.id, "payment_retry", "stripe_invoice", payment_id, {}, ip, risk_level="mittel")
    return result

@router.post("/{payment_id}/refund")
async def refund_payment(
    payment_id: str,
    payload: RefundRequest,
    admin: User = Depends(require_admin),
    ip: str = Depends(client_ip),
):
    result = await stripe_service.refund(payment_id, amount=payload.amount_cents, reason=payload.reason)
    await log_admin_action(db, admin.id, "payment_refund", "stripe_payment", payment_id, payload.model_dump(), ip, risk_level="hoch")
    return result

@router.post("/sync")
async def sync_stripe(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    ip: str = Depends(client_ip),
):
    """Manueller Stripe-Sync."""
    result = await stripe_sync_service.run(db)
    await log_admin_action(db, admin.id, "stripe_sync", "stripe", None, {"records": result.count}, ip, risk_level="mittel")
    return result

@router.get("/revenue-report")
async def revenue_report(
    period: Literal["month", "quarter", "year"] = Query("month"),
    format: Literal["json", "csv"] = Query("json"),
    admin: User = Depends(require_admin),
):
    data = await payment_service.revenue_report(period)
    if format == "csv":
        return StreamingResponse(
            io.StringIO(csv_export(data)),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=revenue-{period}.csv"}
        )
    return data
```

### MRR-Chart (Frontend)

```vue
<!-- AdminMrrChart.vue -->
<template>
  <div class="card chart-card">
    <h3 class="card-title">MRR-Entwicklung</h3>
    <div class="chart-wrapper">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
const props = defineProps(['data'])
const chartCanvas = ref(null)

onMounted(() => {
  // Eigene Mini-Chart-Engine (kein externer Dependency)
  drawLineChart(chartCanvas.value, props.data)
})
</script>
```

---

## 6. KI-Kosten-Tracking

### Funktionsumfang

| Metrik | Beschreibung |
|--------|--------------|
| **KI-Aufrufe pro Vermieter** | Tokens, Kosten |
| **KI-Kosten gesamt** | Pro Monat |
| **Marge** | KI-Kosten vs. Einnahmen |
| **Use-Cases** | Welche KI-Features kosten am meisten? |
| **Budget pro Vermieter** | Limit festlegen |
| **Cache-Trefferrate** | Wie viele Aufrufe aus Cache statt API? |

### SQL: KI-Kosten pro Vermieter

```sql
SELECT
    a.vermieter_id,
    u.full_name AS vermieter_name,
    COUNT(*) AS aufrufe,
    SUM(a.tokens_used) AS tokens_gesamt,
    SUM(COALESCE(a.tokens_used, 0) * 0.000002) AS geschaetzte_kosten_eur, -- Beispiel-Preis
    a.use_case,
    COUNT(*) FILTER (WHERE a.created_at >= NOW() - INTERVAL '1 hour' AND
        EXISTS (SELECT 1 FROM ai_stored_results b WHERE b.prompt_hash = a.prompt_hash AND b.id < a.id)
    ) AS cache_hits
FROM ai_stored_results a
JOIN users u ON u.id = a.vermieter_id
WHERE a.created_at >= DATE_TRUNC('month', NOW())
GROUP BY a.vermieter_id, u.full_name, a.use_case
ORDER BY geschaetzte_kosten_eur DESC;
```

### Budget-Limit

```python
# backend/app/services/admin/ki_service.py
async def set_ki_budget(db: AsyncSession, vermieter_id: int, monthly_eur: float, admin_id: int):
    # Speichert in Redis oder subscription metadata
    await redis.hset(f"ki:budget:{vermieter_id}", mapping={
        "monthly_eur": monthly_eur,
        "set_by": admin_id,
        "set_at": datetime.utcnow().isoformat(),
    })
    await redis.expire(f"ki:budget:{vermieter_id}", 86400 * 365)

async def check_budget(vermieter_id: int) -> bool:
    budget = await redis.hget(f"ki:budget:{vermieter_id}", "monthly_eur")
    if budget is None:
        return True  # Default: kein Limit
    spent = await redis.get(f"ki:spent:{vermieter_id}:{current_month()}") or 0
    return float(spent) < float(budget)
```

---

## 7. E-Mail / System-Verwaltung

### E-Mail-Logs

| Feld | Beschreibung |
|------|--------------|
| `recipient` | Empfänger |
| `subject` | Betreff |
| `status` | sent / failed / bounced / deferred |
| `sent_at` | Zeitpunkt |
| `error` | Fehlermeldung |

### Massen-E-Mail

```python
@router.post("/broadcast")
async def broadcast_email(
    payload: BroadcastEmailRequest,
    admin: User = Depends(require_admin),
    ip: str = Depends(client_ip),
):
    """
    Manueller E-Mail-Versand an alle Vermieter (z.B. Wartungsankündigung).
    Rate-limited, audit-logged, approval-required für >100 Empfänger.
    """
    if payload.target == "all_vermieter":
        recipients = await user_service.get_all_vermieter_emails()
    else:
        recipients = payload.recipients

    if len(recipients) > 100 and not payload.approval_code:
        raise HTTPException(403, "Massen-E-Mail >100 Empfänger erfordert Approval-Code")

    await email_service.send_bulk(recipients, payload.subject, payload.body)
    await log_admin_action(db, admin.id, "email_broadcast", "email", None, {"count": len(recipients)}, ip, risk_level="hoch")
    return {"sent": len(recipients)}
```

### System-Status & Wartungsmodus

| Komponente | Prüfung |
|------------|---------|
| PostgreSQL | `SELECT 1` |
| Redis | `PING` |
| Stripe | Test-API-Call |
| Ollama Cloud | Health-Endpoint |
| E-Mail-Service | Resend-API-Status |

```python
# backend/app/services/admin/system_health.py
async def health_check() -> dict:
    return {
        "db": await check_db(),
        "redis": await check_redis(),
        "stripe": await check_stripe(),
        "ollama": await check_ollama(),
        "email": await check_email(),
        "timestamp": datetime.utcnow().isoformat(),
    }
```

### Wartungsmodus

```python
@router.post("/maintenance")
async def set_maintenance(
    payload: MaintenanceRequest,
    admin: User = Depends(require_admin),
    ip: str = Depends(client_ip),
):
    await redis.set("maintenance:active", "1", ex=payload.duration_minutes * 60)
    await redis.set("maintenance:message", payload.message, ex=payload.duration_minutes * 60)
    await redis.set("maintenance:ends_at", (datetime.utcnow() + timedelta(minutes=payload.duration_minutes)).isoformat())
    await log_admin_action(db, admin.id, "maintenance_mode", "system", None, payload.model_dump(), ip, risk_level="hoch")
    return {"active": True, "ends_at": "..."}
```

### Feature-Flags

```python
@router.get("/feature-flags")
async def list_feature_flags(db, admin):
    return await db.execute(select(FeatureFlag))

@router.patch("/feature-flags/{key}")
async def update_feature_flag(key: str, payload: FeatureFlagUpdate, db, admin, ip):
    flag = await db.get(FeatureFlag, key)
    flag.value = payload.value
    flag.updated_by = admin.id
    flag.updated_at = datetime.utcnow()
    await db.commit()
    await log_admin_action(db, admin.id, "feature_flag_change", "feature_flags", key, payload.model_dump(), ip, risk_level="mittel")
    return flag
```

---

## 8. Lead-Verwaltung

| Funktion | Beschreibung |
|----------|--------------|
| **Lead-Liste** | Alle Leads aus Website (NK-Check, Mietpreis-Rechner, etc.) |
| **Status** | neu / kontaktiert / registriert / verloren |
| **Conversion-Rate** | Lead → Vermieter |
| **Manuelle Erfassung** | z.B. aus Anrufen |

### Lead-Tabelle

Die Lead-Verwaltung nutzt die Tabelle `referrals` als Basis oder besser eine dedizierte `leads`-Tabelle. Wir empfehlen `leads` zu erstellen (siehe Abschnitt 12).

---

## 9. Support / Ticket-Verwaltung

**Wichtig:** Dies ist das interne Support-Ticket-System für Vermieter → UNS. Nicht zu verwechseln mit dem Vermieter-Ticket-System (Mieter → Vermieter).

| Feld | Beschreibung |
|------|--------------|
| `id` | UUID oder INT |
| `vermieter_id` | Wer meldet das Problem |
| `subject` | Thema |
| `status` | offen / in_bearbeitung / geloest / geschlossen |
| `assigned_admin_id` | Zuständiger Admin |
| `priority` | niedrig / normal / hoch / kritisch |
| `created_at` | Erstellung |

```python
@router.get("/support-tickets")
async def list_support_tickets(...):
    return await support_ticket_service.list(db, status, assigned_to)

@router.patch("/support-tickets/{ticket_id}/assign")
async def assign_support_ticket(ticket_id, admin_id, db, admin, ip):
    ...

@router.patch("/support-tickets/{ticket_id}/status")
async def update_support_status(ticket_id, payload, db, admin, ip):
    ...
```

---

## 10. Audit-Log

### Prinzip

Jede Admin-Aktion wird geloggt: **wer, was, wann, IP, Risiko-Level**.

| Feld | Beschreibung |
|------|--------------|
| `admin_id` | Ausführender Admin |
| `action` | z.B. `suspend_vermieter`, `impersonate_start`, `refund` |
| `entity` | Betroffene Tabelle |
| `entity_id` | Betroffene ID |
| `details` | JSONB mit Kontext |
| `ip_address` | IP des Admins |
| `risk_level` | niedrig / mittel / hoch |
| `created_at` | Zeitpunkt |

### Logging-Helfer

```python
# backend/app/dependencies.py
async def log_admin_action(
    db: AsyncSession,
    admin_id: int,
    action: str,
    entity: str,
    entity_id: int | None,
    details: dict,
    ip: str,
    risk_level: str = "niedrig"
):
    log = AdminAuditLog(
        admin_id=admin_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        details=details,
        ip_address=ip,
        risk_level=risk_level,
    )
    db.add(log)
    await db.commit()
```

### Admin-Audit-Log vs. normaler Audit-Log

- `audit_logs`: Für alle User-Aktionen (DSGVO, allgemein).
- `admin_audit_logs`: Nur für Admin-Aktionen, separat, härter geschützt, längere Aufbewahrung.

---

## 11. Einstellungen

### Globale Planauspreise

```python
@router.patch("/settings/pricing")
async def update_pricing(payload: PricingUpdate, db, admin, ip):
    # Preise für neue Kunden ändern
    # Bestehende Kunden behalten alten Preis (Grandfathering)
    await pricing_service.update_default_prices(db, payload)
    await log_admin_action(db, admin.id, "pricing_update", "settings", None, payload.model_dump(), ip, risk_level="hoch")
    return {"ok": True}
```

### WE-Begrenzung & Schwellenwerte

| Einstellung | Beschreibung |
|-------------|--------------|
| `max_we_basis` | 5 |
| `max_we_pro` | 25 |
| `business_min_we` | Ab wann Business empfohlen |
| `upgrade_request_threshold` | Anfrage-Schwellenwert |

### KI-Modelle

```python
@router.patch("/settings/ai-models")
async def update_ai_models(payload: AIModelSettings, db, admin, ip):
    await redis.set("ai:default_model", payload.default_model)
    await redis.set("ai:complex_model", payload.complex_model)
    await log_admin_action(db, admin.id, "ai_model_change", "settings", None, payload.model_dump(), ip, risk_level="mittel")
    return {"ok": True}
```

### E-Mail-Templates

```python
@router.patch("/settings/email-templates/{template_id}")
async def update_email_template(template_id, payload, db, admin, ip):
    template = await db.get(EmailTemplate, template_id)
    template.subject = payload.subject
    template.body_html = payload.body_html
    template.body_text = payload.body_text
    await db.commit()
    await log_admin_action(db, admin.id, "email_template_edit", "email_templates", template_id, {}, ip, risk_level="niedrig")
    return template
```

### DSGVO-Einstellungen

| Einstellung | Standard |
|-------------|----------|
| Aufbewahrungsfrist Mietvertragsdaten | 10 Jahre |
| Aufbewahrungsfrist Abrechnungen | 10 Jahre |
| Aufbewahrungsfrist Audit-Logs | 12 Monate |
| Automatische Löschung nach Kündigung | 30 Tage |

---

## 12. DB-Schema Erweiterung für Admin-Center

### Neue Tabellen

Wir erweitern das DB-Schema v4 um folgende Tabellen:

1. `admin_users` — Optional, falls Admin-Accounts technisch getrennt werden sollen. Wir nutzen `users WHERE role='admin'` mit zusätzlichen Sicherheitsfeldern.
2. `admin_audit_logs` — Separater Audit-Log für Admin-Aktionen.
3. `support_tickets` — Interne Support-Tickets.
4. `feature_flags` — Feature-Toggles ohne Deploy.
5. `email_logs` — Alle gesendeten E-Mails.
6. `maintenance_windows` — Geplante Wartungsfenster.
7. `leads` — Website-Leads (empfohlen, falls nicht bereits vorhanden).
8. `ki_budgets` — KI-Budget pro Vermieter.

### SQL DDL

```sql
-- ============================================================
-- Admin-Center — Erweiterung zum DB-Schema v4
-- PostgreSQL 17 · IDENTITY · Soft-Delete · Audit
-- ============================================================

-- ============================================================
-- 1. admin_users (optional, alternativ users.role='admin')
-- ============================================================
-- Wir nutzen users.role='admin' aus v4. Zusätzliche Admin-spezifische
-- Daten können in admin_users gespeichert werden, falls nötig.
CREATE TABLE admin_users (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id             INT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    admin_level         VARCHAR(20) NOT NULL DEFAULT 'support'
                        CHECK (admin_level IN ('support', 'billing', 'superadmin')),
    ip_whitelist        JSONB DEFAULT '[]'::jsonb,  -- Liste erlaubter IPs/CIDRs
    two_factor_enabled  BOOLEAN DEFAULT FALSE,
    last_login_at       TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 2. admin_audit_logs — Admin-Aktionen separat loggen
-- ============================================================
CREATE TABLE admin_audit_logs (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    admin_id            INT NOT NULL REFERENCES users(id),
    action              VARCHAR(100) NOT NULL,
    entity              VARCHAR(50),
    entity_id           INT,
    risk_level          VARCHAR(10) NOT NULL DEFAULT 'niedrig'
                        CHECK (risk_level IN ('niedrig','mittel','hoch')),
    details             JSONB,
    ip_address          INET,
    user_agent          VARCHAR(255),
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 3. support_tickets — Interne Support-Tickets (Vermieter → UNS)
-- ============================================================
CREATE TABLE support_tickets (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ticket_number       VARCHAR(20) UNIQUE NOT NULL,
    subject             VARCHAR(200) NOT NULL,
    description         TEXT,
    status              VARCHAR(20) NOT NULL DEFAULT 'offen'
                        CHECK (status IN ('offen','in_bearbeitung','gewartet','geloest','geschlossen')),
    priority            VARCHAR(10) DEFAULT 'normal'
                        CHECK (priority IN ('niedrig','normal','hoch','kritisch')),
    assigned_admin_id   INT REFERENCES users(id),
    channel             VARCHAR(20) DEFAULT 'portal'  -- portal, email, phone
                        CHECK (channel IN ('portal','email','phone')),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    closed_at           TIMESTAMPTZ
);

-- ============================================================
-- 4. support_ticket_comments — Verlauf interner Tickets
-- ============================================================
CREATE TABLE support_ticket_comments (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    support_ticket_id   INT NOT NULL REFERENCES support_tickets(id) ON DELETE CASCADE,
    author_id           INT NOT NULL REFERENCES users(id),
    is_internal         BOOLEAN DEFAULT FALSE,  -- true = nur für Admins sichtbar
    content             TEXT NOT NULL,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 5. feature_flags — Features ohne Deploy ein/ausschalten
-- ============================================================
CREATE TABLE feature_flags (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    key                 VARCHAR(50) UNIQUE NOT NULL,
    value               JSONB NOT NULL DEFAULT 'false'::jsonb,
    description         TEXT,
    scope               VARCHAR(20) DEFAULT 'global'
                        CHECK (scope IN ('global','plan','vermieter')),
    updated_by          INT REFERENCES users(id),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 6. email_logs — Alle gesendeten E-Mails
-- ============================================================
CREATE TABLE email_logs (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    recipient           VARCHAR(255) NOT NULL,
    subject             VARCHAR(255) NOT NULL,
    template_id         VARCHAR(50),
    status              VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending','sent','failed','bounced','deferred')),
    provider_message_id VARCHAR(255),
    error               TEXT,
    sent_at             TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 7. maintenance_windows — Wartungsmodus
-- ============================================================
CREATE TABLE maintenance_windows (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    start_at            TIMESTAMPTZ NOT NULL,
    end_at              TIMESTAMPTZ NOT NULL,
    message             TEXT NOT NULL DEFAULT 'Wartungsarbeiten, zurück in Kürze.',
    is_active           BOOLEAN DEFAULT TRUE,
    created_by          INT REFERENCES users(id),
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 8. leads — Website-Leads (falls noch nicht vorhanden)
-- ============================================================
CREATE TABLE leads (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email               VARCHAR(255) NOT NULL,
    full_name           VARCHAR(100),
    phone               VARCHAR(30),
    source              VARCHAR(50) NOT NULL,  -- nk_check, mietpreis_rechner, contact_form, manual
    source_details      JSONB,
    status              VARCHAR(20) DEFAULT 'neu'
                        CHECK (status IN ('neu','kontaktiert','registriert','verloren','qualifiziert')),
    notes               TEXT,
    converted_user_id   INT REFERENCES users(id),
    converted_at        TIMESTAMPTZ,
    assigned_admin_id   INT REFERENCES users(id),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 9. ki_budgets — KI-Budget pro Vermieter
-- ============================================================
CREATE TABLE ki_budgets (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    monthly_eur         DECIMAL(10,2) NOT NULL DEFAULT 5.00,
    hard_limit          BOOLEAN DEFAULT TRUE,
    set_by              INT REFERENCES users(id),
    set_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 10. admin_sessions — Admin-Login-Sessions (zusätzlich zu user_sessions)
-- ============================================================
CREATE TABLE admin_sessions (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    admin_id            INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ip_address          INET NOT NULL,
    user_agent          VARCHAR(255),
    totp_verified       BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    expires_at          TIMESTAMPTZ NOT NULL,
    revoked_at          TIMESTAMPTZ
);

-- ============================================================
-- Indizes
-- ============================================================
CREATE INDEX idx_admin_audit_logs_admin    ON admin_audit_logs(admin_id);
CREATE INDEX idx_admin_audit_logs_action   ON admin_audit_logs(action);
CREATE INDEX idx_admin_audit_logs_created  ON admin_audit_logs(created_at);
CREATE INDEX idx_support_tickets_vermieter ON support_tickets(vermieter_id);
CREATE INDEX idx_support_tickets_status    ON support_tickets(status);
CREATE INDEX idx_support_tickets_assigned  ON support_tickets(assigned_admin_id);
CREATE INDEX idx_feature_flags_key         ON feature_flags(key);
CREATE INDEX idx_email_logs_recipient      ON email_logs(recipient);
CREATE INDEX idx_email_logs_status         ON email_logs(status);
CREATE INDEX idx_email_logs_sent           ON email_logs(sent_at);
CREATE INDEX idx_leads_status              ON leads(status);
CREATE INDEX idx_leads_source              ON leads(source);
CREATE INDEX idx_ki_budgets_vermieter      ON ki_budgets(vermieter_id);
CREATE INDEX idx_admin_sessions_admin      ON admin_sessions(admin_id);

-- ============================================================
-- RLS aktivieren (Admin-Tabellen: nur Admins sehen alles)
-- ============================================================
ALTER TABLE admin_users              ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_audit_logs         ENABLE ROW LEVEL SECURITY;
ALTER TABLE support_tickets          ENABLE ROW LEVEL SECURITY;
ALTER TABLE support_ticket_comments  ENABLE ROW LEVEL SECURITY;
ALTER TABLE feature_flags            ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_logs               ENABLE ROW LEVEL SECURITY;
ALTER TABLE maintenance_windows      ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads                    ENABLE ROW LEVEL SECURITY;
ALTER TABLE ki_budgets               ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_sessions           ENABLE ROW LEVEL SECURITY;

-- Admin-RLS: Nur Admins dürfen Admin-Tabellen lesen/schreiben.
CREATE POLICY admin_users_admin_only ON admin_users
    FOR ALL USING (current_setting('app.current_user_role') = 'admin');

CREATE POLICY admin_audit_logs_admin_only ON admin_audit_logs
    FOR ALL USING (current_setting('app.current_user_role') = 'admin');

CREATE POLICY support_tickets_admin_only ON support_tickets
    FOR ALL USING (current_setting('app.current_user_role') = 'admin');

CREATE POLICY support_ticket_comments_admin_only ON support_ticket_comments
    FOR ALL USING (current_setting('app.current_user_role') = 'admin');

CREATE POLICY feature_flags_admin_only ON feature_flags
    FOR ALL USING (current_setting('app.current_user_role') = 'admin');

CREATE POLICY email_logs_admin_only ON email_logs
    FOR ALL USING (current_setting('app.current_user_role') = 'admin');

CREATE POLICY maintenance_windows_admin_only ON maintenance_windows
    FOR ALL USING (current_setting('app.current_user_role') = 'admin');

CREATE POLICY leads_admin_only ON leads
    FOR ALL USING (current_setting('app.current_user_role') = 'admin');

CREATE POLICY ki_budgets_admin_only ON ki_budgets
    FOR ALL USING (current_setting('app.current_user_role') = 'admin');

CREATE POLICY admin_sessions_admin_only ON admin_sessions
    FOR ALL USING (current_setting('app.current_user_role') = 'admin');
```

---

## 13. API-Endpunkte

### Übersicht Admin-API

| Method | Path | Auth | Beschreibung |
|--------|------|------|--------------|
| GET | `/api/admin/dashboard` | Admin | KPI-Center |
| GET | `/api/admin/vermieter` | Admin | Vermieter-Liste mit Filter |
| GET | `/api/admin/vermieter/{id}` | Admin | Vermieter-Details |
| PATCH | `/api/admin/vermieter/{id}/suspend` | Admin | Vermieter sperren |
| PATCH | `/api/admin/vermieter/{id}/unsuspend` | Admin | Vermieter entsperren |
| PATCH | `/api/admin/vermieter/{id}/subscription` | Admin | Abo bearbeiten |
| POST | `/api/admin/vermieter/{id}/password-reset` | Admin | Passwort-Reset auslösen |
| POST | `/api/admin/vermieter/{id}/impersonate` | Admin | Als Vermieter einloggen |
| DELETE | `/api/admin/vermieter/{id}` | Admin | DSGVO-Löschung |
| GET | `/api/admin/mieter` | Admin | Mieter-Liste |
| GET | `/api/admin/mieter/{id}` | Admin | Mieter-Details |
| PATCH | `/api/admin/mieter/{id}/suspend` | Admin | Mieter sperren |
| PATCH | `/api/admin/mieter/{id}/unsuspend` | Admin | Mieter entsperren |
| POST | `/api/admin/mieter/{id}/password-reset` | Admin | Mieter-Passwort-Reset |
| DELETE | `/api/admin/mieter/{id}` | Admin | Mieter löschen |
| GET | `/api/admin/payments` | Admin | Zahlungs-Übersicht |
| GET | `/api/admin/payments/failed` | Admin | Fehlgeschlagene Zahlungen |
| POST | `/api/admin/payments/{id}/retry` | Admin | Zahlung erneut versuchen |
| POST | `/api/admin/payments/{id}/refund` | Admin | Rückerstattung |
| POST | `/api/admin/payments/sync` | Admin | Stripe-Sync |
| GET | `/api/admin/payments/revenue-report` | Admin | Umsatz-Report (JSON/CSV) |
| GET | `/api/admin/ki/costs` | Admin | KI-Kosten-Übersicht |
| GET | `/api/admin/ki/costs/{vermieter_id}` | Admin | KI-Kosten pro Vermieter |
| PATCH | `/api/admin/ki/budget/{vermieter_id}` | Admin | KI-Budget setzen |
| GET | `/api/admin/emails` | Admin | E-Mail-Logs |
| POST | `/api/admin/emails/broadcast` | Admin | Massen-E-Mail |
| GET | `/api/admin/system/health` | Admin | System-Status |
| POST | `/api/admin/system/maintenance` | Admin | Wartungsmodus |
| GET | `/api/admin/feature-flags` | Admin | Feature-Flags |
| PATCH | `/api/admin/feature-flags/{key}` | Admin | Feature-Flag ändern |
| GET | `/api/admin/leads` | Admin | Lead-Liste |
| POST | `/api/admin/leads` | Admin | Manuellen Lead erfassen |
| PATCH | `/api/admin/leads/{id}/status` | Admin | Lead-Status ändern |
| GET | `/api/admin/support-tickets` | Admin | Support-Tickets |
| POST | `/api/admin/support-tickets` | Admin | Support-Ticket erstellen |
| PATCH | `/api/admin/support-tickets/{id}/status` | Admin | Ticket-Status ändern |
| PATCH | `/api/admin/support-tickets/{id}/assign` | Admin | Ticket zuweisen |
| GET | `/api/admin/audit-logs` | Admin | Admin-Audit-Log |
| GET | `/api/admin/audit-logs/export` | Admin | Audit-Log CSV-Export |
| GET | `/api/admin/settings/pricing` | Admin | Planauspreise |
| PATCH | `/api/admin/settings/pricing` | Admin | Planauspreise ändern |
| GET | `/api/admin/settings/ai-models` | Admin | KI-Modelle |
| PATCH | `/api/admin/settings/ai-models` | Admin | KI-Modelle ändern |
| GET | `/api/admin/settings/email-templates` | Admin | E-Mail-Templates |
| PATCH | `/api/admin/settings/email-templates/{id}` | Admin | E-Mail-Template ändern |
| GET | `/api/admin/settings/dsgvo` | Admin | DSGVO-Einstellungen |
| PATCH | `/api/admin/settings/dsgvo` | Admin | DSGVO-Einstellungen ändern |

---

## 14. Frontend-Struktur

### Technologie

- **Framework:** Vue.js 3 (Composition API)
- **Styling:** Tailwind CSS (bereits im Projekt)
- **Router:** Eigener `/admin/*` Router-Bereich
- **State:** Pinia Store `admin`
- **API-Client:** axios mit separatem Admin-Interceptor
- **Icons:** Inline SVG oder Heroicons (keine externen Fonts/Icons im Mockup)

### Router-Struktur

```typescript
// frontend/src/router/admin.ts
const adminRoutes = [
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAdmin: true },
    children: [
      { path: '', name: 'admin-dashboard', component: AdminDashboard },
      { path: 'vermieter', name: 'admin-vermieter', component: VermieterListe },
      { path: 'vermieter/:id', name: 'admin-vermieter-detail', component: VermieterDetail },
      { path: 'mieter', name: 'admin-mieter', component: MieterListe },
      { path: 'mieter/:id', name: 'admin-mieter-detail', component: MieterDetail },
      { path: 'zahlungen', name: 'admin-zahlungen', component: ZahlungsUebersicht },
      { path: 'ki-kosten', name: 'admin-ki-kosten', component: KIKosten },
      { path: 'emails', name: 'admin-emails', component: EmailLogs },
      { path: 'leads', name: 'admin-leads', component: LeadListe },
      { path: 'support-tickets', name: 'admin-support', component: SupportTickets },
      { path: 'audit-log', name: 'admin-audit', component: AuditLog },
      { path: 'einstellungen', name: 'admin-einstellungen', component: Einstellungen },
      { path: 'system', name: 'admin-system', component: SystemStatus },
    ],
  },
]
```

### Komponenten-Struktur

```
frontend/src/
├── layouts/
│   └── AdminLayout.vue
├── views/admin/
│   ├── AdminDashboard.vue
│   ├── VermieterListe.vue
│   ├── VermieterDetail.vue
│   ├── MieterListe.vue
│   ├── MieterDetail.vue
│   ├── ZahlungsUebersicht.vue
│   ├── KIKosten.vue
│   ├── EmailLogs.vue
│   ├── LeadListe.vue
│   ├── SupportTickets.vue
│   ├── AuditLog.vue
│   ├── Einstellungen.vue
│   └── SystemStatus.vue
├── components/admin/
│   ├── AdminSidebar.vue
│   ├── AdminTopbar.vue
│   ├── KpiCard.vue
│   ├── MrrChart.vue
│   ├── DataTable.vue
│   ├── StatusBadge.vue
│   ├── ConfirmModal.vue
│   └── ImpersonateBanner.vue
├── stores/
│   └── admin.ts
└── api/
    └── admin.ts
```

### AdminLayout

```vue
<!-- frontend/src/layouts/AdminLayout.vue -->
<template>
  <div class="admin-shell">
    <AdminSidebar />
    <main class="admin-main">
      <AdminTopbar />
      <div class="admin-content">
        <ImpersonateBanner v-if="isImpersonating" />
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import AdminSidebar from '@/components/admin/AdminSidebar.vue'
import AdminTopbar from '@/components/admin/AdminTopbar.vue'
import ImpersonateBanner from '@/components/admin/ImpersonateBanner.vue'
import { useAdminStore } from '@/stores/admin'

const admin = useAdminStore()
const isImpersonating = computed(() => admin.impersonationToken !== null)
</script>
```

### Sidebar-Navigation

```vue
<!-- AdminSidebar.vue -->
<template>
  <aside class="admin-sidebar">
    <div class="sidebar-logo">
      <span class="logo-icon">⚙️</span>
      <span class="logo-text">Admin-Center</span>
    </div>
    <nav class="sidebar-nav">
      <RouterLink to="/admin" exact>Dashboard</RouterLink>
      <RouterLink to="/admin/vermieter">Vermieter</RouterLink>
      <RouterLink to="/admin/mieter">Mieter</RouterLink>
      <RouterLink to="/admin/zahlungen">Zahlungen</RouterLink>
      <RouterLink to="/admin/ki-kosten">KI-Kosten</RouterLink>
      <RouterLink to="/admin/emails">E-Mails</RouterLink>
      <RouterLink to="/admin/leads">Leads</RouterLink>
      <RouterLink to="/admin/support-tickets">Support</RouterLink>
      <RouterLink to="/admin/audit-log">Audit-Log</RouterLink>
      <RouterLink to="/admin/einstellungen">Einstellungen</RouterLink>
      <RouterLink to="/admin/system">System</RouterLink>
    </nav>
  </aside>
</template>
```

---

## 15. Mockup

Das HTML-Mockup liegt unter `/root/mietverwaltung/mockup/admin.html`.

### Anforderungen an das Mockup

- Single-File HTML, inline CSS+JS
- Keine externen Dependencies
- Mobile-First
- Gleiches Design-System wie `index.html` (Navy #0D3B70, Apple-Style, Dark-Mode)
- Zeigt Dashboard mit KPI-Cards, Vermieter-Liste mit Sperren/Entsperren, Zahlungs-Übersicht
- SPA-Navigation innerhalb der Seite

### Mockup-Inhalte

| Screen | Inhalt |
|--------|--------|
| **Dashboard** | 8 KPI-Cards, MRR-Chart, letzte Registrierungen, fehlgeschlagene Zahlungen, offene Tickets |
| **Vermieter** | Tabelle mit Suche/Filter, Sperren/Entsperren/Details Buttons |
| **Zahlungen** | Subscription-Status, MRR pro Plan, fehlgeschlagene Zahlungen |
| **KI-Kosten** | Kosten pro Vermieter, Use-Cases, Budget-Einstellung |
| **System** | Health-Status, Wartungsmodus, Feature-Flags |

---

## 16. Sicherheit

### Admin-Accounts

| Maßnahme | Implementierung |
|----------|-----------------|
| **2FA** | Pflicht vor erstem Admin-Login. TOTP + E-Mail-Code-Fallback. |
| **IP-Whitelist** | `admin_users.ip_whitelist` speichert erlaubte IPs/CIDRs. Login nur von dort. |
| **Admin-Token** | Separater JWT-Scope `admin`, nie mit Vermieter-Token kombinieren. |
| **Sessions** | `admin_sessions` mit IP + User-Agent, Ablauf nach 4h Inaktivität. |

### Impersonate

| Regel | Umsetzung |
|-------|-----------|
| Zeitlimit | 30 Minuten |
| Audit-Log | `impersonate_start`, `impersonate_end` |
| Vermieter-Benachrichtigung | E-Mail nach Beendigung der Impersonation |
| Sichtbarkeit | Banner oben: "Du agierst als [Vermieter] — Session endet in MM:SS" |
| Scope | Admin kann nur als Vermieter agieren, nicht als Mieter |

### Rate-Limiting

| Bereich | Limit |
|---------|-------|
| Admin-Login | 5 Versuche / 15 Min |
| Admin-API allgemein | 30 req / min |
| Impersonate | 10 / Tag / Admin |
| Massen-E-Mail | 1 / Stunde ohne Approval |
| Passwort-Reset auslösen | 20 / Tag / Admin |

### Audit-Pflicht

**Keine Admin-Aktion ohne Audit-Log.** Jeder Endpoint ruft `log_admin_action()` auf. Hochriskante Aktionen erfordern zusätzlich:

- Bestätigung via Checkbox/Modal
- Optional: Zweit-Faktor (für Löschung, Refund, Massen-E-Mail)
- E-Mail-Benachrichtigung an betroffenen Vermieter/Mieter

### Code: Admin-Auth Dependency

```python
# backend/app/dependencies.py
from fastapi import Depends, HTTPException, Request
from app.auth import decode_token

async def require_admin(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    payload = decode_token(token)
    if payload.get("scope") != "admin":
        raise HTTPException(403, "Admin-Scope erforderlich")

    admin = await db.get(User, payload["sub"])
    if not admin or admin.role != "admin" or admin.deleted_at:
        raise HTTPException(403, "Kein Admin")

    # IP-Whitelist prüfen
    client_ip = request.client.host
    whitelist = await get_admin_whitelist(db, admin.id)
    if whitelist and client_ip not in whitelist:
        raise HTTPException(403, "IP nicht freigeschaltet")

    # 2FA geprüft?
    if not await has_verified_2fa(request):
        raise HTTPException(403, "2FA erforderlich")

    # Rate-Limit
    if await is_admin_rate_limited(client_ip, admin.id):
        raise HTTPException(429, "Zu viele Anfragen")

    return admin
```

### Admin-Login-Flow

```
1. POST /api/admin/auth/login {email, password}
2. Prüfe IP-Whitelist
3. Prüfe 2FA-Status
4. Falls 2FA noch nicht geprüft: 2FA-Challenge (TOTP oder E-Mail)
5. POST /api/admin/auth/2fa {code}
6. JWT mit scope=admin ausstellen (15 Min Access + 7 Tage Refresh)
7. Session in admin_sessions speichern
8. Redirect zu /admin/dashboard
```

---

## 17. Log-Management und Log-Retention (DSGVO-konform)

Dieses Kapitel beantwortet die Frage, wie lange wir Logdateien speichern dürfen und wie wir das DSGVO-konform gestalten. Es ersetzt das vorherige Kapitel zum Wartungs-Lockdown.

### 17.1 DSGVO-Regeln für Logs

Logfiles enthalten häufig personenbezogene Daten. Das beginnt bei der IP-Adresse, die laut EuGH als personenbezogenes Datum gilt (EuGH-Urteil C-582/14, Breyer). Weitere personenbezogene Daten in Logs können sein:

- IP-Adressen
- User-IDs
- E-Mail-Adressen (z. B. in Login-Fehlern)
- Zeitstempel von Nutzeraktionen
- Endpoints, die Rückschlüsse auf Verhalten erlauben
- Session-IDs
- Geräte- und Browser-Informationen

#### DSGVO Art. 5 — Grundsätze der Datenverarbeitung

Besonders relevant sind:

- **Art. 5 Abs. 1 lit. c (Datenminimierung):** Es dürfen nur Daten erhoben werden, die für den Zweck erforderlich sind.
- **Art. 5 Abs. 1 lit. e (Speicherbegrenzung):** Daten dürfen nicht länger als nötig gespeichert werden.
- **Art. 5 Abs. 2 (Rechenschaftspflicht):** Wir müssen nachweisen können, dass diese Grundsätze eingehalten werden.

#### DSGVO Art. 25 — Privacy by Design und Default

Logs sollen von vornherein so konzipiert sein, dass sie nur das Minimum an personenbezogenen Daten enthalten. Das bedeutet:

- Keine vollständigen IP-Adressen loggen, sondern anonymisieren.
- Keine Namen, E-Mails oder IBANs in Application Logs.
- Keine Passwörter oder Secrets loggen.
- Nur für den jeweiligen Zweck nötige Felder loggen.

#### DSGVO Art. 32 — Sicherheit der Verarbeitung

Sicherheitslogs (Login-Versuche, fehlgeschlagene Authentifizierungen) sind eine zulässige technische und organisatorische Maßnahme (TOM) zum Schutz der Systeme. Sie dürfen daher länger aufbewahrt werden als reine Access Logs.

#### DSGVO Art. 17 — Recht auf Löschung

Auch in Logs haben betroffene Personen ein Recht auf Löschung. Da Logdaten oft technisch nicht einzeln löschbar sind (z. B. weil sie in Dateien oder aggregierten Streams liegen), ist es zulässig, eine angemessene Aufbewahrungsfrist zu definieren und Daten nach Ablauf automatisch zu löschen. Das ist die gängige Praxis und DSGVO-konform, wenn die Fristen dokumentiert und begründet sind.

### 17.2 Was dürfen wir loggen und wie lange?

| Log-Typ | Inhalt | Empfohlene Aufbewahrung | Begründung |
|---------|--------|------------------------|------------|
| **Access Logs** | IP (anonymisiert), Methode, Endpoint, Status, User-Agent, Zeitstempel | **7 Tage**, max. 14 Tage | Fehleranalyse, Rate-Limiting, Abuse |
| **Error Logs** | Stack Traces, Fehlermeldungen (ohne PII) | **30 Tage** | Debugging, Stabilität |
| **Audit Logs** | Wer hat was wann gemacht (Admin + User) | **12 Monate** | GoBD, DSGVO, Rechtssicherheit |
| **Security Logs** | Login-Versuche, fehlgeschlagene Auth, IP | **90 Tage** | TOM nach DSGVO Art. 32, Incident Response |
| **Event Logs (Queue)** | events-Tabelle, verarbeitet/unverarbeitet | Bis Verarbeitung, max. **7 Tage** | Event-Queue, Retry-Logik |
| **KI-Call Logs** | Anonymisierte Prompts, Token-Counts, Kosten, Use-Case | **6 Monate** | Kostenkontrolle, Qualitätssicherung |
| **E-Mail-Logs** | Recipient (anonymisiert), Subject, Status, Bounce | **6 Monate** | Deliverability, Support |
| **Docker/Container Logs** | Standard-Output der Container | **7 Tage** | Betriebsfehler |
| **PostgreSQL Logs** | DB-Fehler, langsame Queries | **7 Tage** | Performance, DB-Health |

#### Begründungen

- **7 Tage Access Logs:** Ausreichend für technische Fehleranalyse, Rate-Limiting und kurzfristige Abuse-Erkennung. Längere Speicherung ist meist nicht notwendig und erhöht Datenschutzrisiko.
- **30 Tage Error Logs:** Fehler müssen nachvollziehbar sein, aber nicht ewig liegen bleiben. Personenbezogene Daten sollten hier gar nicht enthalten sein.
- **12 Monate Audit Logs:** Relevant für GoBD und Nachweispflichten. Wer hat wann welche kritische Aktion ausgeführt? Das ist ein berechtigtes Interesse.
- **90 Tage Security Logs:** Notwendig für Angriffserkennung, Forensik und TOM.
- **6 Monate KI-/E-Mail-Logs:** Ausreichend für Auswertungen zu Kosten und Deliverability. Anonymisierung vorausgesetzt.

### 17.3 Logging-Best-Practices DSGVO-konform

#### IP-Adressen anonymisieren

Statt `192.168.1.123` loggen wir `192.168.x.x` oder einen Hash:

```python
# backend/app/logging/pii_filter.py
import hashlib
import hmac
import os

_ANON_SALT = os.environ.get("LOG_ANON_SALT", "change-me-in-production").encode()

def anonymize_ip(ip: str) -> str:
    """
    Anonymisiert eine IP-Adresse für das Logging.
    IPv4: letzte zwei Oktette entfernen.
    IPv6: letzte 80 Bit entfernen.
    """
    if "." in ip:
        parts = ip.split(".")
        return f"{parts[0]}.{parts[1]}.0.0"
    if ":" in ip:
        parts = ip.split(":")
        return ":".join(parts[:4]) + ":0:0:0:0"
    return "unknown"

def hash_ip(ip: str) -> str:
    """Hash für Abuse-Erkennung (Rate-Limiting), nicht zum Loggen."""
    return hmac.new(_ANON_SALT, ip.encode(), hashlib.sha256).hexdigest()[:16]
```

#### Keine Personendaten in Application Logs

❌ **Nie so loggen:**

```python
# BAD
logger.info(f"User {user.email} logged in with IBAN {iban}")
logger.debug(f"Password reset token for {user.full_name}: {token}")
```

✅ **So loggen:**

```python
# GOOD
logger.info("user_login", extra={"user_id": user.id, "ip_hash": hash_ip(ip)})
logger.info("password_reset_requested", extra={"user_id": user.id})
```

#### Log-Level diszipliniert nutzen

| Level | Verwendung |
|-------|-----------|
| `DEBUG` | Nur lokal / in Dev. Nie in Produktion. |
| `INFO` | Produktions-Standard. Geschäftsereignisse, keine PII. |
| `WARNING` | Auffälligkeiten, die keinen Fehler darstellen. |
| `ERROR` | Fehler, die behoben werden müssen. |
| `CRITICAL` | Sicherheitsvorfälle, Ausfälle. |

#### Strukturierte JSON-Logs

Structured Logging macht Logs auswertbar und vermeidet, dass freier Text versehentlich PII enthält.

```python
# backend/app/logging/config.py
import structlog
import logging

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.dict_tracebacks,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()

# Verwendung
logger.info(
    "vermieter_suspended",
    admin_id=admin_id,
    vermieter_id=vermieter_id,
    reason="payment_failure",
    ip_anon=anonymize_ip(ip),
)
```

#### Log-Rotation automatisch

Access Logs und Container Logs sollten automatisch rotiert und nach Ablauf der Frist gelöscht werden.

### 17.4 Log-Management im Admin-Center

Das Admin-Center bekommt einen eigenen Bereich **Log-Management** mit folgenden Funktionen:

| Funktion | Beschreibung |
|----------|--------------|
| **Log-Viewer** | Gefilterte Anzeige aller Logs, standardmäßig anonymisiert |
| **Retention-Einstellungen** | Admin kann Aufbewahrungsfristen konfigurieren (mit Obergrenzen) |
| **Log-Export** | CSV-Export für Security-Incidents, anonymisiert |
| **DSGVO-Audit** | Übersicht aller Logs, die noch PII enthalten könnten |
| **Live-Tail** | Echtzeit-Stream aktueller Logs (max. letzte 100 Zeilen) |

#### Admin-API Endpoints

```python
# backend/app/routers/admin/logs.py
from fastapi import APIRouter, Depends, Query
from app.dependencies import require_admin, get_db

router = APIRouter(prefix="/api/admin/logs", tags=["admin-logs"])

@router.get("/")
async def list_logs(
    log_type: str = Query(..., enum=["access", "error", "audit", "security", "email", "ki"]),
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    admin = Depends(require_admin),
):
    """
    Liefert Logs eines bestimmten Typs. IPs sind standardmäßig anonymisiert.
    Nur Admins mit Level 'superadmin' oder 'billing' dürfen auf security/audit zugreifen.
    """
    return await log_service.fetch(log_type, from_date, to_date, limit)

@router.get("/retention")
async def get_retention_settings(admin = Depends(require_admin)):
    return await log_service.get_retention_config()

@router.patch("/retention")
async def update_retention(
    payload: LogRetentionConfig,
    db = Depends(get_db),
    admin = Depends(require_admin),
    ip = Depends(client_ip),
):
    await log_service.update_retention(payload)
    await log_admin_action(db, admin.id, "log_retention_update", "settings", None, payload.model_dump(), ip, risk_level="mittel")
    return {"ok": True}

@router.get("/export/{log_type}")
async def export_logs(
    log_type: str,
    from_date: date,
    to_date: date,
    admin = Depends(require_admin),
):
    data = await log_service.export(log_type, from_date, to_date, anonymize=True)
    return StreamingResponse(
        io.StringIO(csv_export(data)),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={log_type}-logs.csv"}
    )
```

#### Frontend: Log-Viewer

```vue
<!-- frontend/src/views/admin/LogManagement.vue -->
<template>
  <div class="admin-logs">
    <div class="filters">
      <select v-model="logType">
        <option value="access">Access Logs</option>
        <option value="error">Error Logs</option>
        <option value="audit">Audit Logs</option>
        <option value="security">Security Logs</option>
        <option value="email">E-Mail Logs</option>
        <option value="ki">KI Logs</option>
      </select>
      <input type="date" v-model="fromDate" />
      <input type="date" v-model="toDate" />
      <button @click="loadLogs">Laden</button>
    </div>

    <DataTable :rows="logs" :columns="columns" />

    <div class="retention-card">
      <h3>Aufbewahrungsfristen</h3>
      <RetentionSettings v-model="retention" @save="saveRetention" />
    </div>
  </div>
</template>
```

### 17.5 Konkrete Empfehlung für unsere SaaS

#### Aufbewahrungsfristen

| Log-Typ | Aufbewahrung | Anonymisierung |
|---------|--------------|----------------|
| Access Logs | **7 Tage** | IP auf /16 (IPv4) oder /48 (IPv6) kürzen |
| Error Logs | **30 Tage** | Keine PII, Stack-Traces ohne Nutzerdaten |
| Audit Logs | **12 Monate** | User-ID OK, IP anonymisiert |
| Security Logs | **90 Tage** | IP gehasht für Abuse-Erkennung |
| Event Queue (`events`-Tabelle) | Bis Verarbeitung, max. **7 Tage** | Keine PII, verarbeitete Events sofort löschen |
| KI-Call Logs | **6 Monate** | Prompts anonymisiert, keine Namen/Adressen |
| E-Mail Logs (`email_logs`) | **6 Monate** | Recipient auf Domain-Ebene anonymisieren oder hashen |
| Docker Container Logs | **7 Tage** | Log-Rotation in Docker |
| PostgreSQL Logs | **7 Tage** | Langsame Queries ohne User-Daten |

#### Docker Log-Driver Konfiguration

```yaml
# docker-compose.yml (Auszug)
services:
  backend:
    image: mietverwaltung/backend
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    # => max. 30 MB pro Container, ältere Logs werden rotiert
```

#### Loki + Grafana Alloy Konfiguration

```yaml
# alloy/config.alloy (Auszug)
loki.write "default" {
  endpoint {
    name = "loki"
    url = "http://loki:3100/loki/api/v1/push"
  }
}

loki.source.docker "default" {
  host = "unix:///var/run/docker.sock"
  forward_to = [loki.write.default.receiver]
}
```

```yaml
# loki/config.yml
auth_enabled: false

server:
  http_listen_port: 3100

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2026-01-01
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h

# Retention: globale Aufbewahrungsfrist von 90 Tagen (Security-Logs),
# spezifische Streams können kürzer sein.
limits_config:
  retention_period: 90d
```

Für Access Logs empfehlen wir, diese in Loki nur 7 Tage zu halten und ältere Daten automatisch zu löschen. Audit Logs werden in der PostgreSQL-Tabelle `admin_audit_logs` 12 Monate gespeichert.

#### Python structlog Konfiguration (vollständig)

```python
# backend/app/logging/setup.py
import logging
import structlog
from structlog.stdlib import LoggerFactory

def configure_logging(log_level: str = "INFO"):
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper()),
        stream=sys.stdout,
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.ExtraAdder(),
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        cache_logger_on_first_use=True,
    )

# In main.py:
from app.logging.setup import configure_logging
configure_logging(os.environ.get("LOG_LEVEL", "INFO"))
```

### 17.6 Was NIEMALS in Logs stehen darf

| Daten | Warum |
|-------|-------|
| Passwörter | Klartext- oder Hash-Log ist ein Sicherheitsvorfall |
| IBANs, Bankdaten | Finanzdaten, DSGVO + PCI-relevant |
| Geburtsdaten | Personendaten besonderer Kategorie (Art. 9 DSGVO) |
| Kreditkartennummern | PCI-DSS-Verstoß |
| TOTP-Secrets | 2FA-Kompromittierung |
| JWT-Tokens | Session-Hijacking möglich |
| Session-IDs | Session-Diebstahl möglich |
| Private Keys / API-Secrets | Kompromittierung der Infrastruktur |
| Unanonymisierte E-Mail-Adressen | Direkter Personenbezug |
| Wohnungsadressen inkl. Mietername | Mietsachverhalt, höchst sensibel |

### 17.7 Logging-Architektur

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  FastAPI App    │────▶│  JSON-Stdout    │────▶│  Docker Log     │
│  (structlog)    │     │  (PII-filtered) │     │  Driver         │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                              ┌──────────────────────────┘
                              ▼
                       ┌──────────────┐
                       │ Grafana Alloy│
                       │  (scrape)    │
                       └──────┬───────┘
                              │
                              ▼
                       ┌──────────────┐
                       │     Loki     │
                       │  (90 Tage)   │
                       └──────┬───────┘
                              │
                              ▼
                       ┌──────────────┐
                       │   Grafana    │
                       │  Dashboards  │
                       └──────────────┘
```

#### Middleware: PII-Filter

```python
# backend/app/middleware/pii_filter.py
from fastapi import Request
import re

_PII_PATTERNS = [
    (re.compile(r'[A-Z]{2}\d{2}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?([A-Z]{4})?'), '[IBAN]'),
    (re.compile(r'\d{2}\.\d{2}\.\d{4}'), '[BIRTHDATE]'),
    (re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}'), '[EMAIL]'),
]

def sanitize_for_log(text: str) -> str:
    if not text:
        return text
    for pattern, replacement in _PII_PATTERNS:
        text = pattern.sub(replacement, text)
    return text

async def log_request_safe(request: Request):
    ip = anonymize_ip(request.client.host if request.client else "unknown")
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        ip_anon=ip,
        # Body NIEMALS loggen — könnte PII enthalten
    )
```

### 17.8 Redis Event Queue

Die `events`-Tabelle dient als Event-Queue. Verarbeitete Events sollten sofort gelöscht werden, nicht aufbewahrt.

```python
# backend/app/services/events.py
async def mark_event_processed(db: AsyncSession, event_id: int):
    # Hard-Delete nach Verarbeitung — Events sind keine Audit-Daten
    await db.execute(delete(Event).where(Event.id == event_id))
    await db.commit()

# Cleanup-Job für hängende Events
async def cleanup_stale_events(db: AsyncSession):
    await db.execute(
        delete(Event).where(
            Event.processed_at.is_(None)
            & (Event.created_at < datetime.utcnow() - timedelta(days=7))
        )
    )
    await db.commit()
```

### 17.9 Zusammenfassung

| Regel | Umsetzung |
|-------|-----------|
| IP-Adressen | Immer anonymisieren oder kürzen |
| PII in Logs | Vermeiden; wenn nötig, hashen oder pseudonymisieren |
| Log-Level | INFO in Prod, DEBUG nur lokal |
| Aufbewahrung | 7 Tage (Access), 30 Tage (Error), 12 Monate (Audit), 90 Tage (Security) |
| Rotation | Automatisch, z. B. Docker max-size/max-file |
| Löschung | Automatisch nach Ablauf der Frist |
| Dokumentation | Aufbewahrungsfristen in TOM / Datenschutzerklärung |
| Audit | Admin kann Retention-Einstellungen einsehen und ändern |

Diese Regeln stellen sicher, dass wir die notwendigen Logs für Betrieb, Sicherheit und Compliance behalten, gleichzeitig aber DSGVO-konform nur so lange und so viel speichern wie wirklich erforderlich.

---

## Anhang A: Pydantic-Modelle (Auszug)

```python
# backend/app/schemas/admin.py
from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Literal

class AdminDashboardResponse(BaseModel):
    vermieter: VermieterStats
    mieter: MieterStats
    wohnungen: WohnungsStats
    revenue: RevenueStats
    churn: ChurnStats
    aktivitaet: ActivityStats
    ki: KIStats
    email: EmailStats
    stripe: StripeStats

class SuspendRequest(BaseModel):
    reason: str = Field(..., min_length=10, max_length=500)

class AdminSubscriptionUpdate(BaseModel):
    plan: Literal["basis", "pro", "business"]
    wohnungen_limit: int | None
    trial_ends_at: datetime | None
    apply_immediately: bool = False

class DeleteVermieterRequest(BaseModel):
    confirm: bool
    export_requested: bool = True

class RefundRequest(BaseModel):
    amount_cents: int | None = None  # None = full refund
    reason: str | None = None

class BroadcastEmailRequest(BaseModel):
    target: Literal["all_vermieter", "specific"]
    recipients: list[EmailStr] = []
    subject: str
    body: str
    approval_code: str | None = None

class MaintenanceRequest(BaseModel):
    duration_minutes: int = Field(..., ge=5, le=1440)
    message: str = "Wartungsarbeiten, zurück in Kürze."

class FeatureFlagUpdate(BaseModel):
    value: str | bool | int | dict
```

---

## Anhang B: Zusammenhang mit DB-Schema v4

Das Admin-Center baut auf dem bestehenden Schema v4 auf:

- `users.role = 'admin'` für Admin-Accounts
- `subscriptions` + `plan_usage` für Abo-Verwaltung und KPIs
- `objekte`, `einheiten`, `mieter`, `mietvertraege` für Vermieter-Details
- `audit_logs` als Basis; `admin_audit_logs` ergänzt Admin-spezifische Spuren
- `ai_stored_results` für KI-Kosten-Tracking
- RLS-Policies werden um Admin-Tabellen ergänzt

---

## Anhang C: Nächste Schritte

1. DB-Schema-Erweiterung aus Abschnitt 12 als Alembic-Migration erstellen.
2. Backend: Admin-Auth mit 2FA + IP-Whitelist implementieren.
3. Backend: Admin-Router für Dashboard, Vermieter, Mieter, Zahlungen, KI, E-Mail, Leads, Support, Audit, Einstellungen.
4. Frontend: AdminLayout + Sidebar + Views implementieren.
5. Mockup: `mockup/admin.html` finalisieren (siehe separate Datei).
6. Sicherheitsreview: Admin-API gegen OWASP Top 10 prüfen, Rate-Limiting testen, Audit-Log validieren.
7. Deploy: Admin-Router separat dokumentieren, Environment-Variablen für Admin-IPs festlegen.