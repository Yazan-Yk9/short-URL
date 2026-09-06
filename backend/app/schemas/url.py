from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field, computed_field, ConfigDict

from app.core.constants import REGEX_SHORT_CODE_PATTERN
from app.core.config import settings


class URLCreate(BaseModel):
    """Request body for POST /shorten."""
    original_url: HttpUrl
    custom_alias: str | None = Field(
        None,
        max_length=20,
        pattern=REGEX_SHORT_CODE_PATTERN,
        description="Optional custom short code (Base58 characters only, max 20)"
    )


class URLResponse(BaseModel):
    """Response body for URL creation and retrieval."""
    id: int
    short_code: str
    original_url: HttpUrl
    custom_alias: str | None
    clicks: int
    expires_at: datetime | None
    created_at: datetime

    @computed_field
    @property
    def short_url(self) -> str:
        """Dynamically generates the full short URL based on BASE_URL."""
        return f"{settings.BASE_URL}/{self.short_code}"

    # Allows Pydantic to read data directly from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)
