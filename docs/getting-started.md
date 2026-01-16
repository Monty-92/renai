# Getting Started with Renai

This guide will help you set up and run the Renai microservices platform.

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Docker and Docker Compose
- 16GB+ RAM recommended

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/renai.git
cd renai
```

### 2. Run Setup Script

```bash
./scripts/setup.sh
```

This script will:
- Install uv if not present
- Install all dependencies
- Copy environment configuration

### 3. Start Infrastructure Services

```bash
make infra-up
```

This starts PostgreSQL, Redis, RabbitMQ, Qdrant, MinIO, and Ollama.

### 4. Pull LLM Models

```bash
./scripts/pull-models.sh
```

This downloads the required Ollama models:
- `llama3.2` - Main LLM
- `nomic-embed-text` - Embedding model

### 5. Start All Services

```bash
make run-all
```

Or start individual services:

```bash
make run-bff
make run-llm-gateway
make run-text-processor
make run-embedding-service
make run-rag-service
make run-tool-service
make run-agent-orchestrator
```

## Configuration

### Environment Variables

Copy the example environment file:

```bash
cp deploy/.env.example .env
```

Key configurations:

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_HOST` | PostgreSQL host | localhost |
| `POSTGRES_PORT` | PostgreSQL port | 5432 |
| `REDIS_HOST` | Redis host | localhost |
| `OLLAMA_HOST` | Ollama host | localhost |
| `DEBUG` | Enable debug mode | false |
| `LOG_LEVEL` | Logging level | INFO |

### Service Ports

| Service | Port |
|---------|------|
| BFF (API Gateway) | 8000 |
| LLM Gateway | 8001 |
| Text Processor | 8002 |
| Embedding Service | 8003 |
| RAG Service | 8004 |
| Tool Service | 8005 |
| Agent Orchestrator | 8006 |

## Project Structure

```
renai/
├── packages/
│   └── shared/              # Shared utilities
├── services/
│   ├── bff/                 # API Gateway
│   ├── llm-gateway/         # LLM client
│   ├── text-processor/      # Document processing
│   ├── embedding-service/   # Embeddings
│   ├── rag-service/         # RAG pipeline
│   ├── tool-service/        # Tool registry
│   └── agent-orchestrator/  # AI agents
├── deploy/
│   ├── docker-compose.yml   # Infrastructure
│   └── .env.example         # Environment template
├── docs/                    # Documentation
├── scripts/                 # Setup scripts
├── pyproject.toml          # Workspace config
└── Makefile                # Common tasks
```

## Development

### Install Dependencies

```bash
uv sync
```

### Run Tests

```bash
make test
```

### Run Linting

```bash
make lint
```

### Format Code

```bash
make format
```

## Verifying Installation

### Check Service Health

```bash
# Check BFF
curl http://localhost:8000/health

# Check all services
make health-check
```

### Test API Endpoints

```bash
# Generate completion
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?"}'

# List available tools
curl http://localhost:8000/api/v1/tools
```

## Docker Deployment

### Build All Services

```bash
make docker-build
```

### Run with Docker Compose

```bash
docker-compose -f deploy/docker-compose.yml up -d
```

## Troubleshooting

### Ollama Not Starting

Ensure Docker has enough memory allocated (16GB+ recommended).

```bash
# Check Ollama logs
docker logs renai-ollama
```

### Connection Refused Errors

Services may take time to start. Wait 30 seconds and retry.

```bash
# Check all container status
docker-compose -f deploy/docker-compose.yml ps
```

### Model Not Found

Pull the required models:

```bash
./scripts/pull-models.sh
```

## Next Steps

- Read the [Architecture Guide](./architecture.md)
- Check the [API Reference](./api-reference.md)
- Explore individual service READMEs
