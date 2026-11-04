# Konzept: Automatische Adress-Autovervollständigung

**Projekt:** MietVerwaltung SaaS für private Kleinvermieter in DACH  
**Ziel:** Adressen in allen relevanten Formularen schnell, fehlerfrei und DSGVO-konform erfassen.  
**MVP-Ziele:** 0 € Kosten, EU-Hosting, Abdeckung DE/AT/CH, Offline-fähig.  
**Dokument-Status:** Konzept (Vor-Build-Phase) — zur Abstimmung mit dem Product Owner.

---

## 1. Zusammenfassung & Empfehlung

### Gewählte MVP-Lösung: **Eigene lokale PostgreSQL-Adressdatenbank**

Wir hosten die offiziellen/adressähnlichen Straßen- und PLZ-Daten für DACH in einer eigenen PostgreSQL-Datenbank (im gleichen Stack wie die App). Der Grund:

| Kriterium | Bewertung |
|---|---|
| **DSGVO** | ✅ Keine Adressdaten verlassen die EU. Kein US-Anbieter. |
| **Kosten** | ✅ 0 € im MVP (offene Daten + eigene Postgres). |
| **DACH-Abdeckung** | ✅ DE + AT + CH (Liechtenstein optional) abgedeckt. |
| **Performance** | ✅ Sub-50 ms für PLZ→Ort, Sub-100 ms für Straßenvorschläge. |
| **Offline-Fähigkeit** | ✅ Funktioniert ohne Internet-API (Proxmox-LXC). |
| **Wartung** | ⚠️ Monatliches/wochiges Daten-Update nötig (automatisiert per Script). |
| **Genauigkeit** | ⚠️ Hausnummern nicht immer lückenlos vorhanden (daher manuelle HNr). |

### Alternative für Go-Live / Scale: **OpenCage oder HERE**

- **OpenCage** (Berlin, Hetzner, DSGVO-konform): 2.500 Req/Tag kostenlos zum Testen, ab ~45 €/Monat für 10.000/Tag. Vorteil: keine eigene Datenpflege, weltweite Abdeckung.
- **HERE Geocoding & Search** (Niederlande, EU-Residency möglich): Freemium bis 250.000 Transaktionen/Monat (Stand 2026 lt. Dokumentation), dann Pay-as-you-grow. Gute Hausnummernabdeckung.

### Was wir absichtlich NICHT im MVP nutzen

- **Google Places / Mapbox**: US-Anbieter, DSGVO-Risiko, Kostenpflichtig.
- **Nominatim öffentlich**: 1 req/sec, keine Produktivnutzung für Typeahead.
- **Overpass öffentlich**: komplex, überlastet, nicht für Formular-Autocomplete geeignet.

---

## 2. Anwendungsfälle im Produkt

| Use Case | Adresse wird benötigt für | Bemerkung |
|---|---|---|
| **Objekt anlegen** | Vermieter-Adresse / Objekt-Adresse | Pflichtfeld, Basis für Dashboard/Karten |
| **Mieter anlegen** | Korrespondenz-/Meldeadresse | Optional, falls nicht identisch mit Wohnung |
| **Bewerbung** | Aktueller Wohnsitz des Bewerbers | Für Schufa/Wohnungsgeberbestätigung |
| **Handwerker** | Firmenadresse / Rechnungsadresse | Roadmap-Feature |
| **Vermieter-Profil** | Briefkopf-Adresse für PDF-Exports | Bereits in `vermieter_profile` vorhanden |

**Mockup-Änderung:** Die aktuelle Zeile *„Adresse (Straße, PLZ, Ort)“* wird durch vier Felder ersetzt: **PLZ → Ort (automatisch) → Straße (Typeahead) → Hausnummer (manuell)**.

---

## 3. Datenquellen-Vergleich

### 3.1 Übersichtsmatrix

| # | Quelle | Kosten | DSGVO | DACH | Perf. | Wartung | Offline | MVP-tauglich |
|---|---|---|---|---|---|---|---|---|
| 1 | OpenStreetMap / Nominatim (public) | 0 € | Neutral | ✅ | ❌ 1 req/s | Gering | Nein | **Nein** |
| 2 | Overpass API (public) | 0 € | Neutral | ✅ | ❌ Überlastet | Gering | Nein | **Nein** |
| 3 | OpenPLZ API / offene PLZ-Datenbank | 0 € | ✅ EU | ✅ | ✅ Schnell | Mittel | Ja (self-host) | **Ja** |
| 4 | Strassenverzeichnis DE (OSM/BKG) | 0 € | ✅ EU | Nur DE | ✅ | Hoch | Ja | Teilweise |
| 5 | Google Places Autocomplete | Kostenpflichtig | ❌ US | ✅ | Sehr gut | Gering | Nein | **Nein** |
| 6 | HERE Geocoding API | Freemium | ✅ EU-Hosting | ✅ | Sehr gut | Gering | Nein | Go-Live |
| 7 | Mapbox Geocoding | Freemium | ❌ US | ✅ | Sehr gut | Gering | Nein | **Nein** |
| 8 | d-s-europa / Dataprep | Kostenpflichtig | ✅ EU | ✅ | Gut | Niedrig | Optional | Enterprise |
| 9 | BKG Open-Data-Dienste | 0 € | ✅ EU | Nur DE | Mittel | Hoch | Ja | Teilweise |
| 10 | **Eigene lokale PostgreSQL-DB** | **0 €** | **✅** | **✅** | **✅** | **Mittel** | **Ja** | **✅ Empfohlen** |

