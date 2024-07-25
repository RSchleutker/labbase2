from labbase2.forms.forms import FilterForm
from labbase2.forms.forms import EditForm
from labbase2.forms.forms import EditEntityForm
from labbase2.forms.utils import RENDER_KW
from labbase2.forms.filters import strip_input

from labbase2.models import User

from wtforms.fields import StringField
from wtforms.fields import SelectField
from wtforms.fields import TextAreaField
from wtforms.fields import IntegerField
from wtforms.fields import DateField
from wtforms.validators import DataRequired
from wtforms.validators import Optional
from wtforms.validators import NumberRange
from wtforms.validators import Length


__all__: list = ["FilterPlasmids", "EditPlasmid", "EditPreparation"]


class FilterPlasmids(FilterForm):
    """Form for searching plasmids in the database.

    Attributes
    ----------
    insert : StringField
        The insert of the plasmid. Usually, plasmids can be identified by the
        vector (backbone) and the insert.
    vector : StringField
        The vector of the plasmid. Usually, plasmids can be identified by the
        vector (backbone) and the insert.
    constructed_by : StringField
        The person that constructed the plasmid.
    description : StringField
        Some plasmids have a description informing about what the plasmid
        is/was used for. This can be searched. However, search queries should be
        restricted to single tags because the search is exact.
    order_by : SelectField
        The attribute by which the results shall be ordered. This overrides
        the order_field field of the parent SearchBaseForm class.
    """

    label = StringField(
        label="Label",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "filter-form-label",
                               "placeholder": "Label"},
        description="The label, i.e. the name of the entity."
    )
    insert = StringField(
        label="Insert",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "search-form-insert",
                               "placeholder": "aka"},
        description="""
        The construct that was inserted into the vector. The search is case
        insensitive.
        """
    )
    vector = StringField(
        label="Vector",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "search-form-vector",
                               "placeholder": "pUASt-attB"},
        description="The vector, i.e., the backbone of the plasmid."
    )
    owner_id = SelectField(
        label="Owner",
        validators=[Optional()],
        choices=[(0, "All")],
        coerce=int,
        render_kw=RENDER_KW | {"id": "filter-form-owner-id", "size": 1},
        description="The owner of the primer."
    )
    description = StringField(
        label="Description",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "search-form-description",
                               "placeholder": "anne uv flyfos"},
        description="""
        A whitespace separated list of tags in the description of the plasmid.
        For instance, "anne uv flyfos" finds all plasmids with a description 
        that contains the words "anne", "uv", <strong>AND</strong> "flyfos".
        """
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_by.choices += [
            ("label", "Label"),
            ("vector", "Vector"),
            ("cloning_date", "Cloning date")
        ]
        users = User.query\
            .with_entities(User.id, User.username)\
            .order_by(User.username)\
            .all()
        self.owner_id.choices += users

    def fields(self) -> list:
        return [self.id, self.label, self.insert, self.vector, self.owner_id,
                self.description, self.order_by, self.ascending]


class EditPlasmid(EditEntityForm):
    """Form to add or edit a plasmid.

    Attributes
    ----------
    vector : StringField
        Limited to 256 characters.
    insert : StringField
        Limited to 128 characters.
    constructed_by : StringField
        Limited to 128 characters.
    created : DateField
    description : TextAreaField
        Limited to 1024 characters.
    reference : StringField
        Limited to 512 characters.
    """

    insert = StringField(
        label="Insert",
        validators=[DataRequired(), Length(max=128)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-insert",
                               "placeholder": "Insert"}
    )
    vector = StringField(
        label="Vector",
        validators=[Optional(), Length(max=256)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-vector",
                               "placeholder": "Vector"}
    )
    cloning_date = DateField(
        label="Cloning date",
        validators=[Optional()],
        render_kw=RENDER_KW | {"id": "edit-form-created", "type": "date"}
    )
    description = TextAreaField(
        label="Description",
        validators=[Optional(), Length(max=1024)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-description",
                               "placeholder": "Description",
                               "rows": 4}
    )
    reference = StringField(
        label="Reference",
        validators=[Optional(), Length(max=512)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-reference",
                               "placeholder": "Reference"}
    )


class EditPreparation(EditForm):
    """Form to add or edit a plasmid preparation.

    Attributes
    ----------

    """

    preparation_date = DateField(
        label="Date",
        validators=[DataRequired()],
        render_kw=RENDER_KW | {"id": "edit-form-preparation-timestamp",
                               "type": "date"}
    )
    method = StringField(
        label="Method",
        validators=[DataRequired(), Length(max=64)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-preparation-method",
                               "placeholder": "method"}
    )
    eluent = StringField(
        label="Eluent",
        validators=[DataRequired(), Length(max=32)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-preparation-eluent",
                               "placeholder": "Eluent"}
    )
    concentration = IntegerField(
        label="Concentration",
        validators=[DataRequired(), NumberRange(min=1)],
        filters=[lambda x: round(x) if x else x],
        render_kw=RENDER_KW | {"id": "edit-form-preparation-concentration",
                               "type": "number",
                               "min": 1,
                               "step": 1}
    )
    storage_place = StringField(
        label="Location",
        validators=[DataRequired(), Length(max=64)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-preparation-location",
                               "placeholder": "Location"}
    )
    emptied_date = DateField(
        label="Emptied",
        validators=[Optional()],
        render_kw=RENDER_KW | {"id": "edit-form-preparation-empty-timestamp",
                               "type": "date"}
    )
