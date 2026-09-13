from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import InvalidCredentialsException, UserAlreadyExistsException
from app.models.user import User
from app.services.auth_service import AuthService


@pytest.fixture
def mock_user_repository():
    """Mock the UserRepository for isolated service testing."""
    return AsyncMock()


@pytest.fixture
def auth_service(mock_user_repository):
    return AuthService(user_repository=mock_user_repository)


@pytest.mark.asyncio
async def test_register_success(auth_service, mock_user_repository):
    mock_user_repository.get_by_email.return_value = None
    new_user = User(
        id=1, email="new@example.com", hashed_password="hashed",
        plan="free", is_active=True, api_calls_limit=100, api_calls_used=0,
    )
    mock_user_repository.create_user.return_value = new_user

    result = await auth_service.register(email="new@example.com", password="Password123")

    assert result.email == "new@example.com"
    mock_user_repository.create_user.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_duplicate_email(auth_service, mock_user_repository):
    existing = User(id=1, email="existing@example.com", hashed_password="x")
    mock_user_repository.get_by_email.return_value = existing

    with pytest.raises(UserAlreadyExistsException) as exc_info:
        await auth_service.register(email="existing@example.com", password="Password123")

    assert "existing@example.com" in str(exc_info.value)


@pytest.mark.asyncio
async def test_login_success(auth_service, mock_user_repository):
    from app.core.security import hash_password
    hashed = hash_password("CorrectPassword123")
    user = User(
        id=1, email="user@example.com", hashed_password=hashed,
        plan="free", is_active=True, api_calls_limit=100, api_calls_used=0,
    )
    mock_user_repository.get_by_email.return_value = user

    result = await auth_service.login(email="user@example.com", password="CorrectPassword123")

    assert "access_token" in result
    assert "refresh_token" in result
    assert result["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(auth_service, mock_user_repository):
    from app.core.security import hash_password
    hashed = hash_password("CorrectPassword123")
    user = User(id=1, email="user@example.com", hashed_password=hashed, plan="free", is_active=True)
    mock_user_repository.get_by_email.return_value = user

    with pytest.raises(InvalidCredentialsException):
        await auth_service.login(email="user@example.com", password="WrongPassword")


@pytest.mark.asyncio
async def test_login_user_not_found(auth_service, mock_user_repository):
    mock_user_repository.get_by_email.return_value = None

    with pytest.raises(InvalidCredentialsException):
        await auth_service.login(email="ghost@example.com", password="Password123")
