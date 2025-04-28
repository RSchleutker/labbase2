from flask_wtf import FlaskForm
from wtforms.fields import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from labbase2.forms import rendering
from labbase2.forms.filters import strip_input

__all__ = ["EditDilution"]


class EditDilution(FlaskForm):
    """Form to edit an antibody dilution.

    Attributes
    ----------
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
            ("immunoprecipitation", "Immunoprecipitation"),
        ],
        render_kw=rendering.select_field,
    )
    dilution = StringField(
        label="Dilution",
        validators=[DataRequired(), Length(max=32)],
        filters=[strip_input],
        render_kw=rendering.custom_field | {"placeholder": "Dilution"},
    )
    reference = TextAreaField(
        label="Reference",
        validators=[DataRequired(), Length(max=2048)],
        filters=[strip_input],
        render_kw=rendering.custom_field | {"rows": 8},
        description="Give a short description of the sample and condition you used.",
    )
    submit = SubmitField(label="Submit", render_kw=rendering.submit_field)
