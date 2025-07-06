from functools import wraps
from typing import Callable

from flask import current_app as app
from flask import flash, redirect, url_for
from flask_login import current_user

from labbase2.database import db
from labbase2.models import Permission

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

            if current_user.is_admin:
                return func(*args, **kwargs)

            for name in allowed:
                permission = db.session.get(Permission, name)
                if not permission:
                    app.logger.debug("No such permission: %s", name)
                elif current_user.has_permission(permission):
                    return func(*args, **kwargs)

            flash("No permission to enter this site!", "warning")
            return redirect(url_for("base.index"))

        return decorated_view

    return decorator
