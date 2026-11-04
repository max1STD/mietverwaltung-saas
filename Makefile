# ──────────────────────────────────────────────
# MietVerwaltung SaaS — Makefile
# ──────────────────────────────────────────────

.PHONY: dev dev-up dev-down test test-backend test-frontend lint lint-backend lint-frontend migrate migrate-create build deploy-beta deploy-prod clean

# ── Development ──
dev:           ## Start dev environment (docker-compose + hot-reload)
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

dev-up:        ## Start dev environment detached
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

dev-down:      ## Stop dev environment
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down

# ── Testing ──
test:          ## Run all tests
	$(MAKE) test-backend
	$(MAKE) test-frontend

test-backend:  ## Run backend tests (pytest)
	docker compose exec backend pytest --cov=app --cov-report=term-missing

test-frontend: ## Run frontend tests (vitest)
	docker compose exec frontend pnpm vitest run

# ── Linting ──
lint:          ## Run all linters
	$(MAKE) lint-backend
	$(MAKE) lint-frontend

lint-backend:  ## Lint backend (ruff + mypy + bandit)
	docker compose exec backend ruff check app/
	docker compose exec backend mypy app/
	docker compose exec backend bandit -r app/ -ll

lint-frontend: ## Lint frontend (eslint)
	docker compose exec frontend pnpm eslint src/

# ── Database ──
migrate:       ## Run pending migrations
	docker compose exec backend alembic upgrade head

migrate-create: ## Create new migration: make migrate-create m="description"
	docker compose exec backend alembic revision --autogenerate -m "$(m)"

# ── Build ──
build:         ## Build production images
	docker compose build

# ── Deploy ──
deploy-beta:   ## Deploy to Proxmox (beta)
	@echo "Deploy to Proxmox — triggered via GitHub Actions (tag: v0.x-beta.y)"

deploy-prod:   ## Deploy to Hetzner (production)
	@echo "Deploy to Hetzner — triggered via GitHub Actions (tag: v1.x.y)"

# ── Cleanup ──
clean:         ## Remove containers, volumes, and build cache
	docker compose down -v
	docker system prune -f --filter "label=com.docker.compose.project=mietverwaltung-saas"

# ── Help ──
help:          ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
