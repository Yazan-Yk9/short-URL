from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

import jwt
from jwt.exceptions import PyJWTError
from pwdlib import PasswordHash

from app.core.config import settings
from app.core.exceptions import URLShortenerException, InvalidTokenException


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plain-text password using the recommended algorithm (bcrypt/argon2)."""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate a short-lived JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT. Raises InvalidTokenException if invalid/expired."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except PyJWTError as e:
        raise InvalidTokenException(f"Invalid or expired token: {str(e)}")


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Generate a long-lived refresh token with a distinct 'type' claim."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
