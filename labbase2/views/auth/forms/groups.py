from functools import cached_property

from flask_wtf import FlaskForm
from sqlalchemy import select
from wtforms.fields import BooleanField, StringField, TextAreaField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, Length, Optional

from labbase2.database import db
from labbase2.forms import filters, rendering
from labbase2.models import Group, Permission, User

__all__ = ["AddGroupForm", "EditGroupForm", "ChangeGroupsForm"]


class ChangeGroupsForm(FlaskForm):

    submit = SubmitField(label="Submit", render_kw=rendering.submit_field)

    def __init__(self, user_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        user = db.session.get(User, user_id)

        # Add a BooleanField for each permission in the db.
        for group in db.session.scalars(
            select(Group).where(Group.name.notin_(["admin", "user"]))
        ).all():
            field_name = f"g_{group.name}"
            field = BooleanField(
                group.name,
                description=group.description,
                default=group in user.groups,
            )
            bound_field = self.meta.bind_field(
                self, field, {"name": field_name, "prefix": self._prefix}
            )
            bound_field.process(None)
            setattr(self, field_name, bound_field)
            self._fields[field_name] = bound_field

    @cached_property
    def selected_groups(self) -> list[Group]:
        groups = [key[2:] for key, value in self.data.items() if key.startswith("g_") and value]
        return db.session.scalars(select(Group).where(Group.name.in_(groups))).all()


class EditGroupForm(FlaskForm):

    description = TextAreaField(
        label="Description",
        validators=[Optional()],
        filters=[filters.strip_input],
        render_kw=rendering.custom_field | {"placeholder": "Some useful description...", "size": 5},
    )
    submit = SubmitField(label="Submit", render_kw=rendering.submit_field)

    def __init__(self, group_name: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if group_name:
            group = db.session.get(Group, group_name)

        # Add a BooleanField for each permission in the db.
        for permission in db.session.scalars(select(Permission)).all():
            field_name = f"p_{permission.name}".replace("-", "_")
            field = BooleanField(
                permission.name,
                description=permission.description,
                default=False if not group_name else permission in group.permissions,
            )
            bound_field = self.meta.bind_field(
                self, field, {"name": field_name, "prefix": self._prefix}
            )
            bound_field.process(None)
            setattr(self, field_name, bound_field)
            self._fields[field_name] = bound_field

    @cached_property
    def selected_permissions(self) -> list[Permission]:
        permissions = [
            key[2:].replace("_", "-")
            for key, value in self.data.items()
            if key.startswith("p_") and value
        ]
        return db.session.scalars(select(Permission).where(Permission.name.in_(permissions))).all()


class AddGroupForm(EditGroupForm):

    name = StringField(
        label="Name",
        validators=[DataRequired(), Length(max=32)],
        filters=[filters.strip_input, filters.make_lower],
        render_kw=rendering.custom_field | {"placeholder": "Group name"},
        description="A unique name for the group. Choose wisely as you cannot change this name later on.",
    )
