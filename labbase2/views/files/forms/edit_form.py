from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, TextAreaField
from wtforms.validators import Length, Optional

from labbase2.forms import rendering
from labbase2.forms.filters import strip_input

__all__ = ["EditFile"]


class EditFile(FlaskForm):
    filename = StringField(
        "Filename",
        validators=[Optional(), Length(max=64)],
        render_kw=rendering.custom_field | {"placeholder": "(Optional)"},
        description="Choose an optional filename.",
    )
    note = TextAreaField(
        "Note",
        validators=[Optional(), Length(max=2048)],
        filters=[strip_input],
        render_kw=rendering.custom_field | {"placeholder": "Note", "rows": 8},
    )
    submit = SubmitField(label="Submit", render_kw=rendering.submit_field)
