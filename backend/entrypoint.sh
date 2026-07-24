#!/bin/sh
set -eu

alembic upgrade head

if [ "${SEED_DEMO_DATA:-true}" = "true" ]; then
  python -m app.seed
fi

exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --proxy-headers \
  --forwarded-allow-ips="${FORWARDED_ALLOW_IPS:-*}" \
  --log-level="${LOG_LEVEL:-info}"