### 3.2 Detaillierte Bewertung

#### 1) OpenStreetMap / Nominatim API
- **Daten:** Weltweit, community-gepflegt.
- **Nutzen im MVP:** Für Adress-Autocomplete **nicht geeignet**. Usage Policy erlaubt maximal **1 Request/Sekunde** und verbietet ausdrücklich Typeahead/Autocomplete (siehe `operations.osmfoundation.org/policies/nominatim/`).
- **DSGVO:** Kein US-Anbieter, aber öffentlicher Dienst ohne AVV.
- **Fazit:** Nur für einzelne, benutzergetriggerte Geocoding-Aufrufe (z. B. Kartenanzeige) später geeignet. **Nicht für Formular-Autocomplete.**

#### 2) Overpass API
- **Daten:** Roh-OSM-Daten, extrem flexibel.
- **Nutzen im MVP:** Zu komplex für einfache PLZ→Ort/Straßen-Abfragen. Öffentliche Instanzen sind überlastet, Rate-Limits strikt (10.000 Queries/Tag, 1 GB/Tag).
- **DSGVO:** Neutral, aber öffentlich und unzuverlässig.
- **Fazit:** Für Adress-Autocomplete overkill. **Nicht im MVP nutzen.**

#### 3) OpenPLZ API / offene PLZ-Datenbank
- **Daten:** Strukturierte Straßen-, PLZ-, Orts- und Verwaltungsdaten für **DE, AT, CH, LI**.
- **Quellen:** OSM (DE), Statistik Austria (AT), swisstopo / Bundesamt für Statistik (CH).
- **Kosten:** 0 € (Open Data).
- **DSGVO:** Self-hosted = volle Kontrolle; öffentliche API = EU-Dienst.
- **Fazit:** **Ideale Datenbasis für die eigene lokale DB.** Wir nutzen die öffentlichen CSV/JSON-Daten oder die offiziellen Quellen direkt, nicht den fremden API-Endpunkt.

#### 4) Strassenverzeichnis DE (OSM / kommerziell / Statistikamt)
- **Daten:** Es gibt kein zentrales kostenloses deutsches Straßenverzeichnis. OpenPLZ API baut auf OSM + GV-ISys.
- **Fazit:** Teil der OpenPLZ-Pipeline; nicht separat zu pflegen.

#### 5) Google Places Autocomplete
- **Daten:** Beste Vorschläge weltweit, Hausnummern-Autocomplete.
- **DSGVO:** US-Anbieter, Datenweitergabe an Google, SCC/AVV nötig, rechtlich problematisch.
- **Kosten:** Kostenpflichtig ab geringem Volumen.
- **Fazit:** **Nicht für DACH-MVP** geeignet.

#### 6) HERE Geocoding API
- **Daten:** Eigenes Kartenmaterial, sehr gute Abdeckung, echtes Autocomplete.
- **DSGVO:** HERE ist niederländisch, EU-Residency verfügbar, AVV machbar.
- **Kosten:** Freemium bis 250.000 Transaktionen/Monat laut Dokumentation; danach Pay-as-you-grow.
- **Fazit:** **Beste Go-Live-Alternative**, wenn eigene Datenpflege zu aufwändig wird oder Koordinaten/Karten kommen.

#### 7) Mapbox Geocoding
- **Daten:** Sehr gut, aber US-Anbieter.
- **DSGVO:** US-Hosting, Datenweitergabe problematisch.
- **Fazit:** **Ausschließen** für DACH-DSGVO-Produkt.

#### 8) d-s-europa / Dataprep
- **Daten:** Kommerzielle Adressdaten, validiert, inkl. Hausnummern.
- **Kosten:** Lizenzgebühren.
- **Fazit:** Für Enterprise-Kunden später interessant, nicht für 0 € MVP.

#### 9) BKG (Bundesamt für Kartographie und Geodäsie)
- **Daten:** Open-Data-Geodaten für DE, eher topographisch/kartographisch.
- **Fazit:** Nicht das richtige Werkzeug für PLZ→Straßen-Autocomplete. Nicht im MVP.

#### 10) Eigene lokale PostgreSQL-DB
Siehe Kapitel 5 und 9. Dies ist unsere **MVP-Empfehlung**.

---

## 4. Architektur

```
┌─────────────────────────────────────────────────────────────────┐
│  Frontend (Vue.js 3 + TypeScript)                                │
│  • AddressAutocomplete-Komponente                               │
│  • PLZ-Feld mit onBlur → Ort auto-füllen                        │
│  • Straßen-Typeahead mit Debounce (150 ms)                      │
│  • Hausnummer manuell                                           │
└──────────────────────┬──────────────────────────────────────────┘
                       │ GET /api/addresses/plz/{plz}
                       │ GET /api/addresses/streets?plz=...&q=...
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  Backend (FastAPI + Python)                                      │
│  • Authentifizierung & Tenant-Isolation prüfen                  │
│  • Redis-Cache (PLZ→Ort, Straßen-Präfix)                        │
│  • Falls Cache-Miss: PostgreSQL-Lookup                          │
│  • Keine Weitergabe an externe APIs im MVP                        │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  PostgreSQL 17 (selbe Instanz wie App-DB)                        │
│  Schema: plz_orte, strassen, strassen_plz (n:m)                 │
│  GIN-Index für schnelle Typeahead-Suche                           │
└─────────────────────────────────────────────────────────────────┘
```

