from datetime import date

from labbase2.models import db
from labbase2.models.base_entity import BaseEntity
from labbase2.models.fields import CustomDate
from labbase2.models.mixins.importer import Importer

__all__ = ["Modification", "FlyStock"]


class Modification(db.Model, Importer):
    """
    Information about modification of fly stocks. This should be things
    like re-establishing a dead fly stock. If the genotype is altered it
    might be rather better to create a new fly stock entry.

    Attributes
    ----------
    id : int
        An internal identifier for this modifcation.
    fly_id : int
        The identifier of the fly stock to which this modifcation belongs.
    user_id : int
        ID of the person that did the modification.
    date : date
        Date of the modification. Defaults to the current date.
    description : str
        A short and precise explanation of what was done.

    """

    id = db.Column(db.Integer, primary_key=True)
    fly_id = db.Column(db.Integer, db.ForeignKey("fly_stock.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    date = db.Column(db.Date)
    description = db.Column(db.String(1024))


class FlyStock(BaseEntity):
    """A fly stock.

    Attributes
    ----------
    id : int
        The internal ID of this fly stock. This ID is unique among ALL entities
        in the database.
    short_genotype : str
        The complete genotype of this stock. Heterologeous chromosomes are
        separated by ';' and homologeous chromosomes are separated by '/'.
        The order of the chromosomes is 'x ; y ; 2 ; 3 ; 4'.
    chromosome_xa : str
    chromosome_xb : str
    chromosome_y : str
    chromosome_2a : str
    chromosome_2b : str
    chromosome_3a : str
    chromosome_3b : str
    chromosome_4a : str
    chromosome_4b : str
    location : str
        A string describing where this stock is located.
    created_date : date
        The date at which this stock was created.
    source : str
        The source of this stock. This might be either the token of the person
        that created this stock or Bloomington, VDRC, Kyoto, etc.
    documentation : str
        If this stock was created in our lab this should be a short
        description about how this stock was created or, even better,
        the pages in the lab book describing the generation of this stock.
    reference : str
        The DOI of a publication in which this stock was used.
    discarded_date : date
        The date at which this stock was discarded or died out.

    """

    id = db.Column(
        db.Integer,
        db.ForeignKey("base_entity.id"),
        primary_key=True,
        info={"importable": False},
    )
    short_genotype = db.Column(db.String(2048), info={"importable": True})
    chromosome_xa = db.Column(
        db.String(2048), nullable=False, default="+", info={"importable": True}
    )
    chromosome_xb = db.Column(
        db.String(2048), nullable=False, default="+", info={"importable": True}
    )
    chromosome_y = db.Column(
        db.String(2048), nullable=False, default="+", info={"importable": True}
    )
    chromosome_2a = db.Column(
        db.String(2048), nullable=False, default="+", info={"importable": True}
    )
    chromosome_2b = db.Column(
        db.String(2048), nullable=False, default="+", info={"importable": True}
    )
    chromosome_3a = db.Column(
        db.String(2048), nullable=False, default="+", info={"importable": True}
    )
    chromosome_3b = db.Column(
        db.String(2048), nullable=False, default="+", info={"importable": True}
    )
    chromosome_4a = db.Column(
        db.String(2048), nullable=False, default="+", info={"importable": True}
    )
    chromosome_4b = db.Column(
        db.String(2048), nullable=False, default="+", info={"importable": True}
    )
    location = db.Column(db.String(64), info={"importable": True})
    created_date = db.Column(CustomDate, info={"importable": True})
    source = db.Column(db.String(512), info={"importable": True})
    documentation = db.Column(db.String(2048), info={"importable": True})
    reference = db.Column(db.String(512), info={"importable": True})
    discarded_date = db.Column(CustomDate, info={"importable": True})

    # One-to-many relationships.
    modifications = db.relationship(
        "Modification",
        backref="fly_stock",
        order_by="Modification.date.desc()",
        lazy=True,
    )

    # Proper setup for joined table inheritance.
    __mapper_args__ = {"polymorphic_identity": "fly_stock"}

    @classmethod
    def _filters(cls, **fields) -> list:
        filters = []

        match fields.pop("discarded", "all"):
            case "discarded":
                filters.append(cls.discarded_date.isnot(None))
            case "recent":
                filters.append(cls.discarded_date.is_(None))
            case _:
                pass

        return super()._filters(**fields) + filters
