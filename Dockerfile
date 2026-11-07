FROM python:3.12-slim AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev git && rm -rf /var/lib/apt/lists/*
ARG CONTRACTS_GIT_URL=https://github.com/TGuapyassu/oficina-contracts.git@v0.1.0
RUN pip install --no-cache-dir "oficina-contracts @ git+${CONTRACTS_GIT_URL}"
COPY pyproject.toml requirements.txt ./
COPY app ./app
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir --prefix=/install -e .

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/install/bin:$PATH" \
    PYTHONPATH="/install/lib/python3.12/site-packages" RUN_MIGRATIONS=false
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 appuser && useradd --uid 1000 --gid appuser --create-home --shell /usr/sbin/nologin appuser
WORKDIR /app
COPY --from=builder /install /install
COPY alembic.ini alembic ./
COPY app ./app
COPY scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
