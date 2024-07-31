from labbase2.forms import render
from labbase2.forms.filters import strip_input
from labbase2.forms.forms import BaseForm
from wtforms.fields import DateField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

__all__ = ["EditRequest"]


class EditRequest(BaseForm):
    """Form to add or edit a request.

    Attributes
    ----------

    """

    requested_by = StringField(
        label="Requested by",
        validators=[DataRequired(), Length(max=128)],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Requested by"},
    )
    timestamp = DateField(
        label="Date of request",
        validators=[DataRequired()],
        render_kw=render.custom_field | {"type": "date"},
    )
    timestamp_sent = DateField(
        label="Sent",
        validators=[Optional()],
        render_kw=render.custom_field | {"type": "date"},
    )
    note = TextAreaField(
        label="Note",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=render.custom_field | {"rows": 4},
    )
