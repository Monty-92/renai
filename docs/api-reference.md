# Renai API Reference

This document describes the REST API endpoints available through the BFF (API Gateway).

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In production, add JWT bearer tokens:

```
Authorization: Bearer <token>
```

## Response Format

All responses follow this structure:

```json
{
  "success": true,
  "data": {...},
  "message": "Optional message"
}
```

Error responses:

```json
{
  "success": false,
  "error": "Error description",
  "detail": "Optional details",
  "code": "ERROR_CODE"
}
```

---

## Health Check

### GET /health

Check service health.

**Response:**

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "bff"
  }
}
```

---

## Chat & Completions

### POST /api/v1/chat

Generate a chat completion.

**Request Body:**

```json
{
  "prompt": "What is the capital of France?",
  "model": "llama3.2",
  "temperature": 0.7,
  "max_tokens": 500,
  "system_prompt": "You are a helpful assistant."
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| prompt | string | Yes | - | The user's prompt |
| model | string | No | llama3.2 | Model to use |
| temperature | float | No | 0.7 | Sampling temperature (0-2) |
| max_tokens | int | No | null | Maximum tokens to generate |
| system_prompt | string | No | null | System instructions |

**Response:**

```json
{
  "success": true,
  "data": {
    "content": "The capital of France is Paris.",
    "model": "llama3.2",
    "tokens_used": 15,
    "finish_reason": "stop"
  }
}
```

---

## Embeddings

### POST /api/v1/embeddings

Generate embeddings for text.

**Request Body:**

```json
{
  "texts": ["Hello world", "How are you?"],
  "model": "nomic-embed-text"
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| texts | string[] | Yes | - | Texts to embed |
| model | string | No | nomic-embed-text | Embedding model |

**Response:**

```json
{
  "success": true,
  "data": {
    "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...]],
    "model": "nomic-embed-text",
    "dimensions": 768
  }
}
```

---

## RAG (Retrieval-Augmented Generation)

### POST /api/v1/query

Query the RAG pipeline.

**Request Body:**

```json
{
  "query": "What are the key features?",
  "collection": "documents",
  "top_k": 5,
  "filters": {"source": "manual"}
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| query | string | Yes | - | Query text |
| collection | string | Yes | - | Vector collection name |
| top_k | int | No | 5 | Number of results |
| filters | object | No | null | Metadata filters |

**Response:**

```json
{
  "success": true,
  "data": {
    "answer": "The key features include...",
    "sources": [
      {
        "content": "Relevant chunk...",
        "metadata": {
          "source": "manual",
          "page": 5
        }
      }
    ],
    "confidence": 0.89
  }
}
```

---

## Tools

### GET /api/v1/tools

List all available tools.

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "name": "calculator",
      "description": "Perform basic arithmetic calculations",
      "parameters": {
        "type": "object",
        "properties": {
          "expression": {
            "type": "string",
            "description": "Mathematical expression"
          }
        }
      },
      "required": ["expression"]
    }
  ]
}
```

---

## Agent Tasks

### POST /api/v1/agents/tasks

Create a new agent task.

**Request Body:**

```json
{
  "task_id": "optional-custom-id",
  "description": "Calculate 25 * 4 and tell me the result",
  "tools": ["calculator"],
  "context": {},
  "max_iterations": 10
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| task_id | string | No | auto-generated | Custom task ID |
| description | string | Yes | - | Task description |
| tools | string[] | No | [] | Tools to use |
| context | object | No | {} | Additional context |
| max_iterations | int | No | 10 | Max reasoning steps |

**Response:**

```json
{
  "success": true,
  "data": {
    "task_id": "abc123",
    "status": "completed",
    "result": "25 * 4 = 100"
  },
  "message": "Task abc123 created"
}
```

---

## Direct Service APIs

These endpoints are available on individual services:

### LLM Gateway (Port 8001)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/models | List available models |
| POST | /api/v1/models/pull | Pull a model |
| POST | /api/v1/chat | Chat completion |

### Text Processor (Port 8002)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/parse/pdf | Parse PDF document |
| POST | /api/v1/parse/markdown | Parse markdown |
| POST | /api/v1/chunk | Chunk text |
| POST | /api/v1/tokens/count | Count tokens |

### Embedding Service (Port 8003)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/embeddings | Generate embeddings |
| POST | /api/v1/embeddings/batch | Batch embeddings |
| POST | /api/v1/similarity | Calculate similarity |

### RAG Service (Port 8004)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/collections | List collections |
| POST | /api/v1/collections | Create collection |
| DELETE | /api/v1/collections/{name} | Delete collection |
| POST | /api/v1/ingest | Ingest document |
| POST | /api/v1/query | RAG query |

### Tool Service (Port 8005)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/tools | List tools |
| GET | /api/v1/tools/{name} | Get tool |
| POST | /api/v1/tools | Register tool |
| DELETE | /api/v1/tools/{name} | Unregister tool |
| POST | /api/v1/tools/{name}/execute | Execute tool |
| GET | /mcp/tools | MCP list tools |
| POST | /mcp/tools/call | MCP call tool |

### Agent Orchestrator (Port 8006)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/tasks | Create task |
| GET | /api/v1/tasks/{id} | Get task status |
| GET | /api/v1/tasks/{id}/result | Get task result |
| DELETE | /api/v1/tasks/{id} | Cancel task |

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| 400 | Bad Request | Invalid request body |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 500 | Internal Error | Server error |
| 503 | Service Unavailable | Downstream service unavailable |

---

## Rate Limits

Default rate limits (configurable):

| Endpoint | Limit |
|----------|-------|
| /api/v1/chat | 60 req/min |
| /api/v1/embeddings | 100 req/min |
| /api/v1/query | 60 req/min |
| Other | 1000 req/min |
