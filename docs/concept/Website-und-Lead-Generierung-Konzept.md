# Öffentliche Marketing-Website & Lead-Generierung — MietVerwaltung SaaS

> **Version:** 1.0  
> **Ziel:** Konzept für die öffentliche Website (Landing Page, Features, Pricing, Demo, Über uns, Blog) mit Live-Stats, interaktiver Demo, DACH-Karte, Lead-Generierung, SEO und DSGVO-konformem Analytics.  
> **Design-Prinzip:** Apple-Style, Navy `#0D3B70`, minimalistisch, clean.  
> **Tech-Stack:** Vue.js 3 / Nuxt.js 3, FastAPI, PostgreSQL 17, Redis, Leaflet.js, OpenStreetMap, Plausible Analytics.

---

## 1. Öffentliche Website — Übersicht & Architektur

### 1.1 Seitenstruktur

| Seite | Zweck | Haupt-CTA |
|-------|-------|-----------|
| **Landing Page** (`/`) | Wertversprechen, Live-Stats, Hero, Social Proof | „Jetzt kostenlos starten“ / „Demo testen“ |
| **Features** (`/features`) | Detaillierte Feature-Liste mit Screenshots | „14 Tage kostenlos testen“ |
| **Pricing** (`/pricing`) | Preise & Abo-Modelle | „Kostenlos registrieren“ |
| **Demo** (`/demo`) | Interaktive Demo ohne Registrierung | „Jetzt kostenlos registrieren“ |
| **Über uns** (`/ueber-uns`) | Team, Mission, Trust | Newsletter |
| **Blog** (`/blog`) | SEO-Content (später) | Lead-Magneten |
| **Impressum / Datenschutz / AGB** | Rechtlich erforderlich | — |

### 1.2 Trennung Website vs. SaaS-App

Die öffentliche Marketing-Website ist technisch und inhaltlich klar von der eigentlichen SaaS-Anwendung getrennt:

- **Öffentliche Website:** `www.mietverwaltung.de` (später) / `marketing.mietverwaltung.de`
- **SaaS-Login/App:** `app.mietverwaltung.de`

Vorteile:
- Marketing-Website kann unabhängig deployed werden.
- SaaS-App hat eigenen Auth-Bereich und höhere Sicherheitsanforderungen.
- Website kann statisch/SSR-optimiert werden, ohne die App-Performance zu beeinflussen.
- A/B-Tests und Content-Updates auf der Website haben kein Risiko für die App.

### 1.3 Tech-Stack

| Schicht | Technologie | Begründung |
|---------|-------------|------------|
| Frontend | **Nuxt.js 3** + Vue.js 3 + TypeScript | SSR für SEO, einfaches Routing, i18n, gutes Ökosystem |
| Styling | **TailwindCSS** + Custom Design-System | Apple-Style, schnelle UI-Entwicklung |
| State | **Pinia** | Einfacher globaler State für Demo/Stats |
| Backend | **FastAPI** | Bestehend im Stack, schnell, async |
| Datenbank | **PostgreSQL 17** | Bestehendes Schema, Aggregat-Queries |
| Cache | **Redis** | 5-Min-Cache für Live-Stats, Rate-Limiting, Sessions |
| Maps | **Leaflet.js** + **OpenStreetMap** | Open Source, kostenlos, DSGVO-konform |
| Analytics | **Plausible** (self-hosted) | DSGVO-konform, keine Cookies |
| Hosting (MVP) | **Proxmox** | 0€, interne Infrastruktur |
| Hosting (Go-Live) | **Hetzner** | DSGVO-konform, kostengünstig |

**Entscheidung SSR/SSG:**

Wir empfehlen **Nuxt.js 3 mit SSR** statt `vite-ssg`.

- `vite-ssg` ist simpler, aber Nuxt bietet besseres Routing, i18n-Unterstützung, automatische Sitemap-Generierung und ein reiferes Ökosystem für SaaS-Marketing-Websites.
- Für statische Seiten (Pricing, Impressum) kann Nuxt auf SSG-Modus umgeschaltet werden.
- Blog-Beiträge können als SSG vorgerendert werden, während Landing Page mit Live-Stats SSR nutzt.

### 1.4 Datenfluss Website ↔ SaaS

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────┐      ┌──────────────┐
│   Nuxt.js 3     │──────▶│  FastAPI Public  │──────▶│  PostgreSQL │      │    Redis     │
│   (Website)     │◀──────│     API          │◀──────│  (Aggregat) │◀─────│  (Cache)     │
└─────────────────┘      └──────────────────┘      └─────────────┘      └──────────────┘
        │
        ▼
