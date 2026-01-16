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

"""Common type definitions for Renai services."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ServiceResponse(BaseModel, Generic[T]):
    """Standard response wrapper for service endpoints."""

    success: bool = True
    data: T | None = None
    message: str | None = None


class ErrorResponse(BaseModel):
    """Standard error response model."""

    success: bool = False
    error: str
    detail: str | None = None
    code: str | None = None


class ChunkMetadata(BaseModel):
    """Metadata for a text chunk."""

    source: str
    page: int | None = None
    chunk_index: int
    total_chunks: int
    start_char: int
    end_char: int


class TextChunk(BaseModel):
    """A chunk of text with metadata."""

    content: str
    metadata: ChunkMetadata
    embedding: list[float] | None = None


class Document(BaseModel):
    """A document with optional chunks."""

    id: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    chunks: list[TextChunk] = Field(default_factory=list)


class EmbeddingRequest(BaseModel):
    """Request for generating embeddings."""

    texts: list[str]
    model: str = "nomic-embed-text"


class EmbeddingResponse(BaseModel):
    """Response containing embeddings."""

    embeddings: list[list[float]]
    model: str
    dimensions: int


class LLMRequest(BaseModel):
    """Request for LLM completion."""

    prompt: str
    model: str = "llama3.2"
    temperature: float = 0.7
    max_tokens: int | None = None
    system_prompt: str | None = None


class LLMResponse(BaseModel):
    """Response from LLM completion."""

    content: str
    model: str
    tokens_used: int | None = None
    finish_reason: str | None = None


class RAGQuery(BaseModel):
    """Request for RAG query."""

    query: str
    collection: str
    top_k: int = 5
    filters: dict[str, Any] | None = None


class RAGResult(BaseModel):
    """Result from RAG query."""

    answer: str
    sources: list[TextChunk]
    confidence: float | None = None


class ToolDefinition(BaseModel):
    """Definition of a tool for agent use."""

    name: str
    description: str
    parameters: dict[str, Any]
    required: list[str] = Field(default_factory=list)


class ToolCall(BaseModel):
    """A tool call made by an agent."""

    tool_name: str
    arguments: dict[str, Any]


class ToolResult(BaseModel):
    """Result of a tool execution."""

    tool_name: str
    success: bool
    result: Any | None = None
    error: str | None = None


class AgentMessage(BaseModel):
    """A message in an agent conversation."""

    role: str  # "user", "assistant", "system", "tool"
    content: str
    tool_calls: list[ToolCall] | None = None
    tool_results: list[ToolResult] | None = None


class AgentTask(BaseModel):
    """A task for an agent to execute."""

    task_id: str | None = None
    description: str
    tools: list[str] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)
    max_iterations: int = 10