### Grundsätze

1. **Kein Adress-Datensatz verlässt die Server.** Keine US-APIs.
2. **Alle Lookups laufen über unser Backend**, nie direkt aus dem Browser an externe APIs.
3. **Tenant-Isolation bleibt erhalten** — Adressdaten sind öffentliche Referenzdaten, aber das Backend prüft trotzdem den eingeloggten User.
4. **Offline-fähig:** Solange Postgres läuft, funktioniert Autocomplete auch ohne Internet.

---

## 5. Datenquelle im Detail

### 5.1 Was wir speichern

| Entität | Felder | Quelle |
|---|---|---|
| `plz_orte` | `country`, `plz`, `ort`, `gemeinde`, `bezirk`, `bundesland/kanton` | OpenPLZ API / offizielle Verzeichnisse |
| `strassen` | `country`, `strasse`, `strassen_key` (optional) | OpenPLZ API / Statistik Austria / swisstopo |
| `strassen_plz` | n:m Verknüpfung Straße ↔ PLZ/Ort | OpenPLZ API |
| `adressen_cache` (optional) | Häufige Benutzeradressen anonymisiert | Intern (DSGVO-konform) |

### 5.2 Datenbezug & Aktualisierung

**Variante A (empfohlen für MVP):** Monatlicher Import aus dem OpenPLZ-Data-Repository.

```bash
# Beispiel: Download der CSV-Dumps (DE, AT, CH) aus openpotato/openplzapi.data
# oder direkt von statistik.at / swisstopo / OSM-Extrakten
python scripts/import_openplz_data.py \
  --de-url https://github.com/openpotato/openplzapi.data/raw/main/de/streets.csv \
  --at-url https://www.statistik.at/verzeichnis/strassenliste/gemplzstr_1.csv \
  --ch-url https://data.geo.admin.ch/ch.swisstopo.amtliches-strassenverzeichnis/...
```

**Variante B (später):** Nightly-Job, der offizielle Quellen prüft und bei Änderung neu importiert.

**Aktualität:**
- Deutschland: ca. wöchentlich (OSM-Planet + GV-ISys).
- Österreich: wöchentlich (Statistik Austria).
- Schweiz: täglich (swisstopo).

**Schätzung Datenbankgröße:**
- ~1,2 Mio Straßen (DE) + ~150.000 (AT) + ~120.000 (CH) = ~1,5 Mio Datensätze.
- Mit GIN-Index und Verknüpfungstabelle: **~500 MB – 1,5 GB** im Postgres — für MVP absolut tragbar.

### 5.3 Lizenz / Impressum

- OpenPLZ-Daten: Open Data (CC-BY / Datenlizenz Deutschland).
- Im Impressum / Datenschutzerklärung Quellen nennen: „Straßen- und Postleitzahldaten basieren auf OpenStreetMap-Daten sowie amtlichen Verzeichnissen von Statistik Austria und swisstopo.“

---

## 6. Backend API (FastAPI)

### 6.1 Endpunkte

| Methode | URL | Zweck | Antwort |
|---|---|---|---|
| `GET` | `/api/addresses/plz/{plz}` | PLZ → Ort(e) | `[{"plz":"21635","ort":"Jork","bundesland":"Niedersachsen"}]` |
| `GET` | `/api/addresses/streets` | Straßen-Typeahead | `[{"strasse":"Kurze Straße","plz":"21635","ort":"Jork"}]` |
| `GET` | `/api/addresses/resolve` | Vollständige Adresse normalisieren | `{plz,ort,strasse,hausnummer,land}` |

### 6.2 Python-Code (FastAPI)

