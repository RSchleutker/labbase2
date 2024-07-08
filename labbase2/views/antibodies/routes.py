from .forms import EditAntibody
from .forms import FilterAntibodies
from . import dilutions
from .dilutions.forms import EditDilution

from app.forms.utils import err2message

from app.utils import Message
from comments.forms import EditComment
from files.forms import UploadFile
from requests.forms import EditRequest
from batches.forms import EditBatch
from app.blueprints.utils import role_required
from app.models import db
from app.models import Antibody

from flask import Blueprint
from flask import render_template
from flask import request
from flask import flash
from flask_login import login_required


__all__: list = ["bp"]


bp = Blueprint(
    "antibodies",
    __name__,
    url_prefix="/antibody",
    template_folder="templates"
)

bp.register_blueprint(dilutions.bp)


@bp.route("/", methods=["GET"])
# @login_required
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
        entities=entities.paginate(page=page, per_page=100),
        title="Antibodies"
    )


@bp.route("/add", methods=["POST"])
@login_required
def add():
    if (form := EditAntibody()).validate():
        antibody = Antibody()
        form.populate_obj(antibody)

        try:
            db.session.add(antibody)
            db.session.commit()
        except Exception as err:
            return Message.ERROR(str(err)), 400
        else:
            return Message.SUCCESS(f"Successfully added antibody!"), 201

    else:
        return err2message(form.errors), 400


@bp.route("/edit/<int:id>", methods=["PUT"])
@login_required
@role_required(roles=["editor", "viewer"])
def edit(id: int):
    if (form := EditAntibody()).validate():
        if not (antibody := Antibody.query.get(id)):
            return Message.ERROR(f"No antibody with ID {id}!"), 404
        else:
            form.populate_obj(antibody)

        try:
            db.session.commit()
        except Exception as err:
            return Message.ERROR(str(err)), 400
        else:
            return Message.SUCCESS(f"Successfully edited antibody!"), 200

    else:
        return err2message(form.errors), 400


@bp.route("/delete/<int:id>", methods=["DELETE"])
@login_required
@role_required(roles=["editor", "viewer"])
def delete(id):
    if not (antibody := Antibody.query.get(id)):
        return Message.ERROR(f"No antibody with ID {id}!"), 404
    else:
        try:
            db.session.delete(antibody)
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            return Message.ERROR(str(err)), 400
        else:
            return Message.SUCCESS("Successfully deleted antibody!"), 200


@bp.route("/details/<int:id>", methods=["GET"])
@login_required
def details(id: int):
    if (antibody := Antibody.query.get(id)) is None:
        return Message.ERROR("Invalid ID: {}".format(id))
    else:
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


@bp.route("/export/<string:format>/", methods=["GET"])
@login_required
def export(format: str):
    data = FilterAntibodies(request.args).data
    del data["submit"]
    del data["csrf_token"]

    try:
        entities = Antibody.filter_(**data)
    except Exception:
        return "An internal error occured! Please inform the admin!", 500

    match format:
        case "csv":
            return Antibody.export_to_csv(entities)
        case "json":
            return Antibody.export_to_json(entities)
        case _:
            return Message.ERROR(f"Unsupported format: {format}"), 400
