.PHONY: help install dev test lint format clean docker-up docker-down

help:
	@echo "Renai - LLM Platform Monorepo"
	@echo ""
	@echo "Available commands:"
	@echo "  make install      - Install all dependencies"
	@echo "  make dev          - Install development dependencies"
	@echo "  make test         - Run all tests"
	@echo "  make lint         - Run linters (ruff, mypy)"
	@echo "  make format       - Format code (black, ruff)"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make docker-up    - Start all infrastructure services"
	@echo "  make docker-down  - Stop all infrastructure services"

install:
	uv sync

dev:
	uv sync --all-extras

test:
	uv run pytest -v

test-cov:
	uv run pytest --cov=services --cov=packages --cov-report=html --cov-report=term

lint:
	uv run ruff check .
	uv run mypy services packages

format:
	uv run black .
	uv run ruff check --fix .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/ .coverage

docker-up:
	cd deploy && docker-compose up -d

docker-down:
	cd deploy && docker-compose down

docker-logs:
	cd deploy && docker-compose logs -f

docker-restart:
	cd deploy && docker-compose restart

# Service-specific commands
run-bff:
	cd services/bff && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-llm-gateway:
	cd services/llm-gateway && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

run-text-processor:
	cd services/text-processor && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

run-embedding-service:
	cd services/embedding-service && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8003

run-rag-service:
	cd services/rag-service && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8004

run-tool-service:
	cd services/tool-service && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8005

run-agent-orchestrator:
	cd services/agent-orchestrator && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8006
