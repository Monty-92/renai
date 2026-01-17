# LLM Gateway

Unified gateway for multiple LLM providers (OpenAI, Anthropic, local models via Ollama).

## Purpose

The LLM Gateway service provides:
- Abstract different LLM provider APIs
- Load balancing across providers
- Fallback mechanisms
- Token counting and cost tracking
- Response caching

## Configuration

Set API keys for LLM providers:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_BASE_URL=http://localhost:11434
```

## Running

```bash
# From root directory
make run-llm-gateway

# Or directly
cd services/llm-gateway
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

## API Documentation

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `POST /v1/completions` - Generate completion
- `POST /v1/chat/completions` - Chat completion
- `GET /v1/models` - List available models

## Supported Providers

- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Ollama (Local models)
