from sqlite3 import IntegrityError

from flask import Blueprint
from flask import current_app as app
from flask import flash, render_template, request
from flask_login import current_user, login_required
from labbase2.models import Antibody, db
from labbase2.utils.message import Message
from labbase2.utils.permission_required import permission_required
from labbase2.views.batches.forms import EditBatch
from labbase2.views.comments.forms import EditComment
from labbase2.views.files.forms import UploadFile
from labbase2.views.requests.forms import EditRequest
from sqlalchemy import func, select

from . import dilutions
from .dilutions.forms import EditDilution
from .forms import EditAntibody, FilterAntibodies


__all__ = ["bp"]


bp = Blueprint("antibodies", __name__, url_prefix="/antibody", template_folder="templates")

bp.register_blueprint(dilutions.bp)


@bp.route("/", methods=["GET"])
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    form = FilterAntibodies(request.args)

    data = form.data
    del data["submit"]
    del data["csrf_token"]

    try:
        entities = Antibody.filter_(**data)
    except Exception as error:
        flash(str(error), "danger")
        app.logger.error("Couldn't filter antibodies: %s", error)
        entities = Antibody.filter_(order_by="label")
    else:
        app.logger.debug("Found %d antibodies.", select(func.count()).select_from(entities))

    return render_template(
        "antibodies/main.html",
        filter_form=form,
        import_file_form=UploadFile(),
        add_form=EditAntibody(formdata=None),
        entities=db.paginate(entities, page=page, per_page=app.config["PER_PAGE"]),
        total=db.session.scalar(select(func.count()).select_from(Antibody)),
        title="Antibodies",
    )


@bp.route("/<int:id_>", methods=["GET"])
@login_required
def details(id_: int):
    if (antibody := db.session.get(Antibody, id_)) is None:
        app.logger.warning("Couldn't find antibody with ID %s.", id_)
        return Message.ERROR(f"No antibody found with ID {id_}!")

    return render_template(
        "antibodies/details.html",
        antibody=antibody,
        form=EditAntibody(formdata=None, obj=antibody),
        comment_form=EditComment,
        request_form=EditRequest,
        file_form=UploadFile,
        batch_form=EditBatch,
        dilution_form=EditDilution,
    )


@bp.route("/", methods=["POST"])
@login_required
@permission_required("Add antibodies")
def add():
    form = EditAntibody()

    if not form.validate():
        app.logger.info("Couldn't add antibody due to invalid input.")
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    antibody = Antibody()
    antibody.origin = f"Created via import form by {current_user.username}."
    form.populate_obj(antibody)

    try:
        db.session.add(antibody)
        db.session.commit()
    except IntegrityError as error:
        db.session.rollback()
        app.logger.info("Couldn't add antibody due to integrity error.")
        return Message.ERROR(error)
    except Exception as error:
        db.session.rollback()
        app.logger.warning("Couldn't add antibody to database due to unknown database error: %s", error)
        return Message.ERROR(error)
    else:
        app.logger.info("Added new antibody with ID %5d.", antibody.id)

    return Message.SUCCESS(f"Successfully added antibody '{antibody.label}'!")


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
@permission_required("Add antibodies")
def edit(id_: int):
    form = EditAntibody()

    if not form.validate():
        app.logger.info("Couldn't edit antibody with ID %d due to invalid user input.", id_)
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    if not (antibody := db.session.get(Antibody, id_)):
        app.logger.warning("Couldn't find antibody with ID %d.", id_)
        return Message.ERROR(f"No antibody found with ID {id_}!")

    form.populate_obj(antibody)

    try:
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        app.logger.warning("Couldn't edit antibody with ID %d due to unknown database error.", id_)
        return Message.ERROR(error)
    else:
        app.logger.info("Edited antibody with ID %d.", id_)

    return Message.SUCCESS(f"Successfully edited antibody '{antibody.label}'!")


@bp.route("/delete/<int:id_>", methods=["DELETE"])
@login_required
@permission_required("Add antibodies")
def delete(id_):
    if (antibody := db.session.get(Antibody, id_)) is None:
        app.logger.warning("Couldn't find antibody with ID %d.", id_)
        return Message.ERROR(f"No antibody found with ID {id_}!")

    try:
        db.session.delete(antibody)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        app.logger.warning("Couldn't delete antibody with ID %d due to unknown database error.", id_)
        return Message.ERROR(error)
    else:
        app.logger.info("Deleted antibody with ID %d.", id_)

    return Message.SUCCESS(f"Successfully deleted antibody '{antibody.label}'!")


@bp.route("/export/<string:format_>/", methods=["GET"])
@login_required
@permission_required("Export content")
def export(format_: str):
    data = FilterAntibodies(request.args).data
    del data["submit"]
    del data["csrf_token"]

    try:
        entities = Antibody.filter_(**data)
    except Exception as error:
        app.logger.warning("Couldn't export antibodies: %s.", error)
        return Message.ERROR(error)

    match format_:
        case "csv":
            return Antibody.export_to_csv(entities)
        case "json":
            return Antibody.export_to_json(entities)
        case _:
            app.logger.warning("Tried to export antibodies with unsupported format: %s.", format_)
            return Message.ERROR(f"Unsupported format '{format_}'!")
