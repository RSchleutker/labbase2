from wtforms.fields import DateField, TextAreaField
from wtforms.validators import DataRequired, Length

from labbase2.forms import EditEntityForm, render

__all__ = ["EditModification"]


class EditModification(EditEntityForm):

    date = DateField(
        label="Date",
        validators=[DataRequired()],
        render_kw=render.custom_field | {"id": "edit-form-modification-date", "type": "date"},
    )
    description = TextAreaField(
        label="Description",
        validators=[DataRequired(), Length(max=2048)],
        filters=[],
        render_kw=render.custom_field
        | {
            "id": "edit-form-modification-description",
            "placeholder": "Description",
            "rows": 8,
        },
    )
