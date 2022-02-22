def get_ms_from_hms(hms: str) -> int:
    """Convert a duration from HH:MM:SS into ms."""
    hrs, mins, secs = hms.split(":")
    ms = ((int(hrs) * 60 + int(mins)) * 60 + int(secs)) * 1000
    return int(ms)
