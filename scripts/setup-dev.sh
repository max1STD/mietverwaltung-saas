#!/bin/bash
# setup-dev.sh — Einmalige Native-Dev-Einrichtung für MietVerwaltung SaaS
# Kein Docker. Läuft direkt auf Proxmox-LXC.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "╔══════════════════════════════════════════════╗"
echo "║  MietVerwaltung SaaS — Native Dev Setup      ║"
echo "╚══════════════════════════════════════════════╝"

# ── 1. Python Venv ──
echo "▸ Python Venv einrichten..."
if [ ! -d "backend/.venv" ]; then
  python3 -m venv backend/.venv
fi
source backend/.venv/bin/activate
pip install --upgrade pip wheel setuptools -q
pip install -r backend/requirements.txt -q
pip install -r backend/requirements-dev.txt -q
echo "  ✓ Python deps installiert"

# ── 2. Frontend ──
echo "▸ Frontend deps installieren..."
cd frontend
if command -v fnm &>/dev/null; then
  eval "$(fnm env)"
fi
pnpm install --frozen-lockfile 2>/dev/null || pnpm install
echo "  ✓ Frontend deps installiert"
cd "$PROJECT_ROOT"

# ── 3. Redis ──
echo "▸ Redis prüfen..."
if ! redis-cli ping &>/dev/null; then
  echo "  ⚠ Redis nicht erreichbar — installiere..."
  apt-get update -qq && apt-get install -y -qq redis-server
  systemctl enable redis-server
  systemctl start redis-server
fi
echo "  ✓ Redis: $(redis-cli ping)"

# ── 4. PostgreSQL ──
echo "▸ PostgreSQL prüfen..."
if ! pg_isready &>/dev/null; then
  echo "  ⚠ PostgreSQL nicht erreichbar — starte..."
  systemctl start postgresql
fi
# DB + User anlegen falls nicht vorhanden
su - postgres -c "psql -tc \"SELECT 1 FROM pg_user WHERE usename='mv'\" | grep -q 1 || psql -c \"CREATE USER mv WITH PASSWORD 'mietverwaltung_dev_2026' CREATEDB;\"" 2>/dev/null || true
su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname='mietverwaltung'\" | grep -q 1 || createdb -O mv mietverwaltung" 2>/dev/null || true
su - postgres -c "psql -d mietverwaltung -c 'CREATE EXTENSION IF NOT EXISTS pgcrypto;'" 2>/dev/null || true
echo "  ✓ PostgreSQL: DB 'mietverwaltung' bereit"

# ── 5. Alembic Migration ──
echo "▸ Alembic Migration ausführen..."
cd backend
source .venv/bin/activate
alembic upgrade head 2>&1 || echo "  ⚠ Migration fehlgeschlagen — ggf. 'make migrate-create' ausführen"
cd "$PROJECT_ROOT"

# ── 6. .env prüfen ──
if [ ! -f ".env" ]; then
  echo "  ⚠ .env fehlt — kopiere .env.example"
  cp .env.example .env
fi

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  ✓ Setup abgeschlossen!                     ║"
echo "║  Starte mit:  make dev                       ║"
echo "║  Health:      make health                    ║"
echo "║  Docs:        http://localhost:8000/docs     ║"
echo "║  Frontend:    http://localhost:5173          ║"
echo "╚══════════════════════════════════════════════╝"
