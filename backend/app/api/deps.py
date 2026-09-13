<<<<<<< HEAD
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InvalidTokenException,
    InvalidApiKeyException,
    QuotaExceededException,
)
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.api_key_repository import ApiKeyRepository
from app.repositories.url_repository import URLRepository
from app.repositories.user_repository import UserRepository
from app.services.api_key_service import ApiKeyService
from app.services.auth_service import AuthService
from app.services.url_service import URLService


# Extracts 'Authorization: Bearer <token>' (optional, no auto-error)
bearer_scheme = HTTPBearer(auto_error=False)


# ============================================================
# Service Factories
# ============================================================
async def get_url_service(db: AsyncSession = Depends(get_db)) -> URLService:
    return URLService(URLRepository(db))


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


async def get_api_key_service(db: AsyncSession = Depends(get_db)) -> ApiKeyService:
    return ApiKeyService(ApiKeyRepository(db))


# ============================================================
# JWT Authentication
# ============================================================
async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Mandatory JWT authentication. Raises 401 if missing or invalid."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)
    except InvalidTokenException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = await UserRepository(db).get_by_id(int(user_id))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    return user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Optional JWT authentication. Returns None for anonymous users."""
    if credentials is None:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        if user_id is None:
            return None
        user = await UserRepository(db).get_by_id(int(user_id))
        return user if user and user.is_active else None
    except InvalidTokenException:
        return None


# ============================================================
# Unified Authentication (JWT OR API Key)
# ============================================================
async def get_user_from_jwt_or_api_key(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """
    Unified authentication for endpoints that accept BOTH:
    - Web users via JWT (Authorization: Bearer)
    - Developers via API Key (X-API-Key)

    Returns None only if neither is provided (allows anonymous access).
    Raises 401 if a credential is provided but invalid.
    Raises 429 if API quota exceeded.
    """
    # Priority 1: JWT (web users)
    if credentials is not None:
        try:
            payload = decode_access_token(credentials.credentials)
            if payload.get("type") == "access":
                user_id = payload.get("sub")
                if user_id:
                    user = await UserRepository(db).get_by_id(int(user_id))
                    if user and user.is_active:
                        return user
        except InvalidTokenException:
            pass  # Fall through to check API key
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Priority 2: API Key (developer access)
    if x_api_key is not None:
        service = ApiKeyService(ApiKeyRepository(db))
        try:
            return await service.verify_key(x_api_key)
        except InvalidApiKeyException:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
        except QuotaExceededException:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="API quota exceeded")


    return None
=======
import logging
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.url_repository import URLRepository
from app.services.url_service import URLService

logger = logging.getLogger(__name__)

async def get_url_service(
    db: AsyncSession = Depends(get_db),
) -> URLService:
    repository = URLRepository(db)
    service = URLService(repository)
    logger.debug("URLService instance created")
    return service
>>>>>>> d2e479d03b956f1d7f60a89bc428ef5d76e7a722
