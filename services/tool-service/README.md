# Renai Tool Service

Tool registry service implementing the Model Context Protocol (MCP).

## Features

- Tool registration and discovery
- MCP protocol support
- Tool execution with sandboxing
- Tool result caching
- Tool versioning

## Running

```bash
cd services/tool-service
uv run python -m src.main
```

## API Endpoints

- `GET /health` - Health check
- `GET /api/v1/tools` - List all tools
- `GET /api/v1/tools/{name}` - Get tool details
- `POST /api/v1/tools` - Register a tool
- `POST /api/v1/tools/{name}/execute` - Execute a tool
- `DELETE /api/v1/tools/{name}` - Unregister a tool

## MCP Protocol

This service implements the Model Context Protocol for tool interaction:
- Tool discovery via standard schema
- Parameter validation
- Result formatting

## Configuration

- `SERVICE_PORT` - Service port (default: 8005)