```python
# backend/app/api/addresses.py
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from app.db import get_db
from app.auth import get_current_user
from app.cache import redis_cache
import asyncpg
import json

router = APIRouter(prefix="/api/addresses", tags=["Adressen"])

class OrtDto(BaseModel):
    plz: str
    ort: str
    land: str
    bundesland: Optional[str] = None
    kanton: Optional[str] = None

class StrasseDto(BaseModel):
    strasse: str
    plz: str
    ort: str
    land: str

@router.get("/plz/{plz}", response_model=List[OrtDto])
async def ort_zu_plz(
    plz: str,
    db: asyncpg.Pool = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    PLZ eingeben → Ort(e) zurückliefern.
    Mehrere Orte möglich, wenn eine PLZ mehrere Orte abdeckt.
    """
    cache_key = f"plz:{plz}"
    cached = await redis_cache.get(cache_key)
    if cached:
        return json.loads(cached)

    rows = await db.fetch(
        """
        SELECT DISTINCT plz, ort, land_code AS land, region
        FROM refdata.plz_orte
        WHERE plz = $1
        ORDER BY ort
        """,
        plz,
    )
    result = [dict(r) for r in rows]
    await redis_cache.set(cache_key, json.dumps(result), ttl=86400)
    return result

@router.get("/streets", response_model=List[StrasseDto])
async def strassen_typeahead(
    q: str = Query(..., min_length=2, description="Straßen-Präfix, z. B. 'Kurze'"),
    plz: Optional[str] = Query(None, description="Optional PLZ zur Eingrenzung"),
    ort: Optional[str] = Query(None, description="Optional Ort"),
    limit: int = Query(10, ge=1, le=50),
    db: asyncpg.Pool = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Straßenvorschläge für Typeahead.
    Werden PLZ/Ort mitgegeben, wird die Suche eingegrenzt.
    """
    cache_key = f"streets:{plz}:{ort}:{q}:{limit}"
    cached = await redis_cache.get(cache_key)
    if cached:
        return json.loads(cached)

    # Suche mit case-insensitive Prefix-Match + GIN-Index-Fallback
    params = [f"{q}%"]
    where = ["s.strasse ILIKE $1"]
    if plz:
        params.append(plz)
        where.append(f"sp.plz = ${len(params)}")
    if ort:
        params.append(ort)
        where.append(f"sp.ort ILIKE ${len(params)}")

    query = f"""
        SELECT DISTINCT s.strasse, sp.plz, sp.ort, s.land_code AS land
        FROM refdata.strassen s
        JOIN refdata.strassen_plz sp ON s.id = sp.strassen_id
        WHERE {" AND ".join(where)}
        ORDER BY s.strasse
        LIMIT ${len(params) + 1}
    """
    params.append(limit)

    rows = await db.fetch(query, *params)
    result = [dict(r) for r in rows]
    await redis_cache.set(cache_key, json.dumps(result), ttl=3600)
    return result

@router.get("/resolve")
async def resolve_address(
    plz: str,
    ort: str,
    strasse: str,
    hausnummer: Optional[str] = None,
    db: asyncpg.Pool = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Normalisiert eine vollständige Adresse und prüft, ob Straße+PLZ existieren.
    Hausnummer bleibt manuell und wird nur formal validiert.
    """
    row = await db.fetchrow(
        """
        SELECT s.land_code AS land
        FROM refdata.strassen s
        JOIN refdata.strassen_plz sp ON s.id = sp.strassen_id
        WHERE s.strasse = $1 AND sp.plz = $2 AND sp.ort ILIKE $3
        LIMIT 1
        """,
        strasse, plz, ort,
    )
    if not row:
        raise HTTPException(404, "Adresse nicht in Referenzdaten gefunden")
    return {
        "plz": plz,
        "ort": ort,
        "strasse": strasse,
        "hausnummer": hausnummer,
        "land": row["land"],
        "formatiert": f"{strasse} {hausnummer or ''}, {plz} {ort}".strip(),
    }
```

### 6.3 Sicherheit

- **Auth:** Jeder Endpunkt erfordert `get_current_user`.
- **Rate-Limiting:** 30 Requests/Minute pro User für `/streets` (Typeahead).
- **Input-Validierung:** PLZ auf 4–10 Ziffern, Straße mindestens 2 Zeichen.
- **Kein Logging sensibler Adressdaten:** Adressen sind zwar Stammdaten, aber wir loggen nur Hash/ID, nie den Klartext in externe Systeme.

---

## 7. Frontend UX (Vue.js 3 + TypeScript)

### 7.1 UX-Flow

```
[ PLZ ]          [ Ort ] (auto-filled)
   │                    ▲
   │  onBlur            │
   └────────────────────┘

[ Straße ] — type —> Dropdown [Kurze Straße, Kurzer Weg, …]
   │
   └─ onSelect —> [ Hausnummer ] (manuell)
```

**Verhalten:**
1. Nutzer tippt PLZ (z. B. `21635`).
2. Beim Verlassen des Feldes (oder nach 3 Ziffern) ruft das Backend `GET /plz/21635` auf.
3. Ort-Feld wird mit `Jork` befüllt (wenn eindeutig) oder ein Dropdown gezeigt (wenn mehrere Orte).
4. Nutzer tippt Straße (z. B. `Kurze`).
5. Nach Debounce von 150 ms ruft das Backend `GET /streets?plz=21635&q=Kurze` auf.
6. Vorschläge erscheinen; bei Auswahl wird Straße gesetzt.
7. Hausnummer wird manuell eingegeben (kein Typeahead, da freie Hausnummern-Daten lückenhaft sind).
8. Vollständige Adresse wird im Store/Parent-Formular gesetzt.

### 7.2 Vue-Komponente

