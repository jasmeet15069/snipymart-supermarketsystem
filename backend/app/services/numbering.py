from datetime import datetime


def make_number(prefix: str) -> str:
    return f"{prefix}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
