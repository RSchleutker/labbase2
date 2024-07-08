from .forms import EditComment

from labbase2.models import db
from labbase2.models import Comment
from labbase2.forms.utils import err2message

from flask import Blueprint
from flask_login import login_required
from flask_login import current_user


__all__ = ["bp"]


bp = Blueprint(
    "comments",
    __name__,
    url_prefix="/comment",
    template_folder="templates"
)


@bp.route("/attach/<int:entity_id>", methods=["POST"])
@login_required
def add(entity_id: int):
    if not (form := EditComment()).validate():
        return err2message(form.errors), 400

    comment = Comment(entity_id=entity_id, user_id=current_user.id)
    form.populate_obj(comment)

    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as err:
        return str(err), 400
    else:
        return f"Successfully added comment!", 201


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
def edit(id_: int):
    if not (form := EditComment()).validate():
        return err2message(form.errors), 400

    if not (comment := Comment.query.get(id_)):
        return f"No comment with ID {id_}!", 404

    if comment.user_id != current_user.id:
        return "Comment can only be edited by original author!", 403

    form.populate_obj(comment)

    try:
        db.session.commit()
    except Exception as err:
        return str(err), 400
    else:
        return f"Successfully edited comment {id_}!", 200


@bp.route("/<int:id_>", methods=["DELETE"])
@login_required
def delete(id_):
    if not (comment := Comment.query.get(id_)):
        return f"No comment with ID {id_}!", 404

    if comment.user_id != current_user.id:
        return "Comment can only be deleted by original author!", 403

    try:
        db.session.delete(comment)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return str(err), 400
    else:
        return f"Successfully deleted comment {id_}!", 200
