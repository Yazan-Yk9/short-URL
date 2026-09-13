import logging

from app.core.exceptions import UserAlreadyExistsException, InvalidCredentialsException
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class AuthService:
    """Business logic for user authentication."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register(self, email: str, password: str):
        existing = await self.user_repository.get_by_email(email)
        if existing:
            raise UserAlreadyExistsException(email)

        hashed = hash_password(password)
        user = await self.user_repository.create_user(email=email, hashed_password=hashed)
        logger.info(f"New user registered: {email}")
        return user

    async def login(self, email: str, password: str):
        user = await self.user_repository.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()

        token_data = {"sub": str(user.id), "email": user.email, "plan": user.plan}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        logger.info(f"User logged in: {email}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
