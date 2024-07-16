from labbase2.forms.forms import EditForm
from labbase2.forms.filters import strip_input
from labbase2.forms.utils import RENDER_KW
from labbase2.forms.utils import RENDER_KW_FILE

from wtforms.fields import FileField
from wtforms.fields import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Optional
from wtforms.validators import Length


__all__ = ["UploadFile"]


class UploadFile(EditForm):
    """Form to upload files.

    Attributes
    ----------

    """

    file = FileField(
        "Select File",
        validators=[DataRequired()],
        render_kw=RENDER_KW_FILE | {"id": "edit-form-upload-filepath",
                                    "type": "file"}
    )
    note = TextAreaField(
        "Note",
        validators=[Optional(), Length(max=256)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-upload-note",
                               "placeholder": "Note",
                               "rows": 8}
    )
