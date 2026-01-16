# Renai LLM Gateway

LLM Gateway service for interacting with Ollama-hosted language models.

## Features

- Text completion and chat endpoints
- Streaming response support
- Model management (list, pull, delete)
- Token counting and usage tracking
- Prompt caching

## Running

```bash
cd services/llm-gateway
uv run python -m src.main
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/v1/completions` - Generate text completion
- `POST /api/v1/chat` - Chat completion
- `GET /api/v1/models` - List available models
- `POST /api/v1/models/pull` - Pull a model

## Configuration

- `OLLAMA_HOST` - Ollama server host (default: localhost)
- `OLLAMA_PORT` - Ollama server port (default: 11434)
- `SERVICE_PORT` - Service port (default: 8001)
