from .forms import UploadFile
from .forms import EditFile

from labbase2.models import db
from labbase2.models import BaseEntity
from labbase2.models import File
from labbase2.models import FileDocument
from labbase2.models import FileImage
from labbase2.models import FilePlasmid
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


__all__ = ["bp"]


# The blueprint to register all coming routes with.
bp = Blueprint(
    "files",
    __name__,
    url_prefix="/files",
    template_folder="templates"
)


@bp.route("/", defaults={"entity_id": None})
@bp.route("/attach/<int:entity_id>", methods=["POST"])
@login_required
def add(entity_id: Optional[int] = None):
    previous_site = request.referrer

    if entity_id and BaseEntity.query.get(entity_id) is None:
        return f"No entity with ID {entity_id}!", 404

    if not (form := UploadFile()).validate():
        return redirect(previous_site)

    data = form.file.data
    save_filename = Path(secure_filename(data.filename))

    # Get appropriate file class based on suffix of uploaded file.
    match save_filename.suffix.lower():
        case ".pdf":
            file_class = FileDocument
        case ".jpg" | ".jpeg" | ".png" | ".tif" | ".tiff":
            file_class = FileImage
        case ".gb" | ".gbk" | ".dna" | ".xdna":
            file_class = FilePlasmid
        case _:
            file_class = File

    # Create file instance without internal filename. That will be later assigned based on the
    # database ID.
    file = file_class(
        entity_id=entity_id,
        user_id=current_user.id,
        note=form.note.data,
        original_filename=str(save_filename)
    )

    # A database ID should be assigned to the file now. Use that to create filename to store file.
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
        return redirect(previous_site)

    # Lastly, commit changes to database. Don't know if this requires a try-except block since at
    # this point the flush was already successful. But better be safe than sorry.
    try:
        db.session.commit()
    except Exception as error:
        file.path.unlink(missing_ok=True)
        db.session.rollback()
        return str(error), 400

    return redirect(previous_site)


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
def edit(id_: int):
    if not (form := EditFile()).validate():
        return str(form.errors), 400

    if not (file := File.query.get(id_)):
        return f"No file with ID {id_}!", 404
    elif file.user_id != current_user.id:
        return "File can only be edited by owner!", 400
    else:
        form.populate_obj(file)

    try:
        db.session.commit()
    except Exception as error:
        return str(error), 400
    else:
        return f"Successfully edited file {file.original_filename}!", 200


@bp.route("/<int:id_>", methods=["GET"])
@login_required
def download(id_: int):
    if not (file := File.query.get(id_)):
        return f"No file with ID {id_}!", 404

    as_attachment = request.args.get("download", False, type=bool)

    return send_from_directory(
        file.path.parent,
        file.filename,
        as_attachment=as_attachment,
        mimetype=file.mimetype
    )

    # match request.args.get("format", None):
    #     case "bytes" | None:
    #         return Response(file.data, mimetype="image/png")
    #     case "base64":
    #         data = base64.b64encode(file.data)
    #         img = "<img src='data:image/png;base64,{}' style='width: 100%; height: auto'/>"
    #         return img.format(data.decode())
    #     case _:
    #         return


@bp.route("/<int:id_>", methods=["DELETE"])
@login_required
def delete(id_: int):
    if not (file := File.query.get(id_)):
        return f"No file with ID {id_}!", 404

    try:
        db.session.delete(file)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return str(error)
    else:
        return f"Successfully deleted file {id_}!", 200
