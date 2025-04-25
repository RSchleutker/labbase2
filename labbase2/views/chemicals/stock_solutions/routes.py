from flask import Blueprint
from flask import current_app as app
from flask import flash, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import func, select

from labbase2.database import db
from labbase2.models import StockSolution
from labbase2.utils.message import Message
from labbase2.utils.permission_required import permission_required
from labbase2.views.chemicals.forms import EditChemical
from labbase2.views.files.forms import UploadFile

from .forms import EditStockSolution, FilterStockSolution

__all__ = ["bp"]


# The blueprint to register all coming blueprints with.
bp = Blueprint("solutions", __name__, url_prefix="/stock-solutions", template_folder="templates")


@bp.route("/", methods=["GET"])
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    form = FilterStockSolution(request.args)

    data = form.data
    del data["submit"]
    del data["csrf_token"]

    try:
        entities = StockSolution.filter_(**data)
    except Exception as err:
        flash(str(err), "danger")
        entities = StockSolution.filter_(order_by="label")

    return render_template(
        "stock_solutions/main.html",
        filter_form=form,
        add_form=EditStockSolution(formdata=None),
        entities=db.paginate(entities, page=page, per_page=app.config["PER_PAGE"]),
        total=db.session.scalar(select(func.count()).select_from(StockSolution)),
        title="Stock Solutions",
    )


@bp.route("/<int:chemical_id>", methods=["POST"])
@login_required
@permission_required("Add stock solution")
def add(chemical_id: int):
    form = EditStockSolution()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    solution = StockSolution(chemical_id=chemical_id, user_id=current_user.id)
    form.populate_obj(solution)

    try:
        db.session.add(solution)
        db.session.commit()
    except Exception as error:
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully added stock of '{solution.chemical.label}'!")


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
@permission_required("Add stock solution")
def edit(id_: int):
    form = EditStockSolution()

    if not form.validate():
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    if (solution := db.session.get(StockSolution, id_)) is None:
        return Message.ERROR(f"No stock solution with ID {id_}!")

    form.populate_obj(solution)

    try:
        db.session.commit()
    except Exception as error:
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully edited stock solution {id_}!")


@bp.route("/<int:id_>", methods=["DELETE"])
@login_required
@permission_required("Add stock solution")
def delete(id_):
    if (solution := db.session.get(StockSolution, id_)) is None:
        return Message.ERROR(f"No stock solution with ID {id_}!")

    try:
        db.session.delete(solution)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return Message.ERROR(error)

    return Message.SUCCESS(f"Successfully deleted stock solution {id_}!")


@bp.route("/<int:id_>/<string:format_>", methods=["GET"])
@login_required
def details(id_: int, format_: str):
    if (solution := db.session.get(StockSolution, id_)) is None:
        return Message.ERROR(f"No stock solution wth ID {id_}!")

    match format_:
        case "long":
            template = "stock_solutions/details.html"
        case "tab":
            template = "stock_solutions/details-tab.html"
        case _:
            return Message.ERROR(f"Invalid format '{format_}'!")

    edit_form = EditStockSolution(None, obj=solution)

    return render_template(
        template,
        stock=solution,
        form=edit_form,
        file_form=UploadFile,
        chemical_form=EditChemical(None, obj=solution.chemical),
    )
