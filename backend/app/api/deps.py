import logging
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.url_repository import URLRepository
from app.services.url_service import URLService

logger = logging.getLogger(__name__)

async def get_url_service(
    db: AsyncSession = Depends(get_db),
) -> URLService:
    repository = URLRepository(db)
    service = URLService(repository)
    logger.debug("URLService instance created")
    return service
