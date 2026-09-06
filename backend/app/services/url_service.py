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


class URLService:
    """Core business logic for URL shortening and retrieval."""

    # Maximum allowed custom aliases for free users
    MAX_FREE_CUSTOM_ALIASES = 3

    def __init__(self, repository: URLRepository):
        self.repository = repository

    async def create_short_url(
        self,
        original_url: str,
        user_id: int | None = None,
        custom_alias: str | None = None
    ):
        """
        Creates a shortened URL based on user authentication status and input.
        - Anonymous: auto-generated, expires in 7 days, no tracking.
        - Authenticated + no alias: returns existing or creates permanent.
        - Authenticated + alias: enforces 3-alias limit, expires in 7 days (trial).
        """
        # 1. Validate URL format (redundant safety check, though Schema already does it)
        if not validate_url(original_url):
            raise InvalidURLException()

        # ------------------------------------------------------------
        # 2. CASE: Authenticated User (user_id is provided)
        # ------------------------------------------------------------
        if user_id is not None:

            # --- Sub-case A: Custom Alias provided ---
            if custom_alias:
                # a. Check if alias is already taken globally
                existing_alias = await self.repository.get_by_custom_alias(custom_alias)
                if existing_alias:
                    raise CustomAliasTakenException(custom_alias)

                # b. Check user's current custom alias count
                current_count = await self.repository.count_custom_aliases_by_user(user_id)
                if current_count >= self.MAX_FREE_CUSTOM_ALIASES:
                    raise CustomAliasLimitExceededException()

                # c. Create new link with custom alias
                expires_at = datetime.now(timezone.utc) + timedelta(days=ANONYMOUS_URL_EXPIRE_DAYS)
                new_url = await self.repository.create_url(
                    short_code="",  # Placeholder, we'll use custom_alias as short_code
                    original_url=original_url,
                    custom_alias=custom_alias,
                    user_id=user_id,
                    expires_at=expires_at
                )
                # For custom aliases, the short_code IS the alias itself
                await self.repository.update_short_code(new_url.id, custom_alias)
                return new_url

            # --- Sub-case B: No custom alias (Standard shortening) ---
            else:
                # Check if this user already shortened this URL
                existing = await self.repository.get_by_user_and_url(original_url, user_id)
                if existing:
                    return existing

                # Create permanent link for authenticated user
                new_url = await self.repository.create_url(
                    short_code="",
                    original_url=original_url,
                    custom_alias=None,
                    user_id=user_id,
                    expires_at=None
                )
                # Generate Base58 short code from the DB-generated ID
                short_code = generate_unique_short_code_from_id(new_url.id)
                await self.repository.update_short_code(new_url.id, short_code)
                return new_url

        # ------------------------------------------------------------
        # 3. CASE: Anonymous User (user_id is None)
        # ------------------------------------------------------------
        else:
            # a. Block custom aliases entirely for anonymous users
            if custom_alias:
                raise AnonymousAliasNotAllowedException()

            # b. No duplicate check. Always create a new link with 7-day expiry.
            expires_at = datetime.now(timezone.utc) + timedelta(days=ANONYMOUS_URL_EXPIRE_DAYS)
            new_url = await self.repository.create_url(
                short_code="",
                original_url=original_url,
                custom_alias=None,
                user_id=None,
                expires_at=expires_at
            )
            # Generate Base58 short code from the DB-generated ID
            short_code = generate_unique_short_code_from_id(new_url.id)
            await self.repository.update_short_code(new_url.id, short_code)
            return new_url

    async def get_original_url(self, short_code: str):
        """
        Retrieves the original URL for redirection.
        Increments click counter ONLY if the link belongs to a registered user.
        """
        url_data = await self.repository.get_by_short_code(short_code)
        if not url_data:
            return None

        # Track clicks only for authenticated users (user_id is not None)
        if url_data.user_id is not None:
            await self.repository.increment_clicks(short_code)

        return url_data
