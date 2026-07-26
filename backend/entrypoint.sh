#!/bin/sh
set -eu

alembic upgrade head

if [ "${SEED_DEMO_DATA:-true}" = "true" ]; then
  python -m app.seed
fi

log_level="$(printf '%s' "${LOG_LEVEL:-info}" | tr '[:upper:]' '[:lower:]')"
case "$log_level" in
  critical|error|warning|info|debug|trace) ;;
  *)
    printf 'Invalid LOG_LEVEL: %s\n' "${LOG_LEVEL:-}" >&2
    exit 64
    ;;
esac

exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --proxy-headers \
  --forwarded-allow-ips="${FORWARDED_ALLOW_IPS:-*}" \
  --log-level="$log_level"
