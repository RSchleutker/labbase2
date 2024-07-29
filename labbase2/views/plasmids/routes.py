from .forms import FilterPlasmids
from .forms import EditPlasmid
from . import bacteria
from . import preparations

from labbase2.utils.message import Message
from labbase2.views.comments.forms import EditComment
from labbase2.views.files.forms import UploadFile
from labbase2.views.requests.forms import EditRequest
from .preparations.forms import EditPreparation
from .bacteria.forms import EditBacterium
from labbase2.utils.permission_required import permission_required
from labbase2.models import db
from labbase2.models import Plasmid

from flask import Blueprint
from flask import render_template
from flask import request
from flask import flash
from flask import current_app as app
from flask_login import login_required
from flask_login import current_user

# from dna_features_viewer import BiopythonTranslator


__all__ = ["bp"]


# class MyCustomTranslator(BiopythonTranslator):
#     """Custom translator implementing the following theme:
#
#     - Color terminators in green, CDS in blue, all other features in gold.
#     - Do not display features that are restriction sites unless they are BamHI
#     - Do not display labels for restriction sites
#     - For CDS labels just write "CDS here" instead of the name of the gene.
#
#     """
#
#     def compute_feature_color(self, feature):
#         match feature.type:
#             case "CDS":
#                 return "#118ab2"
#             case "rep_origin":
#                 return "#ef476f"
#             case _:
#                 return "#ffd166"
#
#     def compute_filtered_features(self, features):
#         filtered = []
#
#         for ftr in features:
#             label, = ftr.qualifiers.get("label", [None])
#             if label != "source" and label is not None:
#                 filtered.append(ftr)
#
#         return filtered


# The blueprint to register all coming blueprints with.
bp = Blueprint(
    "plasmids",
    __name__,
    url_prefix="/plasmid",
    template_folder="templates"
)

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
        title="Plasmids"
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
        bacteria_form=EditBacterium
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
