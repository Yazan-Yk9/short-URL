import logging

from fastapi import APIRouter, Depends, status

from app.api.deps import get_api_key_service, get_current_user
from app.core.exceptions import ApiKeyNotFoundException, ApiKeyLimitExceededException
from app.models.user import User
from app.schemas.api_key import ApiKeyCreate, ApiKeyResponse, ApiKeyCreatedResponse
from app.services.api_key_service import ApiKeyService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api-keys", tags=["API Keys"])


@router.post("", response_model=ApiKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    payload: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    service: ApiKeyService = Depends(get_api_key_service),
):
    """
    Create a new API key.
    The full key is returned ONLY ONCE — store it securely.
    """
    try:
        raw_key, api_key = await service.create_key(
            user=current_user,
            name=payload.name,
            is_live=payload.is_live,
        )
        return ApiKeyCreatedResponse(
            id=api_key.id,
            name=api_key.name,
            key_prefix=api_key.key_prefix,
            key=raw_key,  # ⚠️ Shown only in this response
            is_active=api_key.is_active,
            created_at=api_key.created_at,
        )
    except ApiKeyLimitExceededException as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@router.get("", response_model=list[ApiKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    service: ApiKeyService = Depends(get_api_key_service),
):
    """List all active API keys for the current user."""
    return await service.list_keys(current_user.id)


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    service: ApiKeyService = Depends(get_api_key_service),
):
    """Revoke (soft-delete) an API key."""
    try:
        await service.revoke_key(key_id=key_id, user_id=current_user.id)
    except ApiKeyNotFoundException as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
