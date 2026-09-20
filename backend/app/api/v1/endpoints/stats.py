import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_analytics_service, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.url_repository import URLRepository
from app.schemas.analytics import (
    RecentClickResponse,
    URLStatsResponse,
    UserDashboardResponse,
)
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stats", tags=["Analytics"])


# ============================================================
# GET /stats/me — User Dashboard
# ============================================================
@router.get("/me", response_model=UserDashboardResponse)
async def get_my_dashboard(
    current_user: User = Depends(get_current_user),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """Aggregated stats across all URLs owned by the current user."""
    return await analytics.get_user_dashboard(current_user.id)


# ============================================================
# GET /stats/{short_code} — Full URL Stats
# ============================================================
@router.get("/{short_code}", response_model=URLStatsResponse)
async def get_url_stats(
    short_code: str,
    period: str = Query("30d", description="7d, 30d, 90d, 1y, or all"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """Full analytics for a specific URL. Only the owner can access."""
    repo = URLRepository(db)
    url = await repo.get_by_short_code(short_code)

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short code not found.",
        )

    if url.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this URL's stats.",
        )

    return await analytics.get_url_stats(
        url_id=url.id,
        short_code=url.short_code,
        original_url=url.original_url,
        period=period,
        user_plan=current_user.plan,
    )


# ============================================================
# GET /stats/{short_code}/clicks — Recent Clicks
# ============================================================
@router.get("/{short_code}/clicks", response_model=list[RecentClickResponse])
async def get_recent_clicks(
    short_code: str,
    limit: int = Query(20, ge=1, le=100, description="Number of clicks (1-100)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """Recent individual clicks for a specific URL."""
    repo = URLRepository(db)
    url = await repo.get_by_short_code(short_code)

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short code not found.",
        )

    if url.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this URL's stats.",
        )

    return await analytics.get_recent_clicks(url_id=url.id, limit=limit)
