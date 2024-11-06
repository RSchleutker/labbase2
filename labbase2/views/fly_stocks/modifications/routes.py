from app.forms.utils import err2message
from app.models import Modification, db
from flask import Blueprint
from flask_login import current_user, login_required

from .forms import EditModification

__all__: list[str] = ["bp"]


# The blueprint to register all coming blueprints with.
bp = Blueprint(
    "modifications", __name__, url_prefix="/modifications", template_folder="templates"
)


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
        else:
            return "Successfully added modification!", 201
    else:
        return err2message(form.errors), 400


@bp.route("/<int:id>", methods=["PUT"])
@login_required
def edit(id: int):
    if (form := EditModification()).validate():
        if (modification := Modification.query.get(id)) is None:
            return f"No preparation with ID {id}!", 404
        elif modification.user_id != current_user.id:
            return "Modification can only be edited by source user!", 400
        else:
            form.populate_obj(modification)

        try:
            db.session.commit()
        except Exception as error:
            return str(error), 400
        else:
            return f"Successfully edited modification!", 200
    else:
        return err2message(form.errors), 400


@bp.route("/<int:flystock_id>/<int:id>", methods=["DELETE"])
@login_required
def delete(flystock_id: int, id: int):
    if (modification := Modification.query.get(id)) is None:
        return f"No modification with ID {id}!", 404
    elif modification.user_id != current_user.id:
        return "Modification can only be deleted by source user!", 400
    else:
        try:
            db.session.delete(modification)
            db.session.commit()
        except Exception as error:
            return str(error), 400
        else:
            return f"Successfully deleted modification {id}!", 200
