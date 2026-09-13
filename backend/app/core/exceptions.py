from typing import Optional

class URLShortenerException(Exception):
    """Base class for all domain-specific exceptions."""
    pass


# ============================================================
# URL-related Exceptions
# ============================================================
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
    def __init__(self, message: str = "Custom aliases are only available for registered users. Please sign up."):
        self.message = message
        super().__init__(self.message)

class CustomAliasLimitExceededException(URLShortenerException):
    def __init__(self, message: str = "Maximum of 3 custom aliases reached. Upgrade to Pro for unlimited aliases."):
        self.message = message
        super().__init__(self.message)


# ============================================================
# User / Auth Exceptions
# ============================================================
class UserAlreadyExistsException(URLShortenerException):
    def __init__(self, email: str, message: Optional[str] = None):
        self.email = email
        self.message = message or f"User with email '{email}' already exists."
        super().__init__(self.message)


class InvalidCredentialsException(URLShortenerException):
    def __init__(self, message: str = "Invalid email or password."):
        self.message = message
        super().__init__(self.message)


class InvalidTokenException(URLShortenerException):
    def __init__(self, message: str = "Invalid or expired token."):
        self.message = message
        super().__init__(self.message)


# ============================================================
# API Key Exceptions
# ============================================================
class ApiKeyNotFoundException(URLShortenerException):
    def __init__(self, message: str = "API key not found or does not belong to you."):
        self.message = message
        super().__init__(self.message)


class InvalidApiKeyException(URLShortenerException):
    def __init__(self, message: str = "Invalid or inactive API key."):
        self.message = message
        super().__init__(self.message)


class ApiKeyLimitExceededException(URLShortenerException):
    def __init__(self, message: str = "Maximum number of API keys reached for your plan."):
        self.message = message
        super().__init__(self.message)


class QuotaExceededException(URLShortenerException):
    def __init__(self, message: str = "Monthly API quota exceeded. Upgrade your plan."):
        self.message = message
        super().__init__(self.message)
