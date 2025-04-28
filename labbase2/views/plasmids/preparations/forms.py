from flask import current_app
from flask_wtf import FlaskForm
from wtforms.fields import (DateField, IntegerField, SelectField, StringField,
                            SubmitField)
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from labbase2.forms import rendering
from labbase2.forms.filters import strip_input

__all__ = ["EditPreparation"]


class EditPreparation(FlaskForm):
    """Form to add or edit a plasmid preparation.

    Attributes
    ----------

    """

    preparation_date = DateField(
        label="Date",
        validators=[DataRequired()],
        render_kw=rendering.custom_field | {"type": "date"},
    )
    method = StringField(
        label="Method",
        validators=[DataRequired(), Length(max=64)],
        filters=[strip_input],
        render_kw=rendering.custom_field | {"placeholder": "method"},
    )
    eluent = StringField(
        label="Eluent",
        validators=[DataRequired(), Length(max=32)],
        filters=[strip_input],
        render_kw=rendering.custom_field | {"placeholder": "Eluent"},
    )
    strain = SelectField(
        label="Strain",
        validators=[DataRequired()],
        choices=[],
        default="DH10B",
        render_kw=rendering.select_field,
    )
    concentration = IntegerField(
        label="Concentration",
        validators=[DataRequired(), NumberRange(min=1)],
        filters=[lambda x: round(x) if x else x],
        render_kw=rendering.custom_field | {"type": "number", "min": 1, "step": 1},
    )
    storage_place = StringField(
        label="Location",
        validators=[DataRequired(), Length(max=64)],
        filters=[strip_input],
        render_kw=rendering.custom_field | {"placeholder": "Location"},
    )
    emptied_date = DateField(
        label="Emptied",
        validators=[Optional()],
        render_kw=rendering.custom_field | {"type": "date"},
    )
    submit = SubmitField(label="Submit", render_kw=rendering.submit_field)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.strain.choices = [(strain, strain) for strain in current_app.config["STRAINS"]]
