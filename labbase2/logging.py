import logging

from flask import Flask, has_request_context, request
from flask_login import AnonymousUserMixin
from flask_login import current_user as user

__all__ = ["init_app", "RequestFormatter"]


def init_app(app: Flask):
    """Initialize logging with the current app

    Parameters
    ----------
    app: Flask
        A flask app to initialize.

    Returns
    -------
    None
    """

    @app.before_request
    def auto_log_request():
        if not request.path.startswith("/static") and not request.path.startswith("/favicon"):
            app.logger.info(
                "%(method)-6s %(path)s", {"method": request.method, "path": request.url}
            )


class RequestFormatter(logging.Formatter):
    """Customized logging formatter to inject flask request information"""

    def format(self, record: logging.LogRecord):
        """Inject request information to logging messages and format that message

        Parameters
        ----------
        record: logging.LogRecord
            A LogRecord instance.

        Returns
        -------
        str
            A formatted log message.
        """

        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.user = "Anonymous" if isinstance(user, AnonymousUserMixin) else user.username
        else:
            record.url = None
            record.remote_addr = None
            record.user = "Anonymous"

        return super().format(record)
