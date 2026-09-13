from sqlalchemy import select

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by email (used for login and duplicate check)."""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        """Fetch a user by primary key."""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, email: str, hashed_password: str) -> User:
        """Create a new user with a pre-hashed password."""
        new_user = User(
            email=email,
            hashed_password=hashed_password,
        )
        return await self.create(new_user)
