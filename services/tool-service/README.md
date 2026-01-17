# Tool Service

Manages and executes tools/functions for LLM agents.

## Purpose

The Tool Service provides:
- Tool registration and discovery
- Tool execution and sandboxing
- Parameter validation
- Result formatting
- Error handling

## Running

```bash
# From root directory
make run-tool-service

# Or directly
cd services/tool-service
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8005
```

## API Documentation

- Swagger UI: http://localhost:8005/docs
- ReDoc: http://localhost:8005/redoc

## Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `GET /v1/tools` - List tools
- `POST /v1/tools` - Register tool
- `POST /v1/tools/{id}/execute` - Execute tool

## Built-in Tools

- Calculator
- Web search
- Weather lookup
- Code execution (sandboxed)
