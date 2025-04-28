from flask_wtf import FlaskForm
from wtforms.fields import DateField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from labbase2.forms import rendering
from labbase2.forms.filters import strip_input

__all__ = ["EditRequest"]


class EditRequest(FlaskForm):
    """Form to add or edit a request.

    Attributes
    ----------

    """

    requested_by = StringField(
        label="Requested by",
        validators=[DataRequired(), Length(max=128)],
        filters=[strip_input],
        render_kw=rendering.custom_field | {"placeholder": "Requested by"},
    )
    timestamp = DateField(
        label="Date of request",
        validators=[DataRequired()],
        render_kw=rendering.custom_field | {"type": "date"},
    )
    timestamp_sent = DateField(
        label="Sent",
        validators=[Optional()],
        render_kw=rendering.custom_field | {"type": "date"},
    )
    note = TextAreaField(
        label="Note",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=rendering.custom_field | {"rows": 4},
    )
    submit = SubmitField(label="Submit", render_kw=rendering.submit_field)
