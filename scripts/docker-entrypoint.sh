#!/bin/sh
set -e

if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
  echo "Executando migrations (alembic upgrade head)..."
  alembic upgrade head
fi

if [ "${RUN_SEED_ADMIN:-false}" = "true" ]; then
  echo "Garantindo usuário admin (seed)..."
  python /app/scripts/seed_admin.py || true
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
