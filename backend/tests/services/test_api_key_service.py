from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import (
    ApiKeyLimitExceededException,
    ApiKeyNotFoundException,
    InvalidApiKeyException,
    QuotaExceededException,
)
from app.models.api_key import ApiKey
from app.models.user import User
from app.services.api_key_service import ApiKeyService


@pytest.fixture
def mock_api_key_repository():
    return AsyncMock()


@pytest.fixture
def api_key_service(mock_api_key_repository):
    return ApiKeyService(repository=mock_api_key_repository)


@pytest.fixture
def free_user():
    return User(
        id=1, email="user@example.com", hashed_password="x",
        plan="free", is_active=True, api_calls_limit=100, api_calls_used=0,
    )


@pytest.mark.asyncio
async def test_create_key_success(api_key_service, mock_api_key_repository, free_user):
    mock_api_key_repository.count_active_by_user.return_value = 0
    new_key = ApiKey(
        id=1, user_id=1, key_hash="hash", key_prefix="sk_live_abc",
        name="test", is_active=True, created_at=datetime.now(timezone.utc),
    )
    mock_api_key_repository.create_key.return_value = new_key

    raw_key, api_key = await api_key_service.create_key(user=free_user, name="test", is_live=True)

    assert raw_key.startswith("sk_live_") or raw_key.startswith("ark_live_")
    assert api_key.name == "test"
    mock_api_key_repository.create_key.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_key_limit_exceeded(api_key_service, mock_api_key_repository, free_user):
    # Free plan allows only 1 key
    mock_api_key_repository.count_active_by_user.return_value = 1

    with pytest.raises(ApiKeyLimitExceededException):
        await api_key_service.create_key(user=free_user, name="another", is_live=True)


@pytest.mark.asyncio
async def test_verify_key_success(api_key_service, mock_api_key_repository, free_user):
    api_key = ApiKey(
        id=1, user_id=1, key_hash="hash", key_prefix="sk_live_abc",
        name="test", is_active=True, user=free_user,
    )
    mock_api_key_repository.get_by_hash_with_user.return_value = api_key

    result = await api_key_service.verify_key("sk_live_somekey")

    assert result.id == free_user.id
    mock_api_key_repository.update_last_used.assert_awaited_once()


@pytest.mark.asyncio
async def test_verify_key_invalid(api_key_service, mock_api_key_repository):
    mock_api_key_repository.get_by_hash_with_user.return_value = None

    with pytest.raises(InvalidApiKeyException):
        await api_key_service.verify_key("sk_live_invalid")


@pytest.mark.asyncio
async def test_verify_key_inactive(api_key_service, mock_api_key_repository, free_user):
    api_key = ApiKey(
        id=1, user_id=1, key_hash="hash", key_prefix="sk_live_abc",
        name="test", is_active=False, user=free_user,
    )
    mock_api_key_repository.get_by_hash_with_user.return_value = api_key

    with pytest.raises(InvalidApiKeyException):
        await api_key_service.verify_key("sk_live_inactive")


@pytest.mark.asyncio
async def test_verify_key_quota_exceeded(api_key_service, mock_api_key_repository):
    user_with_quota = User(
        id=1, email="user@example.com", hashed_password="x",
        plan="free", is_active=True, api_calls_limit=100, api_calls_used=100,
    )
    api_key = ApiKey(
        id=1, user_id=1, key_hash="hash", key_prefix="sk_live_abc",
        name="test", is_active=True, user=user_with_quota,
    )
    mock_api_key_repository.get_by_hash_with_user.return_value = api_key

    with pytest.raises(QuotaExceededException):
        await api_key_service.verify_key("sk_live_valid")


@pytest.mark.asyncio
async def test_revoke_key_success(api_key_service, mock_api_key_repository):
    mock_api_key_repository.deactivate.return_value = True

    await api_key_service.revoke_key(key_id=1, user_id=1)

    mock_api_key_repository.deactivate.assert_awaited_once_with(1, 1)


@pytest.mark.asyncio
async def test_revoke_key_not_found(api_key_service, mock_api_key_repository):
    mock_api_key_repository.deactivate.return_value = False

    with pytest.raises(ApiKeyNotFoundException):
        await api_key_service.revoke_key(key_id=999, user_id=1)
