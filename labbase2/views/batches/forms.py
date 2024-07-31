from labbase2.forms import render
from labbase2.forms.filters import strip_input
from labbase2.forms.forms import BaseForm, FilterForm
from labbase2.models import Batch
from wtforms.fields import (
    DateField,
    DecimalField,
    IntegerField,
    SelectField,
    StringField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional

__all__ = ["FilterBatch", "EditBatch"]


class FilterBatch(FilterForm):
    id = IntegerField(
        "ID",
        validators=[Optional()],
        render_kw=render.custom_field | {"placeholder": "Batch ID"},
    )
    label = StringField(
        label="Label",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Name of consumable."},
        description="The label, i.e. the name of the consumable.",
    )
    consumable_type = SelectField(
        "Type",
        choices=[
            ("", "All"),
            ("antibody", "Antibody"),
            ("chemical", "Chemical"),
            ("enzyme", "Enzyme"),
        ],
        render_kw=render.select_field,
        description="""
        Batches can be added for all kinds of consumables like antibodies, chemicals,
        or enzmyes. This field allows  to select only batches of a certain type.
        """,
    )
    supplier = SelectField(
        "Supplier",
        choices=[("", "All")],
        render_kw=render.select_field,
        description="The supplier from which the batch was ordered.",
    )
    lot = StringField(
        "Lot",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Lot#"},
        description="""
        Batches have a field for lot numbers. This is usually only necessary 
        for batches of antibodies.
        """,
    )
    empty = SelectField(
        "Empty",
        choices=[
            ("all", "All"),
            ("empty", "Empty only"),
            ("not_empty", "Non-empty only"),
        ],
        default="all",
        render_kw=render.select_field,
        description="""
        Batches can be marked as empty once it was used up. However, 
        empty batches are kept in the database. This field allows to search 
        only for empty or non-empty batches.
        """,
    )
    in_use = SelectField(
        "In use",
        choices=[("all", "All"), ("in_use", "In use"), ("not_in_use", "Not in use")],
        default="all",
        render_kw=render.select_field,
    )
    order_by = SelectField(
        label="Order by",
        choices=[
            ("label", "Label"),
            ("id", "ID"),
            ("consumable_type", "Type"),
            ("supplier", "Supplier"),
            ("ordered", "Ordered"),
        ],
        default="label",
        render_kw=render.select_field,
        description="The column by which the results shall be ordered.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        supplier = (
            Batch.query.with_entities(Batch.supplier, Batch.supplier)
            .order_by(Batch.supplier)
            .distinct()
        )
        self.supplier.choices += supplier

    def fields(self) -> list:
        return [
            self.id,
            self.consumable_type,
            self.label,
            self.supplier,
            self.lot,
            self.empty,
            self.in_use,
            self.order_by,
            self.ascending,
        ]


class EditBatch(BaseForm):
    """A form for adding or editing of a batch.

    Attributes
    ----------
    supplier : StringField
        The company/person that provided the batch. Limited to 64 characters.
    article_number : StringField
        The article number of the batch to easier find it again. Limited to
        32 characters.
    amount : StringField
        The amount (volume, weight, possibly also concentration) of the
        batch. Limited to 32 characters.
    date_ordered : DateField
        The date the batch was ordered.
    date_opened : DateField
        The date the batch was first used/opened.
    date_expiration : DateField
        The expiration date of the batch if provided.
    date_emptied : DateField
        The date the batch was emptied.
    price : DecimalField
        The price (if possible in €) of the batch.
    storage_place : StringField
        The place the batch is stored. Limited to 54 characters.
    lot : StringField
        The lot number of the batch.
    """

    supplier = StringField(
        "Supplier",
        validators=[DataRequired(), Length(max=64)],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Supplier"},
    )
    article_number = StringField(
        "Article number",
        validators=[Optional(), Length(max=32)],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Article number"},
    )
    amount = StringField(
        "Amount",
        validators=[Optional(), Length(max=32)],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Amount"},
    )
    date_ordered = DateField(
        "Ordered",
        validators=[Optional()],
        render_kw=render.custom_field | {"type": "date"},
    )
    date_opened = DateField(
        "Opened",
        validators=[Optional()],
        render_kw=render.custom_field | {"type": "date"},
    )
    date_expiration = DateField(
        "Expiration date",
        validators=[Optional()],
        render_kw=render.custom_field | {"type": "date"},
    )
    date_emptied = DateField(
        "Emptied at",
        validators=[Optional()],
        render_kw=render.custom_field | {"type": "date"},
    )
    price = DecimalField(
        "Price",
        validators=[Optional(), NumberRange(min=0)],
        render_kw=render.custom_field
        | {"placeholder": "Price (€)", "min": 0, "type": "number", "step": 0.01},
    )
    storage_place = StringField(
        "Storage place",
        validators=[DataRequired(), Length(max=64)],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Storage place"},
    )
    lot = StringField(
        "Lot number",
        validators=[DataRequired(), Length(max=64)],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Lot number"},
    )
