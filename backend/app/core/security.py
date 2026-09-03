from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

import jwt
from jwt.exceptions import PyJWTError

from app.core.config import settings
from app.core.exceptions import URLShortenerException

class InvalidTokenException(URLShortenerException):
    pass

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except PyJWTError as e:
        raise InvalidTokenException(f"Invalid or expired token: {str(e)}")

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Generates a long-lived token; includes 'type' claim to distinguish from access tokens."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
