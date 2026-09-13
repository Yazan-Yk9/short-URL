from sqlalchemy.orm import declarative_base

<<<<<<< HEAD
Base = declarative_base()
=======
# Central base class for all ORM models.
Base = declarative_base()

# Import all models here so Alembic and SQLAlchemy can discover them.
from app.models.url import URL
>>>>>>> d2e479d03b956f1d7f60a89bc428ef5d76e7a722
