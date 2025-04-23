from flask import Blueprint
from flask_login import current_user, login_required
from labbase2.models import Comment, db
from labbase2.utils.message import Message
from labbase2.utils.permission_required import permission_required
from sqlalchemy import select

from .forms import EditComment

__all__ = ["bp"]


bp = Blueprint("comments", __name__, url_prefix="/comment", template_folder="templates")


@bp.route("/attach/<int:entity_id>", methods=["POST"])
@login_required
@permission_required("Write comment")
def add(entity_id: int):
    form = EditComment()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    comment = Comment(entity_id=entity_id, user_id=current_user.id)
    form.populate_obj(comment)

    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as error:
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully added comment to '{comment.entity.label}'!")


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
@permission_required("Write comment")
def edit(id_: int):
    form = EditComment()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    if (comment := db.session.get(Comment, id_)) is None:
        return Message.ERROR(f"No comment found with ID {id_}!")

    if comment.user_id != current_user.id:
        return Message.ERROR("Comment can only be edited by original author!")

    form.populate_obj(comment)

    try:
        db.session.commit()
    except Exception as error:
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully edited comment {id_}!")


@bp.route("/<int:id_>", methods=["DELETE"])
@login_required
@permission_required("Write comment")
def delete(id_):
    if not (comment := db.session.get(Comment, id_)):
        return Message.ERROR(f"No comment with ID {id_}!")

    if comment.user_id != current_user.id:
        return Message.ERROR("Comment can only be deleted by original author!")

    try:
        db.session.delete(comment)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully deleted comment {id_}!")
