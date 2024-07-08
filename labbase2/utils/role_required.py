from flask import request
from flask import flash
from flask import redirect
from flask_login import current_user
from functools import wraps

from typing import Callable


__all__ = ["role_required"]


def role_required(roles: list) -> Callable:
    """Check whether the current user has sufficient role to access a ressource.

    This is a very simple decorator op to add user role system to the
    website.

    Parameters
    ----------
    roles : list of str
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

    allowed_roles = set(roles) | {"Admin"}

    def decorator(func: Callable):

        @wraps(func)
        def decorated_view(*args, **kwargs):
            has_roles = {r.name for r in current_user.roles}

            # Check if allowed and actual roles have non-empty intersection.
            if "admin" in has_roles or (allowed_roles & has_roles):
                return func(*args, **kwargs)
            else:
                flash("No permission to enter this site!", "warning")
                return redirect(request.referrer), 403

        return decorated_view

    return decorator
