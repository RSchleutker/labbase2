from datetime import date, datetime
from typing import Optional
from zoneinfo import ZoneInfo

from flask_login import current_user

__all__ = ["format_date", "format_datetime"]


def format_date(x: Optional[date] = None) -> str:
    """Format a date for HTML templates

    Parameters
    ----------
    x: Optional[date]
        A date or `None`.

    Returns
    -------
    str
        An empty string if `x` was empty, otherwise a date in the format
        September 04, 2025.
    """

    if not x:
        return ""

    return x.strftime("%B %d, %Y")


def format_datetime(x: Optional[datetime] = None) -> str:
    """Format a datetime for HTML templates

    Parameters
    ----------
    x: Optional[date]
        A datetime or `None`.

    Returns
    -------
    str
        An empty string if `x` was empty, otherwise a datetime in the format
        September 04, 2025 11:45 PM.
    """

    if not x:
        return ""

    tz = getattr(current_user, "timezone", "Europe/Berlin")

    return x.astimezone(ZoneInfo(tz)).strftime("%B %d, %Y %I:%M %p")
