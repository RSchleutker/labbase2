from .forms import FilterBacteria
from .forms import EditBacterium
from labbase2.views.plasmids.forms import EditPlasmid

from labbase2.utils.message import Message
from labbase2.utils.permission_required import permission_required

from labbase2.models import db
from labbase2.models import Plasmid
from labbase2.models import GlycerolStock

from flask import Blueprint
from flask import render_template
from flask import request
from flask import flash
from flask_login import login_required
from flask_login import current_user


__all__ = ["bp"]


# The blueprint to register all coming blueprints with.
bp = Blueprint(
    "bacteria",
    __name__,
    url_prefix="/glycerol-stocks",
    template_folder="templates"
)


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
        entities=entities.paginate(page=page, per_page=100),
        total=GlycerolStock.query.count(),
        title="Glycerol stocks"
    )


@bp.route("/<int:plasmid_id>", methods=["POST"])
@login_required
@permission_required("Add glycerol stocks")
def add(plasmid_id: int):
    form = EditBacterium()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    if (plasmid := Plasmid.query.get(plasmid_id)) is None:
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
@permission_required("Add glycerol stocks")
def edit(id_: int):
    form = EditBacterium()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    if not (plasmid := GlycerolStock.query.get(id_)):
        return Message.ERROR(f"No glycerol stock with ID {id_}!")

    if plasmid.owner_id != current_user.id:
        return Message.ERROR("Glycerol stocks can only be edited by owner!")

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
    if (stock := GlycerolStock.query.get(id_)) is None:
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
        plasmid_form=EditPlasmid(None, obj=stock.plasmid)
    )


@bp.route("/glycerol-stock/export/<string:format_>/", methods=["GET"])
@login_required
@permission_required("Export content")
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
