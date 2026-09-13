from fastapi import APIRouter
from app.api.v1.endpoints import api_keys, auth, urls

v1_router = APIRouter()
v1_router.include_router(auth.router)
v1_router.include_router(api_keys.router)
v1_router.include_router(urls.router, tags=["URLs"])