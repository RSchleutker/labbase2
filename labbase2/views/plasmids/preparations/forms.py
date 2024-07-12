from labbase2.forms.forms import EditForm
from labbase2.forms.utils import RENDER_KW
from labbase2.forms.filters import strip_input

from wtforms.fields import StringField
from wtforms.fields import IntegerField
from wtforms.fields import DateField
from wtforms.validators import DataRequired
from wtforms.validators import Optional
from wtforms.validators import NumberRange
from wtforms.validators import Length


__all__: list[str] = ["EditPreparation"]


class EditPreparation(EditForm):
    """Form to add or edit a plasmid preparation.

    Attributes
    ----------

    """

    preparation_date = DateField(
        label="Date",
        validators=[DataRequired()],
        render_kw=RENDER_KW | {"id": "edit-form-preparation-timestamp",
                               "type": "date"}
    )
    method = StringField(
        label="Method",
        validators=[DataRequired(), Length(max=64)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-preparation-method",
                               "placeholder": "method"}
    )
    eluent = StringField(
        label="Eluent",
        validators=[DataRequired(), Length(max=32)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-preparation-eluent",
                               "placeholder": "Eluent"}
    )
    concentration = IntegerField(
        label="Concentration",
        validators=[DataRequired(), NumberRange(min=1)],
        filters=[lambda x: round(x) if x else x],
        render_kw=RENDER_KW | {"id": "edit-form-preparation-concentration",
                               "type": "number",
                               "min": 1,
                               "step": 1}
    )
    storage_place = StringField(
        label="Location",
        validators=[DataRequired(), Length(max=64)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-preparation-location",
                               "placeholder": "Location"}
    )
    emptied_date = DateField(
        label="Emptied",
        validators=[Optional()],
        render_kw=RENDER_KW | {"id": "edit-form-preparation-empty-timestamp",
                               "type": "date"}
    )
