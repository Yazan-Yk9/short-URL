import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from app.api.deps import get_url_service, get_user_from_jwt_or_api_key

from app.core.exceptions import (
    AnonymousAliasNotAllowedException,
    CustomAliasLimitExceededException,
    CustomAliasTakenException,
    InvalidURLException,
)
from app.models.user import User
from app.schemas.url import URLCreate, URLResponse
from app.services.url_service import URLService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/shorten", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
async def shorten_url(
    payload: URLCreate,
    current_user: User | None = Depends(get_user_from_jwt_or_api_key),
    service: URLService = Depends(get_url_service),
):
    """Shorten a URL. Anonymous users get 7-day links; authenticated users get permanent links."""
    try:
        result = await service.create_short_url(
            original_url=str(payload.original_url),
            user_id=current_user.id if current_user else None,
            custom_alias=payload.custom_alias,
        )
        if result is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Service returned None")
        return result
    except InvalidURLException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except CustomAliasTakenException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except AnonymousAliasNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
    except CustomAliasLimitExceededException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@router.get("/{short_code}", status_code=status.HTTP_302_FOUND)
async def redirect_to_original(
    short_code: str,
    service: URLService = Depends(get_url_service),
):
    """Redirect to the original URL. Clicks are tracked for authenticated owners only."""
    url_data = await service.get_original_url(short_code)
    if not url_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short code not found or expired.")
    return RedirectResponse(url=url_data.original_url, status_code=status.HTTP_302_FOUND)