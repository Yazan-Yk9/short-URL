import pytest
from app.core.utils import (
    encode_base58,
    decode_base58,
    validate_url,
    validate_short_code_format,
    generate_unique_short_code_from_id,
)
from app.core.exceptions import InvalidShortCodeFormatException


def test_encode_base58_zero():
    # Base58 alphabet starts with '1'
    assert encode_base58(0) == "1"


def test_encode_base58_positive_numbers():
    assert encode_base58(58) == "21"
    assert encode_base58(100) == "2j"


def test_decode_base58_consistency():
    # Encoding then decoding must return the original number
    numbers = [0, 1, 58, 999, 10**6, 58**6 - 1]
    for num in numbers:
        encoded = encode_base58(num)
        decoded = decode_base58(encoded)
        assert decoded == num


def test_decode_base58_invalid_characters():
    # Characters outside Base58 set must raise our custom exception
    with pytest.raises(InvalidShortCodeFormatException):
        decode_base58("hello!")
    with pytest.raises(InvalidShortCodeFormatException):
        decode_base58("0OIl")  # Contains excluded characters


def test_validate_url_valid():
    assert validate_url("https://example.com") is True
    assert validate_url("http://localhost:8000/path") is True
    assert validate_url("http://127.0.0.1") is True


def test_validate_url_invalid():
    assert validate_url("ftp://example.com") is False
    assert validate_url("not-a-url") is False
    assert validate_url("http://") is False
    assert validate_url("") is False


def test_validate_short_code_format():
    # Only Base58 characters (excluding 0, O, I, l) are valid
    assert validate_short_code_format("1A2B3C") is True
    assert validate_short_code_format("abc123") is True
    assert validate_short_code_format("ABC") is True
    assert validate_short_code_format("0") is False   # Zero not allowed
    assert validate_short_code_format("O") is False   # Capital O not allowed
    assert validate_short_code_format("l") is False   # Lowercase L not allowed
    assert validate_short_code_format("") is False


def test_generate_unique_short_code_from_id_length():
    # Ensures padding creates uniform 6-character codes
    code = generate_unique_short_code_from_id(1, length=6)
    assert len(code) == 6
    # ID 1 -> Base58 = "2", left padded with '1' => "111112"
    assert code == "111112"


def test_generate_unique_short_code_from_id_truncation():
    # Very large IDs are truncated to the exact length if longer
    huge_id = 58**10  # Far beyond 6 characters
    code = generate_unique_short_code_from_id(huge_id, length=6)
    assert len(code) == 6
