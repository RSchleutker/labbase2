from labbase2.forms.utils import RENDER_KW
from labbase2.forms.utils import RENDER_KW_BTN
from labbase2.forms.utils import AllowCharacters
from labbase2.forms.filters import strip_input
from labbase2.forms.filters import make_upper

from flask import render_template
from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField
from wtforms.fields import IntegerField
from wtforms.fields import BooleanField
from wtforms.fields import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import NumberRange
from wtforms.validators import Length


__all__: list = ["FindOligonucleotide"]


class FindOligonucleotide(FlaskForm):
    sequence = TextAreaField(
        "Target sequence",
        validators=[DataRequired(), Length(max=20_000)],
        filters=[strip_input, make_upper, AllowCharacters("ACTGactg")],
        render_kw=RENDER_KW | {"id": "find-primers-form-sequence",
                               "size": 4,
                               "Placeholder": "Target sequence..."},
        description="""The target sequence, for which a matching primer shall be found. Please note, that long 
        sequence will considerably take longer to search. Therefor, consider to restrict the search to a part of the 
        sequence if possible."""
    )
    min_match = IntegerField(
        "Minimum continuous match",
        validators=[DataRequired(), NumberRange(max=40)],
        default=20,
        render_kw=RENDER_KW | {"id": "find-primers-form-min-match",
                               "size": 4,
                               "placeholder": "Minimum match"},
        description="""The minimum CONTINUOUS match length such that the primer shall be considered 'matching'. Lower 
        numbers result in less specific primers but speed up the search."""
    )
    max_len = IntegerField(
        "Maximal primer length",
        validators=[DataRequired()],
        default=40,
        render_kw=RENDER_KW | {"id": "find-primers-form-start",
                               "size": 4,
                               "placeholder": "Start"},
        description="""Consider only primers that are at most this long. This excludes unlikely oligonucleotides (for 
        instance for PCR). Lower numbers speed up the search."""
    )
    reverse_complement = BooleanField(
        "Reverse complement",
        default=False,
        description="""Specificy if the original sequence or the reverse complement shall be queried. If checked, 
        the target sequence will be turned into the reverse complement bewfore searching."""
    )
    submit = SubmitField(
        "Search",
        render_kw={**RENDER_KW_BTN, "id": "search-form-search"}
    )

    def fields(self) -> list:
        return [self.sequence, self.min_match, self.max_len, self.reverse_complement]

    def render(self, action: str = "", method: str = "POST") -> str:
        return render_template(
            "forms/filter.html",
            form=self,
            action=action,
            method=method,
            csrf=True
        )
