# Renai Architecture

## Overview

Renai is a Python microservices monorepo designed for building LLM (Large Language Model) applications. The architecture follows a modular, event-driven design with clear separation of concerns.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Client Applications                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BFF (API Gateway)                                   │
│                           Port: 8000                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
          ┌──────────────┬────────────┼────────────┬──────────────┐
          ▼              ▼            ▼            ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ LLM Gateway  │ │    Text      │ │  Embedding   │ │     RAG      │ │    Agent     │
│  Port: 8001  │ │  Processor   │ │   Service    │ │   Service    │ │ Orchestrator │
└──────────────┘ │  Port: 8002  │ │  Port: 8003  │ │  Port: 8004  │ │  Port: 8006  │
       │         └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
       │                                   │              │              │
       │                                   │              │              ▼
       │                                   │              │       ┌──────────────┐
       │                                   │              │       │    Tool      │
       │                                   │              │       │   Service    │
       │                                   │              │       │  Port: 8005  │
       │                                   │              │       └──────────────┘
       ▼                                   ▼              ▼
┌──────────────┐                   ┌──────────────┐ ┌──────────────┐
│    Ollama    │                   │    Qdrant    │ │   RabbitMQ   │
│   (LLMs)     │                   │   (Vectors)  │ │   (Tasks)    │
└──────────────┘                   └──────────────┘ └──────────────┘
```

## Services

### BFF (Backend for Frontend) - Port 8000

The API gateway that serves as the single entry point for all client applications.

**Responsibilities:**
- Request routing to downstream services
- Authentication and authorization
- Rate limiting
- Response aggregation
- API versioning

### LLM Gateway - Port 8001

Interface to Ollama-hosted language models.

**Responsibilities:**
- Text completion and chat endpoints
- Streaming response support
- Model management (list, pull, delete)
- Token usage tracking

### Text Processor - Port 8002

Document processing and text chunking service.

**Responsibilities:**
- PDF text extraction
- Markdown parsing
- Semantic text chunking
- Token counting

### Embedding Service - Port 8003

Text embedding generation using Ollama models.

**Responsibilities:**
- Single and batch embedding generation
- Embedding similarity calculation
- Support for multiple embedding models

### RAG Service - Port 8004

Retrieval-Augmented Generation pipeline.

**Responsibilities:**
- Document ingestion
- Vector storage with Qdrant
- Semantic search
- RAG query processing
- Celery task processing

### Tool Service - Port 8005

Tool registry implementing the Model Context Protocol (MCP).

**Responsibilities:**
- Tool registration and discovery
- MCP protocol support
- Tool execution
- Built-in tools (calculator, web search, weather)

### Agent Orchestrator - Port 8006

AI agent orchestration with tool calling capabilities.

**Responsibilities:**
- Agent task management
- ReAct-style reasoning loops
- Tool selection and execution
- Multi-step task planning

## Infrastructure

### PostgreSQL
Primary database for application data, user information, and metadata.

### Redis
Caching layer and Celery result backend.

### RabbitMQ
Message broker for Celery task queues and async processing.

### Qdrant
Vector database for storing and searching embeddings.

### MinIO
S3-compatible object storage for documents and files.

### Ollama
Local LLM runtime for text generation and embeddings.

## Shared Package

The `packages/shared` directory contains common utilities:

- **types.py**: Common data models (ServiceResponse, TextChunk, etc.)
- **config.py**: Centralized configuration with Pydantic Settings
- **logging.py**: Structured logging utilities

## Data Flow

### RAG Query Flow

1. Client sends query to BFF
2. BFF forwards to RAG Service
3. RAG Service:
   - Generates query embedding via Embedding Service
   - Searches Qdrant for similar chunks
   - Sends context + query to LLM Gateway
   - Returns answer with sources

### Document Ingestion Flow

1. Client uploads document to BFF
2. BFF forwards to Text Processor
3. Text Processor extracts and chunks text
4. Chunks sent to Embedding Service
5. Embeddings stored in Qdrant via RAG Service

### Agent Task Flow

1. Client creates task via BFF
2. Agent Orchestrator:
   - Gets available tools from Tool Service
   - Runs ReAct reasoning loop
   - Calls tools as needed
   - Returns final result

## Security Considerations

- All inter-service communication should use TLS in production
- API authentication via JWT tokens
- Rate limiting at BFF level
- Input validation at each service
- Secrets managed via environment variables

## Scalability

Each service can be independently scaled:
- Horizontal scaling with multiple instances
- Load balancing via Kubernetes or Docker Swarm
- Async processing with Celery workers
- Vector search optimized with Qdrant clustering
