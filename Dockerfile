FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

COPY main.py rag_graph.py metrics.py ./
COPY sql_rag/ ./sql_rag/

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "main.py"]