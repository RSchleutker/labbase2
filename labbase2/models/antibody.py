from labbase2.models import db, mixins
from labbase2.models.consumable import Consumable
from sqlalchemy import func

__all__ = ["Antibody", "Dilution"]


class Antibody(Consumable):
    """This class models a table for antibodies.

    Attributes
    ----------
    id : int
        An internal identifier of this antibody. This not to be set by the user but
        by the database.
    clone : str
        The clone from which this antibody was produced. Only relevant for monoclonal
        antibodies.
    host : str
        The host, i.e. die animal, in which this antibody has been raised. For
        nanobodies, something like 'Camelid' is appropriate.
    antigen : str
        The antigen against which this antibody has been raised.
    specification : str
        The clonality of the antibody. Usually one of 'Monoclonal', 'Polyclonal', or
        'Superclonal'.
    storage_temp : int
        The temperature in °C at which this antibody should be stored.
    source : str
        The source of this antibody. This is most important if the antibody is not
        commercially available.
    conjugate : str
        Some antibodies (e.g. secondaries) are conjugated with fluorophores or
        enzymes for detection.
    dilutions : list[Dilution]
        A list of dilutions. Each dilution indicates how this antibody should be
        diluted for a given application.
    """

    __tablename__: str = "antibody"

    id = db.Column(db.Integer, db.ForeignKey("consumable.id"), primary_key=True)
    clone = db.Column(db.String(32), info={"importable": True})
    host = db.Column(db.String(64), nullable=False, info={"importable": True})
    antigen = db.Column(db.String(256), nullable=False, info={"importable": True})
    specification = db.Column(db.String(64), info={"importable": True})
    storage_temp = db.Column(db.Integer, info={"importable": True})
    source = db.Column(db.String(64), info={"importable": True})
    conjugate = db.Column(db.String(64), info={"importable": True})

    # One-to-many relationships.
    dilutions = db.relationship(
        "Dilution",
        backref="antibody",
        lazy=True,
        order_by="Dilution.application, Dilution.timestamp_created.desc(), Dilution.id",
        cascade="all, delete-orphan",
    )

    __mapper_args__ = {"polymorphic_identity": "antibody"}

    def to_dict(self) -> dict:
        as_dict = super().to_dict()

        return as_dict | {"dilutions": [d.to_dict() for d in self.dilutions]}


class Dilution(db.Model, mixins.Export):
    """This table is considered to hold information about working dilutions
    for antibodies for different applications like immunostaining or western
    blot.

    Attributes
    ----------
    id : int
        An internal identifier of this dilution.
    antibody_id : int
        The ID of the antibody for the given entry.
    user_id : int
        ID of the user who determined this dilution (experimentally).
    application : str
        Specification of the application, e.g. 'Western blot' or 'Immunostaining'.
    dilution : str
        The dilution for the given antibody and application. This might be given in
        the form '1:x' or as an absolute concentration.
    reference : str
        A short explanation how this dilution was determined. This might refer to the
        spec sheet or the lab book.
    timestamp_created : DateTime
        The time at which this dilution was added to the database.
    timestamp_edited : DateTime
        The time at which this dilution was last edited. Might be `None` is it was
        never modified.
    """

    id = db.Column(db.Integer, primary_key=True)
    antibody_id = db.Column(db.Integer, db.ForeignKey("antibody.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    application = db.Column(db.String(64), nullable=False)
    dilution = db.Column(db.String(32), nullable=False)
    reference = db.Column(db.String(2048), nullable=False, info={"importable": True})
    timestamp_created = db.Column(
        db.DateTime, server_default=func.now(timezone=True), info={"importable": True}
    )
    timestamp_edited = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
        onupdate=func.now(timezone=True),
        info={"importable": True},
    )


# TODO: Implement an upvote system for dilutions.
