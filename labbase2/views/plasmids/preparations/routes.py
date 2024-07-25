from .forms import EditPreparation

from labbase2.forms.utils import err2message

from labbase2.models import db
from labbase2.models import Preparation
from labbase2.utils.message import Message
from labbase2.models import Plasmid

from flask import Blueprint
from flask_login import login_required
from flask_login import current_user


__all__ = ["bp"]


# The blueprint to register all coming blueprints with.
bp = Blueprint(
    "preparations",
    __name__,
    url_prefix="/preparations",
    template_folder="templates"
)


@bp.route("/<int:plasmid_id>", methods=["POST"])
@login_required
def add(plasmid_id: int):
    form = EditPreparation()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    if Plasmid.query.get(plasmid_id) is None:
        return Message.ERROR(f"No plasmid with ID {plasmid_id}!")

    preparation = Preparation(owner_id=current_user.id, plasmid_id=plasmid_id)
    form.populate_obj(preparation)

    try:
        db.session.add(preparation)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully added preparation to '{preparation.plasmid.label}'!")


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
def edit(id_: int):
    form = EditPreparation()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    if (preparation := Preparation.query.get(id_)) is None:
        return Message.ERROR(f"No preparation with ID {id_}!")

    if preparation.owner_id != current_user.id:
        return Message.ERROR("Preparations can only be edited by owner!")

    form.populate_obj(preparation)

    try:
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return Message.ERROR(error)

    return f"Successfully edited preparation!", 200


@bp.route("/<int:id_>", methods=["DELETE"])
@login_required
def delete(id_: int):
    if not (preparation := Preparation.query.get(id_)):
        return Message.ERROR(f"No preparation with ID {id_}!")

    try:
        db.session.delete(preparation)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return Message.ERROR(error)

    return Message.ERROR(f"Successfully deleted preparation {id_}!")
