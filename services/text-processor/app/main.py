"""Text processing service for chunking and transformation."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import config

app = FastAPI(
    title="Renai Text Processor",
    description="Text processing service for chunking and transformation",
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
    return {"service": "text-processor", "status": "running"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
