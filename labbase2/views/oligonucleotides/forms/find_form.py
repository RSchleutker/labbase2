from flask import render_template
from flask_wtf import FlaskForm
from labbase2.forms import render
from labbase2.forms.filters import make_upper, strip_input
from labbase2.forms.validators import AllowCharacters
from wtforms.fields import BooleanField, IntegerField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange

__all__ = ["FindOligonucleotide"]


class FindOligonucleotide(FlaskForm):
    sequence = TextAreaField(
        "Target sequence",
        validators=[DataRequired(), Length(max=20_000), AllowCharacters("ACTGactg")],
        filters=[strip_input, make_upper],
        render_kw=render.custom_field
        | {"size": 4, "Placeholder": "Target sequence..."},
        description="""
        The target sequence, for which a matching primer shall be found. Please note,
        that long sequence will considerably take longer to search. Therefor, 
        consider to restrict the search to a part of the sequence if possible.
        """,
    )
    min_match = IntegerField(
        "Minimum continuous match",
        validators=[DataRequired(), NumberRange(max=40)],
        default=20,
        render_kw=render.custom_field | {"size": 4, "placeholder": "Minimum match"},
        description="""
        The minimum CONTINUOUS match length such that the primer shall be considered
        'matching'. Lower numbers result in less specific primers but speed up the 
        search.
        """,
    )
    max_len = IntegerField(
        "Maximal primer length",
        validators=[DataRequired()],
        default=40,
        render_kw=render.custom_field | {"size": 4, "placeholder": "Start"},
        description="""
        Consider only primers that are at most this long. This excludes unlikely
        oligonucleotides (for instance for PCR). Lower numbers speed up the search.
        """,
    )
    reverse_complement = BooleanField(
        "Reverse complement",
        default=False,
        render_kw=render.boolean_field,
        description="""
        Specificy if the original sequence or the reverse complement shall be queried.
        If checked, the target sequence will be turned into the reverse complement 
        before searching.
        """,
    )
    submit = SubmitField("Search", render_kw=render.submit_field)

    def fields(self) -> list:
        return [self.sequence, self.min_match, self.max_len, self.reverse_complement]

    def render(self, action: str = "", method: str = "POST") -> str:
        return render_template(
            "forms/filter.html", form=self, action=action, method=method, csrf=True
        )
