# RAG Service

Implements Retrieval-Augmented Generation workflows.

## Purpose

The RAG Service provides:
- Vector similarity search
- Context retrieval
- Re-ranking results
- Hybrid search (vector + keyword)
- Query expansion

## Running

```bash
# From root directory
make run-rag-service

# Or directly
cd services/rag-service
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8004
```

## API Documentation

- Swagger UI: http://localhost:8004/docs
- ReDoc: http://localhost:8004/redoc

## Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `POST /v1/collections` - Create collection
- `POST /v1/collections/{id}/documents` - Index documents
- `POST /v1/collections/{id}/search` - Search documents
- `POST /v1/rag/query` - RAG query

## Dependencies

- Qdrant for vector storage
- Embedding Service for vectorization
- LLM Gateway for generation