┌─────────────────┐
│  Plausible      │
│  Analytics      │
└─────────────────┘
```

Die Website fragt nur öffentliche, anonymisierte Aggregate über `/api/public/*` ab. Nie personenbezogene Daten.

### 1.5 SEO-Grundlagen

- **KI-generierte Meta-Tags:** Pro Seite werden Titel, Description, OG-Tags dynamisch generiert.
- **Structured Data:** `schema.org/SoftwareApplication`, `schema.org/Organization`, `schema.org/FAQPage`.
- **Sitemap.xml:** Automatisch generiert, inkl. Blog-Posts.
- **robots.txt:** Erlaubt alles außer Admin-/App-Bereichen.
- **Canonical URLs:** Verhindert Duplicate Content.
- **Core Web Vitals:** Ladezeit < 2 Sek, LCP < 2,5 s, CLS < 0,1.
- **Hreflang:** `de-DE`, `de-AT`, `de-CH` für DACH.

### 1.6 Design-System (Apple-Style)

| Farbe | Hex | Verwendung |
|-------|-----|------------|
| Navy Primary | `#0D3B70` | Header, Primary-Buttons, Markenfarbe |
| Navy Hover | `#2a5a9e` | Hover-States, aktive Tabs |
| Navy Light | `#e8eff8` | Selektierte Zeilen, Subtle-Badges |
| Background | `#f5f5f7` | Seitenhintergrund |
| Surface/Card | `#ffffff` | Karten, Modals |
| Text Primary | `#1d1d1f` | Haupttext |
| Text Secondary | `#6e6e73` | Labels, Hilfetexte |
| Border | `#d2d2d7` | Trennlinien, Input-Borders |
| Erfolg Grün | `#34c759` | Erfolg, positive Indikatoren |
| Warnung Orange | `#ff9500` | Hinweise, offene Fristen |
| Fehler Rot | `#ff3b30` | Fehler, Dringlichkeit |

- **Typografie:** `-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", system-ui, sans-serif`
- **Border-Radius:** 12 px (Inputs/Buttons), 16 px (Cards), 20 px (Dashboard-Karten)
- **Spacing:** 4 px Basiseinheit
- **Buttons:** Primary Navy, 44 px min-height, 12 px Radius

---

## 2. Live-Statistiken auf der Website

### 2.1 Anforderungen

Die Website zeigt in Echtzeit (near-Echtzeit via 5-Min-Cache) folgende Aggregate:

| Statistik | Datenquelle | Beschreibung |
|-----------|-------------|--------------|
| Anzahl verwalteter Objekte gesamt | `objekte` (nicht gelöscht) | Gesamtzahl aller Objekte in der Plattform |
| Anzahl Vermieter auf der Plattform | `vermieter_profile` (nicht gelöscht) | Eindeutige aktive Vermieter |
| Anzahl freie Wohnungen | `einheiten` (`aktuell_vermietet = FALSE`) | Nicht vermietete Einheiten |
| Anzahl vermietete Wohnungen | `einheiten` (`aktuell_vermietet = TRUE`) | Vermietete Einheiten |
| Anzahl bearbeiteter Tickets | `tickets` (nicht gelöscht) | Alle Tickets (Offen + Erledigt) |
| Anzahl erstellter Abrechnungen | `abrechnungen` (nicht gelöscht) | Erstellte NK-Abrechnungen |

### 2.2 DSGVO & Datenschutz

- **NUR Aggregat-Daten.** Keine Personendaten, keine Einzeldaten, keine Vermieter-Namen, keine Adressen.
- Keine Rückschlüsse auf einzelne Nutzer möglich.
- Cache-Dauer 5 Minuten reduziert Datenbank-Last.

### 2.3 PostgreSQL-Query

```sql
SELECT
    (SELECT COUNT(*) FROM objekte WHERE deleted_at IS NULL) AS total_objekte,
    (SELECT COUNT(DISTINCT vermieter_id) FROM vermieter_profile WHERE deleted_at IS NULL) AS total_vermieter,
    (SELECT COUNT(*) FROM einheiten WHERE aktuell_vermietet = FALSE AND deleted_at IS NULL) AS freie_wohnungen,
    (SELECT COUNT(*) FROM einheiten WHERE aktuell_vermietet = TRUE AND deleted_at IS NULL) AS vermietete_wohnungen,
    (SELECT COUNT(*) FROM tickets WHERE deleted_at IS NULL) AS total_tickets,
    (SELECT COUNT(*) FROM abrechnungen WHERE deleted_at IS NULL) AS total_abrechnungen;
```

### 2.4 FastAPI-Endpoint mit Redis-Cache

```python
# backend/app/api/public/stats.py
import json
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from redis.asyncio import Redis
from typing import Annotated

from app.database import get_db
from app.cache import get_redis
from app.security.public_rate_limit import public_rate_limit
from app.schemas.public import PublicStatsResponse

router = APIRouter(prefix="/api/public", tags=["public"])

@router.get("/stats", response_model=PublicStatsResponse)
async def get_public_stats(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    redis: Annotated[Redis, Depends(get_redis)],
):
    """
    Öffentliche Aggregate-Statistiken für die Marketing-Website.
    Keine Authentifizierung nötig, aber Rate-Limiting und Cache.
    """
    cache_key = "public:stats"
    cached = await redis.get(cache_key)
    
    if cached:
        data = json.loads(cached)
        return JSONResponse(
            content=data,
            headers={"X-Cache": "HIT"}
        )
    
    query = text("""
        SELECT
            (SELECT COUNT(*) FROM objekte WHERE deleted_at IS NULL) AS total_objekte,
            (SELECT COUNT(DISTINCT id) FROM vermieter_profile WHERE deleted_at IS NULL) AS total_vermieter,
            (SELECT COUNT(*) FROM einheiten WHERE aktuell_vermietet = FALSE AND deleted_at IS NULL) AS freie_wohnungen,
            (SELECT COUNT(*) FROM einheiten WHERE aktuell_vermietet = TRUE AND deleted_at IS NULL) AS vermietete_wohnungen,
            (SELECT COUNT(*) FROM tickets WHERE deleted_at IS NULL) AS total_tickets,
            (SELECT COUNT(*) FROM abrechnungen WHERE deleted_at IS NULL) AS total_abrechnungen
    """)
    
    result = await db.execute(query)
    stats = dict(result.mappings().one())
    
    await redis.setex(cache_key, 300, json.dumps(stats))  # 5 Minuten Cache
    
    return JSONResponse(
        content=stats,
        headers={"X-Cache": "MISS"}
    )
```

### 2.5 Pydantic-Schema

```python
# backend/app/schemas/public.py
from pydantic import BaseModel, Field

class PublicStatsResponse(BaseModel):
    total_objekte: int = Field(..., ge=0, description="Anzahl verwalteter Objekte")
    total_vermieter: int = Field(..., ge=0, description="Anzahl Vermieter auf der Plattform")
    freie_wohnungen: int = Field(..., ge=0, description="Anzahl freie Wohnungen")
    vermietete_wohnungen: int = Field(..., ge=0, description="Anzahl vermietete Wohnungen")
    total_tickets: int = Field(..., ge=0, description="Anzahl bearbeiteter Tickets")
    total_abrechnungen: int = Field(..., ge=0, description="Anzahl erstellter Abrechnungen")
```

### 2.6 Redis-Cache-Initialisierung

```python
# backend/app/cache.py
from redis.asyncio import Redis
from functools import lru_cache
from app.config import settings

@lru_cache()
def get_redis() -> Redis:
    return Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        max_connections=50,
    )
```

### 2.7 Vue.js 3 Counter-Komponente mit CountUp

```vue
<!-- website/components/LiveStats.vue -->
<template>
  <section class="py-24 bg-[#f5f5f7]">
    <div class="max-w-6xl mx-auto px-6">
      <h2 class="text-3xl md:text-4xl font-semibold text-center text-[#1d1d1f] mb-16">
        MietVerwaltung in Zahlen
      </h2>
      
      <div class="grid grid-cols-2 md:grid-cols-3 gap-8">
        <div
          v-for="stat in stats"
          :key="stat.key"
          class="bg-white rounded-2xl p-8 text-center shadow-sm"
        >
          <div class="text-4xl md:text-5xl font-bold text-[#0D3B70] mb-2">
            {{ animatedValues[stat.key] }}
          </div>
          <div class="text-[#6e6e73] text-sm md:text-base">
            {{ stat.label }}
          </div>
        </div>
      </div>
      
      <p class="text-center text-[#6e6e73] text-sm mt-8">
        Aktualisiert alle 5 Minuten · DSGVO-konforme Aggregat-Daten
      </p>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'

const stats = [
  { key: 'total_objekte', label: 'Verwaltete Objekte' },
  { key: 'total_vermieter', label: 'Vermieter auf der Plattform' },
  { key: 'freie_wohnungen', label: 'Freie Wohnungen' },
  { key: 'vermietete_wohnungen', label: 'Vermietete Wohnungen' },
  { key: 'total_tickets', label: 'Bearbeitete Tickets' },
  { key: 'total_abrechnungen', label: 'Erstellte Abrechnungen' },
]

const rawValues = reactive({})
const animatedValues = reactive({})

const fetchStats = async () => {
  const res = await fetch('/api/public/stats')
  const data = await res.json()
  Object.assign(rawValues, data)
  animateCounters()
}

const animateCounters = () => {
  stats.forEach(stat => {
    const target = rawValues[stat.key] || 0
    const start = animatedValues[stat.key] || 0
    const duration = 1500
    const startTime = performance.now()
    
    const step = (currentTime) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)
      const easeOut = 1 - Math.pow(1 - progress, 3)
      animatedValues[stat.key] = Math.floor(start + (target - start) * easeOut)
      
      if (progress < 1) {
        requestAnimationFrame(step)
      }
    }
    
    requestAnimationFrame(step)
  })
}

onMounted(() => {
  fetchStats()
  // Alle 5 Minuten neu laden (Cache im Backend erneuert sich ebenfalls)
  setInterval(fetchStats, 5 * 60 * 1000)
})
</script>
```

### 2.8 Cache-Invalidierung / Update

Der Cache wird automatisch nach 5 Minuten erneuert (Redis `setex`). Zusätzlich kann er bei relevanten Datenänderungen invalidiert werden:

```python
# Invalidierung bei größeren Datenänderungen (optional)
async def invalidate_public_stats(redis: Redis):
    await redis.delete("public:stats")
```

Empfohlen: **Lazy-Cache** reicht für MVP. Bei Wachstum kann ein Event-Trigger oder Cron-Job ergänzt werden.

---

## 3. Interaktive Demo auf der Website

### 3.1 Ziel

Potenzielle Kunden können die App ausprobieren, **ohne sich zu registrieren**. Die Demo soll in 2–3 Minuten den Wert der Software zeigen:

- Dashboard mit Kennzahlen
- Ein Ticket anklicken und Verlauf sehen
- Eine Nebenkostenabrechnung anschauen
- CTA: „Jetzt kostenlos registrieren“

### 3.2 Optionen A/B/C

| Option | Beschreibung | Pro | Contra |
|--------|--------------|-----|--------|
| **A: Dedizierter Demo-Tenant** | Eigener Demo-Tenant in der Produktions-DB mit vorgefüllten Testdaten. Read-only Middleware blockiert schreibende Operationen. | Echte App, keine Code-Duplikation, wartungsarm | Read-only muss technisch sauber erzwungen werden |
| **B: Statisches Mockup** | HTML/Vue-Komponenten, die nur aussehen wie die App. | Sicher, einfach deploybar | Nutzer merkt schnell, dass es keine echte App ist; hoher Pflegeaufwand bei UI-Änderungen |
| **C: Echte App mit Demo-Login** | Demo-Account `demo@mietverwaltung.de` mit festem Passwort, volle App. | Authentisch, alle Features zeigbar | Risiko von Daten-Manipulation, Missbrauch, Demo-Daten verfälschen sich |

### 3.3 Empfohlene Lösung: Option A (Demo-Tenant + Read-only Mode)

Wir empfehlen **Option A** als Primärlösung, ergänzt um Session-Limit und stündlichen Reset:

- **Echtes Produkt-Erlebnis** ohne separate Codebasis.
- **Read-only Middleware** garantiert Datensicherheit.
- **Session-Limit von 10 Minuten** verhindert Dauerbenutzung.
- **Stündlicher Reset** stellt konsistente Demo-Daten wieder her.
- **Demo-Tenant-Isolation** über Row-Level Security (RLS).

Option B ist nur als Fallback für sehr frühe MVP-Phasen sinnvoll, wenn die App noch nicht stabil ist. Option C lehnen wir ab, weil schreibende Operationen im Demo-Modus Daten-Manipulation und Compliance-Risiken (z. B. versehentliche echte Personendaten) ermöglichen.

### 3.4 Architektur Demo

```
┌─────────────────┐      ┌──────────────────────┐      ┌──────────────────┐
│   Website       │      │   Demo-Login         │      │   FastAPI App    │
│   /demo         │──────▶│   (öffentlich)       │──────▶│   (Middleware    │
│                 │      │   demo@... / pw      │      │    prüft Demo)   │
└─────────────────┘      └──────────────────────┘      └────────┬─────────┘
                                                                  │
                                                   ┌──────────────┼──────────────┐
                                                   ▼              ▼              ▼
                                          ┌────────────┐  ┌────────────┐  ┌────────────┐
                                          │ Demo-Tenant│  │ PostgreSQL │  │ Redis      │
                                          │ Read-Only  │  │ Demo-Daten │  │ Session    │
                                          └────────────┘  └────────────┘  └────────────┘
```

### 3.5 Demo-Daten

Vorgefüllte Testdaten für den Demo-Tenant:

- **3 Objekte:** „Musterstraße 1 Berlin“, „Hauptstraße 5 München“, „Rheinufer 12 Hamburg“
- **5 Wohnungen:** 2 vermietet, 3 frei
- **4 Mieter:** „Max Mustermann“, „Anna Schmidt“, „Laura Weber“, „Tom Becker“ (nur Dummy-Daten)
- **3 Tickets:** 1 offen (Heizung), 1 in Bearbeitung, 1 erledigt
- **2 Abrechnungen:** 2025 und 2026 als PDF-Vorschau

### 3.6 UX-Flow der Demo

1. Besucher klickt auf Website „Demo testen“.
2. Backend erstellt anonyme Demo-Session oder nutzt gemeinsamen Demo-Account.
3. Nutzer sieht Demo-Dashboard (ohne Login-Formular im MVP).
4. Highlight: „Probieren Sie es aus: Klicken Sie auf ein Ticket oder eine Abrechnung.“
5. Nach 10 Minuten: Auto-Logout mit Hinweis „Jetzt kostenlos registrieren“.
6. Stündlich: Demo-Daten werden zurückgesetzt.

### 3.7 Read-only Middleware

```python
# backend/app/middleware/demo_readonly.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

DEMO_USER_IDS = {"demo-user-uuid-hier"}
WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
WRITE_EXCEPTIONS = {"/api/v1/auth/logout", "/api/v1/demo/heartbeat"}

class DemoReadOnlyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user_id = request.state.user_id if hasattr(request.state, "user_id") else None
        
        if user_id in DEMO_USER_IDS:
            if request.method in WRITE_METHODS and request.url.path not in WRITE_EXCEPTIONS:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Demo-Modus ist read-only. Registrieren Sie sich für volle Funktionen."}
                )
        
        response = await call_next(request)
        response.headers["X-Demo-Mode"] = "read-only"
        return response
```

### 3.8 Demo-Session-Reset (stündlich)

```python
# backend/app/tasks/demo_reset.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

async def reset_demo_tenant(db: AsyncSession):
    """
    Löscht alle Demo-Daten und seeded sie neu.
    Läuft stündlich als Cron-Job.
    """
    demo_vermieter_id = "demo-vermieter-uuid-hier"
    
    # Soft-Delete aller Demo-Daten
    await db.execute(text("""
        UPDATE objekte SET deleted_at = NOW() WHERE vermieter_id = :vid;
        UPDATE einheiten SET deleted_at = NOW() WHERE objekt_id IN (
            SELECT id FROM objekte WHERE vermieter_id = :vid
        );
        -- Weitere Tabellen analog...
    """), {"vid": demo_vermieter_id})
    
    # Re-Seed mit Demo-Daten
    await seed_demo_data(db, demo_vermieter_id)
    await db.commit()
```

### 3.9 Session-Limit

- Redis-Schlüssel `demo:session:{session_id}` mit TTL 600 Sekunden (10 Minuten).
- Frontend zeigt Countdown-Timer.
- Bei Ablauf: Auto-Redirect zur Landing Page mit Registrierungs-CTA.

```python
# Redis-Session mit 10-Min-TTL
await redis.setex(f"demo:session:{session_id}", 600, json.dumps({"started_at": time.time()}))
```

### 3.10 Demo-CTA

Überall in der Demo sichtbar:

> **„Gefällt Ihnen, was Sie sehen?"**  
> Button: **„Jetzt kostenlos registrieren"** → `/register?source=demo`

---

## 4. Deutschland-Karte / DACH-Karte

### 4.1 Ziel

Interaktive Karte zeigt, in welchen Städten/Regionen Vermieter auf der Plattform aktiv sind. Dient als Social Proof und lockt Besucher aus der eigenen Region an.

### 4.2 Datenquelle & DSGVO

- **Nur Aggregat-Daten** pro PLZ/Ort.
- Keine einzelnen Adressen, keine Personendaten.
- Beispiel: „München: 12 Vermieter, 45 Wohnungen“.

PostgreSQL-Aggregation:

```sql
SELECT
    o.plz,
    o.ort,
    COUNT(DISTINCT o.vermieter_id) AS anzahl_vermieter,
    COUNT(DISTINCT e.id) AS anzahl_wohnungen,
    AVG(o.lat) AS lat,
    AVG(o.lon) AS lon
FROM objekte o
LEFT JOIN einheiten e ON e.objekt_id = o.id AND e.deleted_at IS NULL
WHERE o.deleted_at IS NULL
GROUP BY o.plz, o.ort
HAVING COUNT(DISTINCT o.vermieter_id) >= 3;  -- Nur Regionen mit mind. 3 Vermietern
```

> **Hinweis:** Für die Karte müssen `lat`/`lon` in `objekte` ergänzt werden (Geocoding bei Objekt-Anlage).

### 4.3 FastAPI-Endpoint für Karte

```python
# backend/app/api/public/map.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List
from redis.asyncio import Redis

from app.database import get_db
from app.cache import get_redis
from app.schemas.public import MapRegionResponse
import json

router = APIRouter(prefix="/api/public", tags=["public"])

@router.get("/map-regions", response_model=List[MapRegionResponse])
async def get_map_regions(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    cache_key = "public:map_regions"
    cached = await redis.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    query = text("""
        SELECT
            o.plz,
            o.ort,
            COUNT(DISTINCT o.vermieter_id) AS anzahl_vermieter,
            COUNT(DISTINCT e.id) AS anzahl_wohnungen,
            AVG(o.lat)::FLOAT AS lat,
            AVG(o.lon)::FLOAT AS lon
        FROM objekte o
        LEFT JOIN einheiten e ON e.objekt_id = o.id AND e.deleted_at IS NULL
        WHERE o.deleted_at IS NULL AND o.lat IS NOT NULL AND o.lon IS NOT NULL
        GROUP BY o.plz, o.ort
        HAVING COUNT(DISTINCT o.vermieter_id) >= 3
        ORDER BY anzahl_vermieter DESC
    """)
    
    result = await db.execute(query)
    regions = [dict(row) for row in result.mappings().all()]
    
    await redis.setex(cache_key, 3600, json.dumps(regions))  # 1 Stunde Cache
    return regions
```

### 4.4 Pydantic-Schema

```python
# backend/app/schemas/public.py
from pydantic import BaseModel, Field
from typing import Optional

class MapRegionResponse(BaseModel):
    plz: str = Field(..., max_length=10)
    ort: str = Field(..., max_length=100)
    anzahl_vermieter: int = Field(..., ge=0)
    anzahl_wohnungen: int = Field(..., ge=0)
    lat: float
    lon: float
```

### 4.5 Vue.js 3 + Leaflet-Komponente

```vue
<!-- website/components/DachMap.vue -->
<template>
  <section class="py-24 bg-white">
    <div class="max-w-6xl mx-auto px-6">
      <h2 class="text-3xl md:text-4xl font-semibold text-center text-[#1d1d1f] mb-4">
        MietVerwaltung in ganz Deutschland
      </h2>
      <p class="text-center text-[#6e6e73] mb-12">
        Aktive Vermieter und Wohnungen in Ihrer Region — DSGVO-konform aggregiert.
      </p>
      
      <div
        v-if="regions.length === 0"
        class="text-center py-16 bg-[#f5f5f7] rounded-2xl"
      >
        <p class="text-xl font-medium text-[#1d1d1f] mb-2">
          Noch nicht in deiner Stadt?
        </p>
        <p class="text-[#6e6e73] mb-6">
          Sei der Erste und starte kostenlos.
        </p>
        <NuxtLink
          to="/register"
          class="inline-block bg-[#0D3B70] text-white px-8 py-3 rounded-xl font-medium hover:bg-[#2a5a9e] transition"
        >
          Jetzt kostenlos registrieren
        </NuxtLink>
      </div>
      
      <div v-else id="dach-map" class="w-full h-[500px] rounded-2xl overflow-hidden shadow-sm"></div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const regions = ref([])
let map = null

const fetchRegions = async () => {
  const res = await fetch('/api/public/map-regions')
  regions.value = await res.json()
  initMap()
}

const getMarkerColor = (count) => {
  if (count >= 50) return '#0D3B70'
  if (count >= 20) return '#2a5a9e'
  if (count >= 10) return '#5a8fd8'
  return '#9bbbea'
}

const initMap = () => {
  if (regions.value.length === 0) return
  
  map = L.map('dach-map').setView([51.1657, 10.4515], 6)
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 18,
  }).addTo(map)
  
  regions.value.forEach(region => {
    const color = getMarkerColor(region.anzahl_vermieter)
    
    const marker = L.circleMarker([region.lat, region.lon], {
      radius: 8 + Math.min(region.anzahl_vermieter / 3, 20),
      fillColor: color,
      color: '#ffffff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.8,
    }).addTo(map)
    
    marker.bindPopup(`
      <div class="text-[#1d1d1f]">
        <strong class="text-[#0D3B70]">${region.ort}</strong><br>
        ${region.anzahl_vermieter} Vermieter<br>
        ${region.anzahl_wohnungen} Wohnungen
      </div>
    `)
  })
}

onMounted(() => {
  fetchRegions()
})
</script>
```

### 4.6 Fallback

Wenn keine aggregierten Karten-Daten vorhanden sind:

> **„Noch nicht in deiner Stadt? Sei der Erste!"**  
> CTA: „Jetzt kostenlos registrieren"

---

## 5. Lead-Generierung

### 5.1 Strategie

Ziel: Aus Website-Besuchern messbare Leads machen. Wir nutzen:

1. **Wert vorab bieten** (Lead-Magneten).
2. **Reibungslosen E-Mail-Exchange** (wenig Friction).
3. **Automatisierte Follow-ups** per E-Mail.
4. **Klaren Conversion-Funnel** bis zum Upgrade.

### 5.2 Lead-Magneten

| Lead-Magnet | Mechanismus | Datenerfassung |
|-------------|-------------|----------------|
| **Kostenloser NK-Abrechnungs-Check** | Upload letzte Abrechnung → KI prüft Plausibilität | E-Mail + Einwilligung |
| **Mietpreis-Rechner** | PLZ + qm → Marktmiete-Schätzung | E-Mail für Ergebnis |
| **Checkliste: Wohnungsübergabe** | PDF-Download gegen E-Mail | E-Mail + Einwilligung |
| **Newsletter: Mietrechts-Updates** | Monatliche Updates zu Mietrecht | E-Mail + Einwilligung |
| **14 Tage kostenlos testen** | Free Trial ohne Kreditkarte | Registrierung = starker Lead |

### 5.3 Conversion-Funnel

```
SEO / Ads / Social
        │
        ▼
┌─────────────────┐
│  Besucher auf   │
│  Landing Page   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Sieht Live-    │
│  Stats + Demo   │
└────────┬────────┘
         │ Interesse
         ▼
┌─────────────────┐
│ Klickt Lead-    │
│ Magnet (z. B.   │
│ NK-Check)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Gibt E-Mail ein │
│ + Einwilligung  │
└────────┬────────┘
         │ Lead erfasst
         ▼
┌─────────────────┐
│ Erhält Ergebnis │
│ per E-Mail +    │
│ „Probiere       │
│ kostenlos“      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Registrierung   │
│ Free Plan       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Aha-Moment      │
│ (erstes Objekt, │
│ erste Abrechnung)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Upgrade zu      │
│ Basis / Pro     │
└─────────────────┘
```

### 5.4 Datenbank: `leads`-Tabelle

```sql
-- Ergänzung zu db-schema-v2.sql
CREATE TABLE leads (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email               VARCHAR(255) NOT NULL,
    source              VARCHAR(100) NOT NULL,              -- 'landing_page', 'pricing_page', 'demo_exit', 'blog'
    magnet_type         VARCHAR(100) NOT NULL,             -- 'nk_check', 'mietpreis_rechner', 'checkliste_pdf', 'newsletter', 'free_trial'
    
    -- DSGVO / Double-Opt-In
    opt_in_given        BOOLEAN NOT NULL DEFAULT FALSE,     -- Checkbox aktiv angekreuzt
    opt_in_ip           INET,                               -- IP bei Einwilligung
    opt_in_at           TIMESTAMPTZ,                       -- Zeitpunkt Einwilligung
    double_opt_in_token VARCHAR(64),                       -- Token für Bestätigungslink
    double_opt_in_at    TIMESTAMPTZ,                       -- Wann bestätigt
    double_opt_in_completed BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Marketing-Tracking
    utm_source          VARCHAR(100),
    utm_medium          VARCHAR(100),
    utm_campaign        VARCHAR(100),
    landing_page_url    TEXT,
    
    -- Conversion
    converted_to_user_id UUID REFERENCES users(id),         -- Wenn Lead sich registriert
    converted_at        TIMESTAMPTZ,
    
    -- Status
    status              VARCHAR(20) DEFAULT 'new' CHECK (status IN ('new', 'confirmed', 'nurturing', 'converted', 'unsubscribed')),
    
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT chk_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE UNIQUE INDEX idx_leads_email_magnet ON leads(email, magnet_type) 
    WHERE converted_to_user_id IS NULL AND unsubscribed_at IS NULL;
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_created ON leads(created_at);
CREATE INDEX idx_leads_source ON leads(source);
```

### 5.5 FastAPI Lead-Capture Endpoint

```python
# backend/app/api/public/leads.py
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import EmailStr
from redis.asyncio import Redis
import hashlib
import secrets

from app.database import get_db
from app.cache import get_redis
from app.schemas.public import LeadCaptureRequest, LeadCaptureResponse
from app.models.lead import Lead
from app.security.public_rate_limit import public_rate_limit
from app.services.email import send_double_opt_in_email

router = APIRouter(prefix="/api/public", tags=["public"])

@router.post("/leads", response_model=LeadCaptureResponse)
async def capture_lead(
    request: Request,
    payload: LeadCaptureRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """
    Erfasst einen Lead über öffentliche Lead-Magneten.
    Rate-limited, mit Double-Opt-In und Honeypot-Schutz.
    """
    client_ip = request.client.host
    
    # Honeypot-Feld: Wenn ausgefüllt, ist es ein Bot
    if payload.website_url:  # verstecktes Feld
        return LeadCaptureResponse(success=True)  # Täuschung: Bot denkt Erfolg
    
    # Rate-Limiting: max 3 Submissions pro IP/Tag
    await public_rate_limit(
        redis=redis,
        key=f"lead:{client_ip}",
        limit=3,
        window=86400
    )
    
    # Double-Opt-In Token generieren
    token = secrets.token_urlsafe(32)
    
    lead = Lead(
        email=payload.email.lower().strip(),
        source=payload.source,
        magnet_type=payload.magnet_type,
        opt_in_given=payload.opt_in_given,
        opt_in_ip=client_ip,
        opt_in_at=datetime.utcnow(),
        double_opt_in_token=token,
        utm_source=payload.utm_source,
        utm_medium=payload.utm_medium,
        utm_campaign=payload.utm_campaign,
        landing_page_url=payload.landing_page_url,
    )
    
    db.add(lead)
    await db.commit()
    
    # Double-Opt-In E-Mail senden
    await send_double_opt_in_email(lead.email, token)
    
    return LeadCaptureResponse(
        success=True,
        message="Bitte bestätigen Sie Ihre E-Mail-Adresse."
    )
```

### 5.6 Pydantic-Schema Lead-Capture

```python
# backend/app/schemas/public.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class LeadCaptureRequest(BaseModel):
    email: EmailStr
    source: str = Field(..., max_length=100)
    magnet_type: str = Field(..., max_length=100)
    opt_in_given: bool = Field(..., description="DSGVO-Einwilligung aktiv angekreuzt")
    utm_source: Optional[str] = Field(None, max_length=100)
    utm_medium: Optional[str] = Field(None, max_length=100)
    utm_campaign: Optional[str] = Field(None, max_length=100)
    landing_page_url: Optional[str] = Field(None, max_length=500)
    website_url: Optional[str] = Field(None, max_length=100)  # Honeypot-Feld

class LeadCaptureResponse(BaseModel):
    success: bool
    message: Optional[str] = None
```

### 5.7 Vue.js Lead-Capture-Formular

```vue
<!-- website/components/LeadForm.vue -->
<template>
  <form @submit.prevent="submitLead" class="bg-white rounded-2xl p-8 shadow-sm">
    <h3 class="text-xl font-semibold text-[#1d1d1f] mb-2">
      {{ title }}
    </h3>
    <p class="text-[#6e6e73] mb-6">{{ subtitle }}</p>
    
    <!-- Honeypot: versteckt für Menschen -->
    <input
      v-model="form.website_url"
      type="text"
      name="website_url"
      tabindex="-1"
      autocomplete="off"
      class="absolute opacity-0 top-0 left-0 h-0 w-0"
    />
    
    <div class="mb-4">
      <input
        v-model="form.email"
        type="email"
        required
        placeholder="Ihre E-Mail-Adresse"
        class="w-full px-4 py-3 rounded-xl border border-[#d2d2d7] focus:border-[#0D3B70] focus:outline-none"
      />
    </div>
    
    <div class="mb-6 flex items-start gap-3">
      <input
        id="opt-in"
        v-model="form.opt_in_given"
        type="checkbox"
        required
        class="mt-1"
      />
      <label for="opt-in" class="text-sm text-[#6e6e73]">
        Ich stimme der Verarbeitung meiner E-Mail für den Lead-Magneten und
        Produkt-Updates zu. <a href="/datenschutz" class="text-[#0D3B70]">Datenschutz</a>.
      </label>
    </div>
    
    <button
      type="submit"
      :disabled="isSubmitting"
      class="w-full bg-[#0D3B70] text-white py-3 rounded-xl font-medium hover:bg-[#2a5a9e] transition disabled:opacity-50"
    >
      {{ isSubmitting ? 'Wird gesendet...' : buttonText }}
    </button>
    
    <p v-if="message" class="mt-4 text-sm text-center" :class="success ? 'text-green-600' : 'text-red-500'">
      {{ message }}
    </p>
  </form>
</template>

<script setup>
import { reactive, ref } from 'vue'

const props = defineProps({
  title: { type: String, default: 'Kostenloser NK-Abrechnungs-Check' },
  subtitle: { type: String, default: 'Laden Sie Ihre letzte Abrechnung hoch — wir prüfen sie mit KI.' },
  buttonText: { type: String, default: 'Jetzt kostenlos prüfen' },
  magnetType: { type: String, default: 'nk_check' },
  source: { type: String, default: 'landing_page' }
})

const form = reactive({
  email: '',
  opt_in_given: false,
  website_url: '',  // Honeypot
  source: props.source,
  magnet_type: props.magnetType,
  utm_source: '',
  utm_medium: '',
  utm_campaign: '',
  landing_page_url: typeof window !== 'undefined' ? window.location.href : ''
})

const isSubmitting = ref(false)
const message = ref('')
const success = ref(false)

const submitLead = async () => {
  isSubmitting.value = true
  message.value = ''
  
  try {
    const res = await fetch('/api/public/leads', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })
    
    const data = await res.json()
    success.value = data.success
    message.value = data.message || 'Vielen Dank! Bitte bestätigen Sie Ihre E-Mail.'
    
    if (data.success) {
      form.email = ''
      form.opt_in_given = false
    }
  } catch (err) {
    success.value = false
    message.value = 'Etwas ist schiefgelaufen. Bitte versuchen Sie es erneut.'
  } finally {
    isSubmitting.value = false
  }
}
</script>
```

---

## 6. SEO-Strategie

### 6.1 Keyword-Recherche (DACH)

| Priorität | Keyword | Suchintention |
|-----------|---------|---------------|
| Hoch | Mietverwaltung Software | Informations- / Kauf |
| Hoch | Nebenkostenabrechnung Programm | Problem-Lösung |
| Hoch | Vermieter Software | Kauf |
| Mittel | Mietverwaltung Online | Kauf |
| Mittel | Wohnungsübergabe Checkliste | Information |
| Mittel | Mietpreis rechner | Tool |
| Mittel | Nebenkostenabrechnung prüfen lassen | Service |
| Langschwanz | Mietverwaltung Software für Kleinvermieter | Nischen-Kauf |
| Langschwanz | Kostenlose Mietverwaltung Software | Free-Tier |
| Langschwanz | Mietverwaltung Deutschland Österreich Schweiz | DACH |

### 6.2 KI-generierte Meta-Tags

Beispiel für Landing Page:

```html
<title>MietVerwaltung Software | 80% automatisiert — kostenlos starten</title>
<meta name="description" content="MietVerwaltung für private Kleinvermieter in Deutschland, Österreich und der Schweiz. Objekte, Mieter, Tickets, Nebenkostenabrechnung & KI-Automation. Jetzt kostenlos testen.">
<meta name="keywords" content="Mietverwaltung Software, Vermieter Software, Nebenkostenabrechnung Programm, Kleinvermieter, DACH">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://www.mietverwaltung.de/">

<!-- Open Graph -->
<meta property="og:title" content="MietVerwaltung Software | 80% automatisiert">
<meta property="og:description" content="Die KI-gestützte Mietverwaltung für private Kleinvermieter. Jetzt kostenlos starten.">
<meta property="og:image" content="https://www.mietverwaltung.de/og-image.jpg">
<meta property="og:url" content="https://www.mietverwaltung.de/">
<meta property="og:type" content="website">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="MietVerwaltung Software | 80% automatisiert">
<meta name="twitter:description" content="Die KI-gestützte Mietverwaltung für private Kleinvermieter.">
<meta name="twitter:image" content="https://www.mietverwaltung.de/og-image.jpg">

<!-- Hreflang DACH -->
<link rel="alternate" hreflang="de-DE" href="https://www.mietverwaltung.de/de-de/">
<link rel="alternate" hreflang="de-AT" href="https://www.mietverwaltung.de/de-at/">
<link rel="alternate" hreflang="de-CH" href="https://www.mietverwaltung.de/de-ch/">
<link rel="alternate" hreflang="x-default" href="https://www.mietverwaltung.de/">
```

### 6.3 Structured Data (schema.org)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "MietVerwaltung",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "EUR"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "ratingCount": "124"
  },
  "description": "KI-gestützte Mietverwaltung für private Kleinvermieter in DE/AT/CH.",
  "url": "https://www.mietverwaltung.de",
  "author": {
    "@type": "Organization",
    "name": "MietVerwaltung GmbH"
  }
}
</script>
```

### 6.4 Sitemap & robots.txt

**robots.txt:**

```text
User-agent: *
Allow: /
Disallow: /api/
Disallow: /app/
Disallow: /admin/
Disallow: /demo-internal/

Sitemap: https://www.mietverwaltung.de/sitemap.xml
```

**Sitemap-Generierung in Nuxt:**

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@nuxtjs/sitemap'],
  sitemap: {
    hostname: 'https://www.mietverwaltung.de',
    gzip: true,
    routes: [
      '/',
      '/features',
      '/pricing',
      '/demo',
      '/ueber-uns',
      '/blog'
    ]
  }
})
```

### 6.5 Performance & Core Web Vitals

| Metrik | Ziel | Maßnahme |
|--------|------|----------|
| LCP | < 2,5 s | Bilder lazy, WebP/AVIF, CDN |
| FID/INP | < 200 ms | Code-Splitting, kein render-blockierendes JS |
| CLS | < 0,1 | Feste Größen für Bilder/Maps |
| TTFB | < 600 ms | Nuxt SSR + Redis Cache |
| Gesamtladezeit | < 2 s | Static Assets cachen, gzip/brotli |

---

## 7. Analytics (DSGVO-konform)

### 7.1 Problem Google Analytics

Google Analytics ist US-basiert und erfordert zusätzliche DSGVO-Hürden (Auftragsverarbeitung, Datenübermittlung, Cookie-Banner). Wir vermeiden es.

### 7.2 Empfohlene Lösung: Plausible

**Plausible** wird self-hosted auf Proxmox/Hetzner betrieben:

- EU-hosted (bei Self-Hosting: unsere eigene Infrastruktur in DE/AT/CH).
- Keine Cookies, kein Cookie-Banner nötig.
- DSGVO-konform by Design.
- Leichtes Script (~1 KB).
- Einfache Event-Tracking API.

Alternativ: **Matomo** (self-hosted), aber höherer Wartungsaufwand. Plausible ist für MVP ausreichend.

### 7.3 Plausible-Integration

```html
<!-- In <head> der Website -->
<script
  defer
  data-domain="www.mietverwaltung.de"
  src="https://plausible.mietverwaltung.de/js/plausible.outbound-links.js"
></script>
<script>window.plausible = window.plausible || function() { (window.plausible.q = window.plausible.q || []).push(arguments) }</script>
```

### 7.4 Analytics-Events

| Event | Trigger | Ziel |
|-------|---------|------|
| `pageview` | Jede Seite | Traffic-Messung |
| `demo_start` | Klick auf „Demo testen“ | Demo-Interesse |
| `demo_session_end` | 10-Min-Timeout | Engagement |
| `lead_capture` | Lead-Formular abgeschickt | Lead-Generierung |
| `lead_magnet_click` | Klick auf Lead-Magnet-CTA | Interesse |
| `register_start` | Klick auf „Kostenlos registrieren" | Conversion-Anfang |
| `register_complete` | Erfolgreiche Registrierung | Account-Erstellung |
| `upgrade_click` | Klick auf Upgrade-Button | Upsell-Interesse |
| `upgrade_complete` | Erfolgreicher Stripe-Checkout | Umsatz |
| `pricing_view` | Pricing-Seite besucht | Preisinteresse |

**Beispiel Event-Tracking:**

```javascript
// Demo-Start tracken
function trackDemoStart() {
  if (window.plausible) {
    plausible('demo_start')
  }
}

// Lead-Capture tracken
function trackLeadCapture(magnetType) {
  if (window.plausible) {
    plausible('lead_capture', { props: { magnet: magnetType } })
  }
}
```

### 7.5 Zusammenfassung Tracking-Events als Tabelle

| # | Event | Kategorie | Sensible Daten |
|---|-------|-----------|----------------|
| 1 | `pageview` | Engagement | Nein |
| 2 | `demo_start` | Product | Nein |
| 3 | `demo_session_end` | Product | Nein |
| 4 | `lead_capture` | Conversion | E-Mail nicht an Analytics |
| 5 | `lead_magnet_click` | Conversion | Nein |
| 6 | `register_start` | Conversion | Nein |
| 7 | `register_complete` | Conversion | Nein (nur Event, keine E-Mail) |
| 8 | `upgrade_click` | Revenue | Nein |
| 9 | `upgrade_complete` | Revenue | Nein (nur Plan-Tier) |
| 10 | `pricing_view` | Funnel | Nein |

---

## 8. Öffentliche API-Sicherheit

> **Prinzip:** Alle öffentlichen Endpunkte sind zwar ohne Authentifizierung erreichbar, aber technisch zu 100% abgesichert. Keine Personendaten, keine internen IDs, striktes Rate-Limiting, Redis-Cache und validierter Input.

### 8.1 GET /api/public/stats (Live-Statistiken)

Sicherheitsmaßnahmen:

| Maßnahme | Umsetzung |
|----------|-----------|
| Rate-Limiting | 60 req/min pro IP |
| Redis-Cache | 5 Min — Cache-Hit beantwortet ohne DB-Query |
| Keine Personendaten | Nur Aggregate-Counts |
| SQL-Injection | Parameterized Queries, kein User-Input |
| CORS | Nur eigene Domain, kein `*` |
| Response-Größe | Max ~2 KB JSON |
| Logging | IP, Endpoint, Timestamp für Audit |

#### FastAPI-Rate-Limit-Decorator

```python
# backend/app/security/public_rate_limit.py
from fastapi import Request, HTTPException
from redis.asyncio import Redis
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import time

async def public_rate_limit(
    redis: Redis,
    key: str,
    limit: int,
    window: int
):
    """
    Sliding-Window Rate-Limiting mit Redis.
    key: z. B. 'stats:{client_ip}'
    limit: max Anzahl Requests
    window: Zeitfenster in Sekunden
    """
    now = int(time.time())
    window_start = now - window
    
    # Alte Einträge entfernen
    await redis.zremrangebyscore(key, 0, window_start)
    
    # Aktuelle Anzahl im Fenster
    current = await redis.zcard(key)
    
    if current >= limit:
        raise HTTPException(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail="Zu viele Anfragen. Bitte versuchen Sie es später erneut."
        )
    
    # Neuen Request hinzufügen
    await redis.zadd(key, {str(now): now})
    await redis.expire(key, window)
```

#### Stats-Endpoint mit Rate-Limiting und CORS

```python
# backend/app/api/public/stats.py (erweitert)
from fastapi import APIRouter, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from redis.asyncio import Redis
import json

from app.database import get_db
from app.cache import get_redis
from app.security.public_rate_limit import public_rate_limit
from app.schemas.public import PublicStatsResponse

router = APIRouter(prefix="/api/public", tags=["public"])

@router.get("/stats", response_model=PublicStatsResponse)
async def get_public_stats(
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    client_ip = request.client.host
    
    # Rate-Limiting: 60 req/min pro IP
    await public_rate_limit(
        redis=redis,
        key=f"public:stats:{client_ip}",
        limit=60,
        window=60
    )
    
    cache_key = "public:stats"
    cached = await redis.get(cache_key)
    
    if cached:
        data = json.loads(cached)
        return JSONResponse(content=data, headers={"X-Cache": "HIT"})
    
    query = text("""
        SELECT
            (SELECT COUNT(*) FROM objekte WHERE deleted_at IS NULL) AS total_objekte,
            (SELECT COUNT(DISTINCT id) FROM vermieter_profile WHERE deleted_at IS NULL) AS total_vermieter,
            (SELECT COUNT(*) FROM einheiten WHERE aktuell_vermietet = FALSE AND deleted_at IS NULL) AS freie_wohnungen,
            (SELECT COUNT(*) FROM einheiten WHERE aktuell_vermietet = TRUE AND deleted_at IS NULL) AS vermietete_wohnungen,
            (SELECT COUNT(*) FROM tickets WHERE deleted_at IS NULL) AS total_tickets,
            (SELECT COUNT(*) FROM abrechnungen WHERE deleted_at IS NULL) AS total_abrechnungen
    """)
    
    result = await db.execute(query)
    stats = dict(result.mappings().one())
    
    await redis.setex(cache_key, 300, json.dumps(stats))
    
    return JSONResponse(
        content=stats,
        headers={
            "X-Cache": "MISS",
            "X-RateLimit-Limit": "60",
            "X-Content-Type-Options": "nosniff",
        }
    )
```

#### CORS-Konfiguration

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

allowed_origins = [
    "https://www.mietverwaltung.de",
    "https://marketing.mietverwaltung.de",
    "https://app.mietverwaltung.de",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # KEIN wildcard *
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    max_age=600,
)
```

### 8.2 Demo-Zugang (öffentlicher Login)

Sicherheitsmaßnahmen:

| Maßnahme | Umsetzung |
|----------|-----------|
| Demo-Account | `demo@mietverwaltung.de` |
| Read-only Mode | Middleware blockiert POST/PUT/DELETE/PATCH |
| Session-Limit | 10 Min, dann Auto-Logout |
| Rate-Limiting | Max 5 Demo-Sessions gleichzeitig pro IP |
| Tenant-Isolation | Demo-User sieht nur Demo-Daten (RLS) |
| Demo-Daten-Reset | Stündlich per Cron |
| Keine echten Personendaten | Nur Dummy-Namen |
| Audit-Logging | IP + Zeitstempel bei Demo-Login |

#### Demo-Account-RLS-Policy

```sql
-- Demo-User darf NUR Demo-Tenant-Daten sehen
CREATE POLICY demo_tenant_isolation ON objekte
    FOR SELECT TO public
    USING (vermieter_id = current_setting('app.demo_vermieter_id')::uuid);

-- Gleiche Policies für alle relevanten Tabellen (einheiten, mieter, tickets, etc.)
```

#### Demo-Session-Limit

```python
# backend/app/api/public/demo.py
from fastapi import APIRouter, Depends, Request, HTTPException
from redis.asyncio import Redis
import json
import time

from app.cache import get_redis
from app.security.public_rate_limit import public_rate_limit

router = APIRouter(prefix="/api/public/demo", tags=["public"])

MAX_CONCURRENT_DEMO_SESSIONS = 5

@router.post("/start")
async def start_demo(
    request: Request,
    redis: Redis = Depends(get_redis),
):
    client_ip = request.client.host
    
    # Max 5 gleichzeitige Demo-Sessions pro IP
    await public_rate_limit(
        redis=redis,
        key=f"demo:session_count:{client_ip}",
        limit=MAX_CONCURRENT_DEMO_SESSIONS,
        window=600  # 10 Minuten Fenster
    )
    
    session_id = secrets.token_urlsafe(32)
    session_data = {
        "started_at": time.time(),
        "ip": client_ip,
        "user_agent": request.headers.get("user-agent", "")
    }
    
    # 10-Minuten-TTL
    await redis.setex(
        f"demo:session:{session_id}",
        600,
        json.dumps(session_data)
    )
    
    # Audit-Log-Eintrag (anonymisiert)
    await log_demo_access(client_ip, request.headers.get("user-agent", ""))
    
    return {
        "session_id": session_id,
        "expires_at": time.time() + 600
    }
```

### 8.3 Lead-Capture (E-Mail-Erfassung ohne Auth)

Sicherheitsmaßnahmen:

| Maßnahme | Umsetzung |
|----------|-----------|
| Rate-Limiting | Max 3 Submissions pro IP/Tag |
| E-Mail-Validierung | Pydantic EmailStr + MX-Check |
| Honeypot-Feld | Verstecktes Input-Feld |
| Bot-Schutz | Turnstile (Cloudflare) oder hCaptcha (EU) |
| Double-Opt-In | Bestätigungslink vor Speicherung als aktiver Lead |
| DSGVO | Aktive Einwilligung erforderlich |
| SQL-Injection | Pydantic + parameterized queries |
| XSS | Output-Encoding, CSP |

#### E-Mail-MX-Check

```python
# backend/app/services/email_validation.py
import dns.resolver
from pydantic import EmailStr
import re

def validate_email_with_mx(email: str) -> bool:
    """
    Prüft E-Mail-Format und MX-Record der Domain.
    """
    if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', email):
        return False
    
    domain = email.split('@')[1]
    try:
        records = dns.resolver.resolve(domain, 'MX')
        return len(records) > 0
    except Exception:
        return False
```

#### Turnstile-Validierung

```python
# backend/app/security/turnstile.py
import httpx
from app.config import settings

async def verify_turnstile_token(token: str, client_ip: str) -> bool:
    """
    Validiert Cloudflare Turnstile Token.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": settings.TURNSTILE_SECRET_KEY,
                "response": token,
                "remoteip": client_ip,
            },
            timeout=10.0
        )
    
    result = response.json()
    return result.get("success", False)
```

### 8.4 Stripe Webhook Endpoint

Sicherheitsmaßnahmen:

| Maßnahme | Umsetzung |
|----------|-----------|
| Stripe-Signatur-Verifikation | Stripe SDK `verify` |
| Raw-Body | Nicht geparstes JSON für Signature-Check |
| Idempotenz | `stripe_event_id` als UNIQUE-Constraint |
| Rate-Limiting | Kein Rate-Limiting für Stripe, aber IP-Whitelist |
| IP-Whitelist | Nur Stripe-IPs dürfen Endpoint aufrufen |
| Webhook-Secret | In Environment, nie im Code |
| Responsezeit | 200 OK innerhalb 3 Sekunden |

#### Stripe Webhook Implementation

```python
# backend/app/api/webhooks/stripe.py
from fastapi import APIRouter, Request, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
import stripe
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.services.subscriptions import handle_checkout_completed, handle_subscription_cancelled

router = APIRouter(prefix="/api/webhooks/stripe", tags=["webhooks"])

# Stripe-IPs Whitelist (sollte regelmäßig aktualisiert werden)
STRIPE_IP_RANGES = [
    "3.18.12.0/22",
    "3.130.192.0/21",
    "13.235.14.0/23",
    "35.154.0.0/16",
    "52.15.183.0/24",
    "54.187.174.0/24",
    "54.241.31.0/24",
    "96.47.0.0/16",
    "169.254.0.0/16",
]

@router.post("/")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
):
    # 1. IP-Whitelist prüfen
    client_ip = request.client.host
    if not is_stripe_ip(client_ip):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # 2. Raw-Body lesen
    payload = await request.body()
    
    # 3. Stripe-Signatur verifizieren
    try:
        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # 4. Idempotenz prüfen
    existing = await db.execute(
        select(StripeWebhookEvent).where(StripeWebhookEvent.stripe_event_id == event["id"])
    )
    if existing.scalar_one_or_none():
        return JSONResponse(content={"status": "already processed"})
    
    # 5. Event speichern
    webhook_event = StripeWebhookEvent(
        stripe_event_id=event["id"],
        event_type=event["type"],
        payload=event["data"]["object"],
    )
    db.add(webhook_event)
    await db.commit()
    
    # 6. Asynchrone Verarbeitung (schnell 200 OK zurückgeben)
    if event["type"] == "checkout.session.completed":
        await handle_checkout_completed(event["data"]["object"])
    elif event["type"] == "customer.subscription.deleted":
        await handle_subscription_cancelled(event["data"]["object"])
    
    return JSONResponse(content={"status": "success"})

def is_stripe_ip(ip: str) -> bool:
    import ipaddress
    ip_obj = ipaddress.ip_address(ip)
    return any(ip_obj in ipaddress.ip_network(cidr) for cidr in STRIPE_IP_RANGES)
```

#### Stripe Webhook Event-Tabelle

```sql
CREATE TABLE stripe_webhook_events (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stripe_event_id     VARCHAR(255) NOT NULL UNIQUE,        -- Idempotenz
    event_type          VARCHAR(100) NOT NULL,
    payload             JSONB NOT NULL,
    processed           BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_stripe_events_unprocessed ON stripe_webhook_events(processed) WHERE processed = FALSE;
```

### 8.5 Stripe Checkout / Payment

Sicherheitsmaßnahmen:

| Maßnahme | Umsetzung |
|----------|-----------|
| Keine Kartendaten auf Server | Stripe Elements = iframe, Daten gehen direkt an Stripe |
| PCI-DSS | SAQ-A (niedrigstes Level) |
| Keys | Publishable Key öffentlich, Secret Key nur Server |
| HTTPS | Pflicht für alle Payment-Seiten |
| CSRF-Schutz | Checkout-Formular mit CSRF-Token |
| Source of Truth | Webhook, nicht Frontend-Response |

#### Stripe-Checkout Session

```python
# backend/app/api/public/checkout.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
import stripe

from app.config import settings
from app.database import get_db
from app.auth import get_current_user  # auth-geschützter Endpunkt

router = APIRouter(prefix="/api/v1/checkout", tags=["checkout"])

@router.post("/create-session")
async def create_checkout_session(
    plan: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Erstellt eine Stripe Checkout Session.
    Auth-required — keine öffentliche Schnittstelle, aber Teil der Conversion.
    """
    try:
        session = stripe.checkout.Session.create(
            api_key=settings.STRIPE_SECRET_KEY,
            customer_email=current_user.email,
            line_items=[{
                "price": settings.STRIPE_PRICE_IDS[plan],
                "quantity": 1,
            }],
            mode="subscription",
            success_url="https://app.mietverwaltung.de/payment/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://app.mietverwaltung.de/pricing?canceled=true",
            metadata={
                "user_id": str(current_user.id),
                "plan": plan,
            },
        )
        return {"checkout_url": session.url}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 8.6 Allgemeine API-Security

| Maßnahme | Umsetzung |
|----------|-----------|
| Trennung Public/Auth | `/api/public/*` vs `/api/v1/*` |
| API-Gateway | nginx rate-limiting erste Verteidigungslinie |
| DDoS-Schutz | Cloudflare (kostenlos) |
| Request-Size | Max 10 KB für Public-API |
| Response-Header | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` |
| Keine internen Details | Generische Fehlermeldungen |
| Logging | IP, Endpoint, Timestamp |
| Error-Handling | Keine Stack-Traces in Production |

#### nginx-Rate-Limiting

```nginx
# /etc/nginx/sites-available/mietverwaltung
limit_req_zone $binary_remote_addr zone=public_api:10m rate=60r/m;
limit_req_zone $binary_remote_addr zone=lead_api:10m rate=3r/d;
limit_req_zone $binary_remote_addr zone=demo_api:10m rate=5r/m;

server {
    listen 443 ssl http2;
    server_name www.mietverwaltung.de;

    location /api/public/stats {
        limit_req zone=public_api burst=10 nodelay;
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/public/leads {
        limit_req zone=lead_api burst=5 nodelay;
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/public/demo {
        limit_req zone=demo_api burst=5 nodelay;
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Stripe Webhook: keine Rate-Limiting, aber IP-Whitelist in FastAPI
    location /api/webhooks/stripe {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

### 8.7 Input-Validation für alle öffentlichen Endpunkte

| Maßnahme | Umsetzung |
|----------|-----------|
| Pydantic für alle Endpunkte | Auch GET mit Query-Params |
| String-Längen begrenzt | Max 500 Zeichen für URLs, max 255 für E-Mail |
| Unicode-Normalisierung | NFC vor Validierung |
| HTML/Script-Tags strippen | Bleach oder eigene Sanitize-Funktion |
| JSON-Payload-Size | Max 10 KB |
| Content-Type | Nur `application/json` bei POST |

#### Allgemeine Sanitize-Hilfsfunktion

```python
# backend/app/security/sanitize.py
import re
import unicodedata

def sanitize_string(value: str, max_length: int = 255) -> str:
    """
    Normalisiert, begrenzt und entfernt potenziell gefährliche Zeichen.
    """
    if not value:
        return ""
    
    # Unicode-Normalisierung
    value = unicodedata.normalize("NFC", value)
    
    # Länge begrenzen
    value = value[:max_length]
    
    # HTML-Tags entfernen
    value = re.sub(r'<[^>]+>', '', value)
    
    # Null-Bytes entfernen
    value = value.replace('\x00', '')
    
    return value.strip()
```

---

## 9. Kosten

| Posten | Kosten (MVP) | Kosten (Go-Live) |
|--------|--------------|------------------|
| Website Hosting (Proxmox / Hetzner) | 0€ (intern) | ~5–10€/Monat (Hetzner CX21) |
| Domain `mietverwaltung.de` | — | ~10–15€/Jahr |
| Leaflet.js + OpenStreetMap Tiles | 0€ | 0€ |
| Plausible Analytics (self-hosted) | 0€ | 0€ (eigener Server) |
| Plausible Cloud (Alternative) | — | ~9€/Monat |
| Demo-Daten / Demo-Tenant | 0€ | 0€ |
| SSL-Zertifikat (Let's Encrypt) | 0€ | 0€ |
| Cloudflare (Free Plan) | 0€ | 0€ |
| E-Mail-Versand (Resend/SendGrid) | 0€ (Test-Kontingent) | ~10–20€/Monat |
| **Gesamt (MVP)** | **0€** | — |
| **Gesamt (Go-Live, geschätzt)** | — | **~25–55€/Monat** |

---

## 10. Zusammenfassung & Nächste Schritte

### Was das Konzept abdeckt

1. **Öffentliche Website** mit klarer Architektur, Trennung von SaaS-App, Nuxt.js 3 SSR, SEO und Apple-Style Design.
2. **Live-Statistiken** mit Redis-Cache, animierten Countern, DSGVO-konformen Aggregaten und FastAPI-Endpoint.
3. **Interaktive Demo** ohne Registrierung, Read-only Demo-Tenant, 10-Min-Session-Limit, stündlicher Reset.
4. **DACH-Karte** mit Leaflet.js, OpenStreetMap, aggregierten PLZ-Daten und Fallback-CTA.
5. **Lead-Generierung** mit Lead-Magneten, Conversion-Funnel, `leads`-Tabelle, Double-Opt-In und Lead-Capture-Formular.
6. **SEO-Strategie** mit Keywords, KI-Meta-Tags, schema.org, Sitemap und Performance-Zielen.
7. **DSGVO-konformes Analytics** mit Plausible (self-hosted) und Event-Tabelle.
8. **Öffentliche API-Sicherheit** mit Rate-Limiting, CORS, Input-Validation, Demo-Readonly, Stripe-Webhook-Sicherheit und nginx-Konfiguration.
9. **Kostenübersicht** für MVP (0€) und Go-Live (~25–55€/Monat).

### Nächste Schritte

1. **Domain & Hosting:** MVP auf Proxmox, später `www.mietverwaltung.de` auf Hetzner.
2. **Nuxt.js 3 Website-Setup:** Initiales Projekt mit TailwindCSS, i18n, Sitemap.
3. **FastAPI Public API:** Endpunkte `/api/public/stats`, `/api/public/map-regions`, `/api/public/leads`, `/api/public/demo/start` implementieren.
4. **Redis-Cache & Rate-Limiting:** In Produktions-Infrastruktur einrichten.
5. **Demo-Tenant + Read-only Middleware:** Demo-Daten seeden, Reset-Cron einrichten.
6. **Leaflet-Kartenkomponente:** PLZ-Geocoding für Objekte ergänzen.
7. **Lead-Flow:** Double-Opt-In-E-Mails, Plausible-Events, Conversion-Tracking.
8. **Security-Audit:** Alle öffentlichen Endpunkte vor Launch pentesten.
9. **A/B-Tests:** Landing-Page-Varianten, Lead-Magneten-Performance messen.

---

## 11. Noch offene Themen für eine perfekte SaaS-Lösung

Dieser Abschnitt analysiert systematisch, was bereits im MietVerwaltung-Ökosystem abgedeckt ist und welche Themen für eine vollständige, marktführende SaaS-Lösung noch ergänzt werden müssen. Ziel ist es, Lücken frühzeitig zu identifizieren und eine klare Priorisierung für MVP, Go-Live, Scale und Nice-to-Have zu geben.

---

### 11.1 Was haben wir bereits abgedeckt?

| Bereich | Abgedeckt in | Stand |
|---------|--------------|-------|
| **Abo-Modell & Pricing** | `Abo-Modell.md` | 4 Tiers (Free/Basis/Pro/Business), upsell-fokussiert, klar feature-gestaffelt |
| **Datenbank-Architektur** | `db-schema-v2.sql` | 22 Tabellen, RLS, Soft-Delete, Audit-Logs, Einwilligungen, Sessions |
| **KI-Features** | `KI-Konzept.md` | OCR, Ticket-Kategorisierung, Mahnungen, Mieterhöhung, Smart Insights |
| **UX/UI & Onboarding** | `UX-UI-Konzept-konsolidiert.md`, `konzept-onboarding.md` | Apple-Style, Time-to-Value < 5 Min, Demo-Dashboard, Checklisten |
| **Öffentliche Website & Lead-Gen** | Dieses Dokument | Landing Page, Live-Stats, Demo, DACH-Karte, Lead-Magneten, SEO, Analytics |
| **API-Sicherheit** | Dieses Dokument | Rate-Limiting, CORS, Demo-Readonly, Stripe-Webhooks, Input-Validation |
| **Server-Infrastruktur** | `Server-Konzept-v2.md` | Proxmox-MVP, Hetzner-Go-Live, Docker, Redis, PostgreSQL |
| **Grundlegende Sicherheit** | `db-schema-v2.sql`, `Server-Konzept-v2.md` | 2FA, Argon2, RLS, Audit-Logs, Verschlüsselung sensibler Felder |
| **Conversion-Optimierung** | `konzept-conversion-optimierung.md` | Psychologie-Tricks, Funnel, CTA-Strategien |
| **Mobile UX** | `konzept-mobile-ux.md` | Mobile-first, Bottom-Tabbar, Touch-Targets |

**Fazit:** Die Kernelemente für den MVP (Registrierung, Objekt-/Mieter-Verwaltung, Tickets, Kosten, Abrechnung, KI-Basis, Subscription) sind gut konzipiert. Was noch fehlt, sind überwiegend **Erweiterungen für Rechtssicherheit, Integrationen, Skalierung und professionelle Vermieter-Workflows**.

---

### 11.2 Was fehlt noch für eine perfekte Lösung?

#### A. Rechtliches & DACH-Spezifika

| Thema | Beschreibung | Warum wichtig |
|-------|--------------|---------------|
| **AT/CH-Rechtslagen** | Österreich und Schweiz haben teilweise abweichende Mietrechts-Regelungen (z. B. Kaution in CH max 3 Monatsmieten, Mieterhöhungsregeln in AT). | Sonst keine echte DACH-Tauglichkeit |
| **GoBD-Konformität** | Grundsätze zur ordnungsmäßigen Führung und Aufbewahrung von Büchern. Betrifft Rechnungen, Belege, Abrechnungen, Audit-Trail. | Steuerrechtliche Pflicht in DE |
| **DATEV-Export** | Buchhaltungsdaten-Export für Steuerberater (Buchungsstapel, Kreditoren/Debitoren). | Professionelle Vermieter/Hausverwaltungen erwarten das |
| **Anlage V Export** | Übersicht über Einkünfte aus Vermietung für die Steuererklärung. | Kleinvermieter spart Zeit |
| **eIDAS / QES-Signatur** | Qualifizierte elektronische Signatur für Mietverträge, Kündigungen, Abrechnungen. | Rechtssichere digitale Verträge |
| **Automatisierte Fristen-Warnung** | Kündigungsfristen, Abrechnungsfristen, Einwendungsfristen (§556 BGB). | Vermeidet teure Fehler |
| **Dokumenten-Aufbewahrung & Archivierung** | 10-Jahres-Aufbewahrungspflicht für Steuerbelege und Mietunterlagen, automatisch versioniert. | GoBD + DSGVO |
| **WEG-Verwaltung (Eigentumswohnungen)** | Verwaltung von Eigentumsanteilen, Hausgeld, WEG-Abrechnung, Eigentümerversammlungen. | Deutlich erweitertes Marktsegment |
| **Gewerbliche Vermietung** | Andere Steuerregeln (USt., Gewerbe), Gewerbemietverträge, Indexmiete-Regeln. | Business-Kunden |
| **Gästeverwaltung (AirBnB / FeWo)** | Kurzzeitvermietung, Tourismusabgaben, Belegungspflichten, Meldegesetz. | Neues Segment |

#### B. Finanzen, Banken & Steuerberater

| Thema | Beschreibung | Warum wichtig |
|-------|--------------|---------------|
| **Bank-Anbindung / FinTS/HBCI / PSD2** | Automatischer Import von Mietzahlungen, Zuordnung zu Mieter/Mietvertrag. | Spart massiv Zeit, reduziert Mahnungen |
| **Transaction Import (CSV/MT940/CAMT)** | Fallback zur Bank-Anbindung: Import von Kontoauszügen. | Unverzichtbar für Go-Live |
| **Automatisches Zahlungs-Matching** | KI-Zuordnung von Zahlungseingängen zu offenen Posten. | Reduziert manuelle Arbeit |
| **Steuerberater-Zugang** | Read-only Login für Steuerberater mit eigener Rolle, Zugriff auf relevante Dokumente. | Starker B2B-Sales-Argument |
| **Kassenbuch / Einnahmen-Überschuss-Rechnung (EÜR)** | Einfache EÜR für Kleinvermieter. | Steuerliche Komplettlösung |
| **Automatische Mahnwesen mit Zahlungs-Tracking** | Tag 3/7/14/21 Mahnstufen, Zahlungseingang stoppt Mahnung automatisch. | Cashflow-Optimierung |

#### C. Mieter-Workflows & Bewerbung

| Thema | Beschreibung | Warum wichtig |
|-------|--------------|---------------|
| **Mieter-Score (ohne automatisierte Entscheidung)** | Anzeige von Bonität, Einkommen, Schufa-Status — nur als Indikator, Entscheidung beim Vermieter. | Rechtssicher + hilfreich |
| **Schufa-Anbindung** | Bonitätsprüfung mit expliziter Einwilligung des Bewerbers. | Premium-Feature für Pro/Business |
| **Digitaler Mietvertrag mit eSignatur** | Vollständig digitaler Vertragsabschluss. | Moderner Vermieter-Workflow |
| **Video-Übergabeprotokoll** | Aufnahme des Übergabe-Zustands mit Zeitstempel und Mieter-Einwilligung. | Streitvermeidung |
| **Mieter-Bewerbungs-Portal** | Upload von Ausweis (Kopie), Lohnabrechnung, Schufa, KI-Extraktion. | Bereits teilweise in Pro/Business geplant |
| **Mieter-App / PWA mit Push** | Push-Benachrichtigungen für Tickets, Abrechnungen, Fristen. | Bindung + Response-Rate |
| **Kommunikations-Hub** | Zentrale Kommunikation mit Mieter (E-Mail, In-App, ggf. SMS). | Reduziert E-Mail-Chaos |

#### D. Objekt- & Portfoliomanagement

| Thema | Beschreibung | Warum wichtig |
|-------|--------------|---------------|
| **Energieausweis-Management** | Erfassung von Energieausweisen, Ablauf-Fristen, Anforderungen an Vermieter. | Gesetzlich gefordert, steigende Relevanz |
| **Versicherungs-Checks** | Verwaltung von Gebäudeversicherung, Haftpflicht, Glasversicherung, Ablauf-Fristen. | Risikominimierung |
| **Garage / Stellplatz-Verwaltung** | Separate Verwaltung von Nebenflächen, separaten Mietverträgen. | Praxisrelevant |
| **Leerstands-Analyse & Warnung** | Erkennung von Leerständen, Kosten, Marktvergleich, Vermietungsempfehlung. | Umsatzoptimierung |
| **KI-Mietpreis-Analyse / Mietspiegel-Abgleich** | Automatischer Vergleich mit lokalem Mietspiegel, Mieterhöhungsempfehlung §558 BGB. | Starkes KI-Feature |
| **Automatische NK-Abrechnung mit Zählerständen** | Integration von Strom/Gas/Wasser-Zählerständen, Verbrauchsberechnung. | Zeitersparnis |
| **Versorgungsunternehmen-Anbindung** | Abruf von Zählerständen per API bei Strom-/Gas-/Wasser-Lieferanten. | Langfristige Automatisierung |
| **Wohnungsinserate (ImmobilienScout24, eBay Kleinanzeigen)** | Automatisches Erstellen und Verwalten von Inseraten bei Leerstand. | Vermarktung aus einer Hand |

#### E. Integrationen, API & Ökosystem

| Thema | Beschreibung | Warum wichtig |
|-------|--------------|---------------|
| **Öffentliche API-Dokumentation** | Dokumentierte REST-API für Business-Kunden, OpenAPI/Swagger. | In Business geplant, aber Dokumentation fehlt |
| **API-Rate-Limiting für bezahlte API-Zugänge** | Unterschiedliche Limits je Plan, Billing-Tracking. | Business-Tier notwendig |
| **Webhooks für Kunden** | Ereignis-basierte Benachrichtigungen an externe Systeme (z. B. Slack, CRM). | Integration in Ökosysteme |
| **White-Label / Embedding** | Business-Kunden können eigene Domain/Branding nutzen. | Im Abo-Modell erwähnt, aber konkrete Architektur fehlt |
| **Affiliate / Partner-Programm** | Partner-Links, Provisionen, Tracking für Empfehlungen. | Wachstumskanal |
| **Datenmigration / Onboarding-Import** | Import aus anderen Tools (Excel, CSV, ImmoTool, WISO, etc.) | Reduziert Wechsel-Friction |
| **Automatisierter Datenimport** | PDF-Mietvertrag, Belege, alte Abrechnungen automatisch parsen. | Starkes KI-Feature |
| **CRM / Buchhaltungs-Integrationen** | Zapier, Make, DATEV, Lexoffice, sevDesk. | Professionelle Workflows |

#### F. Sicherheit, Infrastruktur & Betrieb

| Thema | Beschreibung | Warum wichtig |
|-------|--------------|---------------|
| **Disaster Recovery & Backup-Plan** | Automatische Backups (DB, Files), Recovery-Time-Objective (RTO), Recovery-Point-Objective (RPO), Offsite-Backup. | Geschäftskritisch |
| **SSL-Zertifikat-Management** | Automatische Erneuerung (Let’s Encrypt), Monitoring, Multi-Domain für White-Label. | Betriebssicherheit |
| **Multi-Factor-Authentication für Admin-Accounts** | Zusätzliche Sicherheitsebene für interne Admins. | Sicherheit |
| **Audit-Trail für alle Finanz-Transaktionen** | Nachvollziehbarkeit jeder Zahlung, Mahnung, Abrechnung. | GoBD + Vertrauen |
| **Penetration-Testing & Security-Audit** | Regelmäßige externe Sicherheitsprüfung vor Go-Live. | Compliance + Vertrauen |
| **SIEM / zentrales Logging** | Zentrale Sammlung und Alarmierung bei Sicherheitsvorfällen. | Skalierung |
| **DDoS- & Abuse-Monitoring** | Überwachung von Angriffen, Bot-Netzen, Missbrauch der öffentlichen APIs. | Betrieb |

#### G. Multi-Language & Lokalisierung

| Thema | Beschreibung | Warum wichtig |
|-------|--------------|---------------|
| **Sprachvarianten DE/AT/CH** | Nicht nur Übersetzung, sondern lokale Begriffe (z. B. „Nebenkostenabrechnung“ vs. „Nebenkostenabrechnung“, aber CH: „NK-Abrechnung“), Währungen (€ / CHF), Datumsformate. | DACH-Authentizität |
| **Lokale Rechtstexte** | AGB, Datenschutz, Mietvertragsvorlagen je Land. | Rechtssicherheit |
| **Währungs- & Steuer-Unterstützung** | CHF für Schweiz, ggf. Mehrwertsteuer-Szenarien. | Markttauglichkeit |

#### H. Berichte, Reporting & Business Intelligence

| Thema | Beschreibung | Warum wichtig |
|-------|--------------|---------------|
| **Jahresbericht / Steuer-Report automatisch** | Zusammenfassung aller Einnahmen, Ausgaben, Abschreibungen, Zinsen. | Steuererklärung aus einer Hand |
| **Portfolio-Vergleich** | Renditevergleich zwischen Objekten, Benchmarks. | Business-Tier |
| **Custom Reports (KI-generiert)** | Quartalsberichte für Hausverwaltungen. | Business-Tier Upsell |
| **Cashflow-Prognose** | Prognose der kommenden Monate basierend auf Mietzahlungen, Kosten, Leerständen. | Planungshilfe |

#### I. Handwerker- & Dienstleister-Ökosystem

| Thema | Beschreibung | Warum wichtig |
|-------|--------------|---------------|
| **Handwerker-Portal** | Eigene Logins für Handwerker, Auftragsverwaltung, Dokumenten-Freigabe. | Professioneller Workflow |
| **Auftrags-Management** | Angebote, Belege, Abnahme, Rechnungskontrolle für Reparaturen. | Kostentransparenz |
| **Dienstleister-Verzeichnis** | Empfohlene Handwerker pro Region (optional monetarisierbar). | Zusatzgeschäftsmodell |

---

### 11.3 Priorisierung: MVP / Go-Live / Scale / Nice-to-Have

| Thema | Priorität | Begründung |
|-------|-----------|------------|
| **CSV-/Excel-Import für Migration** | **MVP** | Ohne Datenmigration bleibt Wechsel-Friction zu hoch. |
| **Bank-Transaktion-Import (CSV/CAMT/MT940)** | **MVP / Go-Live** | Kern-Feature für Cashflow-Verwaltung; manueller Import reicht für MVP. |
| **GoBD-Konforme Aufbewahrung** | **Go-Live** | Steuerrechtlich erforderlich, sobald echte Umsatzdaten fließen. |
| **DATEV-Export** | **Go-Live / Scale** | Professionelle Vermieter/Hausverwaltungen erwarten es. |
| **Anlage V Export** | **Go-Live** | Starkes Verkaufsargument für Kleinvermieter. |
| **Steuerberater-Zugang** | **Go-Live** | Besonders für Basis/Pro-Kunden attraktiv. |
| **Automatisches Zahlungs-Matching** | **Go-Live** | Erst mit Bank-Import sinnvoll. |
| **Mieter-App / PWA mit Push** | **Go-Live** | Bindung und Aktivierungsrate steigen deutlich. |
| **Schufa-Anbindung** | **Scale** | Rechtlich aufwändig, nur mit Premium-Einwilligungs-Flow. |
| **Mieter-Score (nur Anzeige)** | **Scale** | Nützlich, aber nicht MVP-relevant. |
| **Digitaler Mietvertrag mit eSignatur** | **Scale** | Rechtssicher, aber komplex (eIDAS). |
| **Video-Übergabeprotokoll** | **Scale / Nice-to-Have** | Gut für Pro/Business, aber nicht kritisch. |
| **Energieausweis-Management** | **Go-Live** | Wird gesetzlich immer wichtiger (GEG). |
| **Versicherungs-Checks** | **Go-Live** | Einfach umsetzbar, hoher Praxisnutzen. |
| **Leerstands-Analyse** | **Scale** | Datengetriebenes Upsell-Feature. |
| **KI-Mietpreis-Analyse / Mietspiegel** | **Go-Live** | Sehr starkes Marketing- & KI-Feature. |
| **Automatische NK-Abrechnung mit Zählerständen** | **Scale** | Hoher Automatisierungsgrad, aber komplex. |
| **Versorgungsunternehmen-Anbindung** | **Nice-to-Have** | Langfristige Vision, aktuell wenig APIs verfügbar. |
| **Wohnungsinserate (IS24, Kleinanzeigen)** | **Scale** | Gutes Marketing-Feature, aber externe APIs instabil. |
| **Öffentliche API-Dokumentation** | **Scale** | Nur für Business-Tier relevant. |
| **Webhooks für Kunden** | **Scale** | Wichtig für Integrations-Ökosystem. |
| **White-Label / Embedding** | **Scale** | Business-Tier Upsell. |
| **Affiliate / Partner-Programm** | **Nice-to-Have** | Wachstumskanal, aber erst ab Produkt-Market-Fit. |
| **WEG-Verwaltung** | **Scale** | Neues großes Segment, aber eigene Rechtsdomäne. |
| **Gewerbliche Vermietung** | **Scale** | Spezialisierung, separater Vertrags-Typ. |
| **Gästeverwaltung (AirBnB/FeWo)** | **Nice-to-Have** | Anderes Geschäftsmodell, ggf. separates Produkt. |
| **Disaster Recovery & Backup-Plan** | **MVP** (Konzept) / **Go-Live** (vollständig) | Datenverlust wäre existenzbedrohend. |
| **SSL-Zertifikat-Management** | **Go-Live** | Let's Encrypt-Automation ist Standard. |
| **Admin-MFA** | **Go-Live** | Interne Sicherheit. |
| **Audit-Trail für Finanztransaktionen** | **Go-Live** | GoBD + Vertrauen. |
| **Penetration-Testing** | **Go-Live** | Vor öffentlichem Launch zwingend. |
| **AT/CH-Rechtsanpassungen** | **Go-Live** | Sonst keine echte DACH-Lösung. |
| **Lokalisierung (CHF, Datumsformate)** | **Go-Live** | Schweizer Markt braucht CHF. |
| **Jahresbericht / Steuer-Report** | **Go-Live** | Starkes Verkaufsargument für Kleinvermieter. |
| **Custom Reports (KI)** | **Scale** | Business-Tier. |
| **Handwerker-Portal** | **Scale** | Professioneller Workflow für größere Portfolios. |
| **Dienstleister-Verzeichnis** | **Nice-to-Have** | Monetarisierbar, aber später. |

---

### 11.4 Was könnten Konkurrenten haben, das wir noch nicht bedacht haben?

Basierend auf der bisherigen Recherche (`competitor-deep-dive-2026.md`, `rea-konkurrenten-websites-analyse.md`, `heise-konkurrenten-analyse.md`) und allgemeinem Marktwissen:

| Konkurrenz-Feature | Risiko für uns | Gegenmaßnahme |
|--------------------|----------------|---------------|
| **Fertige Mietvertrags-Vorlagen mit lokalem Recht** | Vertrauensvorteil | AGB-konforme Vorlagen für DE/AT/CH bauen |
| **Integrierte Schufa-/Bonitätsprüfung** | Bessere Mieterauswahl | Schufa-Integration mit Einwilligungs-Flow |
| **Bank-Import direkt aus 1.000+ Banken** | Weniger manuelle Arbeit | FinTS/HBCI + PSD2 + CSV-Fallback |
| **DATEV-konformer Export aus der Box** | Steuerberater-Präferenz | DATEV-CSV/JSON-Format implementieren |
| **Mobile-first App mit Push** | Bessere Mieter-Bindung | PWA zuerst, native App später |
| **WEG-/Eigentumswohnungs-Verwaltung** | Größeres Segment | Phase-2-Erweiterung planen |
| **Eingebaute Makler-/Inserate-Schnittstellen** | Schnellere Vermietung | IS24/eBay Kleinanzeigen-API |
| **Energieausweis-Ablauf-Tracking** | Compliance-Vorteil | Fristen-Modul erweitern |
| **Versicherungsvergleich im Produkt** | Zusatznutzen | Partner-Integration oder Verzeichnis |
| **KI-gestützter Mietspiegel-Check** | Mieterhöhungs-Feature | Lokale Mietspiegel-Daten einbinden |
| ** automatische Zählerstands-Abfrage** | Weniger NK-Arbeit | Versorger-APIs evaluieren |
| **Steuerberater-Dashboard** | B2B-Argument | Read-only Rolle + DATEV-Export |
| **White-Label für Hausverwaltungen** | Enterprise-Upsell | Business-Tier Architektur vorbereiten |
| **Offline-Modus / PWA** | Mobiler Einsatz | PWA mit Service Worker |
| **Community / Vermieter-Forum** | Netzwerkeffekt | Knowledge-Base + Community später |
| **Notfall-Support / Telefon-Support** | Business-Kunden | Priority-Support im Business-Plan |

**Wichtigste Konkurrenz-Lücken, die wir schnell schließen sollten:**

1. **Bank-Import + automatisches Zahlungs-Matching** — größter Zeitersparnis-Faktor.
2. **DATEV/Anlage V / Steuerberater-Zugang** — professionelle Akzeptanz.
3. **Mobile PWA mit Push** — Aktivierung und Bindung.
4. **KI-Mietspiegel-Check** — starkes Marketing-Feature.
5. **AT/CH-Lokalisierung** — echte DACH-Tauglichkeit.

---

### 11.5 Empfohlene Roadmap-Ergänzung

Auf Basis der Analyse empfehlen wir folgende Ergänzungen zur Roadmap:

**Sofort (MVP / bis Closed Beta):**
- Disaster-Recovery-Konzept finalisieren (Backups, RTO/RPO).
- CSV/Excel-Import für Objekte, Mieter, Mietverträge.
- Bank-Transaktion-Import (CSV) mit manuellem Matching.
- GoBD-konforme Dokumenten-Aufbewahrung (10 Jahre, versioniert).

**Vor Go-Live:**
- AT/CH-Rechtsanpassungen und Lokalisierung (CHF).
- DATEV-Export und Anlage V.
- Steuerberater-Zugang.
- Mieter-PWA mit Push-Benachrichtigungen.
- Energieausweis- und Versicherungs-Management.
- KI-Mietspiegel-Check.
- Penetration-Test und Security-Audit.

**Scale (nach Go-Live):**
- Schufa-Anbindung, Mieter-Score.
- Digitaler Mietvertrag mit eSignatur.
- Handwerker-Portal.
- WEG-Verwaltung.
- Öffentliche API + Webhooks.
- White-Label / Affiliate-Programm.

**Nice-to-Have / Vision:**
- Versorgungsunternehmen-Anbindung.
- Gästeverwaltung / AirBnB-Funktionen.
- Dienstleister-Verzeichnis.
- Native Mobile Apps.

---

### 11.6 Zusammenfassung

Das MietVerwaltung-Konzept deckt die **wichtigsten MVP-Elemente** (Datenmodell, Auth, Objekt-/Mieter-Verwaltung, Tickets, Kosten, Abrechnung, KI-Basis, Subscription, Website, Lead-Gen, API-Sicherheit) bereits gut ab. Für eine **perfekte, marktführende SaaS-Lösung** fehlen vor allem:

- **Rechtliche DACH-Tiefe** (AT/CH, GoBD, DATEV, Anlage V, eIDAS).
- **Finanz-Integrationen** (Bank-Import, automatisches Matching, Steuerberater-Zugang).
- **Mobile Experience** (PWA mit Push).
- **KI-gestützte Markt-Features** (Mietspiegel-Check, Leerstands-Analyse).
- **Professionelle Workflows** (Handwerker-Portal, WEG, White-Label).
- **Infrastruktur-Reife** (Disaster Recovery, Monitoring, Pen-Testing).

Die empfohlene Strategie: **MVP mit starkem Kern + schnelle Go-Live-Erweiterungen in Legal/Finanzen/Mobile**, dann **Scale-Features für Business-Kunden und Wettbewerbsdifferenzierung**.
