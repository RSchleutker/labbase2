from flask_wtf import FlaskForm
from wtforms.fields import BooleanField, SubmitField

from labbase2.forms import render

__all__ = ["EditPermissions"]


class EditPermissions(FlaskForm):

    write_comment = BooleanField("Write Comments", default=False, render_kw=render.boolean_field)
    upload_files = BooleanField("Upload Files", default=False, render_kw=render.boolean_field)
    add_dilutions = BooleanField("Add Dilutions", default=False, render_kw=render.boolean_field)
    add_preparations = BooleanField(
        "Add Preparations", default=False, render_kw=render.boolean_field
    )
    add_glycerol_stocks = BooleanField(
        "Add Glycerol Stocks", default=False, render_kw=render.boolean_field
    )
    add_consumable_batches = BooleanField(
        "Add Batches", default=False, render_kw=render.boolean_field
    )
    add_antibodies = BooleanField("Add Antibodies", default=False, render_kw=render.boolean_field)
    add_plasmid = BooleanField("Add plasmids", default=False, render_kw=render.boolean_field)
    add_oligonucleotide = BooleanField(
        "Add Oligonucleotides", default=False, render_kw=render.boolean_field
    )
    manage_users = BooleanField("Manage Users", default=False, render_kw=render.boolean_field)
    export_content = BooleanField("Export content", default=False, render_kw=render.boolean_field)
    add_requests = BooleanField("Add requests", default=False, render_kw=render.boolean_field)

    submit = SubmitField("Update permissions", render_kw=render.submit_field)
