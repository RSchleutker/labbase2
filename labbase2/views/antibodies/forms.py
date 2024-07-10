from labbase2.forms.forms import FilterForm
from labbase2.forms.forms import EditEntityForm
from labbase2.forms.utils import RENDER_KW
from labbase2.forms.filters import strip_input
from labbase2.forms.filters import make_lower

from labbase2.models import Antibody

from wtforms.fields import Field
from wtforms.fields import StringField
from wtforms.fields import SelectField
from wtforms.fields import IntegerField
from wtforms.validators import DataRequired
from wtforms.validators import Optional
from wtforms.validators import NumberRange
from wtforms.validators import Length
from sqlalchemy import func


__all__: list = ["FilterAntibodies", "EditAntibody"]


class FilterAntibodies(FilterForm):
    label = StringField(
        label="Label",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "filter-form-label",
                               "placeholder": "Label"},
        description='The label, i.e. the token of the entity.'
    )
    clone = StringField(
        label="Clone",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "filter-form-clone",
                               "placeholder": "Clone"},
        description="Antibody clone if available."
    )
    host = SelectField(
        label="Host",
        choices=[("", "All")],
        render_kw=RENDER_KW | {"id": "filter-form-host", "size": 1},
        description="The animal, in which the antibody was raised."
    )
    antigen = StringField(
        label="Antigen",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "filter-form-antigen",
                               "placeholder": "gfp"},
        description="The antigen that is recognized by the antibody."
    )
    conjugate = SelectField(
        label="Conjugate",
        choices=[("all", "All"), ("any", "Any"), ("none", "None")],
        render_kw=RENDER_KW | {"id": "filter-form-conjugate", "size": 1},
        description="""The conjugate of the antibody. Primary antibodies are 
        all antibodies without a conjugate."""
    )
    order_by = SelectField(
        label="Order by",
        choices=[("label", "Label"),
                 ("id", "ID"),
                 ("clone", "Clone"),
                 ("host", "Host"),
                 ("antigen", "Antigen"),
                 ("conjugate", "Conjugate")],
        default="label",
        render_kw=RENDER_KW | {"id": "filter-form-order-by", "size": 1},
        description="The column by which the results shall be ordered."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.conjugate.choices += Antibody.query \
            .with_entities(Antibody.conjugate, Antibody.conjugate) \
            .order_by(func.lower(Antibody.conjugate)) \
            .filter(Antibody.conjugate.isnot(None)) \
            .distinct().all()

        self.host.choices += Antibody.query \
            .with_entities(Antibody.host, Antibody.host) \
            .order_by(func.lower(Antibody.host)) \
            .distinct().all()

    def fields(self) -> list[Field]:
        return [self.id, self.label, self.clone, self.host, self.antigen,
                self.conjugate, self.ascending, self.order_by]


class EditAntibody(EditEntityForm):
    clone = StringField(
        label="Clone",
        validators=[Optional(), Length(max=32)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-clone", "placeholder": "Clone"}
    )
    host = StringField(
        label="Host",
        validators=[DataRequired(), Length(max=64)],
        filters=[strip_input, make_lower],
        render_kw=RENDER_KW | {"id": "edit-form-host", "placeholder": "Host"}
    )
    antigen = StringField(
        "Antigen",
        validators=[DataRequired(), Length(max=64)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-antigen",
                               "placeholder": "Antigen"}
    )
    specification = StringField(
        label="Specification",
        validators=[Optional(), Length(max=64)],
        filters=[strip_input, make_lower],
        render_kw=RENDER_KW | {"id": "edit-form-specification",
                               "placeholder": "Clonality"}
    )
    storage_temp = IntegerField(
        label="Storage Temperature",
        validators=[Optional(), NumberRange(min=-80, max=37)],
        render_kw=RENDER_KW | {"id": "edit-form-storage-temp",
                               "min": -80,
                               "max": 37,
                               "type": "number"}
    )
    source = StringField(
        label="Source",
        validators=[Optional(), Length(max=64)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-source",
                               "placeholder": "Source"}
    )
    conjugate = StringField(
        label="Conjugate",
        validators=[Optional(), Length(max=64)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-conjugate",
                               "placeholder": "Conjugate"}
    )
