from enum import Enum
from typing import Any


class Message(Enum):
    """
    An Enum for different message types.
    """

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "danger"

    def __init__(self, cls: str):
        self.div = '<div class="alert alert-' + cls + '">{msg}</div>'

    def __call__(self, msg: Any) -> str:
        """Show message in a custom DIV block.

        Parameters
        ----------
        msg : Any
            The message that should be wrapped into an alert DIV. This must be a str or
            must be convertible to a str.

        Returns
        -------
        str
            A str that display the message in a custom DIV block.
        """

        return self.div.format(msg=msg)
