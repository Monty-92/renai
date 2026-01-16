.PHONY: help setup install test lint format clean
.PHONY: infra-up infra-down infra-logs
.PHONY: run-all run-bff run-llm-gateway run-text-processor run-embedding-service
.PHONY: run-rag-service run-tool-service run-agent-orchestrator
.PHONY: docker-build docker-up docker-down health-check

# Default target
help:
	@echo "Renai - LLM Microservices Platform"
	@echo ""
	@echo "Setup:"
	@echo "  make setup              - Initial project setup"
	@echo "  make install            - Install all dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make test               - Run all tests"
	@echo "  make lint               - Run linter"
	@echo "  make format             - Format code"
	@echo "  make clean              - Clean build artifacts"
	@echo ""
	@echo "Infrastructure:"
	@echo "  make infra-up           - Start infrastructure services"
	@echo "  make infra-down         - Stop infrastructure services"
	@echo "  make infra-logs         - View infrastructure logs"
	@echo ""
	@echo "Services:"
	@echo "  make run-all            - Run all services"
	@echo "  make run-bff            - Run BFF service"
	@echo "  make run-llm-gateway    - Run LLM Gateway service"
	@echo "  make run-text-processor - Run Text Processor service"
	@echo "  make run-embedding-service - Run Embedding service"
	@echo "  make run-rag-service    - Run RAG service"
	@echo "  make run-tool-service   - Run Tool service"
	@echo "  make run-agent-orchestrator - Run Agent Orchestrator"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build       - Build all Docker images"
	@echo "  make docker-up          - Start all services in Docker"
	@echo "  make docker-down        - Stop all Docker services"
	@echo ""
	@echo "Utilities:"
	@echo "  make health-check       - Check service health"

# Setup
setup:
	@echo "Running setup..."
	@./scripts/setup.sh

install:
	@echo "Installing dependencies..."
	@uv sync

# Testing
test:
	@echo "Running tests..."
	@uv run pytest -v

test-cov:
	@echo "Running tests with coverage..."
	@uv run pytest --cov=packages --cov=services --cov-report=html

# Linting & Formatting
lint:
	@echo "Running linter..."
	@uv run ruff check .

format:
	@echo "Formatting code..."
	@uv run ruff format .

type-check:
	@echo "Running type checker..."
	@uv run mypy packages services

# Clean
clean:
	@echo "Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true

# Infrastructure
infra-up:
	@echo "Starting infrastructure services..."
	@docker compose -f deploy/docker-compose.yml up -d

infra-down:
	@echo "Stopping infrastructure services..."
	@docker compose -f deploy/docker-compose.yml down

infra-logs:
	@docker compose -f deploy/docker-compose.yml logs -f

# Run Services
run-bff:
	@echo "Starting BFF service on port 8000..."
	@cd services/bff && uv run python -m src.main

run-llm-gateway:
	@echo "Starting LLM Gateway service on port 8001..."
	@cd services/llm-gateway && uv run python -m src.main

run-text-processor:
	@echo "Starting Text Processor service on port 8002..."
	@cd services/text-processor && uv run python -m src.main

run-embedding-service:
	@echo "Starting Embedding Service on port 8003..."
	@cd services/embedding-service && uv run python -m src.main

run-rag-service:
	@echo "Starting RAG Service on port 8004..."
	@cd services/rag-service && uv run python -m src.main

run-tool-service:
	@echo "Starting Tool Service on port 8005..."
	@cd services/tool-service && uv run python -m src.main

run-agent-orchestrator:
	@echo "Starting Agent Orchestrator on port 8006..."
	@cd services/agent-orchestrator && uv run python -m src.main

run-all:
	@echo "Starting all services..."
	@echo "Note: Run each service in a separate terminal or use Docker"
	@echo ""
	@echo "  make run-bff"
	@echo "  make run-llm-gateway"
	@echo "  make run-text-processor"
	@echo "  make run-embedding-service"
	@echo "  make run-rag-service"
	@echo "  make run-tool-service"
	@echo "  make run-agent-orchestrator"

# Celery Workers
run-rag-worker:
	@echo "Starting RAG Celery worker..."
	@cd services/rag-service && uv run celery -A src.tasks worker --loglevel=info

# Docker
docker-build:
	@echo "Building Docker images..."
	@docker build -t renai-bff -f services/bff/Dockerfile .
	@docker build -t renai-llm-gateway -f services/llm-gateway/Dockerfile .
	@docker build -t renai-text-processor -f services/text-processor/Dockerfile .
	@docker build -t renai-embedding-service -f services/embedding-service/Dockerfile .
	@docker build -t renai-rag-service -f services/rag-service/Dockerfile .
	@docker build -t renai-tool-service -f services/tool-service/Dockerfile .
	@docker build -t renai-agent-orchestrator -f services/agent-orchestrator/Dockerfile .

docker-up: infra-up
	@echo "Starting all services in Docker..."
	@echo "Note: Build images first with 'make docker-build'"

docker-down: infra-down
	@echo "All services stopped."

# Health Check
health-check:
	@echo "Checking service health..."
	@echo ""
	@echo "BFF (8000):"
	@curl -s http://localhost:8000/health | jq . 2>/dev/null || echo "  Not running"
	@echo ""
	@echo "LLM Gateway (8001):"
	@curl -s http://localhost:8001/health | jq . 2>/dev/null || echo "  Not running"
	@echo ""
	@echo "Text Processor (8002):"
	@curl -s http://localhost:8002/health | jq . 2>/dev/null || echo "  Not running"
	@echo ""
	@echo "Embedding Service (8003):"
	@curl -s http://localhost:8003/health | jq . 2>/dev/null || echo "  Not running"
	@echo ""
	@echo "RAG Service (8004):"
	@curl -s http://localhost:8004/health | jq . 2>/dev/null || echo "  Not running"
	@echo ""
	@echo "Tool Service (8005):"
	@curl -s http://localhost:8005/health | jq . 2>/dev/null || echo "  Not running"
	@echo ""
	@echo "Agent Orchestrator (8006):"
	@curl -s http://localhost:8006/health | jq . 2>/dev/null || echo "  Not running"

# Pull Models
pull-models:
	@echo "Pulling Ollama models..."
	@./scripts/pull-models.sh
