from datetime import datetime
from sqlalchemy import select, update, delete, func
from sqlalchemy.sql import func as sql_func

from app.models.url import URL
from app.repositories.base import BaseRepository

class URLRepository(BaseRepository):

    async def get_by_short_code(self, short_code: str) -> URL | None:
        """Fetch active, non-expired URL by short code."""
        stmt = select(URL).where(
            URL.short_code == short_code,
            URL.is_active == True,
            (URL.expires_at.is_(None) | (URL.expires_at > sql_func.now()))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_and_url(self, original_url: str, user_id: int) -> URL | None:
        """
        For authenticated users: find an active, non-expired link
        belonging specifically to this user.
        """
        stmt = select(URL).where(
            URL.original_url == original_url,
            URL.user_id == user_id,
            URL.is_active == True,
            (URL.expires_at.is_(None) | (URL.expires_at > sql_func.now()))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_custom_alias(self, custom_alias: str) -> URL | None:
        """Check if a custom alias is already taken globally."""
        stmt = select(URL).where(URL.custom_alias == custom_alias)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_custom_aliases_by_user(self, user_id: int) -> int:
        """
        Count how many custom aliases a user has already created.
        Used to enforce the free tier limit (max 3 custom aliases).
        """
        stmt = select(func.count()).where(
            URL.user_id == user_id,
            URL.custom_alias.is_not(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def create_url(
        self,
        short_code: str,
        original_url: str,
        custom_alias: str | None = None,
        user_id: int | None = None,
        expires_at: datetime | None = None
    ) -> URL:
        """Create a new URL record."""
        new_url = URL(
            short_code=short_code,
            original_url=original_url,
            custom_alias=custom_alias,
            user_id=user_id,
            expires_at=expires_at
        )
        return await self.create(new_url)

    async def update_short_code(self, url_id: int, new_short_code: str) -> None:
        """Update short code after DB generates the ID."""
        stmt = update(URL).where(URL.id == url_id).values(short_code=new_short_code)
        await self.session.execute(stmt)
        await self.session.commit()

    async def increment_clicks(self, short_code: str) -> None:
        """Atomic increment of click counter."""
        stmt = update(URL).where(URL.short_code == short_code).values(clicks=URL.clicks + 1)
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_expired_anonymous_urls(self) -> int:
        """Permanently delete expired anonymous links (for scheduled cleanup)."""
        stmt = delete(URL).where(
            URL.expires_at < sql_func.now(),
            URL.user_id.is_(None)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount
