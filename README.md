# Renai - LLM Platform

A comprehensive Python monorepo for building Large Language Model (LLM) applications using modern tools and microservices architecture.

## 🚀 Overview

Renai is a scalable LLM platform built with:
- **Python 3.11+** for modern Python features
- **uv** for fast, reliable dependency management
- **FastAPI** for high-performance async APIs
- **Microservices Architecture** for modularity and scalability

## 📁 Project Structure

```
renai/
├── services/                    # Microservices
│   ├── bff/                    # Backend for Frontend
│   ├── llm-gateway/            # LLM Gateway Service
│   ├── text-processor/         # Text Processing Service
│   ├── embedding-service/      # Embedding Generation Service
│   ├── rag-service/            # Retrieval-Augmented Generation Service
│   ├── tool-service/           # Tool Management Service
│   └── agent-orchestrator/     # Agent Orchestration Service
├── packages/                    # Shared packages
│   └── shared/                 # Common utilities and types
├── deploy/                      # Deployment configurations
│   └── docker-compose.yml      # Infrastructure services
├── docs/                        # Documentation
│   ├── architecture.md         # Architecture overview
│   ├── getting-started.md      # Getting started guide
│   └── api-reference.md        # API documentation
├── pyproject.toml              # Workspace configuration
├── Makefile                     # Common tasks
└── README.md                    # This file
```

## 🛠️ Infrastructure

The platform includes the following infrastructure services:

- **PostgreSQL** - Primary database
- **Redis** - Caching and message broker
- **RabbitMQ** - Message queue for async processing
- **Qdrant** - Vector database for embeddings
- **MinIO** - S3-compatible object storage
- **Ollama** - Local LLM inference

## 🏃 Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Docker and Docker Compose

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Monty-92/renai.git
   cd renai
   ```

2. **Install dependencies**
   ```bash
   make install
   ```

3. **Start infrastructure services**
   ```bash
   make docker-up
   ```

4. **Run a service** (example: BFF)
   ```bash
   make run-bff
   ```

## 📚 Documentation

- [Architecture Overview](docs/architecture.md) - System design and architecture
- [Getting Started](docs/getting-started.md) - Detailed setup and usage guide
- [API Reference](docs/api-reference.md) - API endpoints documentation

## 🧪 Development

### Running Tests
```bash
make test
```

### Code Formatting
```bash
make format
```

### Linting
```bash
make lint
```

### Coverage Report
```bash
make test-cov
```

## 📦 Services

### BFF (Backend for Frontend)
Gateway service for frontend applications, handles authentication and request aggregation.
- Port: 8000

### LLM Gateway
Unified gateway for multiple LLM providers (OpenAI, Anthropic, local models via Ollama).
- Port: 8001

### Text Processor
Service for text preprocessing, chunking, and transformation.
- Port: 8002

### Embedding Service
Generates embeddings for text using various models.
- Port: 8003

### RAG Service
Implements Retrieval-Augmented Generation workflows.
- Port: 8004

### Tool Service
Manages and executes tools/functions for LLM agents.
- Port: 8005

### Agent Orchestrator
Orchestrates multi-agent systems and complex workflows.
- Port: 8006

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Documentation](docs/)
- [Issue Tracker](https://github.com/Monty-92/renai/issues)
- [Pull Requests](https://github.com/Monty-92/renai/pulls)