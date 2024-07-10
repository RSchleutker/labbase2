import datetime

from .forms import EditDilution

from labbase2.models import db
from labbase2.models import Dilution
from labbase2.forms.utils import err2message

from flask import Blueprint
from flask_login import current_user
from flask_login import login_required


__all__: list = ["bp"]


bp = Blueprint(
    "dilutions",
    __name__,
    url_prefix="/antibodies",
    template_folder="templates"
)


@bp.route("<int:antibody_id>/dilution/", methods=["POST"])
@login_required
def add(antibody_id: int):
    if (form := EditDilution()).validate():
        dilution = Dilution(
            antibody_id=antibody_id,
            user_id=current_user.id
        )
        form.populate_obj(dilution)

        try:
            db.session.add(dilution)
            db.session.commit()
        except Exception as err:
            return str(err), 400
        else:
            return f"Successfully added dilution!", 201

    else:
        print(form.errors)
        return err2message(form.errors), 400


@bp.route("/<int:antibody_id>/dilution/<int:id_>", methods=["PUT"])
@login_required
def edit(antibody_id: int, id_: int):
    if (form := EditDilution()).validate():
        if not (dilution := Dilution.query.get(id_)):
            return f"No dilution with ID {id_}!", 404
        elif dilution.user_id != current_user.id:
            return "Dilution can only be edited by source user!", 401
        else:
            form.populate_obj(dilution)

        try:
            db.session.commit()
        except Exception as err:
            return str(err), 400
        else:
            return f"Successfully edited dilution!", 200

    else:
        return err2message(form.errors), 400


@bp.route("<int:antibody_id>/dilution/<int:id_>", methods=["DELETE"])
@login_required
def delete(antibody_id: int, id_: int):
    if not (dilution := Dilution.query.get(id_)):
        return f"No dilution with ID {id_}!", 404
    if dilution.antibody_id != antibody_id:
        return f"Dilution belongs to another antibody!", 400
    elif dilution.user_id != current_user.id:
        return "Dilution can only be edeleted by source user!", 401
    else:
        try:
            db.session.delete(dilution)
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            print(err)
            return str(err), 400
        else:
            return f"Successfully deleted dilution {id_}!", 200
