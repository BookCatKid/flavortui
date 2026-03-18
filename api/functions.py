def format_seconds(seconds):
    try:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    except Exception:
        return "0h 0m"
