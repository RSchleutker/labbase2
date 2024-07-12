from labbase2.forms.forms import EditForm
from labbase2.forms.forms import FilterForm
from labbase2.forms.utils import RENDER_KW
from labbase2.forms.filters import strip_input

from labbase2.models.plasmid import GlycerolStock

from wtforms.fields import StringField
from wtforms.fields import SelectField
from wtforms.fields import IntegerField
from wtforms.fields import DateField
from wtforms.validators import DataRequired
from wtforms.validators import Optional
from wtforms.validators import Length


__all__ = ["FilterBacteria", "EditBacterium"]


class FilterBacteria(FilterForm):
    strain = SelectField(
        label="Strain",
        validators=[Optional()],
        choices=[("all", "All")],
        render_kw=RENDER_KW | {"id": "filter-form-bacteria-strain",
                               "size": 1,
                               "placeholder": "DH10B"}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        strains = GlycerolStock.query\
            .with_entities(GlycerolStock.strain, GlycerolStock.strain)\
            .order_by(GlycerolStock.strain)\
            .all()
        self.strain.choices += strains

    def fields(self):
        return [self.id, self.strain, self.order_by, self.ascending]


class EditBacterium(EditForm):
    """A form for adding or editing a bacterial stock.

    Attributes
    ----------
    id : IntegerField
        The internal ID of the bacterial stock.
    plasmid_id : IntegerField
        The ID of the plasmid that the bacteria where transformed with.
    strain : SelectField
        The bacterial strain that was transformed.
    created : DateField
        The date the bacterial stock was generated. This is the day the
        bacteria got transformed.
    created_by : StringField
        The person that created the bacterial stock.
    disposed : DateField
        The date the bacterial stock was trashed.
    location : StringField
        The storage location (exact position in the -80°C freezer) of the
        bacterial stock.
    """

    strain = SelectField(
        label="Strain",
        validators=[DataRequired()],
        choices=["DB3.1",
                 "DH10B",
                 "DH5-Alpha",
                 "XL1 Blue",
                 "XL10 Gold",
                 "ccdB Survival 2 T1R"],
        default="DH10B",
        render_kw=RENDER_KW | {"id": "edit-form-bacteria-strain", "size": 1}
    )
    transformation_date = DateField(
        label="Transformation date",
        validators=[DataRequired()],
        render_kw=RENDER_KW | {"id": "edit-form-bacteria-transformation-date",
                               "type": "date"}
    )
    storage_place = StringField(
        label="Storage place",
        validators=[DataRequired(), Length(max=128)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-bacteria-storage-place",
                               "placeholder": "Storage place"}
    )
    disposal_date = DateField(
        label="Disposal date",
        validators=[Optional()],
        render_kw=RENDER_KW | {"id": "edit-form-bacteria-disposal-date",
                               "type": "date"}
    )
