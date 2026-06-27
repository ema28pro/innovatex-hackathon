#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Entrypoint for diagnostico-backend container.
# 1. Applies pending Alembic migrations (idempotent — safe to run on every start).
# 2. Seeds reference data (blocks, questions) if tables are empty.
# 3. Starts uvicorn.
#
# Designed for Supabase managed PostgreSQL (Path B).
# Uses DATABASE_URL (direct connection) for steps 1-2 to avoid PgBouncer issues.
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

echo "==> Applying database migrations..."
.venv/bin/alembic upgrade head

echo "==> Seeding reference data..."
.venv/bin/python -m app.seeds.runner

echo "==> Starting FastAPI server..."
exec .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
