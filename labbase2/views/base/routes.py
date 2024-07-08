from flask import Blueprint
from flask import render_template
from flask import flash
from flask_login import login_required
from flask_login import current_user

from labbase2.models import db
from labbase2.models import BaseEntity


__all__ = ["bp", "index"]


# The blueprint to register all coming blueprints with.
bp = Blueprint("base", __name__, template_folder="templates")


@bp.route("/", methods=["GET"])
@login_required
def index() -> str:
    return render_template("base/index.html", title="Home")
