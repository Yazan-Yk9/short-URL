from fastapi import APIRouter
from app.api.v1.endpoints import urls

# Main router for v1 of the API
v1_router = APIRouter()

# Include URL endpoints
v1_router.include_router(urls.router, prefix="", tags=["URLs"])
