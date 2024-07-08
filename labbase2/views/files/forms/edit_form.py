from labbase2.forms.forms import EditForm
from labbase2.forms.filters import strip_input
from labbase2.forms.utils import RENDER_KW

from wtforms.fields import TextAreaField
from wtforms.validators import Optional
from wtforms.validators import Length


__all__ = ["EditFile"]


class EditFile(EditForm):
    note = TextAreaField(
        "Note",
        validators=[Optional(), Length(max=256)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-upload-note",
                               "placeholder": "Note",
                               "rows": 8}
    )
