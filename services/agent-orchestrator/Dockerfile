FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy workspace files
COPY pyproject.toml /workspace/
COPY packages/shared /workspace/packages/shared

# Copy service files
COPY services/agent-orchestrator /app

# Install dependencies
RUN uv sync --no-dev

EXPOSE 8006

CMD ["uv", "run", "python", "-m", "src.main"]
