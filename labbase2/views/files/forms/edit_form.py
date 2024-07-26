from labbase2.forms.forms import EditForm
from labbase2.forms.filters import strip_input
from labbase2.forms.utils import RENDER_KW

from wtforms.fields import StringField
from wtforms.fields import TextAreaField
from wtforms.validators import Optional
from wtforms.validators import Length


__all__ = ["EditFile"]


class EditFile(EditForm):
    filename = StringField(
        "Filename",
        validators=[Optional(), Length(max=64)],
        render_kw=RENDER_KW | {"placeholder": "(Optional)"},
        description="Choose an optional filename."
    )
    note = TextAreaField(
        "Note",
        validators=[Optional(), Length(max=2048)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"placeholder": "Note",
                               "rows": 8}
    )
