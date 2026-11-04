# MietVerwaltung — DB-Schema v3: Beziehungen & Verknüpfungen

> Ergänzung zum DB-Schema v3 (30 Tabellen)
> **Fokus:** Foreign Keys, Kardinalitäten, Lösch-Kaskaden, Business-Logik-Verknüpfungen

---

## ER-Übersicht (alle Beziehungen)

### Users (Vermieter) — Zentrum

```
users (1)
├──< user_sessions (n)        — ein User hat viele Sessions (Geräte)
├──< einwilligungen (n)        — ein User hat viele Einwilligungen (versioniert)
├──< audit_logs (n)            — ein User hat viele Audit-Einträge
├──< onboarding_progress (n)   — ein User hat eine Checkliste (6 Schritte)
├──< referrals (n)             — ein User lädt andere ein (als referrer)
├──< objekte (n)               — ein Vermieter hat viele Immobilien
├──< kostenkategorien (n)      — ein Vermieter hat eigene Kategorien
├──< tickets (n)               — ein Vermieter hat viele Tickets (als vermieter_id)
├──< tickets (n)               — ein Vermieter hat Tickets zugewiesen (als assigned_to)
├──< ticket_sla (n)            — ein Vermieter hat SLA-Konfigurationen
├──< ticket_trigger (n)         — ein Vermieter hat Trigger-Regeln
├──< ai_stored_results (n)      — ein Vermieter hat KI-Cache-Einträge
├──< handwerker (n)             — ein Vermieter hat Handwerker-Stammdaten
├──< dokumente (n)              — ein Vermieter hat Dokumente
├──< kosten (n)                — ein Vermieter hat Kosten
├──< mietzahlungen (n)         — ein Vermieter hat Mietzahlungen
├──< abrechnungen (n)           — ein Vermieter hat Abrechnungen
├──< fristen (n)                — ein Vermieter hat Fristen
└──< ticket_kommentare (n)      — ein User schreibt Kommentare (als author_id)
```

### Objekt → Einheit → Mieter → Vertrag (Kette)

```
objekte (1)
├──< einheiten (n)              — ein Objekt hat viele Wohnungen
│   ├──< einheit_ausstattung (n) — eine Einheit hat viele Ausstattungsmerkmale
│   ├──< mieter_historie (n)      — eine Einheit hat vergangene Mieter
│   ├──< bewerbungen (n)         — eine Einheit hat Bewerbungen
│   ├──< mietvertraege (n)        — eine Einheit hat Verträge (über Zeit)
│   ├──< tickets (n)               — eine Einheit hat Tickets
│   └──< dokumente (n)              — eine Einheit hat Dokumente
│
├──< kosten (n)                — ein Objekt hat Kosten (Hausversicherung etc.)
├──< abrechnungen (n)           — ein Objekt hat NK-Abrechnungen
├──< dokumente (n)              — ein Objekt hat Dokumente
└──< fristen (n)                — ein Objekt hat Fristen

mieter (1)
├──< mietvertraege (n)          — ein Mieter hat Verträge (aktuell + historisch)
├──< mietzahlungen (n)         — ein Mieter hat Zahlungen
├──< tickets (n)               — ein Mieter hat Tickets
└──< dokumente (n)              — ein Mieter hat Dokumente

mietvertraege (1)
├──< mietvertrag_aenderungen (n) — ein Vertrag hat Änderungs-Historie
└──< mietzahlungen (n)         — ein Vertrag hat Zahlungen
```

### Kosten → Abrechnung (Finanzen)

```
kostenkategorien (1)
└──< kosten (n)                — eine Kategorie hat viele Kosten-Einträge

kosten (1)
└──< abrechnung_positionen (n)  — eine Kostenposition erscheint in einer Abrechnung

abrechnungen (1)
├──< abrechnung_positionen (n)   — eine Abrechnung hat viele Positionen
└──< kosten (n)                — eine Abrechnung hat zugeordnete Kosten
```

### Tickets (Kommunikation)

```
tickets (1)
├──< ticket_kommentare (n)      — ein Ticket hat viele Kommentare (Verlauf)
├── ticket_sla (1)             — ein Ticket hat eine SLA (n:1)
└── handwerker (1)              — ein Ticket kann einen Handwerker haben (n:1)

ticket_sla (1)
└──< tickets (n)               — eine SLA-Konfig gilt für viele Tickets

ticket_trigger (1)
└── (virtuell)                — Trigger referenziert Tickets über JSONB condition

users (1)
├──< ticket_kommentare (n)      — ein User schreibt Kommentare
└──< tickets (n)               — ein User ist assigned_to
```

