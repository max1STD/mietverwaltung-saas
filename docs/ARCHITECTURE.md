# System-Architektur — MietVerwaltung SaaS

## Übersicht

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Frontend   │────▶│    Backend    │────▶│   PostgreSQL 17  │
│  Vue.js 3    │     │  FastAPI      │     │   (RLS, AES-256) │
│  PWA, Tailwind│    │  Python 3.12  │     └─────────────────┘
└─────────────┘     └──────┬───────┘
                           │
                    ┌──────┴──────┐
                    │   Redis     │  Cache, Rate-Limit
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────┴────┐ ┌────┴────┐ ┌────┴─────┐
        │ Tesseract │ │ WeasyPrt│ │ Ollama   │
        │ OCR (lokal)│ │ PDF    │ │ Cloud KI │
        └───────────┘ └────────┘ └──────────┘
```

## Schichten

### Frontend (Vue.js 3 + Tailwind CSS)
- SPA mit Vue Router, Pinia State Management
- PWA-fähig (installierbar, responsive)
- Apple-Style Design, Navy #0D3B70
- Dark-Mode via prefers-color-scheme
- TypeScript-Typen aus OpenAPI generiert (shared/types/api.d.ts)

### Backend (Python + FastAPI)
- Async (asyncpg + SQLAlchemy 2.0 async)
- Pydantic v2 Schemas als Single Source of Truth
- Argon2id Passwort-Hashing, JWT 15min + Refresh 7d
- 2FA: TOTP oder E-Mail-Code-Fallback
- Row-Level Security (PostgreSQL RLS) für Datenisolation
- Feld-Verschlüsselung (AES-256-GCM): IBAN, Steuernr, Geburtsdatum
- Structured JSON Logging (structlog), PII-Filter Middleware

### KI (3-Schicht-Modell)
1. **Lokal (0€):** Tesseract OCR, PyMuPDF, Presidio Anonymisierung, Keyword-Classifier, Berechnungs-Engine, Redis Cache
2. **Ollama Cloud:** GLM 5.2 (80%) + Kimi K.6 (20%) — nur anonymisierte Daten
3. **Lokal:** Platzhalter auflösen, PDF bauen (WeasyPrint), E-Mail senden, DB speichern

### Datenbank (PostgreSQL 17)
- 33 Tabellen (Schema v4)
- 34 RLS-Policies
- 92 Indizes
- GENERATED ALWAYS AS IDENTITY (nicht SERIAL)
- Soft-Delete (deleted_at) für DSGVO Art. 17
- Alembic Migrationen mit Auto-Rollback

## Hosting

| Phase | Setup | Kosten |
|-------|-------|--------|
| MVP (Closed Beta) | Proxmox LXC + Cloudflared Tunnel | 0€ |
| Go-Live | Hetzner CX22 (Frontend) + CX32 (Backend) | ~25€/Mo |
| Scale | Hetzner Managed PostgreSQL + CDN | variabel |

## Deploy

- GitHub = Single Source of Truth
- GitHub Actions SSH't auf Server (git pull + docker build + alembic upgrade + health-check)
- Deploy nur über Tags: `v0.x-beta.y` → Proxmox, `v1.x.y` → Hetzner
- Production braucht GitHub Environment Approval
- Branch-Protection auf main, kein direkter Push

## Siehe auch

- [Konzept-Dokumente](concept/) — 56 Dokumente
- [Build-Plan v2](architecture/2026-10-28_build-plan-v2.md)
- [DB-Schema v4](architecture/2026-11-02_db-schema-v4.md)
- [Server-Konzept v2](concept/Server-Konzept-v2.md)
- [KI-Konzept](concept/KI-Konzept.md)
