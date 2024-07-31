from flask import Blueprint
from flask import current_app as app
from flask import flash, render_template, request
from flask_login import current_user, login_required
from labbase2.models import Plasmid, db
from labbase2.utils.message import Message
from labbase2.utils.permission_required import permission_required
from labbase2.views.comments.forms import EditComment
from labbase2.views.files.forms import UploadFile
from labbase2.views.requests.forms import EditRequest

from . import bacteria, preparations
from .bacteria.forms import EditBacterium
from .forms import EditPlasmid, FilterPlasmids
from .preparations.forms import EditPreparation

__all__ = ["bp"]


# The blueprint to register all coming blueprints with.
bp = Blueprint("plasmids", __name__, url_prefix="/plasmid", template_folder="templates")

bp.register_blueprint(bacteria.bp)
bp.register_blueprint(preparations.bp)


@bp.route("/", methods=["GET"])
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    form = FilterPlasmids(request.args)

    data = form.data
    del data["submit"]
    del data["csrf_token"]

    try:
        entities = Plasmid.filter_(**data)
    except Exception as error:
        flash(str(error), "danger")
        entities = Plasmid.filter_(order_by="label")

    return render_template(
        "plasmids/main.html",
        filter_form=form,
        import_file_form=UploadFile(),
        add_form=EditPlasmid(formdata=None),
        entities=entities.paginate(page=page, per_page=app.config["PER_PAGE"]),
        total=Plasmid.query.count(),
        title="Plasmids",
    )


@bp.route("/", methods=["POST"])
@login_required
@permission_required("Add plasmid")
def add():
    form = EditPlasmid()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    plasmid = Plasmid(owner_id=current_user.id)
    form.populate_obj(plasmid)

    try:
        db.session.add(plasmid)
        db.session.commit()
    except Exception as error:
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully added plasmid '{plasmid.label}'!")


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
@permission_required("Add plasmid")
def edit(id_: int):
    form = EditPlasmid()

    if not form.validate():
        return Message.ERROR(f"No antibody found with ID {id_}!")

    if (plasmid := Plasmid.query.get(id_)) is None:
        return Message.ERROR(f"No plasmid with ID {id_}!")

    if plasmid.owner_id != current_user.id:
        return Message.ERROR("Plasmids can only be edited by owner!")

    form.populate_obj(plasmid)

    try:
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully edited plasmid!")


@bp.route("/<int:id_>", methods=["DELETE"])
@login_required
@permission_required("Add plasmid")
def delete(id_: int):
    if (plasmid := Plasmid.query.get(id_)) is None:
        return Message.ERROR(f"No plasmid with ID {id_}!")

    if plasmid.owner_id != current_user.id:
        return Message.ERROR("Only owner can delete plasmid!")

    try:
        db.session.delete(plasmid)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully deleted plasmid '{plasmid.label}'!")


@bp.route("/<int:id_>", methods=["GET"])
@login_required
def details(id_: int):
    if (plasmid := Plasmid.query.get(id_)) is None:
        return Message.ERROR(f"No plasmid with ID {id_}!")

    return render_template(
        "plasmids/details.html",
        plasmid=plasmid,
        form=EditPlasmid(None, obj=plasmid),
        file_form=UploadFile,
        comment_form=EditComment,
        request_form=EditRequest,
        preparation_form=EditPreparation,
        bacteria_form=EditBacterium,
    )


@bp.route("/export/<string:format_>/", methods=["GET"])
@login_required
@permission_required("Export content")
def export(format_: str):
    data = FilterPlasmids(request.args).data
    del data["submit"]
    del data["csrf_token"]

    try:
        entities = Plasmid.filter_(**data)
    except Exception as error:
        return Message.ERROR(error)

    match format_:
        case "csv":
            return Plasmid.export_to_csv(entities)
        case "json":
            return Plasmid.export_to_json(entities)
        case "pdf":
            return Plasmid.to_pdf(entities)
        case "fasta":
            return Plasmid.to_fasta(entities)
        case "zip":
            return Plasmid.to_zip(entities)
        case _:
            return Message.ERROR(f"Unsupported format '{format_}'!")
