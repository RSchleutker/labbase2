from labbase2.models import Permission

from flask import request
from flask import flash
from flask import redirect
from flask import url_for
from flask_login import current_user
from functools import wraps

from typing import Callable


__all__ = ["permission_required"]


def permission_required(*allowed) -> Callable:
    """Check whether the current user has sufficient role to access a ressource.

    This is a very simple decorator op to add user role system to the
    website.

    Parameters
    ----------
    *allowed : list of str
        A list of roles that are allowe to access the page. Available roles
        are currently 'guest', 'viewer', 'editor', and 'admin'.

    Returns
    -------
    function
        The decorate route op.

    Notes
    -----
    The user roles are not hierachical. This means that if a guest is allowed to
    view a ressource it does not follow that an editor is allowed to do so as
    well. Instead, you have to explicitly state all roles that are allowed to
    view the resource.
    """

    def decorator(func: Callable):

        @wraps(func)
        def decorated_view(*args, **kwargs):

            verified = []

            for permission in allowed:
                permission_db = Permission.query.get(permission)
                if permission_db is None:
                    flash(f"Permission '{permission}' not found. Please inform the developer!",
                        "warning")
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
