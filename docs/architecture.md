# Architecture Overview

## System Design

Renai is a microservices-based LLM platform designed for scalability, maintainability, and flexibility. The platform follows a distributed architecture with specialized services handling specific concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Applications                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BFF (Backend for Frontend)                    │
│  - API Gateway & Request Aggregation                            │
│  - Authentication & Authorization                                │
│  - Rate Limiting & Caching                                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌──────────────┐   ┌──────────────────┐
│  LLM Gateway  │   │ Text Processor│   │ Agent Orchestrator│
└───────┬───────┘   └──────┬───────┘   └────────┬─────────┘
        │                  │                     │
        ▼                  ▼                     ▼
┌───────────────┐   ┌──────────────┐   ┌──────────────────┐
│ Embedding Svc │   │  RAG Service │   │  Tool Service    │
└───────────────┘   └──────────────┘   └──────────────────┘
        │                  │                     │
        └──────────────────┴─────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌──────────────┐   ┌──────────────────┐
│  PostgreSQL   │   │    Qdrant    │   │     MinIO        │
└───────────────┘   └──────────────┘   └──────────────────┘
        ▼                   ▼                   ▼
┌───────────────┐   ┌──────────────┐   ┌──────────────────┐
│     Redis     │   │   RabbitMQ   │   │     Ollama       │
└───────────────┘   └──────────────┘   └──────────────────┘
```

## Service Responsibilities

### BFF (Backend for Frontend)
- **Port**: 8000
- **Purpose**: Single entry point for client applications
- **Responsibilities**:
  - API gateway and request routing
  - Authentication and authorization
  - Request/response transformation
  - Rate limiting and caching
  - API composition and aggregation

### LLM Gateway
- **Port**: 8001
- **Purpose**: Unified interface for multiple LLM providers
- **Responsibilities**:
  - Abstract different LLM provider APIs (OpenAI, Anthropic, etc.)
  - Load balancing across providers
  - Fallback mechanisms
  - Token counting and cost tracking
  - Response caching
- **Integrations**: OpenAI API, Anthropic API, Ollama (local models)

### Text Processor
- **Port**: 8002
- **Purpose**: Text preprocessing and chunking
- **Responsibilities**:
  - Document parsing (PDF, Word, etc.)
  - Text chunking with overlap
  - Text cleaning and normalization
  - Metadata extraction
  - Format conversion

### Embedding Service
- **Port**: 8003
- **Purpose**: Text vectorization
- **Responsibilities**:
  - Generate embeddings using various models
  - Batch embedding processing
  - Embedding model management
  - Dimensionality reduction
- **Models**: sentence-transformers, OpenAI embeddings

### RAG Service
- **Port**: 8004
- **Purpose**: Retrieval-Augmented Generation workflows
- **Responsibilities**:
  - Vector similarity search
  - Context retrieval
  - Re-ranking results
  - Hybrid search (vector + keyword)
  - Query expansion
- **Dependencies**: Qdrant, Embedding Service, Text Processor

### Tool Service
- **Port**: 8005
- **Purpose**: Tool/function management for LLM agents
- **Responsibilities**:
  - Tool registration and discovery
  - Tool execution and sandboxing
  - Parameter validation
  - Result formatting
  - Error handling

### Agent Orchestrator
- **Port**: 8006
- **Purpose**: Multi-agent system coordination
- **Responsibilities**:
  - Agent workflow orchestration
  - Task decomposition
  - Agent communication
  - State management
  - Execution monitoring
- **Dependencies**: RabbitMQ for task queuing

## Infrastructure Components

### PostgreSQL
- **Purpose**: Primary relational database
- **Use Cases**:
  - User management
  - Conversation history
  - Audit logs
  - Metadata storage

### Redis
- **Purpose**: In-memory cache and message broker
- **Use Cases**:
  - Response caching
  - Session storage
  - Rate limiting
  - Pub/sub messaging

### RabbitMQ
- **Purpose**: Message queue for async processing
- **Use Cases**:
  - Background job processing
  - Event-driven communication
  - Task distribution
  - Workflow orchestration

### Qdrant
- **Purpose**: Vector database
- **Use Cases**:
  - Embedding storage
  - Similarity search
  - Document retrieval
  - Semantic search

### MinIO
- **Purpose**: S3-compatible object storage
- **Use Cases**:
  - Document storage
  - Model artifact storage
  - File uploads
  - Backups

### Ollama
- **Purpose**: Local LLM inference
- **Use Cases**:
  - Running open-source models locally
  - Cost-effective inference
  - Privacy-sensitive workloads
  - Development and testing

## Communication Patterns

### Synchronous (HTTP/REST)
- Client to BFF
- BFF to downstream services
- Service-to-service for real-time operations

### Asynchronous (Message Queue)
- Background processing
- Long-running tasks
- Event notifications
- Batch operations

### Caching Strategy
- Redis for frequently accessed data
- TTL-based invalidation
- Write-through cache for critical paths

## Security Considerations

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- API key management
- Service-to-service authentication

### Data Protection
- Encryption at rest (database)
- Encryption in transit (TLS)
- PII handling and masking
- Audit logging

### Network Security
- Service isolation via Docker networks
- Internal service communication
- API rate limiting
- DDoS protection

## Scalability

### Horizontal Scaling
- Stateless service design
- Load balancing ready
- Shared-nothing architecture
- Database connection pooling

### Performance Optimization
- Caching strategies
- Connection pooling
- Async processing
- Batch operations

## Monitoring & Observability

### Metrics
- Service health checks
- Response times
- Error rates
- Resource utilization

### Logging
- Structured logging
- Centralized log aggregation
- Log levels and filtering
- Request tracing

### Tracing
- Distributed tracing
- Request ID propagation
- Performance profiling

## Development Workflow

### Local Development
1. Start infrastructure: `make docker-up`
2. Install dependencies: `make install`
3. Run service: `make run-<service-name>`

### Testing
- Unit tests per service
- Integration tests
- End-to-end tests
- Load testing

### Deployment
- Docker containers
- Docker Compose for orchestration
- Environment-based configuration
- Rolling updates

## Future Enhancements

- Kubernetes deployment
- API versioning
- GraphQL gateway
- Streaming responses
- Multi-tenancy support
- Advanced monitoring (Prometheus, Grafana)
- Service mesh (Istio)
