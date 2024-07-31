from flask import render_template
from flask_wtf import FlaskForm
from wtforms.fields import (
    BooleanField,
    Field,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import NumberRange, Optional

from . import filters, render

__all__ = ["BaseForm", "FilterForm", "EditEntityForm"]


class BaseForm(FlaskForm):
    submit = SubmitField(label="Submit", render_kw=render.submit_field)

    def render(self, action: str = "", method: str = "GET") -> str:
        raise NotImplementedError


class FilterForm(BaseForm):
    id = IntegerField(
        label="ID",
        validators=[Optional(), NumberRange(min=1)],
        render_kw=render.custom_field | {"placeholder": "ID"},
        description="Internal database ID.",
    )
    ascending = BooleanField(
        label="Sort ascending",
        render_kw=render.boolean_field,
        default=True,
        description="Uncheck to sort results in descending order.",
    )
    order_by = SelectField(
        label="Order by",
        choices=[("id", "ID")],
        default="id",
        render_kw=render.select_field,
        description="The column by which the results shall be ordered.",
    )
    download_csv = SubmitField(label="Export to CSV", render_kw=render.submit_field)
    download_pdf = SubmitField(label="Export to PDF", render_kw=render.submit_field)
    download_excel = SubmitField(label="Export to Excel", render_kw=render.submit_field)

    def fields(self) -> list[Field]:
        raise NotImplementedError

    def render(self, action: str = "", method: str = "GET") -> str:
        return render_template("forms/filter.html", form=self, method=method)


class EditEntityForm(BaseForm):
    label = StringField(
        label="Label",
        validators=[Optional()],
        filters=[filters.strip_input],
        render_kw=render.custom_field | {"placeholder": "Name"},
        description="Must be unique among ALL database entries.",
    )
