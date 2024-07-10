from .forms import EditRequest

from labbase2.models import db
from labbase2.models import Request
from labbase2.forms.utils import err2message

from flask import Blueprint
from flask_login import login_required


__all__: list = ["bp"]


bp = Blueprint(
    "requests",
    __name__,
    url_prefix="/request",
    template_folder="templates"
)


@bp.route("/<int:entity_id>", methods=["POST"])
@login_required
def add(entity_id: int):
    if (form := EditRequest()).validate():
        request = Request(entity_id=entity_id)
        form.populate_obj(request)

        try:
            db.session.add(request)
            db.session.commit()
        except Exception as err:
            return str(err), 400
        else:
            return f"Successfully added request!", 201

    else:
        print(form.errors)
        return err2message(form.errors), 400


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
def edit(id_: int):
    if (form := EditRequest()).validate():
        if not (request := Request.query.get(id_)):
            return f"No request with ID {id_}!", 404
        else:
            form.populate_obj(request)

        try:
            db.session.commit()
        except Exception as err:
            return str(err), 400
        else:
            return f"Successfully edited request {id_}!", 200
    else:
        return err2message(form.errors), 400


@bp.route("/<int:id_>", methods=["DELETE"])
@login_required
def delete(id_):
    if not (request := Request.query.get(id_)):
        return f"No comment with ID {id_}!", 404
    else:
        try:
            db.session.delete(request)
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            return str(err), 400
        else:
            return f"Successfully deleted request {id_}!", 200
