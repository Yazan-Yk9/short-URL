from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.analytics_service import AnalyticsService


# ============================================================
# Fixtures
# ============================================================
@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def analytics_service(mock_repository):
    return AnalyticsService(repository=mock_repository)


# ============================================================
# User-Agent Parsing Tests
# ============================================================
def test_parse_user_agent_chrome_desktop():
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    result = AnalyticsService.parse_user_agent(ua)
    assert result["browser"] == "Chrome"
    assert result["os"] == "Windows"
    assert result["device_type"] == "desktop"
    assert result["is_bot"] is False


def test_parse_user_agent_iphone():
    ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1"
    result = AnalyticsService.parse_user_agent(ua)
    assert result["os"] == "iOS"
    assert result["device_type"] == "mobile"
    assert result["is_bot"] is False


def test_parse_user_agent_ipad():
    ua = "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1"
    result = AnalyticsService.parse_user_agent(ua)
    assert result["device_type"] == "tablet"


def test_parse_user_agent_googlebot():
    ua = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    result = AnalyticsService.parse_user_agent(ua)
    assert result["is_bot"] is True
    assert result["device_type"] == "bot"


def test_parse_user_agent_none():
    result = AnalyticsService.parse_user_agent(None)
    assert result["browser"] is None
    assert result["os"] is None
    assert result["device_type"] is None
    assert result["is_bot"] is False


def test_parse_user_agent_empty_string():
    result = AnalyticsService.parse_user_agent("")
    assert result["is_bot"] is False


# ============================================================
# Referer Extraction Tests
# ============================================================
def test_extract_referer_google():
    result = AnalyticsService.extract_referer_domain("https://www.google.com/search?q=test")
    assert result == "www.google.com"


def test_extract_referer_facebook():
    result = AnalyticsService.extract_referer_domain("https://facebook.com/post/123")
    assert result == "facebook.com"


def test_extract_referer_none():
    assert AnalyticsService.extract_referer_domain(None) == "direct"


def test_extract_referer_empty():
    assert AnalyticsService.extract_referer_domain("") == "direct"


def test_extract_referer_invalid():
    assert AnalyticsService.extract_referer_domain("not-a-url") == "direct"


# ============================================================
# Distribution List Conversion Tests
# ============================================================
def test_dict_to_distribution_list_sorted():
    data = {"Chrome": 120, "Firefox": 30, "Safari": 50}
    result = AnalyticsService._dict_to_distribution_list(data)

    assert len(result) == 3
    # Must be sorted descending by count
    assert result[0] == {"name": "Chrome", "count": 120}
    assert result[1] == {"name": "Safari", "count": 50}
    assert result[2] == {"name": "Firefox", "count": 30}


def test_dict_to_distribution_list_empty():
    result = AnalyticsService._dict_to_distribution_list({})
    assert result == []


def test_dict_to_distribution_list_single():
    result = AnalyticsService._dict_to_distribution_list({"Mobile": 5})
    assert result == [{"name": "Mobile", "count": 5}]


# ============================================================
# Period Validation Tests
# ============================================================
def test_validate_period_valid(analytics_service):
    assert analytics_service._validate_period("7d") == "7d"
    assert analytics_service._validate_period("30d") == "30d"
    assert analytics_service._validate_period("90d") == "90d"
    assert analytics_service._validate_period("1y") == "1y"
    assert analytics_service._validate_period("all") == "all"


def test_validate_period_invalid_defaults_to_30d(analytics_service):
    assert analytics_service._validate_period("xyz") == "30d"
    assert analytics_service._validate_period("") == "30d"
    assert analytics_service._validate_period("999") == "30d"


