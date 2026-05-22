# File: app/utils/timezone_helpers.py
from datetime import datetime, timezone, timedelta

def get_current_utc_time() -> datetime:
    """
    Always use UTC for server operations and database persistence.
    Prevents temporal anomalies when serving clients across multiple time zones.
    """
    return datetime.now(timezone.utc)

def convert_utc_to_local_indonesia(utc_dt: datetime, region: str = "WIB") -> str:
    """
    Converts a UTC datetime object to standard Indonesian local time zones.
    Supported regions: 'WIB' (UTC+7), 'WITA' (UTC+8), 'WIT' (UTC+9).
    """
    timezone_offsets = {
        "WIB": 7,
        "WITA": 8,
        "WIT": 9
    }
    
    offset_hours = timezone_offsets.get(region.upper(), 7) # Default to WIB if unrecognized
    
    local_dt = utc_dt + timedelta(hours=offset_hours)
    
    # Mengembalikan format string yang rapi untuk ditampilkan di UI Command Center
    return local_dt.strftime("%Y-%m-%d %H:%M:%S")