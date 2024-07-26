from flask_login import current_user

from labbase2.forms import EditEntityForm
from labbase2.forms.utils import RENDER_KW
from labbase2.forms.utils import AllowCharacters
from labbase2.forms.utils import RemoveCharacters
from labbase2.forms.filters import strip_input
from labbase2.forms.filters import upper_seq_input
from labbase2.models import User

from flask import render_template
from wtforms.fields import StringField
from wtforms.fields import TextAreaField
from wtforms.fields import DateField
from wtforms.fields import SelectField
from wtforms.validators import DataRequired
from wtforms.validators import Optional
from wtforms.validators import Length

from datetime import date


__all__ = ["EditOligonucleotide"]


class EditOligonucleotide(EditEntityForm):
    date_ordered = DateField(
        "Order date",
        default=date.today,
        validators=[Optional()],
        render_kw=RENDER_KW | {"id": "edit-form-order-date",
                               "type": "date",
                               "placeholder": "Primer name, e.g. oRS-1"}
    )
    owner_id = SelectField(
        "Owner", validators=[DataRequired()],
        validate_choice=False,
        default=lambda: current_user.id,
        coerce=int,
        render_kw=RENDER_KW | {"size": 1},
        description="Be aware that you cannot edit this entry anymore if you select someone else."
    )
    sequence = StringField(
        "Sequence",
        validators=[DataRequired(), Length(max=256)],
        filters=[
            strip_input,
            upper_seq_input,
            RemoveCharacters(" \n\t"),
            AllowCharacters("ACGTacgt")
        ],
        render_kw=RENDER_KW | {"id": "edit-form-sequence",
                               "placeholder": "Sequence"}
    )
    storage_place = StringField(
        "Storage place",
        validators=[Optional(), Length(max=64)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-storage-place",
                               "placeholder": "Storage place"}
    )
    description = TextAreaField(
        "Description",
        validators=[Optional(), Length(max=512)],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-description",
                               "placeholder": "Description",
                               "rows": 6},
        description="Give a short description about the purpose of this oligonucleotide."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = User.query.with_entities(User.id, User.username)
        choices = [tuple(choice) for choice in choices]
        self.owner_id.choices = choices

    def render(self, action: str = "", method: str = "GET") -> str:
        return render_template(
            "oligonucleotides/form.html",
            form=self,
            action=action,
            method=method
        )
