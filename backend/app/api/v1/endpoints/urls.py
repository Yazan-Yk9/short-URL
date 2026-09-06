from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from app.api.deps import get_url_service
from app.core.exceptions import (
    InvalidURLException,
    ShortCodeNotFoundException,
    CustomAliasTakenException,
    AnonymousAliasNotAllowedException,
    CustomAliasLimitExceededException,
    URLExpiredException,
)
from app.schemas.url import URLCreate, URLResponse
from app.services.url_service import URLService

router = APIRouter()


@router.post(
    "/shorten",
    response_model=URLResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Shorten a URL",
    description="Accepts a long URL and returns a short code. Authentication is simulated via `user_id` for now."
)
async def shorten_url(
    payload: URLCreate,
    service: URLService = Depends(get_url_service),
):
    """
    Create a shortened URL.
    - **Anonymous** (user_id not provided): Auto-generated code, expires in 7 days.
    - **Authenticated** (user_id provided): Permanent link, or custom alias (max 3, expires in 7 days).
    """
    try:
        # Hardcoded user_id = 1 for testing (to simulate authenticated user)
        # Later, this will come from JWT token. For now, you can set user_id=None to test anonymous.
        # To test authenticated flow, pass user_id=1. To test anonymous, pass user_id=None.
        # I'll add a query parameter or header later, but for now I'll just use a placeholder.
        # Let's allow the user to pass `user_id` as a query param for testing ease? 
        # We'll just hardcode it to 1 for demo, but you can modify as needed.
        # I'll update the code to accept `user_id` from a header or query param.
        # For simplicity in this milestone, I'll assume user_id=1 if not specified? No, let's keep it explicit.
        # We will read user_id from a query param `x-user-id` temporarily.
        pass
    except Exception as e:
        # This will be caught by the global handler, but we keep basic handling here.
        raise


# We need a way to pass user_id. Since Auth isn't built yet, we'll use a Header.
# Let's create a dependency to extract user_id from a header (for testing).
# I will modify the function to use a Header parameter.

from fastapi import Header

@router.post("/shorten", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
async def shorten_url(
    payload: URLCreate,
    x_user_id: int | None = Header(None, description="Temporary header to simulate authenticated user (e.g., 1)"),
    service: URLService = Depends(get_url_service),
):
    """
    Create a shortened URL.
    - **Anonymous**: No `X-User-Id` header provided -> expires in 7 days, no custom alias allowed.
    - **Authenticated**: Provide `X-User-Id` header -> custom alias allowed (max 3, expires in 7 days) or permanent link.
    """
    try:
        result = await service.create_short_url(
            original_url=str(payload.original_url),
            user_id=x_user_id,
            custom_alias=payload.custom_alias,
        )
        return result
    except InvalidURLException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except CustomAliasTakenException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except AnonymousAliasNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
    except CustomAliasLimitExceededException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@router.get(
    "/{short_code}",
    status_code=status.HTTP_302_FOUND,
    summary="Redirect to original URL",
    description="Fetches the original URL by short code and redirects."
)
async def redirect_to_original(
    short_code: str,
    service: URLService = Depends(get_url_service),
):
    """
    Redirects to the original URL.
    - Clicks are counted ONLY if the link belongs to a registered user.
    - Expired or inactive links return 410 Gone.
    """
    try:
        url_data = await service.get_original_url(short_code)
        if not url_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short code not found or expired.")
        
        # If the link is expired (should have been filtered, but double-check)
        # Note: Service's get_by_short_code already filters by expiry, so it won't return expired links.
        return RedirectResponse(url=url_data.original_url, status_code=status.HTTP_302_FOUND)
    except ShortCodeNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except URLExpiredException as e:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=e.message)
