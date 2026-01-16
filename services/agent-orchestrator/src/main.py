# Copyright 2024 Renai Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Agent Orchestrator main application entry point."""

import asyncio
import json
import re
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum
from typing import Any

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from shared import get_settings, get_logger
from shared.types import (
    ServiceResponse,
    AgentTask,
    AgentMessage,
    ToolCall,
    ToolResult,
    ToolDefinition,
)

logger = get_logger(__name__)
settings = get_settings()


class TaskStatus(str, Enum):
    """Task status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskState(BaseModel):
    """Internal task state."""

    task_id: str
    task: AgentTask
    status: TaskStatus = TaskStatus.PENDING
    messages: list[AgentMessage] = Field(default_factory=list)
    iterations: int = 0
    result: str | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# In-memory task store (would be database in production)
task_store: dict[str, TaskState] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Agent Orchestrator", extra={"port": 8006})
    app.state.http_client = httpx.AsyncClient(timeout=120.0)
    yield
    await app.state.http_client.aclose()
    logger.info("Shutting down Agent Orchestrator")


app = FastAPI(
    title="Renai Agent Orchestrator",
    description="AI agent orchestration with tool calling",
    version="0.1.0",
    lifespan=lifespan,
)


async def get_available_tools(tool_names: list[str] | None = None) -> list[ToolDefinition]:
    """Get available tools from tool service."""
    client: httpx.AsyncClient = app.state.http_client
    response = await client.get(f"{settings.tool_service_url}/api/v1/tools")
    response.raise_for_status()
    data = response.json()
    tools = [ToolDefinition(**t) for t in data["data"]]

    if tool_names:
        tools = [t for t in tools if t.name in tool_names]

    return tools


async def execute_tool(name: str, arguments: dict[str, Any]) -> ToolResult:
    """Execute a tool via tool service."""
    client: httpx.AsyncClient = app.state.http_client
    response = await client.post(
        f"{settings.tool_service_url}/api/v1/tools/{name}/execute",
        json={"arguments": arguments},
    )
    response.raise_for_status()
    data = response.json()
    return ToolResult(**data["data"])


async def call_llm(
    messages: list[dict[str, str]],
    tools: list[ToolDefinition] | None = None,
) -> str:
    """Call LLM with messages and optional tool definitions."""
    client: httpx.AsyncClient = app.state.http_client

    # Build system prompt with tool information
    system_prompt = (
        "You are an AI assistant that can use tools to help complete tasks.\n"
        "When you need to use a tool, respond with JSON in this format:\n"
        '{"action": "tool", "tool": "tool_name", "arguments": {...}}\n'
        "When you have completed the task, respond with:\n"
        '{"action": "finish", "answer": "your final answer"}\n'
    )

    if tools:
        tool_descriptions = "\n".join(
            f"- {t.name}: {t.description}" for t in tools
        )
        system_prompt += f"\nAvailable tools:\n{tool_descriptions}"

    # Build the prompt
    conversation = "\n".join(f"{m['role']}: {m['content']}" for m in messages)

    response = await client.post(
        f"{settings.llm_gateway_url}/api/v1/completions",
        json={
            "prompt": conversation,
            "system_prompt": system_prompt,
            "temperature": 0.1,
        },
    )
    response.raise_for_status()
    data = response.json()
    return data["data"]["content"]


def parse_agent_response(response: str) -> tuple[str, dict[str, Any]]:
    """Parse agent response to extract action."""
    # Try to find JSON in the response
    json_match = re.search(r'\{[^{}]*\}', response)
    if json_match:
        try:
            data = json.loads(json_match.group())
            action = data.get("action", "unknown")
            return action, data
        except json.JSONDecodeError:
            pass

    # If no valid JSON found, assume it's a final answer
    return "finish", {"action": "finish", "answer": response}


async def run_agent_loop(state: TaskState) -> None:
    """Run the agent reasoning loop."""
    state.status = TaskStatus.RUNNING
    state.updated_at = datetime.utcnow()

    # Get available tools
    tools = await get_available_tools(state.task.tools or None)

    # Initialize conversation with task description
    messages = [{"role": "user", "content": state.task.description}]
    state.messages.append(AgentMessage(role="user", content=state.task.description))

    while state.iterations < state.task.max_iterations:
        state.iterations += 1
        state.updated_at = datetime.utcnow()

        try:
            # Get LLM response
            llm_response = await call_llm(messages, tools)
            logger.info(
                "Agent iteration",
                extra={"task_id": state.task_id, "iteration": state.iterations},
            )

            # Parse response
            action, data = parse_agent_response(llm_response)

            if action == "finish":
                # Task completed
                state.result = data.get("answer", llm_response)
                state.status = TaskStatus.COMPLETED
                state.messages.append(
                    AgentMessage(role="assistant", content=state.result)
                )
                return

            elif action == "tool":
                # Execute tool
                tool_name = data.get("tool")
                tool_args = data.get("arguments", {})

                if not tool_name:
                    messages.append({
                        "role": "assistant",
                        "content": llm_response,
                    })
                    messages.append({
                        "role": "user",
                        "content": "Error: No tool name provided. Please specify a tool.",
                    })
                    continue

                # Record tool call
                tool_call = ToolCall(tool_name=tool_name, arguments=tool_args)
                state.messages.append(
                    AgentMessage(
                        role="assistant",
                        content=f"Calling tool: {tool_name}",
                        tool_calls=[tool_call],
                    )
                )

                # Execute the tool
                tool_result = await execute_tool(tool_name, tool_args)

                # Add result to conversation
                result_text = (
                    str(tool_result.result) if tool_result.success else tool_result.error
                )
                messages.append({
                    "role": "assistant",
                    "content": f"Tool call: {tool_name}({tool_args})",
                })
                messages.append({
                    "role": "user",
                    "content": f"Tool result: {result_text}",
                })

                state.messages.append(
                    AgentMessage(
                        role="tool",
                        content=result_text or "",
                        tool_results=[tool_result],
                    )
                )

            else:
                # Unknown action, treat as intermediate thinking
                messages.append({"role": "assistant", "content": llm_response})
                messages.append({
                    "role": "user",
                    "content": "Please continue or provide your final answer.",
                })

        except Exception as e:
            logger.error(
                "Agent loop error",
                extra={"task_id": state.task_id, "error": str(e)},
            )
            state.error = str(e)
            state.status = TaskStatus.FAILED
            return

    # Max iterations reached
    state.status = TaskStatus.FAILED
    state.error = f"Max iterations ({state.task.max_iterations}) reached"


@app.get("/health")
async def health_check() -> ServiceResponse[dict[str, str]]:
    """Health check endpoint."""
    return ServiceResponse(
        data={"status": "healthy", "service": "agent-orchestrator"}
    )


@app.post("/api/v1/tasks")
async def create_task(
    task: AgentTask,
    background_tasks: BackgroundTasks,
) -> ServiceResponse[dict[str, Any]]:
    """Create a new agent task."""
    # Generate task ID if not provided
    if not task.task_id:
        task.task_id = str(uuid.uuid4())

    # Create task state
    state = TaskState(task_id=task.task_id, task=task)
    task_store[task.task_id] = state

    # Schedule agent loop to run in background
    async def run_in_background():
        try:
            await run_agent_loop(state)
        except Exception as e:
            state.status = TaskStatus.FAILED
            state.error = str(e)
            state.updated_at = datetime.utcnow()

    # Add to background tasks
    background_tasks.add_task(asyncio.create_task, run_in_background())

    return ServiceResponse(
        data={
            "task_id": task.task_id,
            "status": state.status,
        },
        message=f"Task {task.task_id} created and scheduled",
    )


@app.get("/api/v1/tasks/{task_id}")
async def get_task_status(task_id: str) -> ServiceResponse[dict[str, Any]]:
    """Get task status."""
    if task_id not in task_store:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")

    state = task_store[task_id]
    return ServiceResponse(
        data={
            "task_id": task_id,
            "status": state.status,
            "iterations": state.iterations,
            "created_at": state.created_at.isoformat(),
            "updated_at": state.updated_at.isoformat(),
        }
    )


@app.get("/api/v1/tasks/{task_id}/result")
async def get_task_result(task_id: str) -> ServiceResponse[dict[str, Any]]:
    """Get task result."""
    if task_id not in task_store:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")

    state = task_store[task_id]
    return ServiceResponse(
        data={
            "task_id": task_id,
            "status": state.status,
            "result": state.result,
            "error": state.error,
            "messages": [m.model_dump() for m in state.messages],
        }
    )


@app.delete("/api/v1/tasks/{task_id}")
async def cancel_task(task_id: str) -> ServiceResponse[dict[str, str]]:
    """Cancel a task."""
    if task_id not in task_store:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")

    state = task_store[task_id]
    if state.status == TaskStatus.RUNNING:
        state.status = TaskStatus.CANCELLED
        state.updated_at = datetime.utcnow()

    return ServiceResponse(
        data={"task_id": task_id, "status": state.status},
        message=f"Task {task_id} cancelled",
    )


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.service_host,
        port=8006,
        reload=settings.debug,
    )