```vue
<!-- frontend/src/components/AddressAutocomplete.vue -->
<template>
  <div class="address-autocomplete">
    <div class="grid-2">
      <div class="form-group">
        <label class="form-label">PLZ</label>
        <input
          v-model="plz"
          type="text"
          maxlength="10"
          class="form-input"
          placeholder="21635"
          @blur="lookupOrt"
        />
      </div>
      <div class="form-group">
        <label class="form-label">Ort</label>
        <input
          v-model="ort"
          type="text"
          class="form-input"
          placeholder="automatisch"
          :readonly="!ortManuell"
        />
      </div>
    </div>

    <div class="form-group">
      <label class="form-label">Straße</label>
      <input
        ref="streetInput"
        v-model="streetQuery"
        type="text"
        class="form-input"
        placeholder="Kurze Straße"
        @input="debouncedSearch"
        @keydown.down="moveDown"
        @keydown.up="moveUp"
        @keydown.enter="selectHighlighted"
      />
      <ul v-if="suggestions.length" class="typeahead-list">
        <li
          v-for="(s, i) in suggestions"
          :key="s.strasse + s.plz"
          :class="{ active: i === highlightedIndex }"
          @click="select(s)"
        >
          {{ s.strasse }} — {{ s.plz }} {{ s.ort }}
        </li>
      </ul>
    </div>

    <div class="form-group">
      <label class="form-label">Hausnummer</label>
      <input
        v-model="hausnummer"
        type="text"
        class="form-input"
        placeholder="12a"
        @blur="emitFull"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineEmits, defineProps } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import { api } from '@/services/api'

interface Adresse {
  plz: string
  ort: string
  strasse: string
  hausnummer: string
  land: string
}

const props = defineProps<{ modelValue?: Partial<Adresse> }>()
const emit = defineEmits<{ (e: 'update:modelValue', v: Adresse): void }>()

const plz = ref(props.modelValue?.plz || '')
const ort = ref(props.modelValue?.ort || '')
const ortManuell = ref(false)
const streetQuery = ref(props.modelValue?.strasse || '')
const strasse = ref(props.modelValue?.strasse || '')
const hausnummer = ref(props.modelValue?.hausnummer || '')
const suggestions = ref<Array<{ strasse: string; plz: string; ort: string }>>([])
const highlightedIndex = ref(-1)

const lookupOrt = async () => {
  if (plz.value.length < 4) return
  const results = await api.get(`/addresses/plz/${plz.value}`)
  if (results.length === 1) {
    ort.value = results[0].ort
    ortManuell.value = false
  } else if (results.length > 1) {
    // Mehrere Orte: Nutzer wählt oder behält manuelle Eingabe
    ortManuell.value = true
  } else {
    // PLZ unbekannt: Ort manuell eingeben lassen
    ortManuell.value = true
  }
  emitFull()
}

const searchStreets = async () => {
  const q = streetQuery.value
  if (q.length < 2) {
    suggestions.value = []
    return
  }
  suggestions.value = await api.get('/addresses/streets', {
    params: { q, plz: plz.value, limit: 10 },
  })
  highlightedIndex.value = -1
}

const debouncedSearch = useDebounceFn(searchStreets, 150)

const select = (s: { strasse: string; plz: string; ort: string }) => {
  strasse.value = s.strasse
  streetQuery.value = s.strasse
  plz.value = s.plz
  ort.value = s.ort
  suggestions.value = []
  emitFull()
}

const moveDown = () => {
  highlightedIndex.value = Math.min(highlightedIndex.value + 1, suggestions.value.length - 1)
}
const moveUp = () => {
  highlightedIndex.value = Math.max(highlightedIndex.value - 1, -1)
}
const selectHighlighted = () => {
  const s = suggestions.value[highlightedIndex.value]
  if (s) select(s)
}

const emitFull = () => {
  emit('update:modelValue', {
    plz: plz.value,
    ort: ort.value,
    strasse: strasse.value,
    hausnummer: hausnummer.value,
    land: 'DE', // später dynamisch aus DB
  })
}

watch(() => props.modelValue, (v) => {
  if (v) {
    plz.value = v.plz || ''
    ort.value = v.ort || ''
    streetQuery.value = v.strasse || ''
    strasse.value = v.strasse || ''
    hausnummer.value = v.hausnummer || ''
  }
}, { deep: true })
</script>

<style scoped>
.typeahead-list {
  list-style: none;
  margin: 4px 0 0;
  padding: 0;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--card);
  box-shadow: var(--shadow);
  max-height: 220px;
  overflow-y: auto;
  position: absolute;
  width: 100%;
  z-index: 50;
}
.typeahead-list li {
  padding: 10px 14px;
  cursor: pointer;
  font-size: 14px;
}
.typeahead-list li.active,
.typeahead-list li:hover {
  background: var(--navy-light);
  color: var(--navy);
}
</style>
```

### 7.3 Verwendung in Formularen

```vue
<!-- Objekt anlegen -->
<AddressAutocomplete v-model="objekt.adresse" />

<!-- Mieter / Bewerber -->
<AddressAutocomplete v-model="bewerber.wohnsitz" label="Aktueller Wohnsitz" />
```

---

## 8. Datenbankschema

Wir erweitern die App-Datenbank um drei Referenztabellen. Sie liegen im gleichen PostgreSQL-Cluster, aber idealerweise in einem eigenen Schema `refdata`, damit sie von den Mieter-/Vermieter-Daten getrennt sind.

