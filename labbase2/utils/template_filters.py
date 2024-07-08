from datetime import date
from datetime import datetime


__all__ = ["format_datetime"]


def format_date(x: date) -> str:
    if not x:
        return ""

    return x.strftime("%b %d, %Y")


def format_datetime(x: datetime) -> str:
    if not x:
        return ""

    return x.strftime("%b %d, %Y %-I:%M %p")

