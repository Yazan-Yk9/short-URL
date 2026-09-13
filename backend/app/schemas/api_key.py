from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ApiKeyCreate(BaseModel):
    """Request body for creating a new API key."""
    name: str = Field(..., min_length=1, max_length=100, description="Label for the key")
    is_live: bool = Field(True, description="True for production keys, False for test keys")


class ApiKeyResponse(BaseModel):
    """Public API key info (does NOT include the raw key)."""
    id: int
    name: str
    key_prefix: str
    is_active: bool
    last_used_at: datetime | None = Field(default=None)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApiKeyCreatedResponse(ApiKeyResponse):
    """Same as ApiKeyResponse but includes the raw key (shown ONCE)."""
    key: str
