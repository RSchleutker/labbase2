
from labbase2.utils.message import Message
from wtforms.validators import ValidationError


RENDER_KW: dict = {'class': 'form-control form-control-sm'}

RENDER_KW_ID: dict = {
    **RENDER_KW,
    'readonly': 'true',
    'placeholder': 'Internal ID'
}

RENDER_KW_BTN: dict = {
    **RENDER_KW,
    'class': 'btn btn-primary mb-2'
}

RENDER_KW_FILE: dict = {
    **RENDER_KW,
    'class': 'custom-filepath-input',
    'type': 'file'
}

# Certain characters are not allowed in genotypes. Most of them if not all
# because they are used internally (e.g. as special strings in search queries).
FORBIDDEN_CHARS: list = [
    '/',
    '==',
    '((',
    '))'
]


class ContainsNot:
    """A validator that checks that certain characters do not appear in the
    input.

    Attributes
    ----------
    forbidden: list of str
        A list of strings that are not allowed in the input field.
    message: str
        A message that is returned when validation fails.
    """

    def __init__(self, forbidden: list = None, message: str = None):
        """Initialization code.

        Parameters
        ----------
        forbidden: list of str
            A list of strings that are not allowed in the input field.
        message: str
            A message that is returned when validation fails.
        """

        self.forbidden = forbidden
        if not message:
            message = 'Forbidden characters: ' + ', '.join(self.forbidden)
        self.message = message

    def __call__(self, form, field) -> None:
        """Test if a field is valid.

        Parameters
        ----------
        form
        field

        Returns
        -------
        None
            If the field does not fulfil the criteria an error is risen.
        """

        data = field.data

        for char in self.forbidden:
            if char in data:
                raise ValidationError(self.message)


class RemoveCharacters:

    def __init__(self, chars: str):

        self.chars = chars

    def __call__(self, x) -> str:
        return ''.join([c for c in x if c not in self.chars])


class AllowCharacters:

    def __init__(self, chars: str):
        self.chars = chars

    def __call__(self, x: str) -> str:
        return ''.join([c for c in x if c in self.chars])


def err2message(errors: dict) -> str:
    messages = []
    for field, error in errors.items():
        messages.append(Message.ERROR(f"<b>{field}</b> {error}"))

    return "<br>".join(messages)
