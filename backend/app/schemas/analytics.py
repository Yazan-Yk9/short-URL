from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# Sub-models (Building Blocks)
# ============================================================
class DailyClicks(BaseModel):
    """A single day's click count."""
    date: str = Field(..., description="Date in ISO format (YYYY-MM-DD)")
    clicks: int = Field(..., description="Number of clicks on this day")


class DistributionItem(BaseModel):
    """A single item in a distribution (e.g., device, browser)."""
    name: str
    count: int


class ReferrerStat(BaseModel):
    """A referrer source and its click count."""
    referer: str
    count: int


class CountryStat(BaseModel):
    """A country code and its click count."""
    country: str
    count: int


class TopLink(BaseModel):
    """A link in the user's top-links list."""
    short_code: str
    original_url: str
    clicks: int


# ============================================================
# Full URL Stats Response
# ============================================================
class URLStatsResponse(BaseModel):
    """Complete analytics for a single URL. Advanced fields are Pro-only."""
    short_code: str
    original_url: str
    period: str = Field(..., description="7d, 30d, 90d, 1y, or all")
    total_clicks: int
    unique_visitors: int
    daily_clicks: list[DailyClicks]

    # Pro/Enterprise features (null for free users)
    devices: Optional[list[DistributionItem]] = None
    browsers: Optional[list[DistributionItem]] = None
    oses: Optional[list[DistributionItem]] = None
    referrers: Optional[list[ReferrerStat]] = None
    countries: Optional[list[CountryStat]] = None

    # Indicates which features are locked for the current plan
    locked_features: list[str] = Field(default_factory=list)


# ============================================================
# Recent Clicks
# ============================================================
class RecentClickResponse(BaseModel):
    """A single click record (recent clicks list)."""
    id: int
    ip_address: Optional[str]
    browser: Optional[str]
    os: Optional[str]
    device_type: Optional[str]
    referer: Optional[str]
    country: Optional[str]
    clicked_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# User Dashboard
# ============================================================
class UserDashboardResponse(BaseModel):
    """Aggregated stats for the user's dashboard."""
    total_clicks: int
    clicks_today: int
    top_links: list[TopLink]
