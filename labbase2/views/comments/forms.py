from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from labbase2.forms import rendering
from labbase2.forms.filters import strip_input

__all__ = ["EditComment"]


class EditComment(FlaskForm):
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
        render_kw=rendering.custom_field | {"placeholder": "Subject"},
    )
    text = TextAreaField(
        label="Comment",
        validators=[DataRequired(), Length(max=2048)],
        filters=[strip_input],
        render_kw=rendering.custom_field | {"placeholder": "Comment", "rows": 8},
    )
    submit = SubmitField(label="Submit", render_kw=rendering.submit_field)
