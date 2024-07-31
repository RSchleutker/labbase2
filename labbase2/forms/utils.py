from typing import Optional

from labbase2.utils.message import Message

__all__ = ["errors2messages"]


def errors2messages(field_errors: Optional[dict[str, str]]) -> list[str]:
    """Turns field errors of forms into a list of error messages.

    Parameters
    ----------
    field_errors : Optional[dict[str, str]]
        A dictionary of errors as produced by the `errors` property of forms. If the
        form was not validated yet, this property will be `None`, in which case this
        function will return an empty list.

    Returns
    -------
    list[str]
        A list of HTML-formatted error messages produced by successive calls to
        `Message.ERROR`. A list entry is created for each error in each form field.
        If the form was not validated yet, the list will be empty.
    """

    messages: list[str] = []

    if field_errors is None:
        return messages

    for field, errors in field_errors.items():
        for error in errors:
            messages.append(Message.ERROR(f"{field}: {error}"))

    return messages
