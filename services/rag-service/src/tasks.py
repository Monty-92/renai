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

"""Celery tasks for RAG Service."""

from celery import Celery

from shared import get_settings

settings = get_settings()

celery_app = Celery(
    "rag_tasks",
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(bind=True)
def ingest_document_task(self, collection: str, document_id: str, chunks: list):
    """Background task to ingest document chunks."""
    # This would be implemented to call the ingest endpoint
    # or directly interact with Qdrant
    return {
        "task_id": self.request.id,
        "collection": collection,
        "document_id": document_id,
        "chunks_count": len(chunks),
        "status": "completed",
    }


@celery_app.task(bind=True)
def reindex_collection_task(self, collection: str):
    """Background task to reindex a collection."""
    return {
        "task_id": self.request.id,
        "collection": collection,
        "status": "completed",
    }
