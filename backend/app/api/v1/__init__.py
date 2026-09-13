from fastapi import APIRouter
<<<<<<< HEAD

from app.api.v1.endpoints import api_keys, auth, urls

v1_router = APIRouter()
v1_router.include_router(auth.router)
v1_router.include_router(api_keys.router)
v1_router.include_router(urls.router, tags=["URLs"])
=======
from app.api.v1.endpoints import urls

v1_router = APIRouter()
v1_router.include_router(urls.router, prefix="", tags=["URLs"])
>>>>>>> d2e479d03b956f1d7f60a89bc428ef5d76e7a722
