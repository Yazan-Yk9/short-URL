from datetime import timedelta
import pytest
from jwt.exceptions import ExpiredSignatureError

from app.core.security import (
    create_access_token,
    decode_access_token,
    create_refresh_token,
    InvalidTokenException,
)
from app.core.config import settings


def test_create_and_decode_access_token():
    # Valid token must be decodable and contain the original data
    test_data = {"sub": "test_user@example.com", "role": "admin"}
    token = create_access_token(test_data)

    decoded = decode_access_token(token)
    assert decoded["sub"] == test_data["sub"]
    assert decoded["role"] == test_data["role"]


def test_decode_access_token_invalid_signature():
    # Tampered tokens or wrong secret must raise InvalidTokenException
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0.invalid_signature"
    with pytest.raises(InvalidTokenException):
        decode_access_token(invalid_token)


def test_decode_access_token_expired():
    # Token with negative expiration delta must be rejected as expired
    test_data = {"sub": "test_user"}
    expired_token = create_access_token(test_data, expires_delta=timedelta(seconds=-1))

    with pytest.raises(InvalidTokenException):
        decode_access_token(expired_token)


def test_create_refresh_token_contains_type():
    # Refresh token must include 'type' claim for distinction
    test_data = {"sub": "test_user"}
    token = create_refresh_token(test_data)

    decoded = decode_access_token(token)  # Uses same decode logic
    assert decoded["type"] == "refresh"
    assert decoded["sub"] == test_data["sub"]
