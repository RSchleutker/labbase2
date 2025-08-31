import pandas as pd
from flask import Blueprint
from flask import current_app as app
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from labbase2.database import db
from labbase2.models import BaseFile, ColumnMapping, ImportJob
from labbase2.utils.message import Message
from labbase2.utils.permission_required import permission_required
from labbase2.views.files.forms import UploadFile
from labbase2.views.files.routes import upload_file

from .forms import MappingForm

__all__ = ["bp"]


bp = Blueprint("imports", __name__, url_prefix="/imports", template_folder="templates")


@bp.route("/", methods=["GET"])
@login_required
def index():
    return render_template(
        "imports/main.html",
        title="Pending imports",
        jobs=current_user.import_jobs,
    )


@bp.route("/upload/<string:type_>", methods=["POST"])
@login_required
@permission_required("upload-file")
def upload(type_: str):
    try:
        entity_class = ImportJob.get_entity_class(type_=type_)
    except ValueError as error:
        flash(str(error), "danger")
        app.logger.warning("Tried to import from file for unsupported entity type: %s", type_)
        return redirect(request.referrer)

    form = UploadFile()

    if not form.validate():
        return redirect(request.referrer)

    file: BaseFile = upload_file(form, BaseFile)

    try:
        file.read_table()
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

    for field in entity_class.importable_fields():
        import_job.mappings.append(ColumnMapping(mapped_field=field))

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
        flash("You are not authorized to work on this import!", "danger")
        return redirect(url_for(".index"))

    try:
        table = import_job.file.read_table()
    except ValueError as error:
        flash(str(error), "danger")
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

    try:
        entity_class = job.class_
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for(".index"))

    fields, columns = job.get_mapping()

    try:
        table = job.file.read_table()
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(request.referrer)

    table = table[columns]  # Reorder columns in the imported file.
    table.columns = fields  # Rename the columns in the file to match the db fields.

    imported = 0

    for row in table.itertuples(index=False):
        entity = entity_class.from_row(row=row)

        try:
            db.session.add(entity)
            db.session.commit()
        except IntegrityError as error:
            flash(
                f"Couldn't import row with label {entity.label} due to integrity error.", "danger"
            )
            app.logger.info("Integrity error during import: %s", error)
            db.session.rollback()
            continue
        except Exception as error:
            flash(f"Couldn't import row with label {entity.label} due to unknown error.", "danger")
            app.logger.info("Unknown error during import: %s", error)
            db.session.rollback()
            continue
        else:
            imported += 1

    db.session.delete(job)
    db.session.commit()

    flash(f"Successfully imported {imported} rows from file!", "success")
    app.logger.info(
        "Imported %d entities (%s) from file (%s).",
        imported,
        entity_class.__name__,
        job.file.filename_exposed,
    )

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

    return Message.SUCCESS(f"Successfully deleted import {id_}!")
