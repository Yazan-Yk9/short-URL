import pytest
from app.core.exceptions import (
    URLShortenerException,
    InvalidURLException,
    ShortCodeNotFoundException,
    CustomAliasTakenException,
    URLExpiredException,
    InvalidShortCodeFormatException,
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
