from flask_login import current_user
from wtforms.fields import DateField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from labbase2.forms import rendering
from labbase2.forms.filters import strip_input
from labbase2.forms.forms import EditEntityForm, FilterForm
from labbase2.forms.validators import ContainsNot
from labbase2.models import User

__all__ = ["FilterFlyStocks", "EditFlyStock"]


class FilterFlyStocks(FilterForm):
    """A form to filter fly stock"""

    label = StringField(
        label="Label",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=rendering.custom_field | {"placeholder": "Label"},
        description="The label, i.e. the name of the entity.",
    )
    owner_id = SelectField(
        label="Owner",
        validators=[Optional()],
        choices=[(0, "All")],
        default=lambda: current_user.id,
        coerce=int,
        render_kw=rendering.select_field,
        description="The owner of the fly stock.",
    )
    short_genotype = StringField(
        label="Short Genotype",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=rendering.custom_field | {"placeholder": "m6[3xcs]"},
        description="The genotype of the fly stock.",
    )
    chromosome_x = StringField(
        label="Chromosome X", validators=[Optional()], render_kw=rendering.custom_field
    )
    chromosome_y = StringField(
        label="Chromosome Y", validators=[Optional()], render_kw=rendering.custom_field
    )
    chromosome_2 = StringField(
        label="Chromosome 2", validators=[Optional()], render_kw=rendering.custom_field
    )
    chromosome_3 = StringField(
        label="Chromosome 3", validators=[Optional()], render_kw=rendering.custom_field
    )
    chromosome_4 = StringField(
        label="Chromosome 4", validators=[Optional()], render_kw=rendering.custom_field
    )
    source = StringField(
        label="Source",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=rendering.custom_field | {"placeholder": "anne uv"},
        description="Where the stock was retrieved from.",
    )
    reference = StringField(
        label="Reference",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=rendering.custom_field | {"id": "filter-form-reference", "placeholder": "byri"},
        description="A paper that was added as a reference for this stock.",
    )
    discarded = SelectField(
        label="Discarded",
        choices=[
            ("all", "All"),
            ("recent", "Available only"),
            ("discarded", "Discarded only"),
        ],
        render_kw=rendering.select_field,
        description="""
        Shall only be discarded or non-discarded (recent) stocks be returned?
        """,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_by.choices += [
            ("label", "Label"),
            ("owner_id", "Owner"),
            ("short_genotype", "Short Genotype"),
            ("source", "Source"),
            ("discarded", "Discarded"),
        ]
        users = User.query.with_entities(User.id, User.username).order_by(User.username).all()
        self.owner_id.choices += users

    def fields(self) -> list:
        return [
            self.label,
            self.owner_id,
            self.short_genotype,
            self.chromosome_x,
            self.chromosome_y,
            self.chromosome_2,
            self.chromosome_3,
            self.chromosome_4,
            self.source,
            self.reference,
            self.discarded,
            self.order_by,
            self.ascending,
        ]


class EditFlyStock(EditEntityForm):
    """Form to add or edit a general fly stock.

    Attributes
    ----------

    """

    owner_id = SelectField(
        "Owner",
        choices=[(0, "-")],
        coerce=int,
        render_kw=rendering.select_field,
    )
    short_genotype = StringField(
        "Short Genotype",
        validators=[Optional(), Length(max=2048)],
        render_kw=rendering.custom_field,
    )
    chromosome_xa = StringField(
        "Chromosome XA",
        validators=[DataRequired(), ContainsNot(["/"]), Length(max=2048)],
        filters=[strip_input],
        render_kw=rendering.custom_field,
        default="+",
    )
    chromosome_xb = StringField(
        "Chromosome XB",
        validators=[DataRequired(), ContainsNot(["/"]), Length(max=2048)],
        filters=[strip_input],
        render_kw=rendering.custom_field,
        default="+",
    )
    chromosome_y = StringField(
        "Chromosome Y",
        validators=[DataRequired(), ContainsNot(["/"]), Length(max=2048)],
        filters=[strip_input],
        render_kw=rendering.custom_field,
        default="+",
    )
    chromosome_2a = StringField(
        "Chromosome 2A",
        validators=[DataRequired(), ContainsNot(["/"]), Length(max=2048)],
        filters=[strip_input],
        render_kw=rendering.custom_field,
        default="+",
    )
    chromosome_2b = StringField(
        "Chromosome 2B",
        validators=[DataRequired(), ContainsNot(["/"]), Length(max=2048)],
        filters=[strip_input],
        render_kw=rendering.custom_field,
        default="+",
    )
    chromosome_3a = StringField(
        "Chromosome XA",
        validators=[DataRequired(), ContainsNot(["/"]), Length(max=2048)],
        filters=[strip_input],
        render_kw=rendering.custom_field,
        default="+",
    )
    chromosome_3b = StringField(
        "Chromosome 3B",
        validators=[DataRequired(), ContainsNot(["/"]), Length(max=2048)],
        filters=[strip_input],
        render_kw=rendering.custom_field,
        default="+",
    )
    chromosome_4a = StringField(
        "Chromosome 4A",
        validators=[DataRequired(), ContainsNot(["/"]), Length(max=2048)],
        filters=[strip_input],
        render_kw=rendering.custom_field,
        default="+",
    )
    chromosome_4b = StringField(
        "Chromosome 4B",
        validators=[DataRequired(), ContainsNot(["/"]), Length(max=2048)],
        filters=[strip_input],
        render_kw=rendering.custom_field,
        default="+",
    )
    created_date = DateField(
        "Created",
        validators=[Optional()],
        render_kw=rendering.custom_field | {"type": "date"},
    )
    location = StringField(
        "Location",
        validators=[Optional(), Length(max=64)],
        filters=[strip_input],
        render_kw=rendering.custom_field | {"placeholder": "Location"},
    )
    source = StringField(
        "Source",
        validators=[Optional(), Length(max=512)],
        filters=[strip_input],
        render_kw=rendering.custom_field | {"placeholder": "Source"},
    )
    documentation = TextAreaField(
        "Documentation",
        validators=[Optional(), Length(max=2048)],
        filters=[strip_input],
        render_kw=rendering.custom_field | {"placeholder": "Documentation"},
    )
    reference = StringField(
        "Reference",
        validators=[Optional(), Length(max=512)],
        filters=[strip_input],
        render_kw=rendering.custom_field | {"placeholder": "Reference"},
    )
    discarded_date = DateField(
        "Discarded",
        validators=[Optional()],
        render_kw=rendering.custom_field | {"type": "date"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        users = User.query.with_entities(User.id, User.username).order_by(User.username).all()
        self.owner_id.choices += users
