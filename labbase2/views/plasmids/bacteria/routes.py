from flask import Blueprint
from flask import current_app as app
from flask import flash, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import func, select

from labbase2.database import db
from labbase2.models import GlycerolStock, Plasmid
from labbase2.utils.message import Message
from labbase2.utils.permission_required import permission_required
from labbase2.views.files.forms import UploadFile
from labbase2.views.plasmids.forms import EditPlasmid

from .forms import EditBacterium, FilterBacteria

__all__ = ["bp"]


# The blueprint to register all coming blueprints with.
bp = Blueprint("bacteria", __name__, url_prefix="/glycerol-stocks", template_folder="templates")


@bp.route("/", methods=["GET"])
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    form = FilterBacteria(request.args)

    data = form.data
    del data["submit"]
    del data["csrf_token"]

    try:
        entities = GlycerolStock.filter_(**data)
    except Exception as error:
        flash(str(error), "danger")
        entities = GlycerolStock.filter_(order_by="label")

    return render_template(
        "bacteria/main.html",
        filter_form=form,
        add_form=EditBacterium(formdata=None),
        entities=db.paginate(entities, page=page, per_page=app.config["PER_PAGE"]),
        total=db.session.scalar(select(func.count()).select_from(GlycerolStock)),
        title="Glycerol stocks",
    )


@bp.route("/<int:plasmid_id>", methods=["POST"])
@login_required
@permission_required("add-glycerol-stock")
def add(plasmid_id: int):
    form = EditBacterium()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    if (plasmid := db.session.get(Plasmid, plasmid_id)) is None:
        return f"No plasmid with ID {plasmid_id}!"

    stock = GlycerolStock(plasmid_id=plasmid_id, owner_id=current_user.id)
    form.populate_obj(stock)

    try:
        db.session.add(stock)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully added glycerol stock with '{plasmid.label}'!")


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
@permission_required("add-glycerol-stock")
def edit(id_: int):
    form = EditBacterium()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    if not (plasmid := db.session.get(GlycerolStock, id_)):
        return Message.ERROR(f"No glycerol stock with ID {id_}!")

    if plasmid.owner_id != current_user.id and not current_user.is_admin:
        return Message.ERROR("Glycerol stocks can only be edited by owner and admins!")

    form.populate_obj(plasmid)

    try:
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return Message.ERROR(str(err))

    return Message.SUCCESS(f"Successfully edited glycerol stock!")


@bp.route("/<int:id_>/<string:format_>", methods=["GET"])
@login_required
def details(id_: int, format_: str):
    if (stock := db.session.get(GlycerolStock, id_)) is None:
        return Message.ERROR(f"No glycerol stock with ID {id_}!")

    edit_form = EditBacterium(None, obj=stock)

    match format_:
        case "long":
            template = "bacteria/details.html"
        case "tab":
            template = "bacteria/details-tab.html"
        case _:
            return Message.ERROR(f"Invalid format '{format_}'!")

    return render_template(
        template,
        stock=stock,
        form=edit_form,
        file_form=UploadFile,
        plasmid_form=EditPlasmid(None, obj=stock.plasmid),
    )


@bp.route("/glycerol-stock/export/<string:format_>/", methods=["GET"])
@login_required
@permission_required("export-content")
def export(format_: str):
    data = FilterBacteria(request.args).data
    del data["submit"]
    del data["csrf_token"]

    try:
        entities = GlycerolStock.filter_(**data)
    except Exception as error:
        return Message.ERROR(error)

    match format_:
        case "csv":
            return GlycerolStock.to_csv(entities)
        case "json":
            return GlycerolStock.to_json(entities)
        case _:
            return Message.ERROR(f"Unsupported format '{format_}'!")
