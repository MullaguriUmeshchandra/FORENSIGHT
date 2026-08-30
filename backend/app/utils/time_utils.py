from datetime import datetime, timezone
from typing import Optional, Union
import dateutil.parser

COMMON_DATE_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y/%m/%d %H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
    "%d-%m-%Y %H:%M:%S",
    "%b %d %H:%M:%S",
    "%d/%b/%Y:%H:%M:%S %z",
    "%a %b %d %H:%M:%S %Y",
]

def parse_forensic_timestamp(val: Union[str, int, float, datetime, None], default_year: Optional[int] = None) -> Optional[datetime]:
    """
    Parse heterogeneous forensic timestamps into UTC timezone-aware datetime.
    Supports ISO-8601, RFC-2822, Unix Epoch (s, ms, us, ns), Syslog, Windows formats.
    Returns None if timestamp cannot be parsed or is invalid.
    """
    if val is None or val == "" or str(val).strip().lower() in ("null", "none", "nan", "nat", "undefined"):
        return None

    if isinstance(val, datetime):
        if val.tzinfo is None:
            return val.replace(tzinfo=timezone.utc)
        return val.astimezone(timezone.utc)

    # Numeric (Unix Epoch)
    if isinstance(val, (int, float)):
        try:
            # Check magnitude: nanoseconds (> 1e18), microseconds (> 1e14), milliseconds (> 1e11), seconds
            if val > 1e17: # Nanoseconds
                secs = val / 1e9
            elif val > 1e13: # Microseconds
                secs = val / 1e6
            elif val > 1e10: # Milliseconds
                secs = val / 1e3
            else: # Seconds
                secs = val
            return datetime.fromtimestamp(secs, tz=timezone.utc)
        except Exception:
            return None

    str_val = str(val).strip()

    # Try numeric string
    try:
        num = float(str_val)
        return parse_forensic_timestamp(num)
    except ValueError:
        pass

    # Try dateutil parser first (very flexible)
    try:
        dt = dateutil.parser.parse(str_val)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt
    except Exception:
        pass

    # Try explicit format fallback
    for fmt in COMMON_DATE_FORMATS:
        try:
            dt = datetime.strptime(str_val, fmt)
            if dt.year == 1900 and default_year:
                dt = dt.replace(year=default_year)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            return dt
        except Exception:
            continue

    return None

def format_iso_utc(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime object into standard ISO 8601 UTC string."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()
