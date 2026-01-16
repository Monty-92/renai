# BFF (Backend for Frontend)

Gateway service for frontend applications, handles authentication and request aggregation.

## Purpose

The BFF service acts as a single entry point for client applications, providing:
- API gateway and request routing
- Authentication and authorization
- Request/response transformation
- Rate limiting and caching
- API composition and aggregation

## Configuration

Set environment variables in `.env` or through system environment.

## Running

```bash
# From root directory
make run-bff

# Or directly
cd services/bff
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

- `GET /` - Service information
- `GET /health` - Health check

## Dependencies

- FastAPI
- Uvicorn
- Pydantic
- httpx
- python-jose (JWT handling)
