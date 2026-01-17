# Agent Orchestrator

Orchestrates multi-agent systems and complex workflows.

## Purpose

The Agent Orchestrator provides:
- Agent workflow orchestration
- Task decomposition
- Agent communication
- State management
- Execution monitoring

## Running

```bash
# From root directory
make run-agent-orchestrator

# Or directly
cd services/agent-orchestrator
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8006
```

## API Documentation

- Swagger UI: http://localhost:8006/docs
- ReDoc: http://localhost:8006/redoc

## Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `POST /v1/agents` - Create agent
- `POST /v1/agents/{id}/execute` - Execute task
- `GET /v1/tasks/{id}` - Get task status
- `POST /v1/workflows` - Create workflow

## Agent Types

- Research Agent
- Coding Agent
- Writing Agent
- Analysis Agent
- Custom Agents
