# Embedding Service

Generates embeddings for text using various models.

## Purpose

The Embedding Service provides:
- Generate embeddings using various models
- Batch embedding processing
- Embedding model management
- Dimensionality reduction

## Running

```bash
# From root directory
make run-embedding-service

# Or directly
cd services/embedding-service
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
```

## API Documentation

- Swagger UI: http://localhost:8003/docs
- ReDoc: http://localhost:8003/redoc

## Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `POST /v1/embeddings` - Generate embeddings
- `GET /v1/models` - List available models

## Supported Models

- sentence-transformers/all-MiniLM-L6-v2
- sentence-transformers/all-mpnet-base-v2
- OpenAI text-embedding-ada-002
