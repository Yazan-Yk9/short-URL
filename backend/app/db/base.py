from sqlalchemy.orm import declarative_base

# Central base class for all ORM models.
Base = declarative_base()

# Import all models here so Alembic and SQLAlchemy can discover them.
from app.models.url import URL
