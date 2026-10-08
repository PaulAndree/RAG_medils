FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

COPY api.py metrics.py ./
COPY ingestion/ ./ingestion/
COPY representations/ ./representations/
COPY stores/ ./stores/
COPY retrieval/ ./retrieval/
COPY routing/ ./routing/
COPY generation/ ./generation/
COPY evaluation/ ./evaluation/
COPY workflows/ ./workflows/

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
