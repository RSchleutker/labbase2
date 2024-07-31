from datetime import date, datetime
from typing import Optional
from zoneinfo import ZoneInfo

from flask_login import current_user

__all__ = ["format_date", "format_datetime"]


def format_date(x: Optional[date] = None) -> str:
    if not x:
        return ""

    return x.strftime("%B %d, %Y")


def format_datetime(x: Optional[datetime] = None) -> str:
    if not x:
        return ""

    tz = getattr(current_user, "timezone", "Europe/Berlin")

    return x.astimezone(ZoneInfo(tz)).strftime("%B %d, %Y %I:%M %p")
