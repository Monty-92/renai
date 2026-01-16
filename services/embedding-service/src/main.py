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

"""Embedding Service main application entry point."""

from contextlib import asynccontextmanager

import numpy as np
import uvicorn
from fastapi import FastAPI, HTTPException
from ollama import AsyncClient
from pydantic import BaseModel

from shared import get_settings, get_logger
from shared.types import ServiceResponse, EmbeddingRequest, EmbeddingResponse

logger = get_logger(__name__)
settings = get_settings()


class SimilarityRequest(BaseModel):
    """Request for similarity calculation."""

    embedding1: list[float]
    embedding2: list[float]


class BatchEmbeddingRequest(BaseModel):
    """Request for batch embedding generation."""

    texts: list[str]
    model: str = "nomic-embed-text"
    batch_size: int = 32


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info(
        "Starting Embedding Service",
        extra={"port": 8003, "ollama_url": settings.ollama_url},
    )
    app.state.ollama_client = AsyncClient(host=settings.ollama_url)
    yield
    logger.info("Shutting down Embedding Service")


app = FastAPI(
    title="Renai Embedding Service",
    description="Text embedding generation service",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check() -> ServiceResponse[dict[str, str]]:
    """Health check endpoint."""
    return ServiceResponse(data={"status": "healthy", "service": "embedding-service"})


@app.post("/api/v1/embeddings")
async def generate_embeddings(
    request: EmbeddingRequest,
) -> ServiceResponse[EmbeddingResponse]:
    """Generate embeddings for texts."""
    try:
        client: AsyncClient = app.state.ollama_client
        embeddings = []

        for text in request.texts:
            response = await client.embeddings(model=request.model, prompt=text)
            embeddings.append(response["embedding"])

        dimensions = len(embeddings[0]) if embeddings else 0

        return ServiceResponse(
            data=EmbeddingResponse(
                embeddings=embeddings,
                model=request.model,
                dimensions=dimensions,
            )
        )
    except Exception as e:
        logger.error("Embedding generation failed", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/embeddings/batch")
async def generate_batch_embeddings(
    request: BatchEmbeddingRequest,
) -> ServiceResponse[EmbeddingResponse]:
    """Generate embeddings for texts in batches."""
    try:
        client: AsyncClient = app.state.ollama_client
        embeddings = []

        # Process in batches
        for i in range(0, len(request.texts), request.batch_size):
            batch = request.texts[i : i + request.batch_size]
            for text in batch:
                response = await client.embeddings(model=request.model, prompt=text)
                embeddings.append(response["embedding"])

        dimensions = len(embeddings[0]) if embeddings else 0

        return ServiceResponse(
            data=EmbeddingResponse(
                embeddings=embeddings,
                model=request.model,
                dimensions=dimensions,
            )
        )
    except Exception as e:
        logger.error("Batch embedding generation failed", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/similarity")
async def calculate_similarity(
    request: SimilarityRequest,
) -> ServiceResponse[dict[str, float]]:
    """Calculate cosine similarity between two embeddings."""
    try:
        vec1 = np.array(request.embedding1)
        vec2 = np.array(request.embedding2)

        # Cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            similarity = 0.0
        else:
            similarity = float(dot_product / (norm1 * norm2))

        return ServiceResponse(data={"similarity": similarity})
    except Exception as e:
        logger.error("Similarity calculation failed", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.service_host,
        port=8003,
        reload=settings.debug,
    )
