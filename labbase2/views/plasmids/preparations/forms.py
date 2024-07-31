from labbase2.forms import render
from labbase2.forms.filters import strip_input
from labbase2.forms.forms import BaseForm
from wtforms.fields import DateField, IntegerField, StringField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

__all__ = ["EditPreparation"]


class EditPreparation(BaseForm):
    """Form to add or edit a plasmid preparation.

    Attributes
    ----------

    """

    preparation_date = DateField(
        label="Date",
        validators=[DataRequired()],
        render_kw=render.custom_field | {"type": "date"},
    )
    method = StringField(
        label="Method",
        validators=[DataRequired(), Length(max=64)],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "method"},
    )
    eluent = StringField(
        label="Eluent",
        validators=[DataRequired(), Length(max=32)],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Eluent"},
    )
    concentration = IntegerField(
        label="Concentration",
        validators=[DataRequired(), NumberRange(min=1)],
        filters=[lambda x: round(x) if x else x],
        render_kw=render.custom_field | {"type": "number", "min": 1, "step": 1},
    )
    storage_place = StringField(
        label="Location",
        validators=[DataRequired(), Length(max=64)],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Location"},
    )
    emptied_date = DateField(
        label="Emptied",
        validators=[Optional()],
        render_kw=render.custom_field | {"type": "date"},
    )
