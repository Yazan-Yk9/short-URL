from sqlalchemy.ext.asyncio import AsyncSession

class BaseRepository:
    """Shared CRUD operations for all repositories."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, model_instance):
        """Add, commit, and refresh a model instance."""
        self.session.add(model_instance)
        await self.session.commit()
        await self.session.refresh(model_instance)
        return model_instance

    async def delete(self, model_instance):
        """Delete a model instance permanently."""
        await self.session.delete(model_instance)
        await self.session.commit()
