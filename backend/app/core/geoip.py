import logging
from pathlib import Path
from typing import Optional

import geoip2.database
import geoip2.errors

logger = logging.getLogger(__name__)

_DB_PATH = Path(__file__).parent.parent / "data" / "GeoLite2-Country.mmdb"
_reader: Optional[geoip2.database.Reader] = None


def get_reader() -> Optional[geoip2.database.Reader]:
    """Lazy-load the GeoIP database reader."""
    global _reader
    if _reader is None:
        if not _DB_PATH.exists():
            logger.warning(f"GeoIP database not found at {_DB_PATH}. Country lookup disabled.")
            return None
        try:
            _reader = geoip2.database.Reader(str(_DB_PATH))
            logger.info("GeoIP database loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load GeoIP database: {e}")
            return None
    return _reader


def close_reader() -> None:
    """Close the reader on app shutdown."""
    global _reader
    if _reader is not None:
        _reader.close()
        _reader = None
        logger.info("GeoIP reader closed.")


def lookup_country(ip: str) -> Optional[str]:
    """Return ISO country code (e.g., 'US', 'SA') for an IP, or None."""
    if not ip:
        return None

    # Skip private / local IPs
    if ip.startswith(("127.", "10.", "192.168.", "172.16.", "::1")):
        return None

    reader = get_reader()
    if reader is None:
        return None

    try:
        response = reader.country(ip)
        return response.country.iso_code
    except geoip2.errors.AddressNotFoundError:
        return None
    except Exception as e:
        logger.warning(f"GeoIP lookup failed for {ip}: {e}")
        return None
