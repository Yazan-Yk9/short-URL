import pytest
from app.core.exceptions import (
    # Core
    URLShortenerException,
    InvalidURLException,
    # URL-related
    ShortCodeNotFoundException,
    CustomAliasTakenException,
    URLExpiredException,
    InvalidShortCodeFormatException,
    AnonymousAliasNotAllowedException,
    CustomAliasLimitExceededException,
    # User/Auth
    UserAlreadyExistsException,
    InvalidCredentialsException,
    InvalidTokenException,
    # API Keys
    ApiKeyNotFoundException,
    InvalidApiKeyException,
    ApiKeyLimitExceededException,
    QuotaExceededException,
)


def test_short_code_not_found_exception_context():
    # Must store the short_code for logging/debugging purposes
    exc = ShortCodeNotFoundException("abc123")
    assert exc.short_code == "abc123"
    assert "abc123" in str(exc)


def test_custom_alias_taken_exception_context():
    exc = CustomAliasTakenException("myalias")
    assert exc.alias == "myalias"
    assert "myalias" in str(exc)


def test_url_expired_exception_context():
    exc = URLExpiredException("xyz789")
    assert exc.short_code == "xyz789"
    assert "xyz789" in str(exc)


def test_invalid_short_code_format_exception_context():
    exc = InvalidShortCodeFormatException("bad@code")
    assert exc.short_code == "bad@code"


def test_invalid_url_exception_default_message():
    exc = InvalidURLException()
    assert exc.message == "Invalid URL. Must start with http:// or https://"


def test_custom_exceptions_inherit_base():
    # All domain exceptions must inherit from the base exception
    assert isinstance(InvalidURLException(), URLShortenerException)
    assert isinstance(ShortCodeNotFoundException("x"), URLShortenerException)
    assert isinstance(CustomAliasTakenException("x"), URLShortenerException)
    assert isinstance(URLExpiredException("x"), URLShortenerException)
    assert isinstance(InvalidShortCodeFormatException("x"), URLShortenerException)

def test_user_already_exists_exception_context():
    exc = UserAlreadyExistsException("test@example.com")
    assert exc.email == "test@example.com"
    assert "test@example.com" in str(exc)


def test_invalid_credentials_exception_default_message():
    exc = InvalidCredentialsException()
    assert "Invalid email or password" in exc.message


def test_invalid_token_exception_default_message():
    exc = InvalidTokenException()
    assert "Invalid or expired token" in exc.message


def test_api_key_not_found_exception():
    exc = ApiKeyNotFoundException()
    assert "not found" in exc.message.lower()


def test_invalid_api_key_exception():
    exc = InvalidApiKeyException()
    assert "Invalid" in exc.message


def test_api_key_limit_exceeded_exception():
    exc = ApiKeyLimitExceededException()
    assert "Maximum" in exc.message


def test_quota_exceeded_exception():
    exc = QuotaExceededException()
    assert "quota" in exc.message.lower()


def test_anonymous_alias_exception_default():
    exc = AnonymousAliasNotAllowedException()
    assert "registered users" in exc.message


def test_custom_alias_limit_exception_default():
    exc = CustomAliasLimitExceededException()
    assert "3" in exc.message
