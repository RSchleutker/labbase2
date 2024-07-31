from flask import Blueprint, render_template
from flask_login import login_required

__all__ = ["bp"]


# The blueprint to register all coming blueprints with.
bp = Blueprint("base", __name__, template_folder="templates")


@bp.route("/", methods=["GET"])
@login_required
def index() -> str:
    return render_template("base/index.html", title="Home")


# TODO: Add changelog.
