from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

import jwt
from jwt.exceptions import PyJWTError
<<<<<<< HEAD
from pwdlib import PasswordHash

from app.core.config import settings
from app.core.exceptions import URLShortenerException, InvalidTokenException

import hashlib
import secrets

password_hash = PasswordHash.recommended()

API_KEY_PREFIX_LIVE = "ark_live_"
API_KEY_PREFIX_TEST = "ark_test_"


def generate_api_key(is_live: bool = True) -> tuple[str, str, str]:
    """
    Generate a new API key.
    Returns: (raw_key, key_hash, key_prefix)
    - raw_key: shown to user ONCE (never stored in plaintext)
    - key_hash: stored in DB for verification
    - key_prefix: first 13 chars, safe to display
    """
    prefix = API_KEY_PREFIX_LIVE if is_live else API_KEY_PREFIX_TEST
    random_part = secrets.token_urlsafe(32)
    raw_key = f"{prefix}{random_part}"
    key_hash = hash_api_key(raw_key)
    key_prefix = raw_key[:13]  # e.g., 'ark_live_Ab1x'
    return raw_key, key_hash, key_prefix


def hash_api_key(raw_key: str) -> str:
    """Hash an API key using SHA-256 for fast verification."""
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()



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
=======

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
>>>>>>> d2e479d03b956f1d7f60a89bc428ef5d76e7a722
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except PyJWTError as e:
        raise InvalidTokenException(f"Invalid or expired token: {str(e)}")

<<<<<<< HEAD

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Generate a long-lived refresh token with a distinct 'type' claim."""
=======
def create_refresh_token(data: Dict[str, Any]) -> str:
    """Generates a long-lived token; includes 'type' claim to distinguish from access tokens."""
>>>>>>> d2e479d03b956f1d7f60a89bc428ef5d76e7a722
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
