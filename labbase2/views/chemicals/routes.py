from sqlite3 import IntegrityError

from flask import Blueprint
from flask import current_app as app
from flask import flash, render_template, request
from flask_login import current_user, login_required
from labbase2.models import Chemical, db
from labbase2.utils.message import Message
from labbase2.utils.permission_required import permission_required
from labbase2.views.batches.forms import EditBatch
from labbase2.views.comments.forms import EditComment
from labbase2.views.files.forms import UploadFile
from sqlalchemy import select, func

from . import stock_solutions
from .forms import EditChemical, FilterChemical
from .stock_solutions.forms import EditStockSolution

__all__ = ["bp"]


# The blueprint to register all coming blueprints with.
bp = Blueprint("chemicals", __name__, url_prefix="/chemical", template_folder="templates")

bp.register_blueprint(stock_solutions.bp)


@bp.route("/", methods=["GET"])
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    form = FilterChemical(request.args)

    data = form.data
    del data["submit"]
    del data["csrf_token"]

    try:
        entities = Chemical.filter_(**data)
    except Exception as err:
        flash(str(err), "danger")
        entities = Chemical.filter_(order_by="label")

    return render_template(
        "chemicals/main.html",
        filter_form=form,
        import_file_form=UploadFile(),
        add_form=EditChemical(formdata=None),
        entities=db.paginate(entities, page=page, per_page=app.config["PER_PAGE"]),
        total=db.session.scalar(select(func.count()).select_from(Chemical)),
        title="Chemicals",
    )


@bp.route("/", methods=["POST"])
@login_required
@permission_required("Add chemicals")
def add():
    form = EditChemical()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    chemical = Chemical()
    chemical.origin = f"Created via import form by {current_user.username}."
    form.populate_obj(chemical)

    try:
        db.session.add(chemical)
        db.session.commit()
    except IntegrityError as error:
        return Message.ERROR(error)
    except Exception as error:
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully added chemical '{chemical.label}'!")


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
@permission_required("Add chemicals")
def edit(id_: int):
    form = EditChemical()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    if not (chemical := db.session.get(Chemical, id_)):
        return Message.ERROR(f"No chemical with ID {id_}!")

    form.populate_obj(chemical)

    try:
        db.session.commit()
    except Exception as error:
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully edited chemical '{chemical.label}'!")


@bp.route("/<int:id_>", methods=["DELETE"])
@login_required
@permission_required("Add chemicals")
def delete(id_: int):
    if (chemical := db.session.get(Chemical, id_)) is None:
        return Message.ERROR(f"No chemical with ID {id_}!")

    try:
        db.session.delete(chemical)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully deleted chemical '{chemical.label}'!")


@bp.route("/<int:id_>", methods=["GET"])
@login_required
def details(id_: int):
    if (chemical := db.session.get(Chemical, id_)) is None:
        return Message.ERROR(f"No chemical found with ID {id_}!")

    return render_template(
        "chemicals/details.html",
        chemical=chemical,
        form=EditChemical(formdata=None, obj=chemical),
        comment_form=EditComment,
        file_form=UploadFile,
        batch_form=EditBatch,
        stock_form=EditStockSolution,
    )


@bp.route("/export/<string:format_>/", methods=["GET"])
@login_required
@permission_required("Export content")
def export(format_: str):
    data = FilterChemical(request.args).data
    del data["submit"]
    del data["csrf_token"]

    try:
        entities = Chemical.filter_(**data)
    except Exception:
        return "An internal error occured! Please inform the admin!", 500

    match format_:
        case "csv":
            return Chemical.export_to_csv(entities)
        case "json":
            return Chemical.export_to_json(entities)
        case _:
            return Message.ERROR(f"Unsupported format: {format_}"), 400
