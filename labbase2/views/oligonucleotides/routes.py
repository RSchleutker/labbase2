from .forms import EditOligonucleotide
from .forms import FilterOligonucleotide
from .forms import FindOligonucleotide
from .lcsfinder import LCSFinder

from labbase2.forms.utils import err2message

from labbase2.utils.message import Message
from labbase2.utils.role_required import role_required
from labbase2.models import db
from labbase2.models import Oligonucleotide
from labbase2.views.files.forms import UploadFile
from labbase2.views.comments.forms import EditComment

from flask import Blueprint
from flask import render_template
from flask import request
from flask import flash
from flask import current_app as app
from flask_login import login_required
from flask_login import current_user
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from Bio.Seq import Seq


__all__ = ["bp"]


# The blueprint to register all coming blueprints with.
bp = Blueprint(
    "oligonucleotides",
    __name__,
    url_prefix="/oligonucleotide",
    template_folder="templates"
)


@bp.route("/", methods=["GET"])
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    form = FilterOligonucleotide(request.args)

    data = form.data
    del data["submit"]
    del data["csrf_token"]

    try:
        entities = Oligonucleotide.filter_(**data)
    except Exception as error:
        flash(str(error), "danger")
        entities = Oligonucleotide.filter_(order_by="label")

    return render_template(
        "oligonucleotides/main.html",
        filter_form=form,
        import_file_form=UploadFile(),
        add_form=EditOligonucleotide(formdata=None),
        entities=entities.paginate(page=page, per_page=app.config["PER_PAGE"]),
        title="Oligonucleotides"
    )


@bp.route("/<int:id_>", methods=["GET"])
@login_required
def details(id_: int):
    if not (oligonucleotide := Oligonucleotide.query.get(id_)):
        return Message.ERROR(f"No oligonucleotide with ID {id_}!")

    return render_template(
        "oligonucleotides/details.html",
        oligonucleotide=oligonucleotide,
        form=EditOligonucleotide(None, obj=oligonucleotide),
        comment_form=EditComment,
        file_form=UploadFile
    )


@bp.route("/", methods=["POST"])
@login_required
def add():
    if (form := EditOligonucleotide()).validate():
        oligonucleotide = Oligonucleotide()
        oligonucleotide.origin = f"Created via import form by {current_user.username}."
        form.populate_obj(oligonucleotide)

        try:
            db.session.add(oligonucleotide)
            db.session.commit()
        except IntegrityError as error:
            return Message.ERROR(error)
        except Exception as error:
            return Message.ERROR(error)
        else:
            return Message.SUCCESS(
                f"Successfully added oligonucleotide '{oligonucleotide.label}'!"), 201

    else:
        return err2message(form.errors), 400


@bp.route("/<int:id_>", methods=["PUT"])
@login_required
@role_required(roles=["editor", "viewer"])
def edit(id_: int):
    if (form := EditOligonucleotide()).validate():
        if not (oligonucleotide := Oligonucleotide.query.get(id_)):
            return Message.ERROR(f"No oligonucleotide with ID {id_}!"), 404
        elif oligonucleotide.owner_id != current_user.id:
            return Message.ERROR("Oligonucleotide can only be edited by owner!"), 403
        else:
            form.populate_obj(oligonucleotide)

        try:
            db.session.commit()
        except Exception as err:
            return Message.ERROR(str(err)), 400
        else:
            return Message.SUCCESS(
                f"Successfully edited oligonucleotide {oligonucleotide.label}!"), 200

    else:
        return err2message(form.errors), 400


@bp.route("/<int:id_>", methods=["DELETE"])
@login_required
@role_required(roles=["editor", "viewer"])
def delete(id_):
    if not (oligonucleotide := Oligonucleotide.query.get(id_)):
        return Message.ERROR(f"No oligonucleotide with ID {id_}!"), 404
    elif oligonucleotide.owner_id != current_user.id:
        return Message.ERROR("Only owner can delete oligonucleotide!"), 403
    else:
        try:
            db.session.delete(oligonucleotide)
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            return Message.ERROR(str(err)), 400
        else:
            return Message.SUCCESS("Successfully deleted oligonucleotide!"), 200


@bp.route("/find", methods=["GET", "POST"])
@login_required
def find():
    form = FindOligonucleotide()
    results = []

    if form.validate_on_submit():
        seq = form.sequence.data
        min_match = form.min_match.data
        max_len = form.max_len.data
        length = len(seq)

        if form.reverse_complement.data:
            seq = str(Seq(seq).reverse_complement())

        lcsfinder = LCSFinder(seq)
        oligonucleotides = Oligonucleotide.query.filter(
            func.length(Oligonucleotide.sequence) >= min_match,
            func.length(Oligonucleotide.sequence) <= max_len,
        )

        for oligonucleotide in oligonucleotides:
            try:
                lcsresult = lcsfinder(oligonucleotide.sequence)
            except Exception as error:
                flash(str(error), "danger")
                continue

            if lcsresult.length >= min_match:
                results.append((oligonucleotide, lcsresult))

        # Sort results from longest to shorted common substring.
        results.sort(key=lambda x: x[1].length, reverse=True)
    else:
        length = 0

    return render_template(
        "oligonucleotides/find.html",
        filter_form=form,
        entities=results,
        length=length,
        title="Find oligonucleotides"
    ), 200


@bp.route("/export/<string:format_>/", methods=["GET"])
@login_required
def export(format_: str):
    data = FilterOligonucleotide(request.args).data

    del data["submit"]
    del data["csrf_token"]

    try:
        entities = Oligonucleotide.filter_(**data)
    except Exception:
        return "An internal error occurred! Please inform the admin!", 500

    match format_.lower():
        case "csv":
            return Oligonucleotide.export_to_csv(entities)
        case "json":
            return Oligonucleotide.export_to_json(entities)
        case "fasta":
            return Oligonucleotide.to_fasta(entities)
        case _:
            return Message.ERROR(f"Unsupported format: {format_}"), 400
