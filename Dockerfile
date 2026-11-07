FROM python:3.12-slim AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
COPY oficina-contracts ./oficina-contracts
COPY pyproject.toml requirements.txt ./
COPY app ./app
RUN pip install --no-cache-dir -U pip setuptools wheel \
    && pip install --no-cache-dir --prefix=/install ./oficina-contracts \
    && pip install --no-cache-dir --prefix=/install .

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/install/bin:$PATH" \
    PYTHONPATH="/install/lib/python3.12/site-packages" RUN_MIGRATIONS=false
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 appuser && useradd --uid 1000 --gid appuser --create-home --shell /usr/sbin/nologin appuser
WORKDIR /app
COPY --from=builder /install /install
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app
COPY scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
COPY scripts/seed_admin.py /app/scripts/seed_admin.py
RUN chmod +x /usr/local/bin/docker-entrypoint.sh && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
