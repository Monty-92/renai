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

"""Configuration management for Renai services."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Base settings for all Renai services."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Service settings
    service_name: str = "renai"
    service_host: str = "0.0.0.0"
    service_port: int = 8000
    debug: bool = False
    log_level: str = "INFO"

    # Database settings
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "renai"
    postgres_password: str = "renai"
    postgres_db: str = "renai"

    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Redis settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""

    @property
    def redis_url(self) -> str:
        """Get Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}"
        return f"redis://{self.redis_host}:{self.redis_port}"

    # RabbitMQ settings
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "renai"
    rabbitmq_password: str = "renai"

    @property
    def rabbitmq_url(self) -> str:
        """Get RabbitMQ connection URL."""
        return (
            f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}"
            f"@{self.rabbitmq_host}:{self.rabbitmq_port}/"
        )

    # Qdrant settings
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    @property
    def qdrant_url(self) -> str:
        """Get Qdrant connection URL."""
        return f"http://{self.qdrant_host}:{self.qdrant_port}"

    # MinIO settings
    minio_host: str = "localhost"
    minio_port: int = 9000
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "renai"

    @property
    def minio_endpoint(self) -> str:
        """Get MinIO endpoint."""
        return f"{self.minio_host}:{self.minio_port}"

    # Ollama settings
    ollama_host: str = "localhost"
    ollama_port: int = 11434

    @property
    def ollama_url(self) -> str:
        """Get Ollama API URL."""
        return f"http://{self.ollama_host}:{self.ollama_port}"

    # Service URLs (for inter-service communication)
    bff_url: str = "http://localhost:8000"
    llm_gateway_url: str = "http://localhost:8001"
    text_processor_url: str = "http://localhost:8002"
    embedding_service_url: str = "http://localhost:8003"
    rag_service_url: str = "http://localhost:8004"
    tool_service_url: str = "http://localhost:8005"
    agent_orchestrator_url: str = "http://localhost:8006"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
