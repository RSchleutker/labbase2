from typing import Optional, Union

from flask import Blueprint, flash, redirect, request, send_file, url_for, current_app as app
from flask_login import current_user, login_required
from labbase2.models import BaseEntity, BaseFile, EntityFile, db
from labbase2.utils.message import Message
from labbase2.utils.permission_required import permission_required
from werkzeug.utils import secure_filename
from pathlib import Path
from sqlalchemy import select

from .forms import EditFile, UploadFile

__all__ = ["bp", "upload_file"]


# The blueprint to register all coming routes with.
bp = Blueprint("files", __name__, url_prefix="/files", template_folder="templates")


def upload_file(form, class_, **kwargs) -> Union[BaseFile, EntityFile]:
    file = form.file.data

    if hasattr(form, "filename") and form.filename.data:
        filename = secure_filename(form.filename.data)
    else:
        filename = secure_filename(file.filename)

    db_file = class_(
        user_id=current_user.id,
        filename_exposed=filename,
        note=form.note.data if hasattr(form, "note") else None,
        **kwargs,
    )

    db.session.add(db_file)
    db.session.commit()

    db_file.set_filename()
    db.session.commit()

    try:
        file.save(db_file.path)
    except Exception as error:
        db.session.delete(db_file)
        db.session.commit()
        raise error

    return db_file


@bp.route("/", defaults={"entity_id": None})
@bp.route("/upload/<int:entity_id>", methods=["POST"])
@login_required
@permission_required("Upload files")
def add(entity_id: Optional[int] = None):
    previous_site = request.referrer

    if entity_id and db.session.get(BaseEntity, id_) is None:
        return f"No entity with ID {entity_id}!", 404

    if not (form := UploadFile()).validate():
        return redirect(previous_site)

    if entity_id is not None:
        file = upload_file(form, EntityFile, entity_id=entity_id)
    else:
        file = upload_file(form, BaseFile)

    flash(f"Successfully uploaded '{file.filename_exposed}'!", "success")

    return redirect(previous_site)


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
@permission_required("Upload files")
def edit(id_: int):
    if not (form := EditFile()).validate():
        return str(form.errors)

    if not (file := db.session.get(BaseFile, id_)):
        return Message.ERROR(f"No file with ID {id_}!")
    elif file.user_id != current_user.id:
        return Message.ERROR("File can only be edited by owner!")
    else:
        file.note = form.note.data
        file.filename_exposed = form.filename.data

    try:
        db.session.commit()
    except Exception as error:
        return str(error)

    return Message.SUCCESS(f"Successfully edited file {file.filename_exposed}!")


@bp.route("/", methods=["GET"], defaults={"id_": None})
@bp.route("/<int:id_>", methods=["GET"])
@login_required
def download(id_: Optional[int] = None):
    if id_ is None:
        return None

    if (file := db.session.get(BaseFile, id_)) is None:
        return f"No file with ID {id_}!"

    as_attachment = request.args.get("download", False, type=bool)

    return send_file(
        file.path,
        download_name=file.filename_exposed,
        as_attachment=as_attachment,
        mimetype=file.mimetype,
    )


@bp.route("/<int:id_>", methods=["DELETE"])
@login_required
@permission_required("Upload files")
def delete(id_: int):
    if (file := db.session.get(BaseFile, id_)) is None:
        return Message.ERROR(f"No file with ID {id_}!")

    try:
        db.session.delete(file)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully deleted file {id_}!")


@bp.route("/delete-orphans", methods=["GET"])
@login_required
def delete_orphans():
    if not current_user.is_admin:
        flash("Only admins can delete orphan files!", "danger")
        return redirect(request.referrer)

    # Get all absolute file paths from the database.
    files_db = [file.path for file in db.session.scalars(select(BaseFile)).all()]

    # Get all files from the upload folder.
    dir = Path(app.instance_path, app.config["UPLOAD_FOLDER"])

    deleted = 0

    for file in dir.iterdir():
        if not file.is_file():
            continue

        for i, file_db in enumerate(files_db):
            if file.samefile(file_db):
                files_db.pop(i)
                break
        else:
            app.logger.debug("Delete file %s", file.name)
            deleted += 1
            file.unlink()

    app.logger.info("Deleted %d orphan files.", deleted)
    flash(f"Deleted {deleted} orphan files.", "success")

    return redirect(request.referrer)