```sql
-- Schema für Referenzdaten
CREATE SCHEMA IF NOT EXISTS refdata;

------------------------------------------------------------
-- 1. Länder (statisch, klein)
------------------------------------------------------------
CREATE TABLE refdata.laender (
    code        CHAR(2) PRIMARY KEY,      -- DE, AT, CH, LI
    name_de     VARCHAR(100) NOT NULL,
    name_en     VARCHAR(100) NOT NULL,
    plz_regex   VARCHAR(50),            -- z. B. '^[0-9]{5}$' für DE
    plz_min_len INTEGER NOT NULL DEFAULT 4,
    plz_max_len INTEGER NOT NULL DEFAULT 10
);

INSERT INTO refdata.laender (code, name_de, name_en, plz_regex, plz_min_len, plz_max_len) VALUES
('DE', 'Deutschland', 'Germany', '^[0-9]{5}$', 5, 5),
('AT', 'Österreich', 'Austria', '^[0-9]{4}$', 4, 4),
('CH', 'Schweiz', 'Switzerland', '^[0-9]{4}$', 4, 4),
('LI', 'Liechtenstein', 'Liechtenstein', '^[0-9]{4}$', 4, 4);

------------------------------------------------------------
-- 2. PLZ + Ort(e)
------------------------------------------------------------
CREATE TABLE refdata.plz_orte (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    land_code   CHAR(2) NOT NULL REFERENCES refdata.laender(code),
    plz         VARCHAR(10) NOT NULL,
    ort         VARCHAR(150) NOT NULL,
    ortsteil    VARCHAR(150),            -- Optional: Stadtteil
    region      VARCHAR(150),            -- Bundesland, Kanton, Bezirk
    gemeinde    VARCHAR(150),            -- Gemeinde
    gemeinde_key VARCHAR(20),            -- Amtlicher Gemeindeschlüssel
    lat         NUMERIC(10, 7),          -- Optional: Mittelpunkt
    lon         NUMERIC(10, 7),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (land_code, plz, ort, COALESCE(ortsteil, ''))
);

CREATE INDEX idx_plz_orte_plz ON refdata.plz_orte(plz);
CREATE INDEX idx_plz_orte_ort ON refdata.plz_orte(ort);
CREATE INDEX idx_plz_orte_land ON refdata.plz_orte(land_code);

------------------------------------------------------------
-- 3. Straßen
------------------------------------------------------------
CREATE TABLE refdata.strassen (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    land_code     CHAR(2) NOT NULL REFERENCES refdata.laender(code),
    strasse       VARCHAR(200) NOT NULL,
    strasse_key   VARCHAR(50),           -- Amtlicher Straßenschlüssel falls vorhanden
    lat           NUMERIC(10, 7),
    lon           NUMERIC(10, 7),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (land_code, strasse, strasse_key)
);

CREATE INDEX idx_strassen_name ON refdata.strassen(strasse);
-- GIN-Index für schnelles ILIKE-Prefix-Matching (via pg_trgm)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_strassen_name_trgm ON refdata.strassen USING GIN (strasse gin_trgm_ops);

------------------------------------------------------------
-- 4. Verknüpfung Straße ↔ PLZ/Ort (n:m, da eine Straße
--    mehrere PLZ/Ort-Kombinationen haben kann)
------------------------------------------------------------
CREATE TABLE refdata.strassen_plz (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    strassen_id   UUID NOT NULL REFERENCES refdata.strassen(id) ON DELETE CASCADE,
    plz_ort_id    UUID NOT NULL REFERENCES refdata.plz_orte(id) ON DELETE CASCADE,
    UNIQUE (strassen_id, plz_ort_id)
);

CREATE INDEX idx_strassen_plz_strasse ON refdata.strassen_plz(strassen_id);
CREATE INDEX idx_strassen_plz_plzort  ON refdata.strassen_plz(plz_ort_id);

------------------------------------------------------------
-- 5. Trigger: updated_at automatisch setzen
------------------------------------------------------------
CREATE OR REPLACE FUNCTION refdata.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_plz_orte_updated
    BEFORE UPDATE ON refdata.plz_orte
    FOR EACH ROW EXECUTE FUNCTION refdata.set_updated_at();

CREATE TRIGGER trg_strassen_updated
    BEFORE UPDATE ON refdata.strassen
    FOR EACH ROW EXECUTE FUNCTION refdata.set_updated_at();
```

### 8.1 Erweiterung bestehender App-Tabellen

Die bestehenden Adressfelder (`adresse`, `plz`, `ort`) werden ergänzt:

```sql
-- In objekte, vermieter_profile, später mieter/handwerker:
ALTER TABLE objekte ADD COLUMN strasse VARCHAR(200);
ALTER TABLE objekte ADD COLUMN hausnummer VARCHAR(20);
ALTER TABLE objekte ADD COLUMN land_code CHAR(2) DEFAULT 'DE' REFERENCES refdata.laender(code);
-- adresse bleibt als berechnetes/formatiertes Feld oder wird entfernt
```

**Empfehlung:** `adresse` wird zu einem `GENERATED`-Spalte:

```sql
ALTER TABLE objekte DROP COLUMN adresse;
ALTER TABLE objekte ADD COLUMN adresse VARCHAR(220) GENERATED ALWAYS AS (
    TRIM(
        COALESCE(NULLIF(TRIM(COALESCE(strasse, '') || ' ' || COALESCE(hausnummer, '')), ''), '') || ', ', ''
    )
    || COALESCE(plz, '') || ' ' || COALESCE(ort, '')
) STORED;
```

---

## 9. Caching mit Redis

### 9.1 Cache-Strategie

| Cache-Key | TTL | Inhalt |
|---|---|---|
| `plz:{plz}` | 24 h | Liste der Orte zur PLZ |
| `streets:{plz}:{ort}:{q}:{limit}` | 1 h | Straßenvorschläge |
| `addr:resolve:{hash}` | 7 Tage | Normalisierte Adresse (nur Meta, nie Personenbezug) |

