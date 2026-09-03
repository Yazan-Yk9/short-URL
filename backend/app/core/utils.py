import re
from urllib.parse import urlparse

#TODO fix it
from app.core.constants import BASE58_ALPHABET, REGEX_SHORT_CODE_PATTERN
from app.core.exceptions import InvalidShortCodeFormatException

def encode_base58(num: int) -> str:
    if num == 0:
        return BASE58_ALPHABET[0]
    encoded = []
    base = len(BASE58_ALPHABET)
    while num > 0:
        num, remainder = divmod(num, base)
        encoded.append(BASE58_ALPHABET[remainder])
    return ''.join(reversed(encoded))

def decode_base58(short_code: str) -> int:
    if not short_code:
        raise ValueError("Cannot decode an empty string")
    decoded = 0
    base = len(BASE58_ALPHABET)
    for char in short_code:
        if char not in BASE58_ALPHABET:
            raise InvalidShortCodeFormatException(short_code)
        decoded = decoded * base + BASE58_ALPHABET.index(char)
    return decoded

def validate_url(url: str) -> bool:
    """Validates scheme and netloc only; does not check DNS or existence."""
    if not url:
        return False
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False

def validate_short_code_format(short_code: str) -> bool:
    """Fast pre-validation to reject invalid chars before hitting the DB."""
    return bool(short_code and re.match(REGEX_SHORT_CODE_PATTERN, short_code))

def generate_unique_short_code_from_id(id: int, length: int = 6) -> str:
    """
    Left-pads with '1' to ensure uniform code length.
    Uniform length improves index performance and user experience.
    """
    encoded = encode_base58(id)
    if len(encoded) >= length:
        return encoded[:length]
    padding_char = BASE58_ALPHABET[0]
    return padding_char * (length - len(encoded)) + encoded
