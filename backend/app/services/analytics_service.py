import logging
from typing import Any, Optional
from urllib.parse import urlparse
from fastapi import Request
from user_agents import parse as parse_ua
from app.repositories.analytics_repository import AnalyticsRepository
from app.core.geoip import lookup_country

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Business logic for click tracking and analytics aggregation."""

    VALID_PERIODS = {"7d", "30d", "90d", "1y", "all"}

    def __init__(self, repository: AnalyticsRepository):
        self.repository = repository

    # ============================================================
    # User-Agent & Referer Parsing
    # ============================================================
    @staticmethod
    def parse_user_agent(user_agent_string: Optional[str]) -> dict[str, Optional[str]]:
        if not user_agent_string:
            return {"browser": None, "os": None, "device_type": None, "is_bot": False}

        try:
            ua = parse_ua(user_agent_string)
            if ua.is_bot:
                device_type = "bot"
            elif ua.is_mobile:
                device_type = "mobile"
            elif ua.is_tablet:
                device_type = "tablet"
            elif ua.is_pc:
                device_type = "desktop"
            else:
                device_type = "other"

            return {
                "browser": ua.browser.family or None,
                "os": ua.os.family or None,
                "device_type": device_type,
                "is_bot": ua.is_bot,
            }
        except Exception as e:
            logger.warning(f"Failed to parse User-Agent: {e}")
            return {"browser": None, "os": None, "device_type": None, "is_bot": False}

    @staticmethod
    def extract_referer_domain(referer: Optional[str]) -> str:
        if not referer:
            return "direct"
        try:
            parsed = urlparse(referer)
            return parsed.netloc or "direct"
        except Exception:
            return "direct"

    # ============================================================
    # Click Logging
    # ============================================================
    async def log_click_from_request(
        self,
        request: Request,
        url_id: int,
        short_code: str,
    ) -> None:
        try:
            forwarded = request.headers.get("x-forwarded-for")
            if forwarded:
                ip_address = forwarded.split(",")[0].strip()
            else:
                ip_address = request.client.host if request.client else None

            user_agent_string = request.headers.get("user-agent")
            referer = request.headers.get("referer")

            #Country lookup
            country = lookup_country(ip_address) if ip_address else None

            ua_data = self.parse_user_agent(user_agent_string)

            if ua_data["is_bot"]:
                logger.debug(f"Skipping bot click for {short_code}")
                return

            referer_domain = self.extract_referer_domain(referer)

            await self.repository.log_click(
                url_id=url_id,
                short_code=short_code,
                ip_address=ip_address,
                user_agent=user_agent_string,
                referer=referer_domain,
                browser=ua_data["browser"],
                os=ua_data["os"],
                device_type=ua_data["device_type"],
                country=country,
            )
            logger.debug(f"Click logged for {short_code} from {ip_address} ({country})")
        except Exception as e:
            logger.error(f"Failed to log click for {short_code}: {e}")

    # ============================================================
    # Helpers
    # ============================================================
    def _validate_period(self, period: str) -> str:
        return period if period in self.VALID_PERIODS else "30d"

    @staticmethod
    def _dict_to_distribution_list(data: dict[str, int]) -> list[dict[str, Any]]:
        """Convert {'Chrome': 120, 'Firefox': 30} to [{'name': 'Chrome', 'count': 120}, ...]"""
        return [
            {"name": name, "count": count}
            for name, count in sorted(data.items(), key=lambda x: -x[1])
        ]

    # ============================================================
    # Stats Aggregation
    # ============================================================
    async def get_url_stats(
        self,
        url_id: int,
        short_code: str,
        original_url: str,
        period: str = "30d",
        user_plan: str = "free",
    ) -> dict[str, Any]:
        """Aggregate full stats for a URL, respecting the user's plan."""
        period = self._validate_period(period)

        # Free users: restrict to last 7 days
        if user_plan == "free" and period not in ("7d",):
            period = "7d"

        # Base stats (available to everyone)
        total_clicks = await self.repository.count_clicks(url_id, period)
        unique_visitors = await self.repository.count_unique_visitors(url_id, period)
        daily_clicks = await self.repository.get_daily_clicks(url_id, period)

        # Advanced stats (Pro/Enterprise only)
        is_pro = user_plan in ("pro", "enterprise")

        if is_pro:
            devices_raw = await self.repository.get_distribution_by(url_id, "device_type", period)
            browsers_raw = await self.repository.get_distribution_by(url_id, "browser", period)
            oses_raw = await self.repository.get_distribution_by(url_id, "os", period)

            devices = self._dict_to_distribution_list(devices_raw)
            browsers = self._dict_to_distribution_list(browsers_raw)
            oses = self._dict_to_distribution_list(oses_raw)

            referrers = await self.repository.get_top_referrers(url_id, period, limit=10)
            countries = await self.repository.get_top_countries(url_id, period, limit=10)
            locked_features: list[str] = []
        else:
            devices = None
            browsers = None
            oses = None
            referrers = None
            countries = None
            locked_features = ["devices", "browsers", "oses", "referrers", "countries"]

        return {
            "short_code": short_code,
            "original_url": original_url,
            "period": period,
            "total_clicks": total_clicks,
            "unique_visitors": unique_visitors,
            "daily_clicks": daily_clicks,
            "devices": devices,
            "browsers": browsers,
            "oses": oses,
            "referrers": referrers,
            "countries": countries,
            "locked_features": locked_features,
        }

    async def get_recent_clicks(
        self,
        url_id: int,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        clicks = await self.repository.get_recent_clicks(url_id, limit=limit)
        return [
            {
                "id": c.id,
                "ip_address": c.ip_address,
                "browser": c.browser,
                "os": c.os,
                "device_type": c.device_type,
                "referer": c.referer,
                "country": c.country,
                "clicked_at": c.clicked_at.isoformat(),
            }
            for c in clicks
        ]

    # ============================================================
    # User Dashboard
    # ============================================================
    async def get_user_dashboard(self, user_id: int) -> dict[str, Any]:
        total_clicks = await self.repository.count_total_clicks_by_user(user_id)
        clicks_today = await self.repository.count_clicks_today_by_user(user_id)
        top_links = await self.repository.get_top_links_by_user(user_id, limit=5)

        return {
            "total_clicks": total_clicks,
            "clicks_today": clicks_today,
            "top_links": top_links,
        }
