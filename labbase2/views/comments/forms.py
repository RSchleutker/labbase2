from labbase2.forms import render
from labbase2.forms.filters import strip_input
from labbase2.forms.forms import BaseForm
from wtforms.fields import StringField, TextAreaField
from wtforms.validators import DataRequired, Length

__all__ = ["EditComment"]


class EditComment(BaseForm):
    """Form to edit a comment.

    Attributes
    ----------
    subject : StringField
        The subject of the comment.
    text : TextAreaField
        The actual comment. This is limited to 2048 characters.
    """

    subject = StringField(
        label="Subject",
        validators=[DataRequired(), Length(max=128)],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Subject"},
    )
    text = TextAreaField(
        label="Comment",
        validators=[DataRequired(), Length(max=2048)],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Comment", "rows": 8},
    )
