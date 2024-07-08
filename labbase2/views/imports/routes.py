import datetime

from .forms import MappingForm

from labbase2.forms.utils import err2message

from labbase2.utils.message import Message
from labbase2.utils.role_required import role_required
from labbase2.models import db
from labbase2.models import Oligonucleotide
from labbase2.models import File
from labbase2.models import ImportJob
from labbase2.models import ColumnMapping
from labbase2.views.files.forms import UploadFile

from flask import Blueprint
from flask import render_template
from flask import request
from flask import flash
from flask import redirect
from flask import url_for
from flask import send_file
from flask import current_app as app
from flask_login import login_required
from flask_login import current_user
from sqlalchemy import func
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from Bio.Seq import Seq

import pandas as pd
from pathlib import Path


__all__ = ["bp"]


bp = Blueprint(
    "imports",
    __name__,
    url_prefix="/imports",
    template_folder="templates"
)


@bp.route("/", methods=["GET"])
@login_required
def index():
    return render_template(
        "imports/main.html",
        title="Pending imports",
        jobs=current_user.import_jobs
    )


@bp.route("/upload/<string:type_>", methods=["GET", "POST"])
@login_required
def upload(type_: str):
    form = UploadFile()

    if form.validate_on_submit():
        data = form.file.data
        file = File(user_id=current_user.id, original_filename=secure_filename(data.filename))

        # A database ID is assigned to the file now. Use that to create filename to store file.
        try:
            db.session.add(file)
            db.session.flush()
        except Exception as error:
            flash(Message.ERROR(error))
        else:
            file.set_filename()

        # Next, try to save the file to disk.
        try:
            data.save(file.path)
        except Exception as error:
            db.session.rollback()
            flash(Message.ERROR(error))
            return redirect(request.referrer)

        # Lastly, commit changes to database. Don't know if this requires a try-except block
        # since at this point the flush was already successful. But better be safe than sorry.
        try:
            db.session.commit()
        except Exception as error:
            file.path.unlink(missing_ok=True)
            db.session.rollback()
            return redirect(request.referrer)

        # Now create the ImportJob.
        import_job = ImportJob(
            user_id=current_user.id,
            file_id=file.id,
            entity_type="oligonucleotide"
        )

        for field in Oligonucleotide.importable_fields():
            import_job.mappings.append(ColumnMapping(mapped_field=field))

        db.session.add(import_job)
        db.session.commit()

    return redirect(url_for("imports.index"))


@bp.route("/edit/<int:id_>", methods=["GET", "POST"])
@login_required
def edit(id_: int):
    import_job = ImportJob.query.get(id_)
    file = import_job.file

    match file.path.suffix:
        case ".csv":
            table = pd.read_csv(file.path)
        case ".xls" | ".xlsx":
            table = pd.read_excel(file.path, engine="openpyxl")

    fields = [mapping.mapped_field for mapping in import_job.mappings]
    defaults = [mapping.input_column for mapping in import_job.mappings]
    choices = [(str(col), str(col)) for col in table.columns]
    form = MappingForm(data={"mapping": defaults}, fields=fields, choices=choices)

    if form.validate_on_submit():
        for mapping, field in zip(import_job.mappings, form.mapping):
            mapping.input_column = None if field.data == "None" else field.data
            db.session.commit()

    return render_template(
        "imports/edit_import.html",
        title="Import Oligonucleotides",
        job=import_job,
        table=table,
        form=form
    )


@bp.route("/import/<int:id_>", methods=["GET", "POST"])
@login_required
def execute(id_: int):
    job = ImportJob.query.get(id_)

    if job.user_id != current_user.id:
        flash(Message.ERROR("You are not authorized to execute this import."))
        return redirect(url_for(".index"))

    match job.entity_type:
        case "oligonucleotide":
            cls = Oligonucleotide

    mappings = ColumnMapping.query.filter(
        ColumnMapping.job_id == job.id,
        ColumnMapping.input_column.isnot(None)
    )
    fields = [mapping.mapped_field for mapping in mappings]
    colmns = [mapping.input_column for mapping in mappings]

    file = job.file

    match file.path.suffix:
        case ".csv":
            table = pd.read_csv(file.path)
        case ".xls" | ".xlsx":
            table = pd.read_excel(file.path, engine="openpyxl")

    table = table[colmns]
    table.columns = fields

    imported_entities = []

    for row in table.itertuples(index=False):
        row = row._asdict()
        for key, value in row.items():
            if pd.isnull(value):
                row[key] = None

            if isinstance(value, str):
                row[key] = value.strip()

        origin = f"Created from file {file.original_filename} by {current_user.username}."
        entity = cls(origin=origin, **row)
        imported_entities.append(entity)

    try:
        db.session.add_all(imported_entities)
        db.session.commit()
    except Exception as error:
        print(error)
        db.session.rollback()
    else:
        db.session.delete(job)
        db.session.commit()

    return redirect(url_for(".index"))


@bp.route("/delete/<int:id_>", methods=["DELETE"])
@login_required
def delete(id_: int):
    if not (job := ImportJob.query.get(id_)):
        return Message.ERROR(f"No import with ID {id_}!")
    elif job.user_id != current_user.id:
        return Message.ERROR("Only owner can delete import!")
    else:
        try:
            db.session.delete(job)
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            return Message.ERROR(str(err))
        else:
            return Message.SUCCESS(f"Successfully deleted import {id_}!")

