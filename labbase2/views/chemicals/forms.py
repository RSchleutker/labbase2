from flask_wtf import FlaskForm
from labbase2.forms import render
from labbase2.forms.filters import strip_input
from labbase2.forms.forms import EditEntityForm, FilterForm
from labbase2.models import Chemical, User
from sqlalchemy import func
from wtforms.fields import (
    DecimalField,
    Field,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
)
from wtforms.validators import Length, NumberRange, Optional
from wtforms.widgets import CheckboxInput, ListWidget

__all__: list = ["FilterChemical", "EditChemical"]


class FilterChemical(FilterForm):
    """Form for searching chemicals in the database.

    Attributes
    ----------
    cas : StringField
        The CAS number or part of it.
    pubchem_cid : StringField
        The PubChem CID. Please do not confuse this with the PubChem SID that
        also exists.
    order_by : SelectField
        The attribute by which the results shall be ordered. This overrides
        the order_field field of the parent SearchBaseForm class.
    """

    label = StringField(
        label="Label",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Label"},
        description="The label, i.e. the name of the entity.",
    )
    owner_id = SelectField(
        "Responsible",
        choices=[(0, "All")],
        coerce=int,
        render_kw=render.select_field,
    )
    order_by = SelectField(
        label="Order by",
        choices=[("label", "Label"), ("id", "ID"), ("order_date", "Order date")],
        default="label",
        render_kw=render.select_field,
        description="The column by which the results shall be ordered.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        user = (
            User.query.join(Chemical)
            .with_entities(User.id, User.username)
            .group_by(User.username)
            .having(func.count(User.id) > 0)
            .order_by(User.username)
        )
        self.owner_id.choices += user

    def fields(self) -> list:
        return [
            self.id,
            self.label,
            self.owner_id,
            self.order_by,
            self.ascending,
        ]


class EditChemical(EditEntityForm):
    """Form to edit chemicals.

    Attributes
    ----------
    cas_number : StringField
        The CAS registry number of the chemical.
    pubchem_cid : IntegerField
        The PubChem CID of the chemical. This should not be confused with the
        PubChem SID.
    """

    molecular_weight = DecimalField(
        "Molecular Weight",
        validators=[Optional(), NumberRange(min=0)],
        render_kw=render.custom_field | {"placeholder": "Molecular weight"},
    )
    owner_id = SelectField(
        "User",
        choices=[(0, "All")],
        coerce=int,
        render_kw=render.select_field,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = (
            User.query.with_entities(User.id, User.username)
            .order_by(User.username)
            .all()
        )
        self.owner_id.choices += user
