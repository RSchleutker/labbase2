from flask_wtf import FlaskForm
from labbase2.forms import render
from wtforms.fields import FieldList, SelectField, SubmitField

__all__ = ["MappingForm"]


class MappingForm(FlaskForm):
    """A form to map columns from uploaded files to the fields of an entity.

    Parameters
    ----------
    fields : list[str]
        A list of names to be shown as labels in the forms. This represents the
        importable fields
        of the respective entity (e.g. plasmid). However, the entity fields are not
        matched
        against this list. Thus, the names can be changed to increase readability. By
        default,
        dashes and underscores are replace by spaces and the names are capitalized.
    choices : list[tuple[str, str]]
        A list of choices to choose from for the mapping. This should be the column
        names of the
        uploaded file.

    Notes
    -----
    The class should be instantiated with the default values for each field.

    >>> defaults = ["name", "-", "-"]
    >>> MappingForm(data={"mapping": defaults})

    The defaults are usually taken from the database and represent the saved state of
    the user from his last edit of this import. The order of the default has to match
    the order of the `fields` parameter.

    IMPORTANT: The mapping field is a `FieldList` of `SelectField`s. In order to allow
    instantiating the class with default values with dynamic choices (they differ for
    each uploaded file), the `SelectField`s do not validate the provided default
    values. Thus, extra care must be taken to ensure integrity of the instance.
    """

    mapping = FieldList(
        SelectField(
            "Name",
            choices=[(None, "-")],
            default=None,
            validate_choice=False,
            render_kw={"class": "form-select form-select-sm"},
        )
    )
    submit = SubmitField(label="Update mapping", render_kw=render.submit_field)

    def __init__(
        self, fields: list[str], choices: list[tuple[str, str]], *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        if len(fields) != len(self.mapping):
            raise ValueError("'fields' must have the same length as mapping")

        for field, mapping in zip(fields, self.mapping):
            # Increase readability of the label.
            label = field.replace("_", " ")
            label = label.replace("-", " ")

            mapping.choices += choices
            mapping.label = label.capitalize()