### Dokumente (DMS)

```
dokumente (1)
├──< dokument_freigaben (n)      — ein Dokument hat Freigaben für Rollen
├── objekte (1)                 — ein Dokument gehört zu einem Objekt (n:1)
├── einheiten (1)               — ein Dokument gehört zu einer Einheit (n:1)
└── mieter (1)                   — ein Dokument gehört zu einem Mieter (n:1)
```

### Events → Notifications (Automatisierung)

```
events (1)
└──< notifications (n)         — ein Event erzeugt Notifications

users (1)
└──< notifications (n)         — ein User empfängt Notifications
```

### Bewerbungen → Mieter (Onboarding-Flow)

```
bewerbungen (1)
├── einheiten (1)               — eine Bewerbung ist für eine Einheit (n:1)
└── mieter (0..1)               — bei Ananahme: Bewerbung → Mieter + Mietvertrag (Business-Logik)

einheiten (1)
├── mieter (0..1)             — eine Einheit hat aktuellen Mieter (1:1, tenant_id)
├──< bewerbungen (n)          — eine Einheit hat viele Bewerbungen
└──< mieter_historie (n)        — eine Einheit hat vergangene Mieter
```

---

## Kardinalitäten (Zusammenfassung)

| Von | Nach | Beziehung | Kardinalität | Lösch-Kaskade |
|-----|------|-----------|---------------|----------------|
| users | user_sessions | hat | 1:n | CASCADE |
| users | einwilligungen | hat | 1:n | CASCADE |
| users | audit_logs | hat | 1:n | SET NULL |
| users | onboarding_progress | hat | 1:n | CASCADE |
| users | referrals | lädt ein | 1:n | CASCADE |
| users | objekte | besitzt | 1:n | CASCADE |
| users | kostenkategorien | hat | 1:n | CASCADE |
| users | handwerker | hat | 1:n | CASCADE |
| users | tickets | erstellt | 1:n | CASCADE |
| users | tickets | assigned_to | 1:n | SET NULL |
| users | ticket_sla | hat | 1:n | CASCADE |
| users | ticket_trigger | hat | 1:n | CASCADE |
| users | ai_stored_results | hat | 1:n | CASCADE |
| users | dokumente | hochgeladen | 1:n | CASCADE |
| users | kosten | erfasst | 1:n | CASCADE |
| users | mietzahlungen | erfasst | 1:n | CASCADE |
| users | abrechnungen | erstellt | 1:n | CASCADE |
| users | fristen | hat | 1:n | CASCADE |
| users | ticket_kommentare | schreibt | 1:n | SET NULL |
| users | notifications | empfängt | 1:n | CASCADE |
| objekte | einheiten | hat | 1:n | CASCADE |
| objekte | kosten | hat | 1:n | CASCADE |
| objekte | abrechnungen | hat | 1:n | CASCADE |
| objekte | dokumente | hat | 1:n | CASCADE |
| objekte | fristen | hat | 1:n | CASCADE |
| einheiten | mieter | aktueller | 1:1 | SET NULL (Mieter weg = frei) |
| einheiten | einheit_ausstattung | hat | 1:n | CASCADE |
| einheiten | mieter_historie | hat | 1:n | CASCADE |
| einheiten | bewerbungen | hat | 1:n | CASCADE |
| einheiten | mietvertraege | hat | 1:n | CASCADE |
| einheiten | tickets | hat | 1:n | SET NULL |
| einheiten | dokumente | hat | 1:n | SET NULL |
| mieter | mietvertraege | hat | 1:n | CASCADE |
| mieter | mietzahlungen | hat | 1:n | CASCADE |
| mieter | tickets | erstellt | 1:n | CASCADE |
| mieter | dokumente | hat | 1:n | CASCADE |
| mietvertraege | mietvertrag_aenderungen | hat | 1:n | CASCADE |
| mietvertraege | mietzahlungen | hat | 1:n | CASCADE |
| kostenkategorien | kosten | hat | 1:n | CASCADE |
| kosten | abrechnung_positionen | erscheint in | 1:n | CASCADE |
| abrechnungen | abrechnung_positionen | hat | 1:n | CASCADE |
| abrechnungen | kosten | hat | 1:n | SET NULL |
| tickets | ticket_kommentare | hat | 1:n | CASCADE |
| tickets | ticket_sla | hat | n:1 | SET NULL |
| tickets | handwerker | hat | n:1 | SET NULL |
| ticket_sla | tickets | gilt für | 1:n | CASCADE |
| dokumente | dokument_freigaben | hat | 1:n | CASCADE |
| events | notifications | erzeugt | 1:n | CASCADE |
| bewerbungen | einheiten | für | n:1 | CASCADE |
| bewerbungen | mieter | wird zu | 0..1 | SET NULL |
| handwerker | tickets | bearbeitet | 1:n | CASCADE |

