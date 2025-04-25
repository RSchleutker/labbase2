from flask import Blueprint
from flask_login import login_required

from labbase2.database import db
from labbase2.utils.permission_required import permission_required
from labbase2.forms.utils import errors2messages
from labbase2.models import Request

from .forms import EditRequest

__all__ = ["bp"]


bp = Blueprint("requests", __name__, url_prefix="/request", template_folder="templates")


@bp.route("/<int:entity_id>", methods=["POST"])
@login_required
@permission_required("add-request")
def add(entity_id: int):
    if (form := EditRequest()).validate():
        request = Request(entity_id=entity_id)
        form.populate_obj(request)

        try:
            db.session.add(request)
            db.session.commit()
        except Exception as err:
            return str(err), 400

        return "Successfully added request!", 201

    print(form.errors)
    return errors2messages(form.errors), 400


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
@permission_required("add-request")
def edit(id_: int):
    if (form := EditRequest()).validate():
        if not (request := db.session.get(Request, id_)):
            return f"No request with ID {id_}!", 404

        form.populate_obj(request)

        try:
            db.session.commit()
        except Exception as err:
            return str(err), 400

        return f"Successfully edited request {id_}!", 200

    return errors2messages(form.errors), 400


@bp.route("/<int:id_>", methods=["DELETE"])
@login_required
@permission_required("add-request")
def delete(id_):
    if not (request := db.session.get(Request, id_)):
        return f"No comment with ID {id_}!", 404

    try:
        db.session.delete(request)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return str(err), 400

    return f"Successfully deleted request {id_}!", 200
