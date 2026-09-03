from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseSettings):
    DATABASE_URL: str

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL must start with 'postgresql+asyncpg://'")
        return v

class RedisSettings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"

class SecuritySettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        # Prevents accidental deployment with the default insecure key
        if v in ["change-me", "your-super-secret-key-change-this-in-production"]:
            raise ValueError("SECRET_KEY is too weak. Please change it in the .env file")
        return v

class AppSettings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    BASE_URL: str = "http://localhost:8000"
    SHORT_CODE_LENGTH: int = 6

class Settings(DatabaseSettings, RedisSettings, SecuritySettings, AppSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
