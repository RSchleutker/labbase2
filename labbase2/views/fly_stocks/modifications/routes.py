from flask import Blueprint
from flask_login import current_user, login_required

from labbase2.forms.utils import errors2messages
from labbase2.models import Modification, db

from .forms import EditModification

__all__ = ["bp"]


# The blueprint to register all coming blueprints with.
bp = Blueprint("modifications", __name__, url_prefix="/modifications", template_folder="templates")


@bp.route("/<int:flystock_id>", methods=["POST"])
@login_required
def add(flystock_id: int):
    if (form := EditModification()).validate():
        modification = Modification(fly_id=flystock_id, user_id=current_user.id)
        form.populate_obj(modification)

        try:
            db.session.add(modification)
            db.session.commit()
        except Exception as error:
            return str(error), 400

        return "Successfully added modification!", 201

    return errors2messages(form.errors), 400


@bp.route("/<int:id>", methods=["PUT"])
@login_required
def edit(id_: int):
    if (form := EditModification()).validate():
        if (modification := db.session.get(Modification, id_)) is None:
            return f"No preparation with ID {id_}!", 404
        if modification.user_id != current_user.id:
            return "Modification can only be edited by source user!", 400

        form.populate_obj(modification)

        try:
            db.session.commit()
        except Exception as error:
            return str(error), 400

        return "Successfully edited modification!", 200

    return errors2messages(form.errors), 400


@bp.route("/<int:flystock_id>/<int:id_>", methods=["DELETE"])
@login_required
def delete(flystock_id: int, id_: int):
    if (modification := db.session.get(Modification, id_)) is None:
        return f"No modification with ID {id}!", 404
    if modification.user_id != current_user.id:
        return "Modification can only be deleted by source user!", 400

    try:
        db.session.delete(modification)
        db.session.commit()
    except Exception as error:
        return str(error), 400

    return f"Successfully deleted modification {id}!", 200
