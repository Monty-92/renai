# Renai Shared Package

Common utilities shared across all Renai microservices.

## Features

- **Types**: Common data models and type definitions
- **Config**: Centralized configuration management
- **Logging**: Structured logging utilities

## Installation

This package is installed automatically as part of the Renai workspace:

```bash
uv sync
```

## Usage

```python
from shared.config import get_settings
from shared.logging import get_logger
from shared.types import ServiceResponse

settings = get_settings()
logger = get_logger(__name__)
```
