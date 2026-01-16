FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy workspace files
COPY pyproject.toml /workspace/
COPY packages/shared /workspace/packages/shared

# Copy service files
COPY services/rag-service /app

# Install dependencies
RUN uv sync --no-dev

EXPOSE 8004

CMD ["uv", "run", "python", "-m", "src.main"]
