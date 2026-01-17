# Text Processor

Service for text preprocessing, chunking, and transformation.

## Purpose

The Text Processor service provides:
- Document parsing (PDF, Word, etc.)
- Text chunking with overlap
- Text cleaning and normalization
- Metadata extraction
- Format conversion

## Running

```bash
# From root directory
make run-text-processor

# Or directly
cd services/text-processor
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

## API Documentation

- Swagger UI: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc

## Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `POST /v1/chunk` - Chunk text
- `POST /v1/process` - Process documents

## Supported Formats

- PDF
- Word (DOCX)
- Plain text
- Markdown
- HTML
