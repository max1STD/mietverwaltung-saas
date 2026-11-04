# MietVerwaltung SaaS

> KI-gestützte Mietverwaltung für private Kleinvermieter in DACH

Die erste KI-gestützte Mietverwaltung, die 80% der Vermieter-Arbeit automatisch erledigt — Dokumente scannen, Abrechnungen erstellen, Tickets kategorisieren, Mahnungen schreiben, Fristen überwachen. Der Vermieter entscheidet, die KI macht den Rest.

## Tech-Stack

| Komponente | Technologie |
|------------|------------|
| Backend | Python + FastAPI |
| Datenbank | PostgreSQL 17 (Row-Level Security) |
| Frontend | Vue.js 3 + Tailwind CSS (Apple-Style, PWA) |
| KI | Ollama Cloud (GLM 5.2 + Kimi K2.6) |
| OCR | Tesseract + PyMuPDF (lokal) |
| PDF | WeasyPrint + Jinja2 |
| Cache | Redis |
| Hosting (MVP) | Proxmox LXC + Cloudflared Tunnel |
| Hosting (Prod) | Hetzner CX22 + CX32 |

## Projekt-Struktur

```
mietverwaltung-saas/
├── .github/          # CI/CD Workflows, Issue-Templates, Dependabot
├── backend/          # FastAPI (Python) — API, Models, Services, AI
├── frontend/         # Vue.js 3 — SPA, PWA
├── shared/           # OpenAPI spec + generierte TypeScript-Typen
├── docs/             # Konzept-Dokumente, Architektur
├── deploy/           # nginx, Proxmox, Hetzner Deploy-Configs
├── monitoring/       # Health-Checks, Metriken
├── docker-compose.yml
├── Makefile
└── package.json
```

## Entwicklung

```bash
# Dev-Environment starten
make dev

# Tests
make test

# DB-Migration
make migrate

# Linting
make lint
```

## Status

- **Phase:** Konzept abgeschlossen — Pre-Build Architektur-Review steht aus
- **Repo:** Private (Closed Beta)
- **Lizenz:** Proprietär — Max Karthoff GbR

## Links

- [Architektur](docs/architecture/)
- [Konzept-Dokumente](docs/concept/)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
