from labbase2.forms import BaseForm, FilterForm, render
from labbase2.forms.filters import strip_input
from labbase2.models import Chemical, User
from sqlalchemy import func
from wtforms.fields import (
    DateField,
    IntegerField,
    SelectField,
    StringField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, Optional

__all__ = ["FilterStockSolution", "EditStockSolution"]


class FilterStockSolution(FilterForm):
    id = IntegerField(
        "ID",
        validators=[Optional()],
        render_kw=render.custom_field | {"placeholder": "ID"},
    )
    label = StringField(
        label="Label",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Label"},
        description="The label, i.e. the name of the entity.",
    )
    responsible_id = SelectField(
        "Responsible",
        choices=[(0, "All")],
        coerce=int,
        render_kw=render.select_field,
    )
    solvent = StringField(
        "Solvent",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "ddH2O"},
    )
    storage_place = StringField(
        "Storage place",
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Freezer..."},
    )
    order_by = SelectField(
        label="Order by",
        choices=[
            ("label", "Label"),
            ("id", "ID"),
            ("user_id", "User"),
            ("solvent", "Solvent"),
        ],
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
        self.responsible_id.choices += user

    def fields(self) -> list:
        return [
            self.id,
            self.label,
            self.responsible_id,
            self.solvent,
            self.storage_place,
            self.order_by,
            self.ascending,
        ]


class EditStockSolution(BaseForm):

    solvent = StringField(
        label="Solvent",
        validators=[DataRequired(), Length(max=64)],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Solvent"},
    )
    concentration = StringField(
        label="Concentration",
        validators=[DataRequired(), Length(max=32)],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Concentration"},
    )
    storage_place = StringField(
        label="Storage Location",
        validators=[DataRequired(), Length(max=64)],
        render_kw=render.custom_field | {"placeholder": "Storage location"},
    )
    date_created = DateField(
        "Created",
        validators=[DataRequired()],
        render_kw=render.custom_field | {"type": "date"},
    )
    date_emptied = DateField(
        "Emptied at",
        validators=[Optional()],
        render_kw=render.custom_field | {"type": "date"},
    )
    details = TextAreaField(
        label="Concentration",
        validators=[Optional(), Length(max=2048)],
        render_kw=render.custom_field
        | {"placeholder": "Further details...", "size": 8},
    )
