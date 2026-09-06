import logging
from datetime import datetime, timezone, timedelta

from app.core.constants import ANONYMOUS_URL_EXPIRE_DAYS
from app.core.exceptions import (
    InvalidURLException,
    CustomAliasTakenException,
    AnonymousAliasNotAllowedException,
    CustomAliasLimitExceededException,
)
from app.core.utils import validate_url, generate_unique_short_code_from_id
from app.repositories.url_repository import URLRepository

logger = logging.getLogger(__name__)

class URLService:
    """Core business logic for URL shortening and retrieval."""

    MAX_FREE_CUSTOM_ALIASES = 3

    def __init__(self, repository: URLRepository):
        self.repository = repository

    async def create_short_url(
        self,
        original_url: str,
        user_id: int | None = None,
        custom_alias: str | None = None
    ):

        logger.debug(f"Creating short URL: original={original_url}, user_id={user_id}, alias={custom_alias}")
        # 1. Validate URL format
        if not validate_url(original_url):
            raise InvalidURLException()

        # 2. Authenticated user flow
        if user_id is not None:
            # --- Custom alias provided ---
            if custom_alias:
                # Check alias availability
                existing_alias = await self.repository.get_by_custom_alias(custom_alias)
                if existing_alias:
                    logger.warning(f"Custom alias '{custom_alias}' already taken")
                    raise CustomAliasTakenException(custom_alias)

                # Check free tier limit (max 3)
                current_count = await self.repository.count_custom_aliases_by_user(user_id)
                if current_count >= self.MAX_FREE_CUSTOM_ALIASES:
                    logger.warning(f"User {user_id} exceeded custom alias limit ({current_count})")
                    raise CustomAliasLimitExceededException()

                # Create link with 7-day expiry for trial
                expires_at = datetime.now(timezone.utc) + timedelta(days=ANONYMOUS_URL_EXPIRE_DAYS)
                new_url = await self.repository.create_url(
                    short_code="",
                    original_url=original_url,
                    custom_alias=custom_alias,
                    user_id=user_id,
                    expires_at=expires_at
                )
                # For custom aliases, the short_code IS the alias itself
                await self.repository.update_short_code(new_url.id, custom_alias)
                logger.info(f"Created custom alias link: {custom_alias} for user {user_id}")
                return new_url

            # --- No custom alias: standard shortening ---
            else:
                # Check if this user already shortened this URL
                existing = await self.repository.get_by_user_and_url(original_url, user_id)
                if existing:
                    logger.info(f"Reused existing link for user {user_id}: {existing.short_code}")
                    return existing

                # Create permanent link (no expiry)
                new_url = await self.repository.create_url(
                    short_code="",
                    original_url=original_url,
                    custom_alias=None,
                    user_id=user_id,
                    expires_at=None
                )
                short_code = generate_unique_short_code_from_id(new_url.id)
                await self.repository.update_short_code(new_url.id, short_code)
                logger.info(f"Created permanent link for user {user_id}: {short_code}")
                return new_url

        # 3. Anonymous user flow
        else:
            # Block custom aliases
            if custom_alias:
                logger.warning("Anonymous user attempted to use custom alias")
                raise AnonymousAliasNotAllowedException()

            # Create link with 7-day expiry
            expires_at = datetime.now(timezone.utc) + timedelta(days=ANONYMOUS_URL_EXPIRE_DAYS)
            new_url = await self.repository.create_url(
                short_code="",
                original_url=original_url,
                custom_alias=None,
                user_id=None,
                expires_at=expires_at
            )
            short_code = generate_unique_short_code_from_id(new_url.id)
            await self.repository.update_short_code(new_url.id, short_code)
            logger.info(f"Created anonymous link: {short_code} (expires at {expires_at})")
            return new_url

        # Fallback (should never be reached)
        raise RuntimeError("Unexpected state in create_short_url")

    async def get_original_url(self, short_code: str):
        url_data = await self.repository.get_by_short_code(short_code)
        if not url_data:
            logger.warning(f"Short code not found: {short_code}")
            return None

        # Track clicks only for authenticated users
        if url_data.user_id is not None:
            await self.repository.increment_clicks(short_code)
            logger.debug(f"Incremented clicks for {short_code} (user {url_data.user_id})")
        return url_data
