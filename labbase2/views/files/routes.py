from .forms import UploadFile
from .forms import EditFile

from labbase2.models import db
from labbase2.models import BaseEntity
from labbase2.models import BaseFile
from labbase2.models import EntityFile
from labbase2.utils.message import Message

from flask import Blueprint
from flask import flash
from flask import request
from flask import redirect
from flask import send_from_directory
from flask_login import login_required
from flask_login import current_user
from werkzeug.utils import secure_filename
from pathlib import Path

from typing import Optional
from typing import Union


__all__ = ["bp"]


# The blueprint to register all coming routes with.
bp = Blueprint(
    "files",
    __name__,
    url_prefix="/files",
    template_folder="templates"
)


def upload_file(form: UploadFile, class_, **kwargs) -> Union[BaseFile, EntityFile]:
    file = form.file.data

    if form.filename.data:
        filename = secure_filename(form.filename.data)
    else:
        filename = secure_filename(file.filename)

    db_file = class_(
        user_id=current_user.id,
        filename_exposed=filename,
        note=form.note.data,
        **kwargs
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
def add(entity_id: Optional[int] = None):
    previous_site = request.referrer

    if entity_id and BaseEntity.query.get(entity_id) is None:
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
def edit(id_: int):
    if not (form := EditFile()).validate():
        return str(form.errors), 400

    if not (file := BaseFile.query.get(id_)):
        return f"No file with ID {id_}!", 404
    elif file.user_id != current_user.id:
        return "File can only be edited by owner!", 400
    else:
        file.note = form.note.data
        file.filename_exposed = form.filename.data

    try:
        db.session.commit()
    except Exception as error:
        return str(error), 400

    return f"Successfully edited file {file.filename_exposed}!", 200


@bp.route("/<int:id_>", methods=["GET"])
@login_required
def download(id_: int):
    if not (file := BaseFile.query.get(id_)):
        return f"No file with ID {id_}!", 404

    as_attachment = request.args.get("download", False, type=bool)

    return send_from_directory(
        file.path.parent,
        file.filename_exposed,
        as_attachment=as_attachment,
        mimetype=file.mimetype
    )


@bp.route("/<int:id_>", methods=["DELETE"])
@login_required
def delete(id_: int):
    if (file := BaseFile.query.get(id_)) is None:
        return Message.ERROR(f"No file with ID {id_}!")

    try:
        db.session.delete(file)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return Message.ERROR(error)

    return f"Successfully deleted file {id_}!", 200
