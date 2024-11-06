from app.forms.filters import strip_input
from app.forms.forms import EditForm
from app.forms.utils import RENDER_KW
from wtforms.fields import DateField, TextAreaField
from wtforms.validators import DataRequired, Length

__all__: list[str] = ["EditModification"]


class EditModification(EditForm):

    date = DateField(
        label="Date",
        validators=[DataRequired()],
        render_kw=RENDER_KW | {"id": "edit-form-modification-date", "type": "date"},
    )
    description = TextAreaField(
        label="Description",
        validators=[DataRequired(), Length(max=2048)],
        filters=[strip_input],
        render_kw=RENDER_KW
        | {
            "id": "edit-form-modification-description",
            "placeholder": "Description",
            "rows": 8,
        },
    )
