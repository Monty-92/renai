# Renai BFF (API Gateway)

The Backend for Frontend service acts as the API gateway for the Renai platform.

## Features

- Unified API endpoint for all client applications
- Request routing to downstream services
- Authentication and authorization
- Rate limiting and request validation
- API response aggregation

## Running

```bash
cd services/bff
uv run python -m src.main
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/v1/chat` - Chat completion
- `POST /api/v1/embeddings` - Generate embeddings
- `POST /api/v1/documents` - Process documents
- `POST /api/v1/query` - RAG query
- `GET /api/v1/tools` - List available tools
- `POST /api/v1/agents/tasks` - Create agent task

## Configuration

Set environment variables or use `.env` file:

- `SERVICE_HOST` - Host to bind (default: 0.0.0.0)
- `SERVICE_PORT` - Port to bind (default: 8000)
- See shared config for additional settings
