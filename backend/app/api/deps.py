from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.url_repository import URLRepository
from app.services.url_service import URLService


async def get_url_service(
    db: AsyncSession = Depends(get_db),
) -> URLService:
    """
    Dependency that provides a new URLService instance per request.
    Injects the database session into the repository, and the repository into the service.
    """
    repository = URLRepository(db)
    return URLService(repository)