### 9.2 Redis-Implementierung (Python)

```python
# backend/app/cache.py
import redis.asyncio as redis
import json

redis_pool = redis.Redis.from_url(
    "redis://redis:6379/1",
    decode_responses=True,
)

class RedisCache:
    async def get(self, key: str):
        val = await redis_pool.get(key)
        return json.loads(val) if val else None

    async def set(self, key: str, value, ttl: int = 3600):
        await redis_pool.setex(key, ttl, json.dumps(value))

redis_cache = RedisCache()
```

**Warum 1 h für Straßen?** Adressreferenzdaten ändern sich selten; bei monatlichem Import reicht 1 h, um Typeahead-Last drastisch zu reduzieren.

---

## 10. Fallback: Wenn keine Daten gefunden werden

| Szenario | Verhalten |
|---|---|
| PLZ unbekannt | Ort-Feld bleibt editierbar; Nutzer kann manuell eingeben. Hinweis: „PLZ nicht gefunden – Ort manuell prüfen.“ |
| Straße unbekannt | Nutzer kann Straße frei eingeben; keine Validierung. |
| PLZ hat mehrere Orte | Dropdown zur Auswahl des richtigen Orts; Fallback manuell. |
| Kein Internet (nur bei SaaS-Hosting relevant) | Da Daten lokal in Postgres liegen: Autocomplete funktioniert weiter. |
| Land außerhalb DACH | Nur manuelle Eingabe (MVP fokussiert auf DACH). |

**Backend-Regel:** Ein 404 bei `/resolve` führt im Frontend **nicht** zur Blockierung. Die Adresse wird mit Warnhinweis gespeichert.

---

## 11. Mockup-Integration

### 11.1 Aktueller Zustand

In `mockup/index.html` (ca. Zeile 902) gibt es heute:

```html
<div class="form-group">
  <label class="form-label">Adresse</label>
  <input type="text" class="form-input" placeholder="Straße, PLZ, Ort"/>
</div>
```

### 11.2 Gewünschter Zustand

Das Adressfeld wird durch die `AddressAutocomplete`-Komponente ersetzt. Für das statische Mockup (kein echtes Backend) implementieren wir eine **Demo-Datenquelle** mit ca. 20 hartcodierten PLZ/Ort/Straße-Kombinationen.

```html
<!-- Im property-create View ersetzen -->
<div class="form-group"><label class="form-label">Objektbezeichnung</label><input type="text" class="form-input" placeholder="Mehrfamilienhaus Berlin"/></div>

<!-- NEU: AddressAutocomplete-Demo -->
<div class="address-autocomplete">
  <div class="grid-2">
    <div class="form-group">
      <label class="form-label">PLZ</label>
      <input type="text" id="prop-plz" class="form-input" placeholder="21635" maxlength="5" onblur="app.fillOrt()"/>
    </div>
    <div class="form-group">
      <label class="form-label">Ort</label>
      <input type="text" id="prop-ort" class="form-input" placeholder="automatisch" readonly/>
    </div>
  </div>
  <div class="form-group" style="position:relative;">
    <label class="form-label">Straße</label>
    <input type="text" id="prop-strasse" class="form-input" placeholder="Kurze Straße" oninput="app.suggestStreets()"/>
    <ul id="street-suggestions" class="typeahead-list hidden"></ul>
  </div>
  <div class="form-group">
    <label class="form-label">Hausnummer</label>
    <input type="text" id="prop-hnr" class="form-input" placeholder="12a"/>
  </div>
</div>
```

### 11.3 Demo-Daten im Mockup

```javascript
// In den app.data-Block einfügen
addressData: [
  { plz: '21635', ort: 'Jork', strassen: ['Kurze Straße', 'Lange Straße', 'Elbchaussee', 'Bahnhofstraße'] },
  { plz: '10115', ort: 'Berlin', strassen: ['Berliner Straße', 'Alexanderplatz', 'Friedrichstraße'] },
  { plz: '80331', ort: 'München', strassen: ['Hauptplatz', 'Marienplatz', 'Sendlinger Straße'] },
  { plz: '40210', ort: 'Düsseldorf', strassen: ['Düsseldorfer Allee', 'Königsallee', 'Heinrich-Heine-Allee'] },
  { plz: '4020',  ort: 'Linz', strassen: ['Schachermayerstraße', 'Hauptplatz', 'Landstraße'] },
  { plz: '3084',  ort: 'Wabern', strassen: ['Seftigenstrasse', 'Könizstrasse'] }
]
```

### 11.4 Demo-Handler

```javascript
// In den app-Objekt-Block einfügen
fillOrt: function(){
  const plz = $('#prop-plz').value.trim();
  const hit = app.data.addressData.find(a => a.plz === plz);
  $('#prop-ort').value = hit ? hit.ort : '';
},
suggestStreets: function(){
  const plz = $('#prop-plz').value.trim();
  const q = $('#prop-strasse').value.trim().toLowerCase();
  const list = $('#street-suggestions');
  const hit = app.data.addressData.find(a => a.plz === plz);
  if (!hit || q.length < 2) { list.classList.add('hidden'); return; }
  const matches = hit.strassen.filter(s => s.toLowerCase().includes(q));
  list.innerHTML = matches.map(s => `<li onclick="app.pickStreet('${s}')">${s}</li>`).join('');
  list.classList.toggle('hidden', matches.length === 0);
},
pickStreet: function(s){
  $('#prop-strasse').value = s;
  $('#street-suggestions').classList.add('hidden');
}
```

