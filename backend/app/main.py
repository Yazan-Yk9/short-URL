from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.api.v1 import v1_router
from app.core.config import settings
from app.core.exceptions import (
    URLShortenerException,
    ShortCodeNotFoundException,
    URLExpiredException,
)
from app.db.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables (if dev)
    if settings.ENVIRONMENT == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables initialized.")
    yield
    # Shutdown: Close connections
    await engine.dispose()
    print("🛑 Database connections closed.")


app = FastAPI(
    title="URL Shortener API",
    description="A powerful URL shortening service with anonymous and authenticated features.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# --- Global Exception Handlers ---
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

@app.exception_handler(URLShortenerException)
async def base_url_exception_handler(request, exc: URLShortenerException):
    # Fallback for any other domain exceptions
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message}
    )


# --- Include Routers ---
app.include_router(v1_router, prefix="/api/v1")

# --- Health Check ---
@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}

@app.get("/")
async def root():
    return {
        "message": "Welcome to the URL Shortener API!",
        "docs": "/docs",
        "health": "/health"
    }
