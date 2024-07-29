from .forms import EditAntibody
from .forms import FilterAntibodies
from . import dilutions
from .dilutions.forms import EditDilution

from labbase2.utils.message import Message
from labbase2.views.requests.forms import EditRequest
from labbase2.views.batches.forms import EditBatch
from labbase2.utils.permission_required import permission_required
from labbase2.models import db
from labbase2.models import Antibody
from labbase2.views.files.forms import UploadFile
from labbase2.views.comments.forms import EditComment

from flask import Blueprint
from flask import render_template
from flask import request
from flask import flash
from flask import current_app as app
from flask_login import login_required
from flask_login import current_user
from sqlite3 import IntegrityError


__all__ = ["bp"]


bp = Blueprint(
    "antibodies",
    __name__,
    url_prefix="/antibody",
    template_folder="templates"
)

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
        entities = Antibody.filter_(order_by="label")

    return render_template(
        "antibodies/main.html",
        filter_form=form,
        import_file_form=UploadFile(),
        add_form=EditAntibody(formdata=None),
        entities=entities.paginate(page=page, per_page=app.config["PER_PAGE"]),
        total=Antibody.query.count(),
        title="Antibodies"
    )


@bp.route("/<int:id_>", methods=["GET"])
@login_required
def details(id_: int):
    if (antibody := Antibody.query.get(id_)) is None:
        return Message.ERROR(f"No antibody found with ID {id_}!")

    return render_template(
        "antibodies/details.html",
        antibody=antibody,
        form=EditAntibody(formdata=None, obj=antibody),
        comment_form=EditComment,
        request_form=EditRequest,
        file_form=UploadFile,
        batch_form=EditBatch,
        dilution_form=EditDilution
    )


@bp.route("/", methods=["POST"])
@login_required
@permission_required("Add antibodies")
def add():
    form = EditAntibody()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    antibody = Antibody()
    antibody.origin = f"Created via import form by {current_user.username}."
    form.populate_obj(antibody)

    try:
        db.session.add(antibody)
        db.session.commit()
    except IntegrityError as error:
        return Message.ERROR(error)
    except Exception as error:
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully added antibody '{antibody.label}'!")


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
@permission_required("Add antibodies")
def edit(id_: int):
    form = EditAntibody()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    if not (antibody := Antibody.query.get(id_)):
        return Message.ERROR(f"No antibody found with ID {id_}!")

    form.populate_obj(antibody)

    try:
        db.session.commit()
    except Exception as error:
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully edited antibody '{antibody.label}'!")


@bp.route("/delete/<int:id_>", methods=["DELETE"])
@login_required
@permission_required("Add antibodies")
def delete(id_):
    if (antibody := Antibody.query.get(id_)) is None:
        return Message.ERROR(f"No antibody found with ID {id_}!")

    try:
        db.session.delete(antibody)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return Message.ERROR(error)

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
        return Message.ERROR(error)

    match format_:
        case "csv":
            return Antibody.export_to_csv(entities)
        case "json":
            return Antibody.export_to_json(entities)
        case _:
            return Message.ERROR(f"Unsupported format '{format_}'!")
