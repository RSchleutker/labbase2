from labbase2.forms import FilterForm, render
from labbase2.forms.filters import strip_input
from labbase2.models import User
from wtforms.fields import Field, SelectField, StringField, SubmitField
from wtforms.validators import Optional

__all__ = ["FilterOligonucleotide"]


class FilterOligonucleotide(FilterForm):
    label = StringField(
        label="Label",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Label"},
        description="The label, i.e. the name of the entity.",
    )
    owner_id = SelectField(
        label="Owner",
        choices=[(0, "All")],
        default=0,
        coerce=int,
        render_kw=render.select_field,
        description="The owner of the primer.",
    )
    sequence = StringField(
        label="Sequence",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "CAAAGCGGAGATAA..."},
        description="""
            The sequence or part of it. The search is case-insensitive. Underscores 
            can be used as wildcards. For instance, 'AC_T' finds all primers that 
            contain the motif 'ACNT' where 'N' can be any base.
            """,
    )
    description = StringField(
        label="Description",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "forward m6 sequencing ..."},
        description="""
            A whitespace separated list of tags in the description of the primer. For
            instance, 'forward m6 sequencing' finds all primers with a description 
            that contains the words 'forward', 'm6', <strong>AND</strong> 'sequencing'.
            """,
    )
    download_fasta = SubmitField(label="Export to FASTA", render_kw=render.submit_field)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = (
            User.query.with_entities(User.id, User.username)
            .order_by(User.username)
            .all()
        )
        self.owner_id.choices += user
        self.order_by.choices += [
            ("label", "Label"),
            ("date_ordered", "Order date"),
            ("length", "Length"),
            ("sequence", "Sequence"),
            ("timestamp_edited", "Last edited"),
        ]

    def fields(self) -> list[Field]:
        return [
            self.id,
            self.label,
            self.owner_id,
            self.sequence,
            self.description,
            self.ascending,
            self.order_by,
        ]
