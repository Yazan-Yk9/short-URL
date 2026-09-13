import logging

from app.core.exceptions import (
    ApiKeyLimitExceededException,
    ApiKeyNotFoundException,
    InvalidApiKeyException,
    QuotaExceededException,
)
from app.core.security import generate_api_key, hash_api_key
from app.models.api_key import ApiKey
from app.models.user import User
from app.repositories.api_key_repository import ApiKeyRepository

logger = logging.getLogger(__name__)


class ApiKeyService:
    """Business logic for API key management and authentication."""

    KEY_LIMITS = {"free": 1, "pro": 3, "enterprise": 999}

    def __init__(self, repository: ApiKeyRepository):
        self.repository = repository

    async def create_key(
        self,
        user: User,
        name: str,
        is_live: bool = True,
    ) -> tuple[str, ApiKey]:
        """Create a new API key. Returns (raw_key, db_record)."""
        limit = self.KEY_LIMITS.get(user.plan, 1)
        current = await self.repository.count_active_by_user(user.id)
        if current >= limit:
            raise ApiKeyLimitExceededException(
                f"Your plan ({user.plan}) allows up to {limit} active key(s). "
                f"You have {current}. Revoke an old key or upgrade."
            )

        raw_key, key_hash, key_prefix = generate_api_key(is_live=is_live)
        api_key = await self.repository.create_key(
            user_id=user.id,
            key_hash=key_hash,
            key_prefix=key_prefix,
            name=name,
        )
        logger.info(f"API key created for user {user.id} ({key_prefix}...)")
        return raw_key, api_key

    async def list_keys(self, user_id: int) -> list[ApiKey]:
        return await self.repository.list_by_user(user_id)

    async def revoke_key(self, key_id: int, user_id: int) -> None:
        success = await self.repository.deactivate(key_id, user_id)
        if not success:
            raise ApiKeyNotFoundException()
        logger.info(f"API key {key_id} revoked by user {user_id}")

    async def verify_key(self, raw_key: str) -> User:
        """
        Verify a raw API key and return its owner.
        Raises InvalidApiKeyException if invalid/inactive.
        Raises QuotaExceededException if monthly quota is exhausted.
        """
        key_hash = hash_api_key(raw_key)
        api_key = await self.repository.get_by_hash_with_user(key_hash)
        if not api_key or not api_key.is_active:
            raise InvalidApiKeyException()

        user = api_key.user
        if not user or not user.is_active:
            raise InvalidApiKeyException()

        # Enforce monthly quota
        if user.api_calls_used >= user.api_calls_limit:
            raise QuotaExceededException()

        # Update audit trail
        await self.repository.update_last_used(api_key.id)
        return user
