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

"""Structured logging utilities for Renai services."""

import logging
import sys
from typing import Any

from shared.config import get_settings


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging output."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured output."""
        # Add extra fields to the log output
        extra_fields = ""
        if hasattr(record, "extra"):
            extra = getattr(record, "extra")
            if extra:
                extra_fields = " " + " ".join(
                    f"{k}={v}" for k, v in extra.items()
                )

        return (
            f"{self.formatTime(record)} "
            f"[{record.levelname}] "
            f"{record.name}: {record.getMessage()}"
            f"{extra_fields}"
        )


def get_logger(name: str, extra: dict[str, Any] | None = None) -> logging.Logger:
    """Get a configured logger instance.

    Args:
        name: Logger name (typically __name__)
        extra: Optional extra fields to include in all log messages

    Returns:
        Configured logger instance
    """
    settings = get_settings()
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(getattr(logging, settings.log_level.upper()))

        # Console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)

        # Prevent propagation to root logger
        logger.propagate = False

    # Add extra fields adapter if provided
    if extra:
        return logging.LoggerAdapter(logger, {"extra": extra})

    return logger


def configure_uvicorn_logging() -> dict[str, Any]:
    """Get uvicorn logging configuration.

    Returns:
        Dictionary configuration for uvicorn logging
    """
    settings = get_settings()
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "shared.logging.StructuredFormatter",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default"],
                "level": settings.log_level,
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["default"],
                "level": settings.log_level,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["default"],
                "level": settings.log_level,
                "propagate": False,
            },
        },
    }
