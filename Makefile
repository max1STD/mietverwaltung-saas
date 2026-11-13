# ──────────────────────────────────────────────
# MietVerwaltung SaaS — Native Dev Makefile
# Kein Docker. Läuft direkt auf dem Proxmox-LXC.
# ──────────────────────────────────────────────

.PHONY: setup dev dev-backend dev-frontend test test-backend test-frontend lint lint-backend lint-frontend migrate migrate-create migrate-down health clean help

# ── Setup ──
setup:          ## Einmalige Native-Dev-Einrichtung
	./scripts/setup-dev.sh

# ── Development ──
dev:            ## Backend + Frontend parallel starten
	@echo "Starting backend (port 8000) and frontend (port 5173)..."
	@make dev-backend & make dev-frontend
	@wait

dev-backend:    ## Uvicorn mit Hot-Reload (port 8000)
	cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:   ## Vite Dev-Server (port 5173)
	cd frontend && pnpm dev --host 0.0.0.0 --port 5173

# ── Testing ──
test:           ## Run all tests (Backend + Frontend)
	$(MAKE) test-backend
	$(MAKE) test-frontend

test-backend:   ## Run backend tests (pytest)
	cd backend && source .venv/bin/activate && pytest -v --cov=app --cov-report=term-missing

test-frontend:  ## Run frontend tests (vitest)
	cd frontend && pnpm vitest run

# ── Linting ──
lint:           ## Run all linters
	$(MAKE) lint-backend
	$(MAKE) lint-frontend

lint-backend:   ## Lint backend (ruff + mypy + bandit)
	cd backend && source .venv/bin/activate && ruff check app/
	cd backend && source .venv/bin/activate && mypy app/
	cd backend && source .venv/bin/activate && bandit -r app/ -ll

lint-frontend:  ## Lint frontend (eslint)
	cd frontend && pnpm eslint src/

# ── Database ──
migrate:        ## Run pending migrations
	cd backend && source .venv/bin/activate && alembic upgrade head

migrate-create: ## Create new migration: make migrate-create m="description"
	cd backend && source .venv/bin/activate && alembic revision --autogenerate -m "$(m)"

migrate-down:   ## Roll back one migration
	cd backend && source .venv/bin/activate && alembic downgrade -1

# ── Health ──
health:         ## Health-Check
	curl -s http://localhost:8000/health | python3 -m json.tool

# ── Deploy (via GitHub Actions, not local) ──
deploy-beta:    ## Deploy to Proxmox (beta) — triggered via GitHub Actions tag v0.x-beta.y
	@echo "Deploy to Proxmox — use: git tag v0.x-beta.y && git push --tags"

deploy-prod:    ## Deploy to Hetzner (production) — triggered via GitHub Actions tag v1.x.y
	@echo "Deploy to Hetzner — use: git tag v1.x.y && git push --tags"

# ── Cleanup ──
clean:          ## Remove build artifacts
	cd backend && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	cd frontend && rm -rf dist node_modules/.cache

# ── Help ──
help:           ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
