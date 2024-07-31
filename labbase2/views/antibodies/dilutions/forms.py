from labbase2.forms import render
from labbase2.forms.filters import strip_input
from labbase2.forms.forms import BaseForm
from wtforms.fields import SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length

__all__ = ["EditDilution"]


class EditDilution(BaseForm):
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
        render_kw=render.select_field,
    )
    dilution = StringField(
        label="Dilution",
        validators=[DataRequired(), Length(max=32)],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Dilution"},
    )
    reference = TextAreaField(
        label="Reference",
        validators=[DataRequired(), Length(max=2048)],
        filters=[strip_input],
        render_kw=render.custom_field | {"rows": 8},
        description="Give a short description of the sample and condition you used.",
    )
