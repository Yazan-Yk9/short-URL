from typing import Optional

class URLShortenerException(Exception):
    """Base domain exception for all application-specific errors."""
    pass

class InvalidURLException(URLShortenerException):
    def __init__(self, message: str = "Invalid URL. Must start with http:// or https://"):
        self.message = message
        super().__init__(self.message)

class ShortCodeNotFoundException(URLShortenerException):
    def __init__(self, short_code: str, message: Optional[str] = None):
        self.short_code = short_code
        self.message = message or f"Short code '{short_code}' not found."
        super().__init__(self.message)

class CustomAliasTakenException(URLShortenerException):
    def __init__(self, alias: str, message: Optional[str] = None):
        self.alias = alias
        self.message = message or f"Custom alias '{alias}' is already taken."
        super().__init__(self.message)

class URLExpiredException(URLShortenerException):
    def __init__(self, short_code: str, message: Optional[str] = None):
        self.short_code = short_code
        self.message = message or f"Short code '{short_code}' has expired."
        super().__init__(self.message)

class InvalidShortCodeFormatException(URLShortenerException):
    def __init__(self, short_code: str, message: Optional[str] = None):
        self.short_code = short_code
        self.message = message or f"Short code '{short_code}' contains invalid characters."
        super().__init__(self.message)

class AnonymousAliasNotAllowedException(URLShortenerException):
    """Raised when an anonymous user tries to use a custom alias."""
    def __init__(self, message: str = "Custom aliases are only available for registered users. Please sign up."):
        self.message = message
        super().__init__(self.message)

class CustomAliasLimitExceededException(URLShortenerException):
    """Raised when a free user exceeds the maximum of 3 custom aliases."""
    def __init__(self, message: str = "Maximum of 3 custom aliases reached. Upgrade to Pro for unlimited aliases."):
        self.message = message
        super().__init__(self.message)
