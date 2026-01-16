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

"""BFF (API Gateway) main application entry point."""

from contextlib import asynccontextmanager
from typing import Any

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from shared import Settings, get_settings, get_logger
from shared.types import (
    ServiceResponse,
    LLMRequest,
    LLMResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    RAGQuery,
    RAGResult,
    AgentTask,
)

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting BFF service", extra={"port": settings.service_port})
    app.state.http_client = httpx.AsyncClient(timeout=60.0)
    yield
    await app.state.http_client.aclose()
    logger.info("Shutting down BFF service")


app = FastAPI(
    title="Renai BFF",
    description="Backend for Frontend API Gateway",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> ServiceResponse[dict[str, str]]:
    """Health check endpoint."""
    return ServiceResponse(data={"status": "healthy", "service": "bff"})


@app.post("/api/v1/chat")
async def chat_completion(request: LLMRequest) -> ServiceResponse[LLMResponse]:
    """Forward chat completion request to LLM Gateway."""
    try:
        client: httpx.AsyncClient = app.state.http_client
        response = await client.post(
            f"{settings.llm_gateway_url}/api/v1/completions",
            json=request.model_dump(),
        )
        response.raise_for_status()
        data = response.json()
        return ServiceResponse(data=LLMResponse(**data["data"]))
    except httpx.HTTPError as e:
        logger.error("LLM Gateway request failed", extra={"error": str(e)})
        raise HTTPException(status_code=503, detail="LLM Gateway unavailable")


@app.post("/api/v1/embeddings")
async def generate_embeddings(
    request: EmbeddingRequest,
) -> ServiceResponse[EmbeddingResponse]:
    """Forward embedding request to Embedding Service."""
    try:
        client: httpx.AsyncClient = app.state.http_client
        response = await client.post(
            f"{settings.embedding_service_url}/api/v1/embeddings",
            json=request.model_dump(),
        )
        response.raise_for_status()
        data = response.json()
        return ServiceResponse(data=EmbeddingResponse(**data["data"]))
    except httpx.HTTPError as e:
        logger.error("Embedding Service request failed", extra={"error": str(e)})
        raise HTTPException(status_code=503, detail="Embedding Service unavailable")


@app.post("/api/v1/query")
async def rag_query(request: RAGQuery) -> ServiceResponse[RAGResult]:
    """Forward RAG query to RAG Service."""
    try:
        client: httpx.AsyncClient = app.state.http_client
        response = await client.post(
            f"{settings.rag_service_url}/api/v1/query",
            json=request.model_dump(),
        )
        response.raise_for_status()
        data = response.json()
        return ServiceResponse(data=RAGResult(**data["data"]))
    except httpx.HTTPError as e:
        logger.error("RAG Service request failed", extra={"error": str(e)})
        raise HTTPException(status_code=503, detail="RAG Service unavailable")


@app.get("/api/v1/tools")
async def list_tools() -> ServiceResponse[list[dict[str, Any]]]:
    """Get list of available tools from Tool Service."""
    try:
        client: httpx.AsyncClient = app.state.http_client
        response = await client.get(f"{settings.tool_service_url}/api/v1/tools")
        response.raise_for_status()
        data = response.json()
        return ServiceResponse(data=data["data"])
    except httpx.HTTPError as e:
        logger.error("Tool Service request failed", extra={"error": str(e)})
        raise HTTPException(status_code=503, detail="Tool Service unavailable")


@app.post("/api/v1/agents/tasks")
async def create_agent_task(task: AgentTask) -> ServiceResponse[dict[str, Any]]:
    """Create a new agent task."""
    try:
        client: httpx.AsyncClient = app.state.http_client
        response = await client.post(
            f"{settings.agent_orchestrator_url}/api/v1/tasks",
            json=task.model_dump(),
        )
        response.raise_for_status()
        data = response.json()
        return ServiceResponse(data=data["data"])
    except httpx.HTTPError as e:
        logger.error("Agent Orchestrator request failed", extra={"error": str(e)})
        raise HTTPException(status_code=503, detail="Agent Orchestrator unavailable")


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.service_host,
        port=settings.service_port,
        reload=settings.debug,
    )
