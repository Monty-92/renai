# Getting Started with Renai

This guide will help you set up and run the Renai LLM platform on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11 or higher**: [Download Python](https://www.python.org/downloads/)
- **uv**: Fast Python package installer
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Docker**: [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: Usually included with Docker Desktop
- **Make**: For running Makefile commands (pre-installed on macOS/Linux)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Monty-92/renai.git
cd renai
```

### 2. Install Dependencies

Install all project dependencies using uv:

```bash
make install
```

This command will:
- Create a virtual environment
- Install all service dependencies
- Set up the workspace

For development dependencies:

```bash
make dev
```

### 3. Start Infrastructure Services

Start all required infrastructure services (PostgreSQL, Redis, RabbitMQ, Qdrant, MinIO, Ollama):

```bash
make docker-up
```

This command will start all services in the background. You can verify they're running:

```bash
docker ps
```

To view logs:

```bash
make docker-logs
```

### 4. Verify Infrastructure

Check that all services are healthy:

- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`
- **RabbitMQ**: `localhost:5672` (Management UI at `http://localhost:15672`)
- **Qdrant**: `localhost:6333` (Dashboard at `http://localhost:6333/dashboard`)
- **MinIO**: `localhost:9000` (Console at `http://localhost:9001`)
- **Ollama**: `localhost:11434`

## Running Services

### Start Individual Services

You can start each service independently:

```bash
# BFF (Backend for Frontend)
make run-bff

# LLM Gateway
make run-llm-gateway

# Text Processor
make run-text-processor

# Embedding Service
make run-embedding-service

# RAG Service
make run-rag-service

# Tool Service
make run-tool-service

# Agent Orchestrator
make run-agent-orchestrator
```

Each service will start on its designated port:
- BFF: http://localhost:8000
- LLM Gateway: http://localhost:8001
- Text Processor: http://localhost:8002
- Embedding Service: http://localhost:8003
- RAG Service: http://localhost:8004
- Tool Service: http://localhost:8005
- Agent Orchestrator: http://localhost:8006

### API Documentation

Once a service is running, you can access its interactive API documentation:

- Swagger UI: `http://localhost:<port>/docs`
- ReDoc: `http://localhost:<port>/redoc`

For example, for the BFF service:
- http://localhost:8000/docs
- http://localhost:8000/redoc

## Configuration

### Environment Variables

Each service can be configured using environment variables. Create a `.env` file in the root directory:

```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=renai
POSTGRES_PASSWORD=renai
POSTGRES_DB=renai

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
```

### Service-Specific Configuration

Each service has its own configuration in `services/<service-name>/app/config.py`. Refer to individual service documentation for specific options.

## Development Workflow

### Code Formatting

Format all code using Black and Ruff:

```bash
make format
```

### Linting

Run linters to check code quality:

```bash
make lint
```

This runs:
- Ruff for Python linting
- MyPy for type checking

### Running Tests

Run all tests:

```bash
make test
```

Run tests with coverage:

```bash
make test-cov
```

The coverage report will be available in `htmlcov/index.html`.

### Clean Build Artifacts

Remove all build artifacts and cache files:

```bash
make clean
```

## Working with Ollama

### Pull a Model

To use Ollama for local LLM inference, first pull a model:

```bash
docker exec renai-ollama ollama pull llama2
```

Available models:
- `llama2`: Meta's Llama 2
- `mistral`: Mistral AI's model
- `codellama`: Code-specialized Llama
- `phi`: Microsoft's Phi models

### List Available Models

```bash
docker exec renai-ollama ollama list
```

### Test Ollama

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "Hello, how are you?",
  "stream": false
}'
```

## Database Setup

### Initialize Database

Run database migrations (when implemented):

```bash
# Example for future implementation
cd services/bff
uv run alembic upgrade head
```

### Access PostgreSQL

```bash
docker exec -it renai-postgres psql -U renai -d renai
```

Common commands:
```sql
\dt          -- List tables
\d+ table    -- Describe table
\l           -- List databases
\q           -- Quit
```

## MinIO Setup

### Create Buckets

Access MinIO console at http://localhost:9001 with credentials:
- Username: `minioadmin`
- Password: `minioadmin`

Or use the MinIO CLI:

```bash
docker exec renai-minio mc alias set myminio http://localhost:9000 minioadmin minioadmin
docker exec renai-minio mc mb myminio/documents
```

## RabbitMQ Management

Access the RabbitMQ management console at http://localhost:15672:
- Username: `guest`
- Password: `guest`

Here you can:
- Monitor queues
- View message rates
- Manage exchanges
- Debug message flow

## Troubleshooting

### Services Won't Start

1. Check if ports are already in use:
   ```bash
   lsof -i :8000  # Check specific port
   ```

2. Ensure Docker is running:
   ```bash
   docker ps
   ```

3. Check service logs:
   ```bash
   make docker-logs
   ```

### Database Connection Issues

1. Verify PostgreSQL is running:
   ```bash
   docker ps | grep postgres
   ```

2. Test connection:
   ```bash
   docker exec renai-postgres pg_isready -U renai
   ```

### Dependency Issues

1. Clean and reinstall:
   ```bash
   make clean
   make install
   ```

2. Check Python version:
   ```bash
   python --version  # Should be 3.11+
   ```

### Docker Issues

1. Restart all services:
   ```bash
   make docker-down
   make docker-up
   ```

2. Remove volumes (warning: deletes data):
   ```bash
   cd deploy
   docker-compose down -v
   ```

## Next Steps

- Read the [Architecture Overview](architecture.md)
- Explore the [API Reference](api-reference.md)
- Check out individual service documentation in `services/<service-name>/README.md`
- Start building your LLM application!

## Getting Help

- Open an issue on [GitHub](https://github.com/Monty-92/renai/issues)
- Check the documentation in the `docs/` directory
- Review service-specific README files

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [uv Documentation](https://github.com/astral-sh/uv)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Ollama Documentation](https://github.com/ollama/ollama)
