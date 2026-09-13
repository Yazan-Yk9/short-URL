import logging

from fastapi import APIRouter, Depends, status

from app.api.deps import get_auth_service, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Register a new user account."""
    return await auth_service.register(
        email=payload.email,
        password=payload.password,
    )


@router.post("/login", response_model=Token)
async def login(
    payload: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Authenticate and receive JWT access + refresh tokens."""
    return await auth_service.login(
        email=payload.email,
        password=payload.password,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user
