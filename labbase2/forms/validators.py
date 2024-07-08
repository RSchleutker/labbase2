from wtforms.form import Form
from wtforms.fields import Field
from wtforms.validators import ValidationError


__all__ = ["ContainsSpecial", "ContainsNot", "ContainsNumber",
           "ContainsLower", "ContainsUpper", "ContainsNotSpace", "AllASCII"]


class ContainsNot:
    """A validator that checks that certain characters do not appear in the
    input.

    Attributes
    ----------
    forbidden: list[str]
        A list of strings that are not allowed in the input field.
    message: str, optional
        A message that is returned when validation fails.
    """

    def __init__(self, forbidden: list = None, message: str = None):
        self.forbidden = forbidden
        if not message:
            message = "Forbidden characters: " + ", ".join(self.forbidden)
        self.message = message

    def __call__(self, form: Form, field: Field) -> None:
        """Test if a field contains valid data.

        Parameters
        ----------
        form : Form
            The form, from which this validator is called.
        field : Field
            The field, of which the data shall be validated.

        Returns
        -------
        None

        Raises
        ------
        ValidationError if any forbidden character appears in the input field
        data.
        """

        data = field.data

        for char in self.forbidden:
            if char in data:
                raise ValidationError(self.message)


class ContainsLower:
    """

    """

    def __init__(self, message: str = None):

        if not message:
            message = "Must contain at least one lowercase letter!"
        self.message = message

    def __call__(self, form: Form, field: Field) -> None:
        """Test if a field contains valid data.

        Parameters
        ----------
        form : Form
            The form, from which this validator is called.
        field : Field
            The field, of which the data shall be validated.

        Returns
        -------
        None

        Raises
        ------
        ValidationError if no character in the field data is lowercase.
        """

        data: str = field.data

        for char in data:
            if char.islower():
                return

        raise ValidationError(self.message)


class ContainsUpper:
    """

    """

    def __init__(self, message: str = None):

        if not message:
            message = "Must contain at least one uppercase letter!"
        self.message = message

    def __call__(self, form: Form, field: Field) -> None:
        """Test if a field contains valid data.

        Parameters
        ----------
        form : Form
            The form, from which this validator is called.
        field : Field
            The field, of which the data shall be validated.

        Returns
        -------
        None

        Raises
        ------
        ValidationError if no character in the field data is uppercase.
        """

        data: str = field.data

        for char in data:
            if char.isupper():
                return

        raise ValidationError(self.message)


class ContainsNumber:
    """

    """

    def __init__(self, message: str = None):

        if not message:
            message = "Must contain at least one number!"
        self.message = message

    def __call__(self, form: Form, field: Field) -> None:
        """Test if a field contains valid data.

        Parameters
        ----------
        form : Form
            The form, from which this validator is called.
        field : Field
            The field, of which the data shall be validated.

        Returns
        -------
        None

        Raises
        ------
        ValidationError if no character in the field data is a number.
        """

        data: str = field.data

        for char in data:
            if char.isdigit():
                return

        raise ValidationError(self.message)


class ContainsSpecial:
    """

    """

    def __init__(self, message: str = None):

        if not message:
            message = "Must contain at least one special character!"
        self.message = message

    def __call__(self, form: Form, field: Field) -> None:
        """Test if a field contains valid data.

        Parameters
        ----------
        form : Form
            The form, from which this validator is called.
        field : Field
            The field, of which the data shall be validated.

        Returns
        -------
        None

        Raises
        ------
        ValidationError if no character in the field data is a number.
        """

        data: str = field.data

        for char in data:
            if not char.isalnum():
                return

        raise ValidationError(self.message)


class ContainsNotSpace:
    """

    """

    def __init__(self, message: str = None):

        if not message:
            message = "Must not contain a whitespace character!"
        self.message = message

    def __call__(self, form: Form, field: Field) -> None:
        """Test if a field contains valid data.

        Parameters
        ----------
        form : Form
            The form, from which this validator is called.
        field : Field
            The field, of which the data shall be validated.

        Returns
        -------
        None

        Raises
        ------
        ValidationError if no character in the field data is a number.
        """

        data: str = field.data

        for char in data:
            if char.isspace():
                raise ValidationError(self.message)


class AllASCII:
    """

    """

    def __init__(self, message: str = None):

        if not message:
            message = "Must contain ASCII characters only!"
        self.message = message

    def __call__(self, form: Form, field: Field) -> None:
        """Test if a field contains valid data.

        Parameters
        ----------
        form : Form
            The form, from which this validator is called.
        field : Field
            The field, of which the data shall be validated.

        Returns
        -------
        None

        Raises
        ------
        ValidationError if no character in the field data is a number.
        """

        data: str = field.data

        for char in data:
            if not char.isascii():
                raise ValidationError(self.message)
