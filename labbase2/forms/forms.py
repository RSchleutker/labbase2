from .utils import RENDER_KW
from .utils import RENDER_KW_BTN
from .filters import strip_input

from flask import render_template
from flask_wtf import FlaskForm
from wtforms.fields import Field
from wtforms.fields import SubmitField
from wtforms.fields import BooleanField
from wtforms.fields import IntegerField
from wtforms.fields import StringField
from wtforms.fields import SelectField
from wtforms.fields import FieldList
from wtforms.validators import Optional
from wtforms.validators import NumberRange


__all__: list[str] = ["BaseForm", "FilterForm", "EditForm", "EditEntityForm"]


class BaseForm(FlaskForm):
    submit = SubmitField(
        label="Submit",
        render_kw=RENDER_KW_BTN | {"id": "form-submit"}
    )

    def render(self, action: str = "", method: str = "GET") -> str:
        raise NotImplementedError


class FilterForm(BaseForm):
    id = IntegerField(
        label="ID",
        validators=[Optional(), NumberRange(min=1)],
        render_kw=RENDER_KW | {"id": "filter-form-id",
                               "placeholder": "ID"},
        description="Internal database ID."
    )
    ascending = BooleanField(
        label="Sort ascending",
        render_kw={"class": "form-check-input", "id": "filter-form-ascending"},
        default=True,
        description="Uncheck to sort results in descending order."
    )
    order_by = SelectField(
        label="Order by",
        choices=[('id', 'ID')],
        default='id',
        render_kw={"size": 1},
        description="The column by which the results shall be ordered."
    )
    download_csv = SubmitField(
        label="Export to CSV",
        render_kw=RENDER_KW_BTN | {"id": "filter-form-download-csv"}
    )
    download_labels = SubmitField(
        label="Export to Labels",
        render_kw=RENDER_KW_BTN | {"id": "filter-form-download-labels"}
    )
    download_pdf = SubmitField(
        label="Export to PDF",
        render_kw=RENDER_KW_BTN | {"id": "filter-form-download-pdf"}
    )
    download_excel = SubmitField(
        label="Export to Excel",
        render_kw=RENDER_KW_BTN | {"id": "filter-form-download-excel"}
    )

    def fields(self) -> list[Field]:
        raise NotImplementedError

    def render(self) -> str:
        return render_template("forms/filter.html", form=self, method="GET")


class EditForm(BaseForm):
    delete = SubmitField(
        label="Delete",
        render_kw=RENDER_KW_BTN | {"id": "edit-form-delete"}
    )


class EditEntityForm(EditForm):
    label = StringField(
        label="Label",
        validators=[Optional()],
        filters=[strip_input],
        render_kw=RENDER_KW | {"id": "edit-form-label",
                               "placeholder": "Name"},
        description="Must be unique among ALL database entries."
    )
