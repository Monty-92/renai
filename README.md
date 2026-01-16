# Renai

A Python microservices monorepo for building LLM (Large Language Model) applications.

## Overview

Renai provides a complete platform for building AI-powered applications with:

- **Local LLM Support**: Powered by Ollama for privacy-first AI
- **RAG Pipeline**: Document ingestion, semantic search, and context-aware responses
- **AI Agents**: Tool-calling agents with ReAct-style reasoning
- **MCP Protocol**: Model Context Protocol support for tool integration
- **Microservices Architecture**: Scalable, modular design

## Services

| Service | Port | Description |
|---------|------|-------------|
| BFF (API Gateway) | 8000 | Unified API entry point |
| LLM Gateway | 8001 | Ollama LLM integration |
| Text Processor | 8002 | PDF/markdown parsing, chunking |
| Embedding Service | 8003 | Text embedding generation |
| RAG Service | 8004 | Retrieval-augmented generation |
| Tool Service | 8005 | Tool registry (MCP protocol) |
| Agent Orchestrator | 8006 | AI agent task execution |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/renai.git
cd renai

# Run setup
./scripts/setup.sh

# Start infrastructure (PostgreSQL, Redis, Qdrant, Ollama, etc.)
make infra-up

# Pull LLM models
./scripts/pull-models.sh

# Run services (in separate terminals)
make run-bff
make run-llm-gateway
# ... or see Makefile for all services
```

## Project Structure

```
renai/
├── packages/
│   └── shared/              # Shared utilities (types, config, logging)
├── services/
│   ├── bff/                 # API Gateway
│   ├── llm-gateway/         # Ollama LLM client
│   ├── text-processor/      # Document processing
│   ├── embedding-service/   # Embeddings generation
│   ├── rag-service/         # RAG pipeline
│   ├── tool-service/        # Tool registry (MCP)
│   └── agent-orchestrator/  # AI agents
├── deploy/
│   ├── docker-compose.yml   # Infrastructure services
│   └── .env.example         # Environment template
├── docs/
│   ├── architecture.md      # System design
│   ├── getting-started.md   # Setup guide
│   └── api-reference.md     # API documentation
├── scripts/
│   ├── setup.sh             # Project setup
│   └── pull-models.sh       # Model download
├── pyproject.toml           # UV workspace config
└── Makefile                 # Common tasks
```

## Requirements

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Docker and Docker Compose
- 16GB+ RAM recommended

## Documentation

- [Getting Started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [API Reference](docs/api-reference.md)

## Example Usage

```bash
# Chat completion
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is machine learning?"}'

# List available tools
curl http://localhost:8000/api/v1/tools

# Create an agent task
curl -X POST http://localhost:8000/api/v1/agents/tasks \
  -H "Content-Type: application/json" \
  -d '{"description": "Calculate 25 * 4", "tools": ["calculator"]}'
```

## Development

```bash
# Install dependencies
uv sync

# Run tests
make test

# Run linting
make lint

# Format code
make format
```

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details