# ============================================================
# get_url_stats Tests (with mocked repository)
# ============================================================
@pytest.mark.asyncio
async def test_get_url_stats_pro_user(analytics_service, mock_repository):
    """Pro users should get all fields populated."""
    mock_repository.count_clicks.return_value = 100
    mock_repository.count_unique_visitors.return_value = 75
    mock_repository.get_daily_clicks.return_value = [
        {"date": "2026-09-20", "clicks": 100}
    ]
    mock_repository.get_distribution_by.side_effect = [
        {"desktop": 70, "mobile": 30},
        {"Chrome": 80, "Firefox": 20},
        {"Windows": 60, "macOS": 40},
    ]
    mock_repository.get_top_referrers.return_value = [{"referer": "google.com", "count": 50}]
    mock_repository.get_top_countries.return_value = [{"country": "SA", "count": 40}]

    result = await analytics_service.get_url_stats(
        url_id=1,
        short_code="abc",
        original_url="https://example.com",
        period="30d",
        user_plan="pro",
    )

    assert result["total_clicks"] == 100
    assert result["unique_visitors"] == 75
    assert result["devices"] is not None
    assert result["browsers"] is not None
    assert result["countries"] is not None
    assert result["locked_features"] == []


@pytest.mark.asyncio
async def test_get_url_stats_free_user(analytics_service, mock_repository):
    """Free users should get base stats only; advanced fields are None."""
    mock_repository.count_clicks.return_value = 100
    mock_repository.count_unique_visitors.return_value = 75
    mock_repository.get_daily_clicks.return_value = []

    result = await analytics_service.get_url_stats(
        url_id=1,
        short_code="abc",
        original_url="https://example.com",
        period="30d",
        user_plan="free",
    )

    assert result["total_clicks"] == 100
    assert result["period"] == "7d"  # Force-restricted for free
    assert result["devices"] is None
    assert result["browsers"] is None
    assert result["oses"] is None
    assert result["referrers"] is None
    assert result["countries"] is None
    assert set(result["locked_features"]) == {
        "devices", "browsers", "oses", "referrers", "countries"
    }


@pytest.mark.asyncio
async def test_get_url_stats_free_user_period_forced(analytics_service, mock_repository):
    """Free users requesting '30d' get forced to '7d'."""
    mock_repository.count_clicks.return_value = 10
    mock_repository.count_unique_visitors.return_value = 5
    mock_repository.get_daily_clicks.return_value = []

    result = await analytics_service.get_url_stats(
        url_id=1,
        short_code="abc",
        original_url="https://example.com",
        period="90d",
        user_plan="free",
    )

    assert result["period"] == "7d"


# ============================================================
# get_user_dashboard Tests
# ============================================================
@pytest.mark.asyncio
async def test_get_user_dashboard(analytics_service, mock_repository):
    mock_repository.count_total_clicks_by_user.return_value = 500
    mock_repository.count_clicks_today_by_user.return_value = 25
    mock_repository.get_top_links_by_user.return_value = [
        {"short_code": "abc", "original_url": "https://a.com", "clicks": 200},
    ]

    result = await analytics_service.get_user_dashboard(user_id=1)

    assert result["total_clicks"] == 500
    assert result["clicks_today"] == 25
    assert len(result["top_links"]) == 1


# ============================================================
# get_recent_clicks Tests
# ============================================================
@pytest.mark.asyncio
async def test_get_recent_clicks(analytics_service, mock_repository):
    from datetime import datetime, timezone
    from app.models.analytics import ClickAnalytics

    fake_click = ClickAnalytics(
        id=1,
        url_id=1,
        short_code="abc",
        ip_address="1.2.3.4",
        browser="Chrome",
        os="Windows",
        device_type="desktop",
        referer="google.com",
        country="US",
        clicked_at=datetime(2026, 9, 20, 12, 0, tzinfo=timezone.utc),
    )
    mock_repository.get_recent_clicks.return_value = [fake_click]

    result = await analytics_service.get_recent_clicks(url_id=1, limit=20)

    assert len(result) == 1
    assert result[0]["browser"] == "Chrome"
    assert result[0]["country"] == "US"
    assert "clicked_at" in result[0]
