# Renai RAG Service

RAG (Retrieval-Augmented Generation) service with Celery task processing.

## Features

- Document ingestion pipeline
- Vector storage with Qdrant
- Semantic search
- RAG query processing
- Async task processing with Celery

## Running

Start the service:
```bash
cd services/rag-service
uv run python -m src.main
```

Start Celery worker:
```bash
cd services/rag-service
uv run celery -A src.tasks worker --loglevel=info
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/v1/ingest` - Ingest document
- `POST /api/v1/query` - RAG query
- `GET /api/v1/collections` - List collections
- `POST /api/v1/collections` - Create collection
- `DELETE /api/v1/collections/{name}` - Delete collection

## Configuration

- `QDRANT_HOST` - Qdrant host (default: localhost)
- `QDRANT_PORT` - Qdrant port (default: 6333)
- `REDIS_URL` - Redis URL for Celery (default: redis://localhost:6379)
- `SERVICE_PORT` - Service port (default: 8004)
