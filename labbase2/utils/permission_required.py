from functools import wraps
from typing import Callable

from flask import flash, redirect, url_for
from flask_login import current_user
from labbase2.models import db, Permission

__all__ = ["permission_required"]


def permission_required(*allowed) -> Callable:
    """Check whether the current user has sufficient role to access a resource.

    This is a very simple decorator op to add user role system to the
    website.

    Parameters
    ----------
    *allowed : *str
        A list of permissions. If the user has any of these permissions, he will be
        granted access to the view.

    Returns
    -------
    function
        The decorate route function.
    """

    def decorator(func: Callable):

        @wraps(func)
        def decorated_view(*args, **kwargs):

            verified = []

            for permission in allowed:
                permission_db = db.session.get(Permission, permission)
                if permission_db is None:
                    flash(
                        f"Permission '{permission}' not found." f"Please inform the developer!",
                        "warning",
                    )
                else:
                    verified.append(permission_db)

            # Check if allowed and actual roles have non-empty intersection.
            if current_user.is_admin:
                return func(*args, **kwargs)

            if not verified:
                flash("No valid permissions defined for this site!", "danger")
                return redirect(url_for("base.index"))

            for permission in current_user.permissions:
                if permission in verified:
                    return func(*args, **kwargs)

            flash("No permission to enter this site!", "warning")
            return redirect(url_for("base.index"))

        return decorated_view

    return decorator
