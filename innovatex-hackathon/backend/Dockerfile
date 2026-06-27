FROM python:3.12-slim

# Pin UV version for reproducible builds
COPY --from=ghcr.io/astral-sh/uv:0.5.29 /uv /usr/local/bin/uv

RUN useradd --create-home appuser

WORKDIR /app

# ── Dependencies layer (cached unless pyproject/uv.lock change) ──────
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# ── App code ─────────────────────────────────────────────────────────
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY entrypoint.sh ./

RUN chmod +x entrypoint.sh
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
