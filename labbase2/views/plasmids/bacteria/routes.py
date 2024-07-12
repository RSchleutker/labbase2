from .forms import FilterBacteria
from .forms import EditBacterium

from labbase2.forms.utils import err2message

from labbase2.utils.message import Message
from labbase2.utils.role_required import role_required

from labbase2.models import db
from labbase2.models import Plasmid
from labbase2.models import GlycerolStock

from flask import Blueprint
from flask import render_template
from flask import request
from flask import flash
from flask_login import login_required
from flask_login import current_user


__all__: list[str] = ["bp"]


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
    except Exception as err:
        flash(str(err), "danger")
        entities = GlycerolStock.filter_(order_by="label")

    return render_template(
        "bacteria/main.html",
        filter_form=form,
        add_form=EditBacterium(formdata=None),
        entities=entities.paginate(page=page, per_page=100),
        title="Glycerol stocks"
    )


@bp.route("/<int:plasmid_id>", methods=["POST"])
@login_required
def add(plasmid_id: int):
    if (form := EditBacterium()).validate():
        if Plasmid.query.get(plasmid_id) is None:
            return f"No plasmid with ID {plasmid_id}!"
        stock = GlycerolStock()
        form.populate_obj(stock)
        stock.owner_id = current_user.id
        stock.plasmid_id = plasmid_id

        try:
            db.session.add(stock)
            db.session.commit()
        except Exception as err:
            return str(err), 400
        else:
            return f"Successfully added glycerol stock!", 201
    else:
        return err2message(form.errors), 400


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
@role_required(roles=["editor", "viewer"])
def edit(id_: int):
    if (form := EditBacterium()).validate():
        if not (plasmid := GlycerolStock.query.get(id_)):
            return Message.ERROR(f"No glycerol stock with ID {id_}!")
        elif plasmid.owner_id != current_user.id:
            return Message.ERROR("Glycerol stocks can only be edited by owner!")
        else:
            form.populate_obj(plasmid)

        try:
            db.session.commit()
        except Exception as err:
            return Message.ERROR(str(err))
        else:
            return Message.SUCCESS(f"Successfully edited glycerol stock!")
    else:
        return err2message(form.errors)


@bp.route("/<int:id_>/<string:format_>", methods=["GET"])
@login_required
def details(id_: int, format_: str):
    if (stock := GlycerolStock.query.get(id_)) is None:
        return Message.ERROR("Invalid ID: {}".format(id_))
    else:
        edit_form = EditBacterium(None, obj=stock)

        match format_:
            case "long":
                template = "bacteria/details.html"
            case "tab":
                template = "bacteria/details-tab.html"
            case _:
                return Message.ERROR(f"Invalid format: {format_}")

        return render_template(
            template,
            stock=stock,
            form=edit_form
        )


@bp.route("/glycerol-stock/export/<string:format_>/", methods=["GET"])
@login_required
def export(format_: str):
    data = FilterBacteria(request.args).data
    del data["submit"]
    del data["csrf_token"]

    try:
        entities = GlycerolStock.filter_(**data)
    except Exception:
        return "An internal error occured! Please inform the admin!", 500

    match format_:
        case "csv":
            return GlycerolStock.to_csv(entities)
        case "json":
            return GlycerolStock.to_json(entities)
        case _:
            return Message.ERROR(f"Unsupported format: {format_}"), 400
