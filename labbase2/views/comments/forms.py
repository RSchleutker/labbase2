from labbase2.forms.forms import EditForm
from labbase2.forms.utils import RENDER_KW
from labbase2.forms.filters import strip_input

from wtforms.fields import IntegerField
from wtforms.fields import TextAreaField
from wtforms.fields import StringField
from wtforms.validators import Optional
from wtforms.validators import DataRequired
from wtforms.validators import Length


__all__: list = ["EditComment"]


class EditComment(EditForm):
    """Form to edit a comment.

    Attributes
    ----------
    id : IntegerField
        The internal ID of this comment. This can never be edited.
    entity_id : IntegerField
        The internal ID of the entity this comment is about.
    user_id : IntegerField
        The internal ID of the person that wrote this comment.
    timestamp : DateField
        The date this comment was written. This might be changed to datetime
        in the future to be more accurate.
    text : TextAreaField
        The actual comment. This is limited to 2048 characters.
    """

    subject = StringField(
        label="Subject",
        validators=[DataRequired(), Length(max=128)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-comment-subject",
                               "placeholder": "Subject"},
    )
    text = TextAreaField(
        label="Comment",
        validators=[DataRequired(), Length(max=2048)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-comment-text",
                               "placeholder": "Comment",
                               "rows": 8}
    )
