# Renai Embedding Service

Embedding service for generating text embeddings using Ollama.

## Features

- Text embedding generation
- Batch embedding support
- Embedding similarity calculation
- Support for multiple embedding models

## Running

```bash
cd services/embedding-service
uv run python -m src.main
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/v1/embeddings` - Generate embeddings
- `POST /api/v1/embeddings/batch` - Batch embedding generation
- `POST /api/v1/similarity` - Calculate embedding similarity

## Configuration

- `OLLAMA_HOST` - Ollama server host (default: localhost)
- `OLLAMA_PORT` - Ollama server port (default: 11434)
- `SERVICE_PORT` - Service port (default: 8003)
- `DEFAULT_EMBEDDING_MODEL` - Default model (default: nomic-embed-text)
