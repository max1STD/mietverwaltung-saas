#!/bin/bash
set -e

echo "[$(date)] Starting MietVerwaltung backend..."

# Run database migrations
if [ "$RUN_MIGRATIONS" != "false" ]; then
    echo "[$(date)] Running Alembic migrations..."
    alembic upgrade head
fi

# Start uvicorn
echo "[$(date)] Starting uvicorn on :8000..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers "${UVICORN_WORKERS:-1}"
