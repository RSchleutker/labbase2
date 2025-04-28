from flask import render_template
from flask_wtf import FlaskForm
from wtforms.fields import BooleanField, Field, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import NumberRange, Optional

from . import filters, rendering

__all__ = ["FilterForm", "EditEntityForm"]


class FilterForm(FlaskForm):
    """Base class for filter forms

    Attributes
    ----------
    id: IntegerField
    ascending: BooleanField
    order_by: SelectField
    submit: SelectField
    download_csv: SelectField
    download_pdf: SelectField
    download_excel: SelectField
    """

    id = IntegerField(
        label="ID",
        validators=[Optional(), NumberRange(min=1)],
        render_kw=rendering.custom_field | {"placeholder": "ID"},
        description="Internal database ID.",
    )
    ascending = BooleanField(
        label="Sort ascending",
        render_kw=rendering.boolean_field,
        default=True,
        description="Uncheck to sort results in descending order.",
    )
    order_by = SelectField(
        label="Order by",
        choices=[("id", "ID")],
        default="id",
        render_kw=rendering.select_field,
        description="The column by which the results shall be ordered.",
    )
    submit = SubmitField(label="Submit", render_kw=rendering.submit_field)
    download_csv = SubmitField(label="Export to CSV", render_kw=rendering.submit_field)
    download_pdf = SubmitField(label="Export to PDF", render_kw=rendering.submit_field)
    download_excel = SubmitField(label="Export to Excel", render_kw=rendering.submit_field)

    def fields(self) -> list[Field]:
        """Returns all fields for rendering"""

        raise NotImplementedError

    def render(self, action: str = "", method: str = "GET") -> str:
        """Render the form to HTML

        Parameters
        ----------
        action: str, optional
            The target URL for the form.
        method: str, optional
            The request method, e.g. 'GET' or 'POST'.

        Returns
        -------
        str
            The rendered HTML.
        """

        return render_template("forms/filter.html", form=self, action=action, method=method)


class EditEntityForm(FlaskForm):
    """The base form to edit entries in the database.

    Attributes
    ----------
    label: StringField
    submit: SubmitField
    """

    label = StringField(
        label="Label",
        validators=[Optional()],
        filters=[filters.strip_input],
        render_kw=rendering.custom_field | {"placeholder": "Name"},
        description="Must be unique among ALL database entries.",
    )
    submit = SubmitField(label="Submit", render_kw=rendering.submit_field)
