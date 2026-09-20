import pytest

from app.core.geoip import lookup_country, get_reader


def test_geoip_database_exists():
    """GeoIP database must be loadable."""
    reader = get_reader()
    assert reader is not None, "GeoIP database not found. Place GeoLite2-Country.mmdb in app/data/"


def test_lookup_public_ip_us():
    """Google DNS (8.8.8.8) should resolve to US."""
    result = lookup_country("8.8.8.8")
    assert result == "US"


def test_lookup_public_ip_cloudflare():
    """Anycast IPs (1.1.1.1) may or may not resolve depending on the GeoIP DB."""
    result = lookup_country("1.1.1.1")
    # Cloudflare DNS is anycast — not always in the DB. Accept either case.
    assert result is None or (isinstance(result, str) and len(result) == 2)



def test_lookup_private_ip_returns_none():
    """Private IPs should never resolve."""
    assert lookup_country("127.0.0.1") is None
    assert lookup_country("10.0.0.1") is None
    assert lookup_country("192.168.1.1") is None
    assert lookup_country("172.16.0.1") is None


def test_lookup_empty_string():
    """Empty or None IPs should return None."""
    assert lookup_country("") is None
    assert lookup_country(None) is None


def test_lookup_invalid_ip():
    """Malformed IPs should return None without raising."""
    assert lookup_country("not-an-ip") is None
    assert lookup_country("999.999.999.999") is None


def test_lookup_unresolvable_ip():
    """IPs not in the database should return None gracefully."""
    #Never in GeoIP DB
    result = lookup_country("192.0.2.1")
    assert result is None
