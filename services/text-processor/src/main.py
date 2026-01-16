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

"""Text Processor main application entry point."""

import io
import uuid
from typing import Any

import markdown
import tiktoken
import uvicorn
from bs4 import BeautifulSoup
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from pypdf import PdfReader

from shared import get_settings, get_logger
from shared.types import (
    ServiceResponse,
    Document,
    TextChunk,
    ChunkMetadata,
)

logger = get_logger(__name__)
settings = get_settings()

app = FastAPI(
    title="Renai Text Processor",
    description="PDF/markdown parsing and semantic chunking service",
    version="0.1.0",
)


class ChunkRequest(BaseModel):
    """Request for text chunking."""

    text: str
    source: str = "unknown"
    chunk_size: int = Field(default=512, ge=100, le=4096)
    chunk_overlap: int = Field(default=50, ge=0, le=200)


class TokenCountRequest(BaseModel):
    """Request for token counting."""

    text: str
    model: str = "gpt-4"


class ParsedDocument(BaseModel):
    """Parsed document response."""

    content: str
    pages: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


def get_tokenizer(model: str = "gpt-4") -> tiktoken.Encoding:
    """Get tokenizer for model."""
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        return tiktoken.get_encoding("cl100k_base")


def semantic_chunk(
    text: str,
    source: str,
    chunk_size: int = 512,
    chunk_overlap: int = 50,
) -> list[TextChunk]:
    """Split text into semantic chunks based on token count."""
    tokenizer = get_tokenizer()
    tokens = tokenizer.encode(text)

    chunks = []
    start_idx = 0
    chunk_index = 0

    while start_idx < len(tokens):
        end_idx = min(start_idx + chunk_size, len(tokens))

        # Try to find a natural break point (sentence boundary)
        if end_idx < len(tokens):
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = tokenizer.decode(chunk_tokens)

            # Find last sentence boundary
            for sep in [". ", ".\n", "!\n", "?\n", "\n\n"]:
                last_sep = chunk_text.rfind(sep)
                if last_sep > len(chunk_text) // 2:
                    chunk_text = chunk_text[: last_sep + len(sep)]
                    end_idx = start_idx + len(tokenizer.encode(chunk_text))
                    break
        else:
            chunk_text = tokenizer.decode(tokens[start_idx:end_idx])

        # Calculate character positions
        start_char = len(tokenizer.decode(tokens[:start_idx]))
        end_char = start_char + len(chunk_text)

        chunks.append(
            TextChunk(
                content=chunk_text.strip(),
                metadata=ChunkMetadata(
                    source=source,
                    chunk_index=chunk_index,
                    total_chunks=0,  # Will be updated
                    start_char=start_char,
                    end_char=end_char,
                ),
            )
        )

        chunk_index += 1
        start_idx = end_idx - chunk_overlap

    # Update total chunks
    for chunk in chunks:
        chunk.metadata.total_chunks = len(chunks)

    return chunks


@app.get("/health")
async def health_check() -> ServiceResponse[dict[str, str]]:
    """Health check endpoint."""
    return ServiceResponse(data={"status": "healthy", "service": "text-processor"})


@app.post("/api/v1/parse/pdf")
async def parse_pdf(file: UploadFile = File(...)) -> ServiceResponse[ParsedDocument]:
    """Parse PDF document and extract text."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        content = await file.read()
        pdf_reader = PdfReader(io.BytesIO(content))

        text_parts = []
        for page in pdf_reader.pages:
            text_parts.append(page.extract_text() or "")

        full_text = "\n\n".join(text_parts)

        return ServiceResponse(
            data=ParsedDocument(
                content=full_text,
                pages=len(pdf_reader.pages),
                metadata={
                    "filename": file.filename,
                    "file_size": len(content),
                },
            )
        )
    except Exception as e:
        logger.error("PDF parsing failed", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(e)}")


@app.post("/api/v1/parse/markdown")
async def parse_markdown(text: str) -> ServiceResponse[ParsedDocument]:
    """Parse markdown text to plain text."""
    try:
        html = markdown.markdown(text)
        soup = BeautifulSoup(html, "html.parser")
        plain_text = soup.get_text(separator="\n\n")

        return ServiceResponse(
            data=ParsedDocument(
                content=plain_text,
                metadata={"original_length": len(text)},
            )
        )
    except Exception as e:
        logger.error("Markdown parsing failed", extra={"error": str(e)})
        raise HTTPException(
            status_code=500, detail=f"Failed to parse markdown: {str(e)}"
        )


@app.post("/api/v1/chunk")
async def chunk_text(request: ChunkRequest) -> ServiceResponse[Document]:
    """Chunk text into semantic segments."""
    try:
        chunks = semantic_chunk(
            text=request.text,
            source=request.source,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )

        doc = Document(
            id=str(uuid.uuid4()),
            content=request.text,
            metadata={"source": request.source},
            chunks=chunks,
        )

        return ServiceResponse(data=doc)
    except Exception as e:
        logger.error("Chunking failed", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Failed to chunk text: {str(e)}")


@app.post("/api/v1/tokens/count")
async def count_tokens(request: TokenCountRequest) -> ServiceResponse[dict[str, int]]:
    """Count tokens in text."""
    try:
        tokenizer = get_tokenizer(request.model)
        token_count = len(tokenizer.encode(request.text))
        return ServiceResponse(data={"token_count": token_count})
    except Exception as e:
        logger.error("Token counting failed", extra={"error": str(e)})
        raise HTTPException(
            status_code=500, detail=f"Failed to count tokens: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.service_host,
        port=8002,
        reload=settings.debug,
    )
