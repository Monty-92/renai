"""Base models for all services."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field


class BaseModel(PydanticBaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
    )


class TimestampModel(BaseModel):
    """Model with timestamp fields.

    Note:
        Services should update ``updated_at`` when modifying and persisting
        instances of this model, for example by calling :meth:`touch`.
    """

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def touch(self) -> None:
        """Update the ``updated_at`` timestamp to the current UTC time.

        This method should be called by services before persisting changes to
        an existing record to reflect the latest modification time.
        """
        self.updated_at = datetime.now(timezone.utc)


class ResponseModel(BaseModel):
    """Standard API response model."""

    success: bool = True
    message: str = "Success"
    data: Any = None
