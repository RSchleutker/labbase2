import datetime

from flask import Blueprint
from flask import current_app as app
from flask import flash, render_template, request
from flask_login import login_required
from sqlalchemy import func, select

from labbase2.models import Batch, db
from labbase2.utils.message import Message
from labbase2.utils.permission_required import permission_required

from .forms import EditBatch, FilterBatch

__all__ = ["bp"]


# The blueprint to register all coming blueprints with.
bp = Blueprint("batches", __name__, url_prefix="/batch", template_folder="templates")


@bp.route("/", methods=["GET"])
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    form = FilterBatch(request.args)

    data = form.data
    del data["submit"]
    del data["csrf_token"]

    try:
        entities = Batch.filter_(**data)
    except Exception as error:
        flash(str(error), "danger")
        app.logger.error("Couldn't filter batches: %s", error)
        entities = Batch.filter_(order_by="label")
    else:
        app.logger.debug("Found %d batches.", select(func.count()).select_from(entities))

    return render_template(
        "batches/main.html",
        filter_form=form,
        add_form=EditBatch(formdata=None),
        entities=db.paginate(entities, page=page, per_page=app.config["PER_PAGE"]),
        total=db.session.scalar(select(func.count()).select_from(Batch)),
        title="Batches",
    )


@bp.route("/<int:consumable_id>", methods=["POST"])
@login_required
@permission_required("Add consumable batches")
def add(consumable_id: int):
    form = EditBatch()

    if not form.validate():
        app.logger.info("Couldn't add batch due to invalid input.")
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    batch = Batch(consumable_id=consumable_id)
    form.populate_obj(batch)

    try:
        db.session.add(batch)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        app.logger.warning("Couldn't add batch due to unknown database error: %s", error)
        return Message.ERROR(error)

    app.logger.info("Added new batch with ID %5d.", batch.id)

    return Message.SUCCESS(f"Successfully added batch to '{batch.consumable.label}'!")


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
@permission_required("Add consumable batches")
def edit(id_: int):
    form = EditBatch()

    if not form.validate():
        app.logger.info("Couldn't edit batch with ID %d due to invalid user input.", id_)
        return "<br>".join(Message.ERROR(error) for error in form.errors)

    if (batch := db.session.get(Batch, id_)) is None:
        app.logger.warning("Couldn't find batch with ID %d.", id_)
        return Message.ERROR(f"No batch with ID {id_}!")

    form.populate_obj(batch)

    try:
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        app.logger.warning(
            "Couldn't edit batch with ID %d due to unknown database error: %s", id_, error
        )
        return Message.ERROR(error)

    app.logger.info("Edited batch eith ID %d.", id_)

    return Message.SUCCESS(f"Successfully edited batch {id_}!")


@bp.route("/open/<int:id_>", methods=["PUT"])
@login_required
def in_use(id_: int):
    if (batch := db.session.get(Batch, id_)) is None:
        app.logger.warning("Couldn't find batch with ID %d.", id_)
        return Message.ERROR(f"No batch with ID {id_}!")

    if batch.date_opened:
        app.logger.warning("Batch with ID %d already marked open.", id_)
        return Message.WARNING(f"Batch {batch.id_} already marked open!")

    batch.date_opened = datetime.date.today()
    batch.in_use = True

    try:
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        app.logger.warning("Couldn't mark batch with ID %d as open: %s", id_, error)
        return Message.ERROR(error)

    app.logger.info("Marked batch with ID %d as open.", id_)

    return Message.SUCCESS(f"Marked batch {id_} as open!")


@bp.route("/empty/<int:id_>", methods=["PUT"])
@login_required
def emptied(id_: int):
    if (batch := db.session.get(Batch, id_)) is None:
        app.logger.warning("Couldn't find batch with ID %d.", id_)
        return Message.ERROR(f"No batch with ID {id_}!")

    if batch.date_emptied:
        app.logger.warning("Batch with ID %d already marked empty.", id_)
        return f"Batch {id_} already marked empty!", 200

    batch.date_emptied = datetime.date.today()
    batch.in_use = False

    try:
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        app.logger.warning(
            "Couldn't mark batch with ID %d empty due to unknown database error: %s", id_, error
        )
        return Message.ERROR(error)

    app.logger.info("Marked batch with ID %d as empty.", id_)

    return Message.SUCCESS(f"Marked batch {id_} as empty!")


@bp.route("/<int:id_>", methods=["DELETE"])
@login_required
@permission_required("Add consumable batches")
def delete(id_: int):
    if (batch := db.session.get(Batch, id_)) is None:
        app.logger.warning("Couldn't find batch with ID %d.", id_)
        return Message.ERROR(f"No batch with ID {id_}!")

    try:
        db.session.delete(batch)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        app.logger.warning(
            "Couldn't delete batch with ID %d due to unknown database error: %s", id_, error
        )
        return Message.ERROR(error)

    app.logger.info("Deleted batch with ID %d.", id_)

    return Message.SUCCESS(f"Successfully deleted batch {id_}!")


@bp.route("/<int:id_>/<string:format_>", methods=["GET"])
@login_required
def details(id_: int, format_: str):
    if (batch := db.session.get(Batch, id_)) is None:
        app.logger.warning("Couldn't find batch with ID %d.", id_)
        return Message.ERROR(f"No batch with ID {id_}!")

    match format_:
        case "long":
            template = "batches/details.html"
        case "tab":
            template = "batches/details-tab.html"
        case _:
            return Message.ERROR(f"Invalid format '{format_}'!")

    edit_form = EditBatch(None, obj=batch)

    return render_template(template, batch=batch, form=edit_form)
