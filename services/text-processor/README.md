# Renai Text Processor

Text processing service for PDF/markdown parsing and semantic chunking.

## Features

- PDF text extraction
- Markdown parsing
- Semantic text chunking
- Token counting
- Document metadata extraction

## Running

```bash
cd services/text-processor
uv run python -m src.main
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/v1/parse/pdf` - Parse PDF document
- `POST /api/v1/parse/markdown` - Parse markdown text
- `POST /api/v1/chunk` - Chunk text semantically
- `POST /api/v1/tokens/count` - Count tokens in text

## Configuration

- `SERVICE_PORT` - Service port (default: 8002)
- `CHUNK_SIZE` - Default chunk size in tokens (default: 512)
- `CHUNK_OVERLAP` - Chunk overlap in tokens (default: 50)
