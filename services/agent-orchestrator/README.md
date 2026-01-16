# Renai Agent Orchestrator

AI agent orchestration service with tool calling capabilities.

## Features

- Agent task management
- ReAct-style reasoning loops
- Tool selection and execution
- Multi-step task planning
- Conversation memory
- Task status tracking

## Running

```bash
cd services/agent-orchestrator
uv run python -m src.main
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/v1/tasks` - Create a new agent task
- `GET /api/v1/tasks/{task_id}` - Get task status
- `GET /api/v1/tasks/{task_id}/result` - Get task result
- `DELETE /api/v1/tasks/{task_id}` - Cancel task

## Configuration

- `SERVICE_PORT` - Service port (default: 8006)
- `LLM_GATEWAY_URL` - LLM Gateway URL
- `TOOL_SERVICE_URL` - Tool Service URL
- `MAX_ITERATIONS` - Maximum agent iterations (default: 10)