### 11.5 CSS für Typeahead im Mockup

```css
.typeahead-list {
  list-style: none;
  margin: 4px 0 0;
  padding: 0;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--card);
  box-shadow: var(--shadow);
  max-height: 220px;
  overflow-y: auto;
  position: absolute;
  width: 100%;
  z-index: 50;
}
.typeahead-list li { padding: 10px 14px; cursor: pointer; font-size: 14px; }
.typeahead-list li:hover { background: var(--navy-light); color: var(--navy); }
```

---

## 12. Kosten

### 12.1 MVP (0 €)

| Posten | Kosten | Bemerkung |
|---|---|---|
| Datenlizenz | 0 € | Open Data |
| PostgreSQL-Storage | 0 € | Nutzt vorhandene DB auf Proxmox |
| Redis-Cache | 0 € | Bereits im Stack |
| Import-Script | 0 € | Eigener Python-Code |
| Backend-Entwicklung | Intern | Bestehendes FastAPI-Team |
| **Gesamt MVP** | **0 €** | |

### 12.2 Go-Live / Scale

| Posten | Geschätzte Kosten | Auslöser |
|---|---|---|
| HERE Geocoding (Freemium) | 0 € bis 250k Req/Monat | Erste echte Go-Live-Phase |
| OpenCage X-Small | ~45 €/Monat | Wenn eigene Datenpflege zu aufwändig |
| HERE paid | ab ~1 €/1.000 Requests | Hohes Volumen, Koordinaten/Karten |
| d-s-europa / Dataprep | ab ~200–500 €/Monat | Validierung + Hausnummern-Check |

**Break-Even-Betrachtung:** Bei 100 aktiven Vermietern mit je 5 Adresseingaben/Monat = 500 Lookups. Eigene DB: 0 €. HERE: 0 €. Selbst bei 10.000 Lookups/Monat bleiben wir im Freemium von HERE.

---

## 13. Roadmap

| Phase | Feature | Datenquelle | Kosten |
|---|---|---|---|
| **MVP** | PLZ→Ort, Straßen-Typeahead, HNr manuell | Eigene Postgres (OpenPLZ-Daten) | 0 € |
| **MVP+1** | Land-Auswahl (DE/AT/CH) | Eigene Postgres | 0 € |
| **Phase 2** | Koordinaten (lat/lon) für Objekte | Eigene Postgres + OpenStreetMap-Nominatim (selten, User-getriggert) | 0 € |
| **Phase 3** | Hausnummern-Vorschläge (wo Daten vorhanden) | HERE / OpenCage Fallback | Freemium / gering |
| **Phase 4** | Karten-Integration (Radius, Umkreis) | MapLibre/Leaflet + eigene Koordinaten | 0 € (Open-Source-Tiles) |
| **Phase 5** | Adressvalidierung für Briefkopf/Postversand | HERE / d-s-europa | Kostenpflichtig |
| **Phase 6** | Mieter-Check: Adresse vs. Schufa/Wohnungsgeberbestätigung | Intern + ggf. externe Validierung | Projektbezogen |

---

## 14. Offene Punkte zur Abstimmung

1. **Adressfeld-Normalisierung in DB:** Sollen `adresse`, `plz`, `ort` in `objekte`/`vermieter_profile` durch `strasse`, `hausnummer`, `plz`, `ort`, `land_code` ersetzt werden? (Empfohlen: Ja, siehe Kapitel 8.1)
2. **Land-Vorauswahl:** Soll das Land immer „Deutschland“ vorausgewählt sein, oder dropdown-basiert? (Empfohlen: DE default, Dropdown für AT/CH sichtbar.)
3. **Hausnummern-Autocomplete:** Im MVP manuell belassen, bis Datenquelle (HERE/d-s-europa) verfügbar?
4. **Daten-Update-Prozess:** Soll der monatliche Import ein separates Docker-Container-Cronjob sein oder Teil des Backend-Startups?
5. **Mockup:** Soll die AddressAutocomplete-Komponente zusätzlich im Mieter-anlegen/Bewerber-Dialog eingebaut werden?

---

## 15. Fazit

Für das **MVP** empfehlen wir eine **eigene PostgreSQL-basierte Adressdatenbank** mit den offenen DACH-Referenzdaten (OpenPLZ-Daten, Statistik Austria, swisstopo). Das erfüllt alle MVP-Anforderungen:

- **0 € Kosten**
- **DSGVO-konform** (EU-Hosting, keine US-Anbieter)
- **DACH-Abdeckung**
- **schnell und offline-fähig**
- **zukunftssicher** (einfacher Wechsel zu HERE/OpenCage bei Scale)

Die technische Umsetzung ist mit dem bestehenden Stack (FastAPI + Vue.js + PostgreSQL + Redis) kompatibel und erfordert keine neuen Lizenzen oder externe Abhängigkeiten.
