from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import ClickAnalytics


class AnalyticsRepository:
    """Data access layer for click analytics."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ============================================================
    # Helper: Period Parsing
    # ============================================================
    @staticmethod
    def period_to_datetime(period: str) -> Optional[datetime]:
        """
        Convert a period string to a starting datetime.
        Returns None for 'all' (no date filtering).
        """
        now = datetime.now(timezone.utc)
        mapping = {
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90),
            "1y": timedelta(days=365),
        }
        if period == "all":
            return None
        delta = mapping.get(period, timedelta(days=30))
        return now - delta

    # ============================================================
    # Write Operations
    # ============================================================
    async def log_click(
        self,
        url_id: int,
        short_code: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referer: Optional[str] = None,
        browser: Optional[str] = None,
        os: Optional[str] = None,
        device_type: Optional[str] = None,
        country: Optional[str] = None,
    ) -> ClickAnalytics:
        """Insert a new click record. Called from background tasks."""
        click = ClickAnalytics(
            url_id=url_id,
            short_code=short_code,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer,
            browser=browser,
            os=os,
            device_type=device_type,
            country=country,
        )
        self.session.add(click)
        await self.session.commit()
        await self.session.refresh(click)
        return click

    # ============================================================
    # Aggregate Stats
    # ============================================================
    async def count_clicks(
        self,
        url_id: int,
        period: str = "30d",
    ) -> int:
        """Total clicks for a specific URL within a period."""
        stmt = select(func.count(ClickAnalytics.id)).where(
            ClickAnalytics.url_id == url_id
        )
        start = self.period_to_datetime(period)
        if start is not None:
            stmt = stmt.where(ClickAnalytics.clicked_at >= start)

        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def count_unique_visitors(
        self,
        url_id: int,
        period: str = "30d",
    ) -> int:
        """Count distinct IP addresses (unique visitors) for a URL."""
        stmt = select(
            func.count(func.distinct(ClickAnalytics.ip_address))
        ).where(
            ClickAnalytics.url_id == url_id,
            ClickAnalytics.ip_address.is_not(None),
        )
        start = self.period_to_datetime(period)
        if start is not None:
            stmt = stmt.where(ClickAnalytics.clicked_at >= start)

        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_daily_clicks(
        self,
        url_id: int,
        period: str = "30d",
    ) -> list[dict[str, Any]]:
        """Return clicks aggregated by day (PostgreSQL date_trunc)."""
        stmt = (
            select(
                func.date_trunc("day", ClickAnalytics.clicked_at).label("day"),
                func.count(ClickAnalytics.id).label("clicks"),
            )
            .where(ClickAnalytics.url_id == url_id)
            .group_by("day")
            .order_by("day")
        )
        start = self.period_to_datetime(period)
        if start is not None:
            stmt = stmt.where(ClickAnalytics.clicked_at >= start)

        result = await self.session.execute(stmt)
        return [
            {"date": row.day.date().isoformat(), "clicks": row.clicks}
            for row in result.all()
        ]

    async def get_distribution_by(
        self,
        url_id: int,
        column_name: str,
        period: str = "30d",
    ) -> dict[str, int]:
        """
        Generic distribution: group by a specific column and count.
        Supported columns: browser, os, device_type, country.
        """
        allowed = {"browser", "os", "device_type", "country"}
        if column_name not in allowed:
            raise ValueError(f"Invalid column: {column_name}")

        column = getattr(ClickAnalytics, column_name)
        stmt = (
            select(column, func.count(ClickAnalytics.id).label("count"))
            .where(ClickAnalytics.url_id == url_id, column.is_not(None))
            .group_by(column)
            .order_by(func.count(ClickAnalytics.id).desc())
        )
        start = self.period_to_datetime(period)
        if start is not None:
            stmt = stmt.where(ClickAnalytics.clicked_at >= start)

        result = await self.session.execute(stmt)
        return {row[0]: row[1] for row in result.all()}

    async def get_top_referrers(
        self,
        url_id: int,
        period: str = "30d",
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Return top referrer sources for a URL."""
        stmt = (
            select(
                ClickAnalytics.referer,
                func.count(ClickAnalytics.id).label("count"),
            )
            .where(
                ClickAnalytics.url_id == url_id,
                ClickAnalytics.referer.is_not(None),
            )
            .group_by(ClickAnalytics.referer)
            .order_by(func.count(ClickAnalytics.id).desc())
            .limit(limit)
        )
        start = self.period_to_datetime(period)
        if start is not None:
            stmt = stmt.where(ClickAnalytics.clicked_at >= start)

        result = await self.session.execute(stmt)
        return [{"referer": row[0], "count": row[1]} for row in result.all()]

    async def get_top_countries(
        self,
        url_id: int,
        period: str = "30d",
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Return top countries for a URL."""
        stmt = (
            select(
                ClickAnalytics.country,
                func.count(ClickAnalytics.id).label("count"),
            )
            .where(
                ClickAnalytics.url_id == url_id,
                ClickAnalytics.country.is_not(None),
            )
            .group_by(ClickAnalytics.country)
            .order_by(func.count(ClickAnalytics.id).desc())
            .limit(limit)
        )
        start = self.period_to_datetime(period)
        if start is not None:
            stmt = stmt.where(ClickAnalytics.clicked_at >= start)

        result = await self.session.execute(stmt)
        return [{"country": row[0], "count": row[1]} for row in result.all()]

    async def get_recent_clicks(
        self,
        url_id: int,
        limit: int = 20,
    ) -> list[ClickAnalytics]:
        """Fetch the most recent N clicks for a URL."""
        stmt = (
            select(ClickAnalytics)
            .where(ClickAnalytics.url_id == url_id)
            .order_by(ClickAnalytics.clicked_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ============================================================
    # User-Level Stats
    # ============================================================
    async def count_total_clicks_by_user(self, user_id: int) -> int:
        """Total clicks across all URLs owned by a user."""
        from app.models.url import URL  # local import to avoid circular deps

        stmt = (
            select(func.count(ClickAnalytics.id))
            .join(URL, URL.id == ClickAnalytics.url_id)
            .where(URL.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def count_clicks_today_by_user(self, user_id: int) -> int:
        """Clicks received today across all URLs owned by a user."""
        from app.models.url import URL

        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        stmt = (
            select(func.count(ClickAnalytics.id))
            .join(URL, URL.id == ClickAnalytics.url_id)
            .where(
                URL.user_id == user_id,
                ClickAnalytics.clicked_at >= today_start,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_top_links_by_user(
        self,
        user_id: int,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Return the user's top links by click count."""
        from app.models.url import URL

        stmt = (
            select(
                URL.short_code,
                URL.original_url,
                func.count(ClickAnalytics.id).label("clicks"),
            )
            .join(ClickAnalytics, ClickAnalytics.url_id == URL.id)
            .where(URL.user_id == user_id)
            .group_by(URL.short_code, URL.original_url)
            .order_by(func.count(ClickAnalytics.id).desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [
            {
                "short_code": row.short_code,
                "original_url": row.original_url,
                "clicks": row.clicks,
            }
            for row in result.all()
        ]
