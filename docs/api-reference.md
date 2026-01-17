# API Reference

This document provides a comprehensive reference for all API endpoints in the Renai LLM platform.

## Base URLs

When running locally with default configuration:

- **BFF**: `http://localhost:8000`
- **LLM Gateway**: `http://localhost:8001`
- **Text Processor**: `http://localhost:8002`
- **Embedding Service**: `http://localhost:8003`
- **RAG Service**: `http://localhost:8004`
- **Tool Service**: `http://localhost:8005`
- **Agent Orchestrator**: `http://localhost:8006`

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Common Response Format

All API responses follow this standard format:

```json
{
  "success": true,
  "message": "Success",
  "data": {
    // Response data here
  }
}
```

Error responses:

```json
{
  "success": false,
  "message": "Error description",
  "data": null
}
```

## BFF (Backend for Frontend)

### Health Check

**GET** `/health`

Returns the health status of the service.

**Response:**
```json
{
  "status": "healthy"
}
```

### Root Endpoint

**GET** `/`

Returns basic service information.

**Response:**
```json
{
  "service": "bff",
  "status": "running"
}
```

## LLM Gateway

### Health Check

**GET** `/health`

Returns the health status of the service.

### Generate Completion

**POST** `/v1/completions`

Generate a text completion using an LLM.

**Request Body:**
```json
{
  "model": "gpt-3.5-turbo",
  "prompt": "What is the capital of France?",
  "max_tokens": 100,
  "temperature": 0.7,
  "stream": false
}
```

**Response:**
```json
{
  "id": "cmpl-abc123",
  "model": "gpt-3.5-turbo",
  "choices": [
    {
      "text": "The capital of France is Paris.",
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 8,
    "completion_tokens": 7,
    "total_tokens": 15
  }
}
```

### Chat Completion

**POST** `/v1/chat/completions`

Generate a chat completion.

**Request Body:**
```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "What is Python?"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 150
}
```

**Response:**
```json
{
  "id": "chatcmpl-abc123",
  "model": "gpt-3.5-turbo",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Python is a high-level programming language..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 50,
    "total_tokens": 70
  }
}
```

### List Available Models

**GET** `/v1/models`

List all available LLM models.

**Response:**
```json
{
  "models": [
    {
      "id": "gpt-3.5-turbo",
      "provider": "openai",
      "capabilities": ["chat", "completion"]
    },
    {
      "id": "claude-2",
      "provider": "anthropic",
      "capabilities": ["chat"]
    }
  ]
}
```

## Text Processor

### Health Check

**GET** `/health`

Returns the health status of the service.

### Chunk Text

**POST** `/v1/chunk`

Split text into chunks for processing.

**Request Body:**
```json
{
  "text": "Long text to be chunked...",
  "chunk_size": 1000,
  "chunk_overlap": 200,
  "separator": "\n\n"
}
```

**Response:**
```json
{
  "chunks": [
    {
      "text": "First chunk...",
      "metadata": {
        "chunk_index": 0,
        "start_char": 0,
        "end_char": 1000
      }
    },
    {
      "text": "Second chunk...",
      "metadata": {
        "chunk_index": 1,
        "start_char": 800,
        "end_char": 1800
      }
    }
  ],
  "total_chunks": 2
}
```

### Process Document

**POST** `/v1/process`

Process and extract text from documents.

**Request:**
- Content-Type: `multipart/form-data`
- Field: `file` (document file)

**Response:**
```json
{
  "text": "Extracted text from document...",
  "metadata": {
    "page_count": 5,
    "word_count": 1234,
    "format": "pdf"
  }
}
```

## Embedding Service

### Health Check

**GET** `/health`

Returns the health status of the service.

### Generate Embeddings

**POST** `/v1/embeddings`

Generate embeddings for text.

**Request Body:**
```json
{
  "input": ["Text to embed", "Another text"],
  "model": "sentence-transformers/all-MiniLM-L6-v2"
}
```

**Response:**
```json
{
  "embeddings": [
    [0.123, -0.456, 0.789, ...],
    [0.234, -0.567, 0.890, ...]
  ],
  "model": "sentence-transformers/all-MiniLM-L6-v2",
  "dimensions": 384
}
```

### List Available Models

**GET** `/v1/models`

List available embedding models.

**Response:**
```json
{
  "models": [
    {
      "id": "sentence-transformers/all-MiniLM-L6-v2",
      "dimensions": 384,
      "max_tokens": 512
    },
    {
      "id": "text-embedding-ada-002",
      "dimensions": 1536,
      "max_tokens": 8191
    }
  ]
}
```

## RAG Service

### Health Check

**GET** `/health`

Returns the health status of the service.

### Create Collection

**POST** `/v1/collections`

Create a new vector collection.

**Request Body:**
```json
{
  "name": "documents",
  "vector_size": 384,
  "distance": "cosine"
}
```

**Response:**
```json
{
  "collection_id": "col_abc123",
  "name": "documents",
  "status": "created"
}
```

### Index Documents

**POST** `/v1/collections/{collection_id}/documents`

Add documents to a collection.

**Request Body:**
```json
{
  "documents": [
    {
      "id": "doc_1",
      "text": "Document text...",
      "metadata": {
        "source": "file.pdf",
        "page": 1
      }
    }
  ]
}
```

**Response:**
```json
{
  "indexed": 1,
  "failed": 0
}
```

### Search Documents

**POST** `/v1/collections/{collection_id}/search`

Search for relevant documents.

