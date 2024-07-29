from labbase2.forms.utils import RENDER_KW
from labbase2.forms.utils import RENDER_KW_BTN
from labbase2.models import User
from labbase2.models import Permission
from labbase2.models.user import user_permissions

from flask_wtf import FlaskForm
from wtforms.form import BaseForm
from wtforms.fields import SubmitField
from wtforms.fields import BooleanField
from wtforms.fields import FieldList


__all__ = ["EditPermissions"]


class EditPermissions(FlaskForm):

    write_comment = BooleanField("Write Comments", default=False)
    upload_files = BooleanField("Upload Files", default=False)
    add_dilutions = BooleanField("Add Dilutions", default=False)
    add_preparations = BooleanField("Add Preparations", default=False)
    add_glycerol_stocks = BooleanField("Add Glycerol Stocks", default=False)
    add_consumable_batches = BooleanField("Add Batches", default=False)
    add_antibodies = BooleanField("Add Antibodies", default=False)
    add_plasmid = BooleanField("Add plasmids", default=False)
    add_oligonucleotide = BooleanField("Add Oligonucleotides", default=False)
    manage_users = BooleanField("Manage Users", default=False)
    export_content = BooleanField("Export content", default=False)
    add_requests = BooleanField("Add requests", default=False)

    submit = SubmitField("Update permissions", render_kw=RENDER_KW_BTN)
