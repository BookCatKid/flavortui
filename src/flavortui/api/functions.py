from datetime import datetime, timezone


def format_seconds(seconds):
    try:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    except Exception:
        return "0h 0m"


def get_days_ago(utc_time_string):
    return (
        datetime.now(timezone.utc)
        - datetime.fromisoformat(utc_time_string.replace("Z", "+00:00"))
    ).days