---

## Business-Logik-Verknüpfungen (nicht in SQL, sondern in Code)

| Trigger | Was passiert | Implementiert in |
|----------|-------------|----------------|
| Bewerbung angenommen | `bewerbung.status='angenommen'` → Erstelle `mieter` + `mietvertraege` → Update `einheiten.tenant_id` → Bewerbung → `mieter_historie` | Phase 2 |
| Mieter ausgezogen | `mietvertraege.status='beendet'` → Kopiere zu `mieter_historie` → Set `einheiten.tenant_id=NULL` → `mieter.status='ehemalig'` | Phase 2 |
| Miete fällig | `events(event_type='miete_faellig')` → Erstelle `notifications` → Sende E-Mail → Wenn unbezahlt nach 3 Tagen: `mahnstufe=1` | Phase 8 |
| Mahnung Stufe 3 | `mietzahlungen.mahnstufe=3` → `events(event_type='mahnung_stufe3')` → KI generiert Mahnungstext → PDF → Sende | Phase 7+8 |
| NK-Abrechnung erstellt | `abrechnungen.status='entwurf'` → KI sortiert `kosten` → Erstelle `abrechnung_positionen` → KI generiert Erklärungstext → PDF → Sende an Mieter | Phase 5+7 |
| Ticket neu | `tickets.status='offen'` → `ticket_trigger(condition='ticket_neu')` → KI kategorisiert → `notifications` an Vermieter | Phase 4+7 |
| Ticket Antwort-Entwurf | User klickt 'Antwort vorschlagen' → `ai_stored_results` check → Ollama generiert → `ticket_kommentare(ist_ki_entwurf=True)` → User editiert → Senden | Phase 7 |
| Beleg-Scan | Foto upload → Presidio anonymisiert → OCR + GLM → `kosten(ki_kategorisiert=True)` → `ai_stored_results` → User bestätigt | Phase 7 |
| Frist abgelaufen | `fristen.warn_level='red'` → `events(event_type='frist_faellig')` → `notifications` an Vermieter → E-Mail | Phase 8 |
| Onboarding Schritt | `onboarding_progress.is_done=True` → Update Progress % → Wenn 100%: Verstecke Checkliste | Phase 1 |
| Upgrade | `users.plan` ändern → Prüfe `einheiten.count <= plan_limit` → Wenn drüber: Blockieren + Upgrade-Modal | Phase 2 |
| Referral registriert | `referrals.status='registered'` → Gewähre `reward_amount` (1 Monat Pro) → `referrals.status='rewarded'` | Phase 8 |
| DATEV-Export | Sammle `kosten` + `abrechnung_positionen` für Jahr → Generiere CSV mit `datev_konto` + `datev_buchungstext` → Download | Phase 10 |

---

## Fehlende Verknüpfungen (die ich ergänzt habe)

| Was fehlte in v2 | Was ich in v3 ergänzt habe |
|------------------|------------------------|
| **mietvertraege.einheit_id** | War nicht explizit als FK definiert — jetzt `REFERENCES einheiten(id)` |
| **tickets.handwerker_id** | Fehlte komplett — jetzt `REFERENCES handwerker(id)` |
| **tickets.sla_id** | Fehlte komplett — jetzt `REFERENCES ticket_sla(id)` |
| **objekte.foto_url + foto_data** | Fehlte — jetzt Foto-Upload möglich |
| **einheiten.floor, energy_class, last_renovation, available_from** | Fehlten — jetzt komplett |
| **kosten.datev_konto, datev_buchungstext** | Fehlten — DATEV-Export möglich |
| **abrechnung_positionen.datev_betrag** | Fehlte — DATEV-Export pro Position |
| **mieter_historie** | Komplett neue Tabelle |
| **einheit_ausstattung** | Komplett neue Tabelle |
| **bewerbungen** | Komplett neue Tabelle |
| **ticket_sla** | Komplett neue Tabelle |
| **ticket_trigger** | Komplett neue Tabelle |
| **onboarding_progress** | Komplett neue Tabelle |
| **ai_stored_results** | Komplett neue Tabelle |
| **referrals** | Komplett neue Tabelle |
| **handwerker** | Komplett neue Tabelle (Roadmap) |

---

**Erstellt:** 28. Oktober 2026
**Status:** Alle 30 Tabellen mit kompletten Beziehungen, Kardinalitäten und Lösch-Kaskaden