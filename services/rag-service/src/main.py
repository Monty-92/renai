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

"""RAG Service main application entry point."""

import uuid
from contextlib import asynccontextmanager
from typing import Any

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

from shared import get_settings, get_logger
from shared.types import (
    ServiceResponse,
    RAGQuery,
    RAGResult,
    TextChunk,
    ChunkMetadata,
)

logger = get_logger(__name__)
settings = get_settings()


class IngestRequest(BaseModel):
    """Request for document ingestion."""

    collection: str
    chunks: list[dict[str, Any]]
    metadata: dict[str, Any] = Field(default_factory=dict)


class CreateCollectionRequest(BaseModel):
    """Request to create a collection."""

    name: str
    vector_size: int = 768
    distance: str = "Cosine"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info(
        "Starting RAG Service",
        extra={"port": 8004, "qdrant_url": settings.qdrant_url},
    )
    app.state.qdrant_client = QdrantClient(
        host=settings.qdrant_host, port=settings.qdrant_port
    )
    app.state.http_client = httpx.AsyncClient(timeout=60.0)
    yield
    await app.state.http_client.aclose()
    logger.info("Shutting down RAG Service")


app = FastAPI(
    title="Renai RAG Service",
    description="RAG pipeline service",
    version="0.1.0",
    lifespan=lifespan,
)


async def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Get embeddings from embedding service."""
    client: httpx.AsyncClient = app.state.http_client
    response = await client.post(
        f"{settings.embedding_service_url}/api/v1/embeddings",
        json={"texts": texts},
    )
    response.raise_for_status()
    data = response.json()
    return data["data"]["embeddings"]


async def get_llm_response(prompt: str, context: str) -> str:
    """Get LLM response with context."""
    client: httpx.AsyncClient = app.state.http_client
    system_prompt = (
        "You are a helpful assistant. Use the provided context to answer questions. "
        "If the answer is not in the context, say so."
    )
    full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"

    response = await client.post(
        f"{settings.llm_gateway_url}/api/v1/completions",
        json={
            "prompt": full_prompt,
            "system_prompt": system_prompt,
        },
    )
    response.raise_for_status()
    data = response.json()
    return data["data"]["content"]


@app.get("/health")
async def health_check() -> ServiceResponse[dict[str, str]]:
    """Health check endpoint."""
    return ServiceResponse(data={"status": "healthy", "service": "rag-service"})


@app.post("/api/v1/collections")
async def create_collection(
    request: CreateCollectionRequest,
) -> ServiceResponse[dict[str, str]]:
    """Create a new vector collection."""
    try:
        client: QdrantClient = app.state.qdrant_client

        distance_map = {
            "Cosine": qdrant_models.Distance.COSINE,
            "Euclidean": qdrant_models.Distance.EUCLID,
            "Dot": qdrant_models.Distance.DOT,
        }

        client.create_collection(
            collection_name=request.name,
            vectors_config=qdrant_models.VectorParams(
                size=request.vector_size,
                distance=distance_map.get(request.distance, qdrant_models.Distance.COSINE),
            ),
        )

        return ServiceResponse(
            data={"collection": request.name, "status": "created"},
            message=f"Collection {request.name} created successfully",
        )
    except Exception as e:
        logger.error("Failed to create collection", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/collections")
async def list_collections() -> ServiceResponse[list[str]]:
    """List all collections."""
    try:
        client: QdrantClient = app.state.qdrant_client
        collections = client.get_collections()
        names = [c.name for c in collections.collections]
        return ServiceResponse(data=names)
    except Exception as e:
        logger.error("Failed to list collections", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/collections/{name}")
async def delete_collection(name: str) -> ServiceResponse[dict[str, str]]:
    """Delete a collection."""
    try:
        client: QdrantClient = app.state.qdrant_client
        client.delete_collection(collection_name=name)
        return ServiceResponse(
            data={"collection": name, "status": "deleted"},
            message=f"Collection {name} deleted successfully",
        )
    except Exception as e:
        logger.error("Failed to delete collection", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ingest")
async def ingest_document(request: IngestRequest) -> ServiceResponse[dict[str, Any]]:
    """Ingest document chunks into vector store."""
    try:
        client: QdrantClient = app.state.qdrant_client

        # Get embeddings for all chunks
        texts = [chunk["content"] for chunk in request.chunks]
        embeddings = await get_embeddings(texts)

        # Prepare points
        points = []
        for i, (chunk, embedding) in enumerate(zip(request.chunks, embeddings)):
            point_id = str(uuid.uuid4())
            points.append(
                qdrant_models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "content": chunk["content"],
                        "metadata": chunk.get("metadata", {}),
                        **request.metadata,
                    },
                )
            )

        # Upsert points
        client.upsert(collection_name=request.collection, points=points)

        return ServiceResponse(
            data={
                "collection": request.collection,
                "chunks_ingested": len(points),
            },
            message=f"Ingested {len(points)} chunks into {request.collection}",
        )
    except Exception as e:
        logger.error("Failed to ingest document", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/query")
async def rag_query(request: RAGQuery) -> ServiceResponse[RAGResult]:
    """Execute RAG query."""
    try:
        client: QdrantClient = app.state.qdrant_client

        # Get query embedding
        query_embeddings = await get_embeddings([request.query])
        query_vector = query_embeddings[0]

        # Search for similar chunks
        search_result = client.search(
            collection_name=request.collection,
            query_vector=query_vector,
            limit=request.top_k,
        )

        # Build context from results
        sources = []
        context_parts = []
        for i, hit in enumerate(search_result):
            content = hit.payload.get("content", "")
            metadata = hit.payload.get("metadata", {})
            context_parts.append(f"[{i + 1}] {content}")
            sources.append(
                TextChunk(
                    content=content,
                    metadata=ChunkMetadata(
                        source=metadata.get("source", "unknown"),
                        chunk_index=metadata.get("chunk_index", 0),
                        total_chunks=metadata.get("total_chunks", 1),
                        start_char=0,
                        end_char=len(content),
                    ),
                )
            )

        context = "\n\n".join(context_parts)

        # Get LLM response
        answer = await get_llm_response(request.query, context)

        return ServiceResponse(
            data=RAGResult(
                answer=answer,
                sources=sources,
                confidence=search_result[0].score if search_result else None,
            )
        )
    except Exception as e:
        logger.error("RAG query failed", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.service_host,
        port=8004,
        reload=settings.debug,
    )
