from labbase2.forms import render
from labbase2.forms.filters import strip_input
from labbase2.forms.forms import BaseForm, FilterForm
from labbase2.models.plasmid import GlycerolStock
from wtforms.fields import DateField, SelectField, StringField
from wtforms.validators import DataRequired, Length, Optional

__all__ = ["FilterBacteria", "EditBacterium"]


class FilterBacteria(FilterForm):
    strain = SelectField(
        label="Strain",
        validators=[Optional()],
        choices=[("all", "All")],
        render_kw=render.select_field | {"placeholder": "DH10B"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        strains = (
            GlycerolStock.query.with_entities(
                GlycerolStock.strain, GlycerolStock.strain
            )
            .order_by(GlycerolStock.strain)
            .all()
        )
        self.strain.choices += strains

    def fields(self):
        return [self.id, self.strain, self.order_by, self.ascending]


class EditBacterium(BaseForm):
    """A form for adding or editing a bacterial stock.

    Attributes
    ----------
    strain : SelectField
        The bacterial strain that was transformed.
    transformation_date : DateField
        The date the bacterial stock was generated. This is the day the
        bacteria got transformed.
    disposal_date : DateField
        The date the bacterial stock was trashed.
    storage_place : StringField
        The storage location (exact position in the -80°C freezer) of the
        bacterial stock.
    """

    strain = SelectField(
        label="Strain",
        validators=[DataRequired()],
        choices=[
            ("DB3.1", "DB3.1"),
            ("DH10B", "DH10B"),
            ("DH5-Alpha", "DH5-Alpha"),
            ("XL1 Blue", "XL1 Blue"),
            ("XL10 Gold", "XL10 Gold"),
            ("ccdB Survival 2 T1R", "ccdB Survival 2 T1R"),
        ],
        default="DH10B",
        render_kw=render.select_field,
    )
    transformation_date = DateField(
        label="Transformation date",
        validators=[DataRequired()],
        render_kw=render.custom_field | {"type": "date"},
    )
    storage_place = StringField(
        label="Storage place",
        validators=[DataRequired(), Length(max=128)],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Storage place"},
    )
    disposal_date = DateField(
        label="Disposal date",
        validators=[Optional()],
        render_kw=render.custom_field | {"type": "date"},
    )
