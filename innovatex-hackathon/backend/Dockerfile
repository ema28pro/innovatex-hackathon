FROM python:3.12-slim

# Pin UV version for reproducible builds
COPY --from=ghcr.io/astral-sh/uv:0.5.29 /uv /usr/local/bin/uv

RUN useradd --create-home appuser

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY app/ ./app/
COPY alembic/ ./alembic/

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
