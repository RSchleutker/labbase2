from typing import Optional

from wtforms.fields import Field
from wtforms.form import Form
from wtforms.validators import ValidationError

__all__ = [
    "ContainsSpecial",
    "ContainsNot",
    "ContainsNumber",
    "AllowCharacters",
    "ContainsLower",
    "ContainsUpper",
    "ContainsNotSpace",
    "AllASCII",
]


class RemoveCharacters:
    """A filter that removes certain characters from a string"""

    def __init__(self, chars: Optional[str] = None):

        self.chars = chars if chars is not None else ""

    def __call__(self, x) -> str:
        return "".join([c for c in x if c not in self.chars])


class AllowCharacters:
    """A validator that checks if only allowed characters are in a string

    Attributes
    ----------
    chars: str
        A string of allowed characters.
    """

    def __init__(self, chars: str):
        self.chars = chars

    def __call__(self, form: Form, field: Field):
        data = field.data

        for char in data:
            if char not in self.chars:
                raise ValidationError(f"'{char}' is not a valid character.")


class ContainsNot:
    """A validator that checks that certain characters do not appear in the
    input

    Attributes
    ----------
    forbidden: str
        A list of strings that are not allowed in the input field.
    message: str, optional
        A message that is returned when validation fails.
    """

    def __init__(self, forbidden: str = None, message: str = None):
        self.forbidden = forbidden
        if not message:
            message = "Forbidden characters: " + ", ".join(self.forbidden)
        self.message = message

    def __call__(self, form: Form, field: Field) -> None:
        data = field.data

        for char in self.forbidden:
            if char in data:
                raise ValidationError(self.message)


class ContainsLower:
    """A validator that checks if at least one lowercase character is in a string"""

    def __init__(self, message: str = None):

        if not message:
            message = "Must contain at least one lowercase letter!"
        self.message = message

    def __call__(self, form: Form, field: Field) -> None:
        data: str = field.data

        for char in data:
            if char.islower():
                return

        raise ValidationError(self.message)


class ContainsUpper:
    """A validator that checks if at least one uppercase character is in a string"""

    def __init__(self, message: str = None):

        if not message:
            message = "Must contain at least one uppercase letter!"
        self.message = message

    def __call__(self, form: Form, field: Field) -> None:
        data: str = field.data

        for char in data:
            if char.isupper():
                return

        raise ValidationError(self.message)


class ContainsNumber:
    """A validator that checks if at least one number is in a string"""

    def __init__(self, message: str = None):

        if not message:
            message = "Must contain at least one number!"
        self.message = message

    def __call__(self, form: Form, field: Field) -> None:
        data: str = field.data

        for char in data:
            if char.isdigit():
                return

        raise ValidationError(self.message)


class ContainsSpecial:
    """A validator that checks if at least one special character is in a string"""

    def __init__(self, message: str = None):

        if not message:
            message = "Must contain at least one special character!"
        self.message = message

    def __call__(self, form: Form, field: Field) -> None:
        data: str = field.data

        for char in data:
            if not char.isalnum():
                return

        raise ValidationError(self.message)


class ContainsNotSpace:
    """A validator that checks that no space is in a string"""

    def __init__(self, message: str = None):

        if not message:
            message = "Must not contain a whitespace character!"
        self.message = message

    def __call__(self, form: Form, field: Field) -> None:
        data: str = field.data

        for char in data:
            if char.isspace():
                raise ValidationError(self.message)


class AllASCII:
    """A validator that checks if all characters are ASCII"""

    def __init__(self, message: str = None):

        if not message:
            message = "Must contain ASCII characters only!"
        self.message = message

    def __call__(self, form: Form, field: Field) -> None:
        data: str = field.data

        for char in data:
            if not char.isascii():
                raise ValidationError(self.message)
