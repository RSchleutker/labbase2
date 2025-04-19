from flask import has_request_context, request, Flask
from flask_login import current_user as user, AnonymousUserMixin
import logging


__all__ = ["init_app", "RequestFormatter"]


def init_app(app: Flask):
    @app.before_request
    def auto_log_request():
        if not request.path.startswith("/static") and not request.path.startswith("/favicon"):
            app.logger.info("%(method)-6s %(path)s", {"method": request.method, "path": request.url})


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        record.user = "Anonymous" if isinstance(user, AnonymousUserMixin) else user.username

        return super().format(record)
