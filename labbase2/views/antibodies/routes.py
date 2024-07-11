from .forms import EditAntibody
from .forms import FilterAntibodies
from . import dilutions
from .dilutions.forms import EditDilution

from labbase2.forms.utils import err2message

from labbase2.utils.message import Message
from labbase2.views.requests.forms import EditRequest
from labbase2.views.batches.forms import EditBatch
from labbase2.utils.role_required import role_required
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


__all__: list = ["bp"]


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
    except Exception as err:
        flash(str(err), "danger")
        entities = Antibody.filter_(order_by="label")

    return render_template(
        "antibodies/main.html",
        filter_form=form,
        add_form=EditAntibody(formdata=None),
        entities=entities.paginate(page=page, per_page=app.config["PER_PAGE"]),
        title="Antibodies"
    )


@bp.route("/<int:id_>", methods=["GET"])
@login_required
def details(id_: int):
    if (antibody := Antibody.query.get(id_)) is None:
        return Message.ERROR("Invalid ID: {}".format(id_))

    return render_template(
        "antibodies/details.html",
        antibody=antibody,
        form=EditAntibody(None, obj=antibody),
        comment_form=EditComment,
        request_form=EditRequest,
        file_form=UploadFile,
        batch_form=EditBatch,
        dilution_form=EditDilution
    )


@bp.route("/", methods=["POST"])
@login_required
def add():
    if (form := EditAntibody()).validate():
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
        else:
            return Message.SUCCESS(f"Successfully added antibody '{antibody.label}'!"), 201

    else:
        return err2message(form.errors)


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
@role_required(roles=["editor", "viewer"])
def edit(id_: int):
    if (form := EditAntibody()).validate():
        if not (antibody := Antibody.query.get(id_)):
            return Message.ERROR(f"No antibody with ID {id_}!"), 404
        else:
            form.populate_obj(antibody)

        try:
            db.session.commit()
        except Exception as err:
            return Message.ERROR(str(err))
        else:
            return Message.SUCCESS(f"Successfully edited antibody {antibody.label}!"), 200

    else:
        return err2message(form.errors)


@bp.route("/delete/<int:id_>", methods=["DELETE"])
@login_required
@role_required(roles=["editor", "viewer"])
def delete(id_):
    if not (antibody := Antibody.query.get(id_)):
        return Message.ERROR(f"No antibody with ID {id_}!"), 404
    else:
        try:
            db.session.delete(antibody)
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            return Message.ERROR(str(err)), 400
        else:
            return Message.SUCCESS("Successfully deleted antibody!"), 200


@bp.route("/export/<string:format_>/", methods=["GET"])
@login_required
def export(format_: str):
    data = FilterAntibodies(request.args).data
    del data["submit"]
    del data["csrf_token"]

    try:
        entities = Antibody.filter_(**data)
    except Exception:
        return "An internal error occured! Please inform the admin!", 500

    match format_:
        case "csv":
            return Antibody.export_to_csv(entities)
        case "json":
            return Antibody.export_to_json(entities)
        case _:
            return Message.ERROR(f"Unsupported format: {format_}"), 400
