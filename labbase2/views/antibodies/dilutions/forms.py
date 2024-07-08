from app.forms.forms import EditForm
from app.forms.utils import RENDER_KW
from app.forms.filters import strip_input

from wtforms.fields import StringField
from wtforms.fields import SelectField
from wtforms.fields import IntegerField
from wtforms.validators import DataRequired
from wtforms.validators import Length


__all__: list[str] = ["EditDilution"]


class EditDilution(EditForm):
    """Form to edit an antibody dilution.

    Attributes
    ----------
    id : IntegerField
        The internal ID of the dilution. This can never be edited.
    antibody_id : IntegerField
        The internal ID of the antibody, to which this dilution belongs.
    application : SelectField
        The application this dilution was determined for,
        e.g. 'immunostaining' or 'western blot'.
    dilution : StringField
        The dilution itself. This should be something like 1:x. This is
        limited to 32 characters.
    reference : StringField
        A reference for this dilution. The number of characters is limited 512.
    """

    application = SelectField(
        label="Application",
        validators=[DataRequired(), Length(max=64)],
        choices=[
            ("immunostaining", "Immunostaining"),
            ("western blot", "Western blot"),
            ("immunoprecipitation", "Immunoprecipitation")
        ],
        render_kw=RENDER_KW | {"id": "edit-form-dilution-application",
                               "size": 1}
    )
    dilution = StringField(
        label="Dilution",
        validators=[DataRequired(), Length(max=32)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-dilution-dilution",
                               "placeholder": "Dilution"}
    )
    reference = StringField(
        label="Reference",
        validators=[DataRequired(), Length(max=512)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-dilution-reference",
                               "placeholder": "Reference"}
    )
