import datetime

from .forms import EditBatch
from .forms import FilterBatch

from labbase2.forms.utils import err2message

from labbase2.utils.message import Message
from labbase2.utils.role_required import role_required
from labbase2.models import db
from labbase2.models import Batch

from flask import Blueprint
from flask import render_template
from flask import request
from flask import flash
from flask import current_app as app
from flask_login import login_required
from flask_login import current_user


# The blueprint to register all coming blueprints with.
bp = Blueprint(
    "batches",
    __name__,
    url_prefix="/batch",
    template_folder="templates"
)


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
        entities = Batch.filter_(order_by="label")

    return render_template(
        "batches/main.html",
        filter_form=form,
        add_form=EditBatch(formdata=None),
        entities=entities.paginate(page=page, per_page=app.config["PER_PAGE"]),
        title="Batches"
    )


@bp.route("/<int:consumable_id>", methods=["POST"])
@login_required
def add(consumable_id: int):
    form = EditBatch(obj=request.values)
    if form.validate():
        batch = Batch()
        form.populate_obj(batch)
        batch.consumable_id = consumable_id

        try:
            db.session.add(batch)
            db.session.commit()
        except Exception as err:
            return Message.ERROR(str(err)), 400
        else:
            return Message.SUCCESS("Successfully added batch!"), 201
    else:
        return err2message(form.errors), 400


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
def edit(id_: int):
    form = EditBatch(obj=request.values)
    if form.validate():
        if not (batch := Batch.query.get(id_)):
            return Message.ERROR(f"No batch with ID {id_}!"), 404
        else:
            form.populate_obj(batch)

        try:
            db.session.commit()
        except Exception as err:
            return Message.ERROR(str(err)), 400
        else:
            return Message.SUCCESS(f"Successfully edited batch!"), 200
    else:
        return err2message(form.errors), 400


@bp.route("/in_use/<int:id_>", methods=["PUT"])
@login_required
def in_use(id_: int):
    if not (batch := Batch.query.get(id_)):
        return f"No batch with ID {id_}!", 404
    elif batch.opened_date:
        return f"Batch {id_} has already been opened!", 201
    else:
        batch.opened_date = datetime.date.today()
        batch.in_use = True

        try:
            db.session.commit()
        except Exception as err:
            return str(err), 400
        else:
            return f"Successfully marked batch {id_} as open!", 200


@bp.route("/empty/<int:id_>", methods=["PUT"])
@login_required
def emptied(id_: int):
    if not (batch := Batch.query.get(id_)):
        return f"No batch with ID {id_}!", 404
    elif batch.emptied_date:
        return f"Batch {id_} has already been marked as empty!", 200
    else:
        batch.emptied_date = datetime.date.today()
        batch.in_use = False

        try:
            db.session.commit()
        except Exception as err:
            return str(err), 400
        else:
            return f"Successfully marked batch {id_} as empty!", 200


@bp.route("/<int:id_>", methods=["DELETE"])
@login_required
def delete(id_: int):
    if not (batch := Batch.query.get(id_)):
        return Message.ERROR(f"No batch with ID {id_}!"), 404
    else:
        try:
            db.session.delete(batch)
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            return Message.ERROR(str(err)), 400
        else:
            return Message.SUCCESS("Successfully deleted batch!"), 200


@bp.route("/<int:id_>/<string:format_>", methods=["GET"])
@login_required
def details(id_: int, format_: str):
    if not (batch := Batch.query.get(id_)):
        return Message.ERROR(f"No batch with ID {id_}!"), 404
    else:
        match format_:
            case "long":
                template = "batches/details.html"
            case "tab":
                template = "batches/details-tab.html"
            case _:
                return Message.ERROR(f"Invalid format: {format_}")

        edit_form = EditBatch(None, obj=batch)

        return render_template(template, batch=batch, form=edit_form), 200