**Request Body:**
```json
{
  "query": "What is machine learning?",
  "top_k": 5,
  "filters": {
    "source": "textbook.pdf"
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "doc_1",
      "text": "Machine learning is...",
      "score": 0.95,
      "metadata": {
        "source": "textbook.pdf",
        "page": 42
      }
    }
  ],
  "query_time_ms": 45
}
```

### RAG Query

**POST** `/v1/rag/query`

Perform a complete RAG query with context retrieval and generation.

**Request Body:**
```json
{
  "query": "What is machine learning?",
  "collection_id": "col_abc123",
  "top_k": 3,
  "model": "gpt-3.5-turbo",
  "temperature": 0.7
}
```

**Response:**
```json
{
  "answer": "Machine learning is a subset of artificial intelligence...",
  "sources": [
    {
      "id": "doc_1",
      "text": "Context snippet...",
      "score": 0.95
    }
  ],
  "model": "gpt-3.5-turbo"
}
```

## Tool Service

### Health Check

**GET** `/health`

Returns the health status of the service.

### List Tools

**GET** `/v1/tools`

List all available tools.

**Response:**
```json
{
  "tools": [
    {
      "id": "calculator",
      "name": "Calculator",
      "description": "Perform mathematical calculations",
      "parameters": {
        "expression": {
          "type": "string",
          "description": "Mathematical expression to evaluate"
        }
      }
    }
  ]
}
```

### Execute Tool

**POST** `/v1/tools/{tool_id}/execute`

Execute a tool with given parameters.

**Request Body:**
```json
{
  "parameters": {
    "expression": "2 + 2 * 3"
  }
}
```

**Response:**
```json
{
  "result": 8,
  "execution_time_ms": 12,
  "success": true
}
```

### Register Tool

**POST** `/v1/tools`

Register a new tool.

**Request Body:**
```json
{
  "name": "weather",
  "description": "Get weather information",
  "endpoint": "https://api.weather.com/v1/current",
  "parameters": {
    "location": {
      "type": "string",
      "required": true
    }
  }
}
```

**Response:**
```json
{
  "tool_id": "tool_abc123",
  "status": "registered"
}
```

## Agent Orchestrator

### Health Check

**GET** `/health`

Returns the health status of the service.

### Create Agent

**POST** `/v1/agents`

Create a new agent.

**Request Body:**
```json
{
  "name": "research_agent",
  "description": "Agent for research tasks",
  "model": "gpt-4",
  "tools": ["search", "summarize"],
  "system_prompt": "You are a research assistant..."
}
```

**Response:**
```json
{
  "agent_id": "agent_abc123",
  "name": "research_agent",
  "status": "created"
}
```

### Execute Agent Task

**POST** `/v1/agents/{agent_id}/execute`

Execute a task with an agent.

**Request Body:**
```json
{
  "task": "Research the history of machine learning",
  "context": {},
  "max_iterations": 5
}
```

**Response:**
```json
{
  "task_id": "task_abc123",
  "status": "processing"
}
```

### Get Task Status

**GET** `/v1/tasks/{task_id}`

Get the status of a task.

**Response:**
```json
{
  "task_id": "task_abc123",
  "status": "completed",
  "result": {
    "output": "Machine learning history...",
    "iterations": 3,
    "tools_used": ["search", "summarize"]
  },
  "created_at": "2024-01-16T12:00:00Z",
  "completed_at": "2024-01-16T12:02:30Z"
}
```

### Create Workflow

**POST** `/v1/workflows`

Create a multi-agent workflow.

**Request Body:**
```json
{
  "name": "content_pipeline",
  "agents": [
    {
      "agent_id": "agent_1",
      "step": 1,
      "task": "Research topic"
    },
    {
      "agent_id": "agent_2",
      "step": 2,
      "task": "Write article"
    }
  ]
}
```

**Response:**
```json
{
  "workflow_id": "wf_abc123",
  "status": "created"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing or invalid authentication |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

## Rate Limiting

API rate limits (default):
- 100 requests per minute per IP for anonymous requests
- 1000 requests per minute for authenticated requests

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1234567890
```

## Pagination

For endpoints that return lists, use pagination parameters:

- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

Example:
```
GET /v1/documents?page=2&per_page=50
```

Response includes pagination metadata:
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "per_page": 50,
    "total": 234,
    "pages": 5
  }
}
```

## Webhook Events

Services can send webhook notifications for async operations:

### Event Types
- `task.completed`: Task execution completed
- `task.failed`: Task execution failed
- `document.indexed`: Document added to collection
- `agent.error`: Agent encountered an error

### Webhook Payload
```json
{
  "event": "task.completed",
  "timestamp": "2024-01-16T12:00:00Z",
  "data": {
    "task_id": "task_abc123",
    "result": {...}
  }
}
```

## SDK Examples

### Python

```python
import httpx

# Initialize client
client = httpx.Client(base_url="http://localhost:8000")

# Make a request
response = client.post("/v1/chat/completions", json={
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "user", "content": "Hello!"}
    ]
})

print(response.json())
```

### JavaScript

```javascript
const response = await fetch('http://localhost:8000/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    model: 'gpt-3.5-turbo',
    messages: [
      { role: 'user', content: 'Hello!' }
    ]
  })
});

const data = await response.json();
console.log(data);
```

## Interactive Documentation

For interactive API documentation with request/response examples:
- Swagger UI: `http://localhost:<port>/docs`
- ReDoc: `http://localhost:<port>/redoc`

## Support

For questions or issues:
- Open an issue on [GitHub](https://github.com/Monty-92/renai/issues)
- Check the [Getting Started Guide](getting-started.md)
- Review the [Architecture Documentation](architecture.md)
