from flask import has_request_context, request
from flask_login import current_user
import logging


__all__ = ["RequestFormatter"]

class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.user = current_user.username
        else:
            record.url = None
            record.remote_addr = None
            record.user = "Anonymous"

        return super().format(record)
