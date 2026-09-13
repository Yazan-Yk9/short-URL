from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models.url import URL
from app.models.user import User
from app.models.api_key import ApiKey
