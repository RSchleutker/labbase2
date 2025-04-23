from flask import Blueprint
from flask import current_app as app
from flask_login import current_user, login_required
from labbase2.models import Dilution, db
from labbase2.utils.message import Message
from labbase2.utils.permission_required import permission_required

from .forms import EditDilution

__all__ = ["bp"]


bp = Blueprint("dilutions", __name__, url_prefix="/dilution", template_folder="templates")


@bp.route("/<int:antibody_id>", methods=["POST"])
@login_required
@permission_required("Add dilution")
def add(antibody_id: int):
    form = EditDilution()

    if not form.validate():
        app.logger.info("Couldn't add dilution to antibody with ID %d due to invalid user input.", antibody_id)
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    dilution = Dilution(antibody_id=antibody_id, user_id=current_user.id)
    form.populate_obj(dilution)

    try:
        db.session.add(dilution)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        app.logger.warning("Couldn't add dilution to database due to unknown database error: %s", error)
        return Message.ERROR(error)
    else:
        app.logger.info("Added new dilution with ID %d to database.", dilution.id)

    return Message.SUCCESS(f"Successfully added dilution to '{dilution.antibody.label}'!")


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
@permission_required("Add dilution")
def edit(id_: int):
    form = EditDilution()

    if not form.validate():
        app.logger.info("Couldn't edit dilution with ID %d due to invalid user input.", id_)
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    if (dilution := db.session.get(Dilution, id_)) is None:
        app.logger.warning("Couldn't find dilution with ID %d.", id_)
        return Message.ERROR(f"No dilution found with ID {id_}!")

    if dilution.user_id != current_user.id:
        app.logger.warning("Tried to edit dilution with ID %d that belongs to %s.", id_, dilution.user.username)
        return Message.ERROR("Dilutions can only be edited by owner! Consider adding a new dilution instead.")

    form.populate_obj(dilution)

    try:
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        app.logger.warning("Couldn't write changes for dilution with ID %d to database: %s", id_, error)
        return Message.ERROR(error)
    else:
        app.logger.info("Edited dilution with ID %d.", id_)

    return Message.SUCCESS(f"Successfully edited dilution '{dilution.id}'!")


@bp.route("<int:id_>", methods=["DELETE"])
@login_required
@permission_required("Add dilution")
def delete(id_: int):
    if (dilution := db.session.get(Dilution, id_)) is None:
        app.logger.warning("Couldn't find dilution with ID %d.", id_)
        return Message.ERROR(f"No dilution found with ID {id_}!")

    if dilution.user_id != current_user.id:
        app.logger.warning("Tried to delete dilution with ID %d that belongs to %s.", id_, dilution.user.username)
        return Message.ERROR("Dilutions can only be deleted by owner!")

    try:
        db.session.delete(dilution)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        app.logger.warning("Couldn't delete dilution with ID %d due to unknown database error.", id_)
        return Message.ERROR(error)
    else:
        app.logger.info("Deleted dilution with ID %d.", id_)

    return Message.ERROR(f"Successfully deleted dilution {id_}!")
