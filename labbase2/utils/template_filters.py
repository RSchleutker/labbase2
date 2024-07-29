from datetime import date
from datetime import datetime
from zoneinfo import ZoneInfo

from flask_login import current_user


__all__ = ["format_datetime", "user_has_permission"]


def format_date(x: date) -> str:
    if not x:
        return ""

    return x.strftime("%B %d, %Y")


def format_datetime(x: datetime) -> str:
    if not x:
        return ""

    tz = getattr(current_user, "timezone", "Europe/Berlin")

    return x.astimezone(ZoneInfo(tz)).strftime("%B %d, %Y %I:%M %p")


def user_has_permission(*allowed) -> bool:
    if current_user.is_admin:
        return False

    for permission in allowed:
        if current_user.user_has_permission(permission):
            return True

    return False
