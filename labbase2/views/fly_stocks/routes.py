from flask import Blueprint
from flask import current_app as app
from flask import flash, redirect, render_template, request
from flask_login import current_user, login_required
from labbase2.models import BaseFile, FlyStock, db
from labbase2.utils.message import Message
from labbase2.utils.permission_required import permission_required
from labbase2.views.comments.forms import EditComment
from labbase2.views.files.forms import UploadFile
from labbase2.views.files.routes import upload_file
from labbase2.views.requests.forms import EditRequest
from sqlalchemy import select, func

from .forms import EditFlyStock, FilterFlyStocks

__all__ = ["bp"]


# The blueprint to register all coming blueprints with.
bp = Blueprint("flystocks", __name__, url_prefix="/fly-stocks", template_folder="templates")

# bp.register_blueprint(modifications.bp)


@bp.route("/", methods=["GET"])
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    form = FilterFlyStocks(request.args)

    data = form.data
    del data["submit"]
    del data["csrf_token"]

    try:
        entities = FlyStock.filter_(**data)
    except Exception as err:
        flash(str(err), "danger")
        entities = FlyStock.filter_(order_by="label")

    return render_template(
        "fly_stocks/main.html",
        filter_form=form,
        import_file_form=UploadFile(),
        add_form=EditFlyStock(formdata=None),
        entities=entities.paginate(page=page, per_page=app.config["PER_PAGE"]),
        total=db.session.scalar(select(func.count()).select_from(FlyStock)),
        title="Fly Stocks",
    )


@bp.route("/", methods=["POST"])
@login_required
@permission_required("Add Fly Stock")
def add():
    form = EditFlyStock()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    fly_stock = FlyStock()
    form.populate_obj(fly_stock)

    try:
        db.session.add(fly_stock)
        db.session.commit()
    except Exception as error:
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully added stock '{fly_stock.label}'!")


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
@permission_required("Add Fly Stock")
def edit(id_: int):
    form = EditFlyStock()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    if (fly_stock := db.session.get(FlyStock, id_)) is None:
        return Message.ERROR(f"No fly stock with ID {id_}!")

    if fly_stock.owner_id != current_user.id:
        return Message.ERROR("Fly stocks can only be edited by owner!")

    form.populate_obj(fly_stock)

    try:
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully edited fly stock!")


@bp.route("/<int:id_>", methods=["DELETE"])
@login_required
@permission_required("Add Fly Stock")
def delete(id_):
    if (fly_stock := db.session.get(FlyStock, id_)) is None:
        return Message.ERROR(f"No fly stock with ID {id_}!")

    if fly_stock.owner_id != current_user.id:
        return Message.ERROR("Only owner can delete fly stock!")

    try:
        db.session.delete(fly_stock)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully deleted fly stock '{fly_stock.label}'!")


@bp.route("/<int:id_>", methods=["GET"])
@login_required
def details(id_: int):
    if (fly_stock := db.session.get(FlyStock, id_)) is None:
        return Message.ERROR(f"No fly stock with ID {id_}!")

    return render_template(
        "fly_stocks/details.html",
        flystock=fly_stock,
        form=EditFlyStock(None, obj=fly_stock),
        file_form=UploadFile,
        comment_form=EditComment,
        request_form=EditRequest,
    )


@bp.route("/export/<string:format_>/", methods=["GET"])
@login_required
@permission_required("Export content")
def export(format_: str):
    data = FilterFlyStocks(request.args).data
    del data["submit"]
    del data["csrf_token"]

    try:
        entities = FlyStock.filter_(**data)
    except Exception as error:
        return Message.ERROR(error)

    match format_:
        case "csv":
            return FlyStock.export_to_csv(entities)
        case "json":
            return FlyStock.export_to_json(entities)
        case _:
            return Message.ERROR(f"Unsupported format '{format_}'!")
