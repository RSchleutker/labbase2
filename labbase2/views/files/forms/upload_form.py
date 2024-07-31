from labbase2.forms import render
from labbase2.forms.filters import strip_input
from labbase2.forms.forms import BaseForm
from wtforms.fields import FileField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

__all__ = ["UploadFile"]


class UploadFile(BaseForm):
    """Form to upload files.

    Attributes
    ----------

    """

    file = FileField(
        "Select File", validators=[DataRequired()], render_kw=render.file_field
    )
    filename = StringField(
        "Filename",
        validators=[Optional(), Length(max=64)],
        render_kw=render.custom_field | {"placeholder": "(Optional)"},
        description="Choose an optional filename.",
    )
    note = TextAreaField(
        "Note",
        validators=[Optional(), Length(max=2048)],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Note", "rows": 8},
    )
