from labbase2.forms.forms import EditForm
from labbase2.forms.utils import RENDER_KW
from labbase2.forms.filters import strip_input

from wtforms.fields import TextAreaField
from wtforms.fields import StringField
from wtforms.fields import DateField
from wtforms.validators import Optional
from wtforms.validators import DataRequired
from wtforms.validators import Length


__all__: list = ["EditRequest"]


class EditRequest(EditForm):
    """Form to add or edit a request.

    Attributes
    ----------

    """

    requested_by = StringField(
        label="Requested by",
        validators=[DataRequired(), Length(max=128)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-request-requested-by",
                               "placeholder": "Requested by"}
    )
    timestamp = DateField(
        label="Date of request",
        validators=[DataRequired()],
        render_kw=RENDER_KW | {"id": "edit-form-request-timestamp",
                               "type": "date"}
    )
    timestamp_sent = DateField(
        label="Sent",
        validators=[Optional()],
        render_kw=RENDER_KW | {"id": "edit-form-request-sent", "type": "date"}
    )
    note = TextAreaField(
        label="Note",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-request-note", "rows": 4}
    )
