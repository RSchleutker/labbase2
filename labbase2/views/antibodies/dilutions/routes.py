from .forms import EditDilution

from labbase2.utils.message import Message
from labbase2.utils.permission_required import permission_required
from labbase2.models import db
from labbase2.models import Dilution

from flask import Blueprint
from flask_login import current_user
from flask_login import login_required


__all__ = ["bp"]


bp = Blueprint(
    "dilutions",
    __name__,
    url_prefix="/dilution",
    template_folder="templates"
)


@bp.route("/<int:antibody_id>", methods=["POST"])
@login_required
@permission_required("Add dilution")
def add(antibody_id: int):
    form = EditDilution()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    dilution = Dilution(antibody_id=antibody_id, user_id=current_user.id)
    form.populate_obj(dilution)

    try:
        db.session.add(dilution)
        db.session.commit()
    except Exception as error:
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully added dilution to '{dilution.antibody.label}'!")


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
@permission_required("Add dilution")
def edit(id_: int):
    form = EditDilution()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    if (dilution := Dilution.query.get(id_)) is None:
        return Message.ERROR(f"No dilution found with ID {id_}!")

    if dilution.user_id != current_user.id:
        return Message.ERROR(
            "Dilutions can only be edited by owner! Consider adding a new dilution instead."
        )

    form.populate_obj(dilution)

    try:
        db.session.commit()
    except Exception as error:
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully edited dilution '{dilution.id}'!")


@bp.route("<int:id_>", methods=["DELETE"])
@login_required
@permission_required("Add dilution")
def delete(id_: int):
    if (dilution := Dilution.query.get(id_)) is None:
        return Message.ERROR(f"No dilution found with ID {id_}!")

    if dilution.user_id != current_user.id:
        return Message.ERROR("Dilutions can only be deleted by owner!")

    try:
        db.session.delete(dilution)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return Message.ERROR(error)

    return Message.ERROR(f"Successfully deleted dilution {id_}!")
