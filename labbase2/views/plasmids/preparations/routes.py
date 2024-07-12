from .forms import EditPreparation

from labbase2.forms.utils import err2message

from labbase2.models import db
from labbase2.models import Preparation
from labbase2.utils.message import Message
from labbase2.models import Plasmid

from flask import Blueprint
from flask_login import login_required
from flask_login import current_user


__all__: list[str] = ["bp"]


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
    if (form := EditPreparation()).validate():
        if Plasmid.query.get(plasmid_id) is None:
            return f"No plasmid with id {plasmid_id}!"
        preparation = Preparation(
            owner_id=current_user.id,
            plasmid_id=plasmid_id
        )
        form.populate_obj(preparation)

        try:
            db.session.add(preparation)
            db.session.commit()
        except Exception as err:
            return Message.ERROR(str(err)), 400
        else:
            return Message.SUCCESS(f"Successfully added preparation!"), 201
    else:
        return err2message(form.errors), 400


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
def edit(id_: int):
    if (form := EditPreparation()).validate():
        if not (preparation := Preparation.query.get(id_)):
            return Message.ERROR(f"No preparation with ID {id_}!"), 404
        elif preparation.owner_id != current_user.id:
            return "Preparation can only be edited by owner!", 400
        else:
            form.populate_obj(preparation)

        try:
            db.session.commit()
        except Exception as err:
            return str(err), 400
        else:
            return f"Successfully edited preparation!", 200
    else:
        return err2message(form.errors), 400


@bp.route("/<int:id_>", methods=["DELETE"])
@login_required
def delete(id_: int):
    if not (preparation := Preparation.query.get(id_)):
        return f"No preparation with ID {id_}!", 404
    else:
        try:
            db.session.delete(preparation)
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            return str(err), 400
        else:
            return f"Successfully deleted preparation {id_}!", 200
