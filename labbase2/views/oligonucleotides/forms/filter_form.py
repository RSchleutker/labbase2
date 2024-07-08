from labbase2.forms import FilterForm
from labbase2.forms.utils import RENDER_KW
from labbase2.forms.utils import RENDER_KW_BTN
from labbase2.forms.filters import strip_input

from labbase2.models import User

from wtforms.fields import Field
from wtforms.fields import StringField
from wtforms.fields import SelectField
from wtforms.fields import SubmitField
from wtforms.validators import Optional


__all__: list = ["FilterOligonucleotide"]


class FilterOligonucleotide(FilterForm):
    label = StringField(
        label="Label",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "filter-form-label",
                               "placeholder": "Label"},
        description='The label, i.e. the name of the entity.'
    )
    owner_id = SelectField(
        label="Owner",
        validators=[Optional()],
        choices=[(0, "All")],
        coerce=int,
        render_kw=RENDER_KW | {"id": "filter-form-owner-id", "size": 1},
        description="The owner of the primer."
    )
    sequence = StringField(
        label="Sequence",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "filter-form-sequence",
                               "placeholder": "CAAAGCGGAGATAA..."},
        description="""
            The sequence or part of it. The search is case-insensitive. 
            Underscores can be used as wildcards. For instance, 'AC_T' finds 
            all primers that contain the motif 'ACNT' where 'N' can be any base.
            """
    )
    description = StringField(
        label="Description",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "filter-form-description",
                               "placeholder": "forward m6 sequencing ..."},
        description="""
            A whitespace separated list of tags in the description of the 
            primer. For instance, 'forward m6 sequencing' finds all primers 
            with a description that contains the words 'forward', 'm6',
            <strong>AND</strong> 'sequencing'.
            """
    )
    order_by = SelectField(
        label="Order by",
        choices=[("label", "Label"),
                 ("id", "ID"),
                 ("order_date", "Order date"),
                 ("length", "Length")],
        default="label",
        render_kw=RENDER_KW | {"id": "filter-form-order-by", "size": 1},
        description="The column by which the results shall be ordered."
    )
    download_fasta = SubmitField(
        label="Export to FASTA",
        render_kw=RENDER_KW_BTN | {"id": "filter-form-download-fasta"}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = User.query\
            .with_entities(User.id, User.username)\
            .order_by(User.username)\
            .all()
        self.owner_id.choices += user

    def fields(self) -> list[Field]:
        return [self.id, self.label, self.owner_id, self.sequence,
                self.description, self.ascending, self.order_by]
