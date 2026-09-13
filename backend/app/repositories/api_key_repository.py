from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload

from app.models.api_key import ApiKey
from app.repositories.base import BaseRepository


class ApiKeyRepository(BaseRepository):

    async def get_by_hash(self, key_hash: str) -> ApiKey | None:
        """Fetch key by hash (used during authentication)."""
        stmt = select(ApiKey).where(ApiKey.key_hash == key_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_hash_with_user(self, key_hash: str) -> ApiKey | None:
        """
        Fetch key + eagerly load its owner (needed for async).
        Lazy loading is disabled in async SQLAlchemy.
        """
        stmt = (
            select(ApiKey)
            .where(ApiKey.key_hash == key_hash)
            .options(selectinload(ApiKey.user))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int) -> list[ApiKey]:
        """List all active keys for a user (newest first)."""
        stmt = (
            select(ApiKey)
            .where(ApiKey.user_id == user_id, ApiKey.is_active == True)
            .order_by(ApiKey.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_active_by_user(self, user_id: int) -> int:
        """Count active keys (used for plan limit checks)."""
        stmt = select(func.count()).where(
            ApiKey.user_id == user_id,
            ApiKey.is_active == True,
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def create_key(
        self,
        user_id: int,
        key_hash: str,
        key_prefix: str,
        name: str,
    ) -> ApiKey:
        new_key = ApiKey(
            user_id=user_id,
            key_hash=key_hash,
            key_prefix=key_prefix,
            name=name,
        )
        return await self.create(new_key)

    async def deactivate(self, key_id: int, user_id: int) -> bool:
        """Soft-delete a key (only if it belongs to the user)."""
        stmt = (
            update(ApiKey)
            .where(ApiKey.id == key_id, ApiKey.user_id == user_id)
            .values(is_active=False)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def update_last_used(self, key_id: int) -> None:
        stmt = update(ApiKey).where(ApiKey.id == key_id).values(last_used_at=func.now())
        await self.session.execute(stmt)
        await self.session.commit()
