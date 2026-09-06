from fastapi import APIRouter
from app.api.v1.endpoints import urls

v1_router = APIRouter()
v1_router.include_router(urls.router, prefix="", tags=["URLs"])
