import logging
from fastapi import APIRouter, Depends, HTTPException, status, Header
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

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/shorten", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
async def shorten_url(
    payload: URLCreate,
    x_user_id: int | None = Header(None, description="Temporary header to simulate authenticated user (e.g., 1)"),
    service: URLService = Depends(get_url_service),
):
    logger.debug(f"shorten_url called with original_url={payload.original_url}, x_user_id={x_user_id}, custom_alias={payload.custom_alias}")
    try:
        result = await service.create_short_url(
            original_url=str(payload.original_url),
            user_id=x_user_id,
            custom_alias=payload.custom_alias,
        )
        logger.debug(f"Result from service: {result}")
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Service returned None unexpectedly"
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get(
    "/{short_code}",
    status_code=status.HTTP_302_FOUND,
    summary="Redirect to original URL",
)
async def redirect_to_original(
    short_code: str,
    service: URLService = Depends(get_url_service),
):
    print(f"DEBUG: redirect_to_original called with short_code={short_code}")  # <-- إضافة
    try:
        url_data = await service.get_original_url(short_code)
        if not url_data:
            print("DEBUG: URL not found or expired")  # <-- إضافة
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short code not found or expired.")
        print(f"DEBUG: Redirecting to {url_data.original_url}")  # <-- إضافة
        return RedirectResponse(url=url_data.original_url, status_code=status.HTTP_302_FOUND)
    except Exception as e:
        print(f"DEBUG: Unexpected exception in redirect: {type(e).__name__}: {str(e)}")  # <-- إضافة
        raise
