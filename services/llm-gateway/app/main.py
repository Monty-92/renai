"""LLM Gateway service for unified LLM provider access."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import config

app = FastAPI(
    title="Renai LLM Gateway",
    description="Unified gateway for multiple LLM providers",
    version="0.1.0",
)

# Configure CORS with environment-based origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"service": "llm-gateway", "status": "running"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
