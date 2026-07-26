FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system --gid 10001 lefodigital \
    && adduser --system --uid 10001 --ingroup lefodigital --no-create-home lefodigital

COPY pyproject.toml ./
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini entrypoint.sh ./

RUN pip install . \
    && chmod +x /app/entrypoint.sh \
    && mkdir -p /app/data/evidence \
    && chown -R lefodigital:lefodigital /app

USER lefodigital

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health/live', timeout=3)"

ENTRYPOINT ["/app/entrypoint.sh"]
