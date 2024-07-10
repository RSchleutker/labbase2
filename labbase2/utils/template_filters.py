from datetime import date
from datetime import datetime
from zoneinfo import ZoneInfo

from flask_login import current_user


__all__ = ["format_datetime"]


def format_date(x: date) -> str:
    if not x:
        return ""

    return x.strftime("%b %d, %Y")


def format_datetime(x: datetime) -> str:
    if not x:
        return ""

    tz = getattr(current_user, "tz", "Europe/Berlin")

    return x.astimezone(ZoneInfo(tz)).strftime("%b %d, %Y %-I:%M %p")

