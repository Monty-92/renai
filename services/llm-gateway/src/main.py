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

"""LLM Gateway main application entry point."""

from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from ollama import AsyncClient
from pydantic import BaseModel

from shared import get_settings, get_logger
from shared.types import ServiceResponse, LLMRequest, LLMResponse

logger = get_logger(__name__)
settings = get_settings()


class ChatMessage(BaseModel):
    """Chat message model."""

    role: str
    content: str


class ChatRequest(BaseModel):
    """Chat completion request."""

    messages: list[ChatMessage]
    model: str = "llama3.2"
    temperature: float = 0.7
    stream: bool = False


class ModelPullRequest(BaseModel):
    """Model pull request."""

    name: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info(
        "Starting LLM Gateway service",
        extra={"port": 8001, "ollama_url": settings.ollama_url},
    )
    app.state.ollama_client = AsyncClient(host=settings.ollama_url)
    yield
    logger.info("Shutting down LLM Gateway service")


app = FastAPI(
    title="Renai LLM Gateway",
    description="LLM Gateway for Ollama integration",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check() -> ServiceResponse[dict[str, str]]:
    """Health check endpoint."""
    return ServiceResponse(data={"status": "healthy", "service": "llm-gateway"})


@app.post("/api/v1/completions")
async def generate_completion(request: LLMRequest) -> ServiceResponse[LLMResponse]:
    """Generate text completion using Ollama."""
    try:
        client: AsyncClient = app.state.ollama_client
        messages = []

        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})

        messages.append({"role": "user", "content": request.prompt})

        response = await client.chat(
            model=request.model,
            messages=messages,
            options={
                "temperature": request.temperature,
                **({"num_predict": request.max_tokens} if request.max_tokens else {}),
            },
        )

        return ServiceResponse(
            data=LLMResponse(
                content=response["message"]["content"],
                model=request.model,
                tokens_used=response.get("eval_count"),
                finish_reason="stop",
            )
        )
    except Exception as e:
        logger.error("Completion request failed", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/chat")
async def chat_completion(request: ChatRequest):
    """Chat completion with optional streaming."""
    try:
        client: AsyncClient = app.state.ollama_client
        messages = [{"role": m.role, "content": m.content} for m in request.messages]

        if request.stream:

            async def generate():
                async for chunk in await client.chat(
                    model=request.model,
                    messages=messages,
                    stream=True,
                    options={"temperature": request.temperature},
                ):
                    yield chunk["message"]["content"]

            return StreamingResponse(generate(), media_type="text/plain")

        response = await client.chat(
            model=request.model,
            messages=messages,
            options={"temperature": request.temperature},
        )

        return ServiceResponse(
            data=LLMResponse(
                content=response["message"]["content"],
                model=request.model,
                tokens_used=response.get("eval_count"),
                finish_reason="stop",
            )
        )
    except Exception as e:
        logger.error("Chat request failed", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/models")
async def list_models() -> ServiceResponse[list[dict[str, Any]]]:
    """List available models."""
    try:
        client: AsyncClient = app.state.ollama_client
        response = await client.list()
        models = [
            {
                "name": m["name"],
                "size": m.get("size"),
                "modified_at": m.get("modified_at"),
            }
            for m in response.get("models", [])
        ]
        return ServiceResponse(data=models)
    except Exception as e:
        logger.error("List models failed", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/models/pull")
async def pull_model(request: ModelPullRequest) -> ServiceResponse[dict[str, str]]:
    """Pull a model from Ollama registry."""
    try:
        client: AsyncClient = app.state.ollama_client
        await client.pull(request.name)
        return ServiceResponse(
            data={"status": "success", "model": request.name},
            message=f"Model {request.name} pulled successfully",
        )
    except Exception as e:
        logger.error("Pull model failed", extra={"error": str(e), "model": request.name})
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.service_host,
        port=8001,
        reload=settings.debug,
    )
