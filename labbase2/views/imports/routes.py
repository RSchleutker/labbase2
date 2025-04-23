from functools import partial

import pandas as pd
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from labbase2.models import (
    Antibody,
    BaseFile,
    Chemical,
    ColumnMapping,
    FlyStock,
    ImportJob,
    Oligonucleotide,
    Plasmid,
    db,
)
from labbase2.utils.message import Message
from labbase2.utils.permission_required import permission_required
from labbase2.views.files.forms import UploadFile
from labbase2.views.files.routes import upload_file
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .forms import MappingForm

__all__ = ["bp"]


bp = Blueprint("imports", __name__, url_prefix="/imports", template_folder="templates")


@bp.route("/", methods=["GET"])
@login_required
def index():
    return render_template("imports/main.html", title="Pending imports", jobs=current_user.import_jobs)


@bp.route("/upload/<string:type_>", methods=["POST"])
@login_required
@permission_required("Upload files")
def upload(type_: str):
    form = UploadFile()

    match type_.lower():
        case "antibody":
            entity_cls = Antibody
        case "chemical":
            entity_cls = Chemical
        case "fly_stock":
            entity_cls = FlyStock
        case "oligonucleotide":
            entity_cls = Oligonucleotide
        case "plasmid":
            entity_cls = Plasmid
        case _:
            flash(f"Unknown type {type}", "danger")
            return redirect(request.referrer)

    if not form.validate():
        return redirect(request.referrer)

    file = upload_file(form, BaseFile)

    # Try to read the file.
    match file.path.suffix:
        case ".csv":
            read_fnc = pd.read_csv
        case ".xls" | ".xlsx":
            read_fnc = partial(pd.read_excel, engine="openpyxl")
        case _:
            flash("Unknown file type!", "danger")
            return redirect(request.referrer)

    try:
        read_fnc(file.path)
    except pd.errors.ParserError:
        flash("File could not be parsed properly!", "danger")
        db.session.delete(file)
        db.session.commit()
        return redirect(request.referrer)
    except pd.errors.EmptyDataError:
        flash("File is empty or has improper header!", "danger")
        db.session.delete(file)
        db.session.commit()
        return redirect(request.referrer)
    except Exception as error:
        flash(f"An unknown error occurred during file parsing! {error}", "danger")
        db.session.delete(file)
        db.session.commit()
        return redirect(request.referrer)

    # Now create the ImportJob.
    import_job = ImportJob(user_id=current_user.id, file_id=file.id, entity_type=type_)

    for field in entity_cls.importable_fields():
        column_mapping = ColumnMapping(mapped_field=field)
        import_job.mappings.append(column_mapping)

    db.session.add(import_job)
    db.session.commit()

    return redirect(url_for("imports.edit", id_=import_job.id))


@bp.route("/edit/<int:id_>", methods=["GET", "POST"])
@login_required
def edit(id_: int):
    import_job = db.session.get(ImportJob, id_)

    if import_job is None:
        flash(f"No import with ID {id_}!", "danger")
        return redirect(url_for(".index"))
    if import_job.user_id != current_user.id:
        flash(f"You are not authorized to work on this import!", "danger")
        return redirect(url_for(".index"))

    file = import_job.file

    match file.path.suffix:
        case ".csv":
            table = pd.read_csv(file.path)
        case ".xls" | ".xlsx":
            table = pd.read_excel(file.path, engine="openpyxl")
        case _:
            flash("Unknown file type!", "danger")
            return redirect(url_for(".index"))

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
        form=form,
    )


@bp.route("/import/<int:id_>", methods=["GET", "POST"])
@login_required
def execute(id_: int):
    job = db.session.get(ImportJob, id_)

    if job.user_id != current_user.id:
        flash(Message.ERROR("You are not authorized to execute this import."))
        return redirect(url_for(".index"))

    match job.entity_type:
        case "antibody":
            entity_cls = Antibody
        case "chemical":
            entity_cls = Chemical
        case "fly_stock":
            entity_cls = FlyStock
        case "oligonucleotide":
            entity_cls = Oligonucleotide
        case "plasmid":
            entity_cls = Plasmid
        case _:
            flash(f"Unknown entity type {job.entity_type}!", "danger")
            return redirect(request.referrer)

    mappings = db.session.scalars(
        select(ColumnMapping).where(ColumnMapping.job_id == job.id & ColumnMapping.input_column.isnot(None))
    )
    fields = [mapping.mapped_field for mapping in mappings]
    colmns = [mapping.input_column for mapping in mappings]

    file = job.file

    match file.path.suffix:
        case ".csv":
            read_fnc = pd.read_csv
        case ".xls" | ".xlsx":
            read_fnc = partial(pd.read_excel, engine="openpyxl")
        case _:
            flash("Unknown file type!", "danger")
            return redirect(request.referrer)

    table = read_fnc(file.path)

    table = table[colmns]
    table.columns = fields

    successfull = 0
    unsuccessfull = 0

    for row in table.itertuples(index=False):
        row = row._asdict()

        for key, value in row.items():
            if pd.isnull(value):
                row[key] = None
            if isinstance(value, str):
                row[key] = value.strip()

        origin = f"Created from file {file.filename_exposed} by {current_user.username}."
        entity = entity_cls(origin=origin, **row)

        try:
            db.session.add(entity)
            db.session.commit()
        except IntegrityError:
            unsuccessfull += 1
            db.session.rollback()
            continue
        except Exception as error:
            unsuccessfull += 1
            db.session.rollback()
            return redirect(url_for(".index"))
        else:
            successfull += 1

    db.session.delete(job)
    db.session.commit()

    return redirect(url_for(".index"))


@bp.route("/delete/<int:id_>", methods=["DELETE"])
@login_required
def delete(id_: int):
    if not (job := db.session.get(ImportJob, id_)):
        return Message.ERROR(f"No import with ID {id_}!")

    if job.user_id != current_user.id:
        return Message.ERROR("Only owner can delete import!")

    try:
        db.session.delete(job)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return Message.ERROR(str(err))
    else:
        return Message.SUCCESS(f"Successfully deleted import {id_}!")
