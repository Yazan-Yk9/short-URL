from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.api.v1 import v1_router
from app.core.config import settings
from app.core.exceptions import (
    URLShortenerException,
    ShortCodeNotFoundException,
    URLExpiredException,
    CustomAliasTakenException,
    AnonymousAliasNotAllowedException,
    CustomAliasLimitExceededException,
    InvalidURLException,
)
from app.db.base import Base
from app.db.session import engine
from app.core.logging import setup_logging

setup_logging()

# ============================================================
# Lifespan: creates tables on startup, closes connections on shutdown
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.ENVIRONMENT == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables initialized.")
    yield
    await engine.dispose()
    print("🛑 Database connections closed.")


# ============================================================
# FastAPI app instance
# ============================================================
app = FastAPI(
    title="URL Shortener API",
    description="A powerful URL shortening service with anonymous and authenticated features.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ============================================================
# Global exception handlers for domain-specific exceptions
# ============================================================
@app.exception_handler(ShortCodeNotFoundException)
async def short_code_not_found_handler(request, exc: ShortCodeNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message, "short_code": exc.short_code}
    )


@app.exception_handler(URLExpiredException)
async def url_expired_handler(request, exc: URLExpiredException):
    return JSONResponse(
        status_code=status.HTTP_410_GONE,
        content={"detail": exc.message, "short_code": exc.short_code}
    )


@app.exception_handler(CustomAliasTakenException)
async def custom_alias_taken_handler(request, exc: CustomAliasTakenException):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message}
    )


@app.exception_handler(AnonymousAliasNotAllowedException)
async def anonymous_alias_not_allowed_handler(request, exc: AnonymousAliasNotAllowedException):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": exc.message}
    )


@app.exception_handler(CustomAliasLimitExceededException)
async def custom_alias_limit_exceeded_handler(request, exc: CustomAliasLimitExceededException):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": exc.message}
    )


@app.exception_handler(InvalidURLException)
async def invalid_url_handler(request, exc: InvalidURLException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message}
    )


@app.exception_handler(URLShortenerException)
async def base_url_exception_handler(request, exc: URLShortenerException):
    # Fallback for any other domain exceptions
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message}
    )


# ============================================================
# Include v1 API router
# ============================================================
app.include_router(v1_router, prefix="/api/v1")


# ============================================================
# Basic endpoints: health check and root
# ============================================================
@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


@app.get("/")
async def root():
    return {
        "message": "Welcome to the URL Shortener API!",
        "docs": "/docs",
        "health": "/health",
    }
