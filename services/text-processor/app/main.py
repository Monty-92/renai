"""Text processing service for chunking and transformation."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Renai Text Processor",
    description="Text processing service for chunking and transformation",
    version="0.1.0",
)

# TODO: Configure CORS with environment-based origins for production
# See services/bff/app/config.py for example
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]  # Development only - restrict in production,
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
