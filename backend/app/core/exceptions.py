from typing import Optional

<<<<<<< HEAD

class URLShortenerException(Exception):
    """Base class for all domain-specific exceptions."""
    pass


# ============================================================
# URL-related Exceptions
# ============================================================
=======
class URLShortenerException(Exception):
    """Base domain exception for all application-specific errors."""
    pass

>>>>>>> d2e479d03b956f1d7f60a89bc428ef5d76e7a722
class InvalidURLException(URLShortenerException):
    def __init__(self, message: str = "Invalid URL. Must start with http:// or https://"):
        self.message = message
        super().__init__(self.message)

<<<<<<< HEAD

=======
>>>>>>> d2e479d03b956f1d7f60a89bc428ef5d76e7a722
class ShortCodeNotFoundException(URLShortenerException):
    def __init__(self, short_code: str, message: Optional[str] = None):
        self.short_code = short_code
        self.message = message or f"Short code '{short_code}' not found."
        super().__init__(self.message)

<<<<<<< HEAD

=======
>>>>>>> d2e479d03b956f1d7f60a89bc428ef5d76e7a722
class CustomAliasTakenException(URLShortenerException):
    def __init__(self, alias: str, message: Optional[str] = None):
        self.alias = alias
        self.message = message or f"Custom alias '{alias}' is already taken."
        super().__init__(self.message)

<<<<<<< HEAD

=======
>>>>>>> d2e479d03b956f1d7f60a89bc428ef5d76e7a722
class URLExpiredException(URLShortenerException):
    def __init__(self, short_code: str, message: Optional[str] = None):
        self.short_code = short_code
        self.message = message or f"Short code '{short_code}' has expired."
        super().__init__(self.message)

<<<<<<< HEAD

=======
>>>>>>> d2e479d03b956f1d7f60a89bc428ef5d76e7a722
class InvalidShortCodeFormatException(URLShortenerException):
    def __init__(self, short_code: str, message: Optional[str] = None):
        self.short_code = short_code
        self.message = message or f"Short code '{short_code}' contains invalid characters."
        super().__init__(self.message)

<<<<<<< HEAD

class AnonymousAliasNotAllowedException(URLShortenerException):
=======
class AnonymousAliasNotAllowedException(URLShortenerException):
    """Raised when an anonymous user tries to use a custom alias."""
>>>>>>> d2e479d03b956f1d7f60a89bc428ef5d76e7a722
    def __init__(self, message: str = "Custom aliases are only available for registered users. Please sign up."):
        self.message = message
        super().__init__(self.message)

<<<<<<< HEAD

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
=======
class CustomAliasLimitExceededException(URLShortenerException):
    """Raised when a free user exceeds the maximum of 3 custom aliases."""
    def __init__(self, message: str = "Maximum of 3 custom aliases reached. Upgrade to Pro for unlimited aliases."):
        self.message = message
        super().__init__(self.message)
>>>>>>> d2e479d03b956f1d7f60a89bc428ef5d76e7a722
