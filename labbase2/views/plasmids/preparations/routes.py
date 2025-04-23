from datetime import date, timedelta

from flask import Blueprint
from flask_login import current_user, login_required
from labbase2.models import GlycerolStock, Plasmid, Preparation, db
from labbase2.utils.message import Message
from labbase2.utils.permission_required import permission_required
from sqlalchemy import select

from .forms import EditPreparation

__all__ = ["bp"]


# The blueprint to register all coming blueprints with.
bp = Blueprint("preparations", __name__, url_prefix="/preparations", template_folder="templates")


@bp.route("/<int:plasmid_id>", methods=["POST"])
@login_required
@permission_required("Add preparations")
def add(plasmid_id: int):
    form = EditPreparation()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    if db.session.get(Plasmid, plasmid_id) is None:
        return Message.ERROR(f"No plasmid with ID {plasmid_id}!")

    preparation = Preparation(owner_id=current_user.id, plasmid_id=plasmid_id)
    form.populate_obj(preparation)

    stock = GlycerolStock(
        plasmid_id=plasmid_id,
        owner_id=current_user.id,
        strain=form.strain.data,
        transformation_date=form.preparation_date.data - timedelta(days=1),
        disposal_date=form.preparation_date.data,
        storage_place="Immediately disposed.",
    )

    preparation.stock = stock

    try:
        db.session.add(preparation)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully added preparation to '{preparation.plasmid.label}'!")


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
@permission_required("Add preparations")
def edit(id_: int):
    form = EditPreparation()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    if (preparation := db.session.get(Preparation, id_)) is None:
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
@permission_required("Add preparations")
def delete(id_: int):
    if not (preparation := db.session.get(Preparation, id_)):
        return Message.ERROR(f"No preparation with ID {id_}!")

    try:
        db.session.delete(preparation)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return Message.ERROR(error)

    return Message.ERROR(f"Successfully deleted preparation {id_}!")
