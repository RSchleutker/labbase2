from datetime import timedelta
from datetime import datetime

from labbase2.models.mixins.export import Export
from labbase2.models.mixins.filter import Filter
from labbase2.models.mixins.importer import Importer

from labbase2.models import db

from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import column_property
from flask_login import current_user
from flask import current_app


__all__ = ["BaseEntity"]


class BaseEntity(db.Model, Filter, Export, Importer):
    """The basic class from which every entry in the database inherits.

    Attributes
    ----------
    id : int
        The identifier of this entity. This ID is unique among all fly
        stocks, primer, antibodies, etc.
    label : str
        A string naming the entity. The token of a stock, a chemical, etc.,
        for instance.
    entity_type : str
        The type of the instance. This is needed for proper mapping in the
        database.
    owner_id : int
        The user ID of the person who imported this entity.
    under_review : bool
        A flag indicating whether the entity is under review. That flag can be set during manual import on single
        instances (optional) and is always set when entitites are batch imported. The responsible person then has the
        chance to review each imported instance to make sure the entity was properly imported. Only instances under
        review can be deleted from the database. Once set to 'False' the entity cannot be set for review again und thus
        cannot be deleted anymore. Entities under review can only been seen by the user who imported the entity.
    comments : list of Comment
        A list of all comments that were created for this entity.
    files : list of File
        A list of all files that are attached to this entity including
        documents, images, plasmid files, etc.
    requests : list of Request
        A list of all requests that were made for this entity.

    Notes
    -----
    This base class allows that every child has a comments and files as well as a requests attribute that
    is stored in a single table in the final database. The inheritance is implemented as joined inheritance. That
    means that there is one table in the database for all entities with file_columns common to all children (those
    defined in this class) and one table for each child with file_columns specific to the respective class.
    Therefore, instances of child classes can only be constructed from the database by joining several tables.
    """

    __tablename__: str = "base_entity"

    id = db.Column(
        db.Integer,
        primary_key=True,
        info={"importable": False}
    )
    label = db.Column(
        db.String(64),
        nullable=False,
        unique=True,
        index=True,
        info={"importable": True}
    )
    timestamp_created = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(timezone=True),
        info={"importable": False}
    )
    timestamp_edited = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
        onupdate=func.now(),
        info={"importable": True}
    )
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        default=lambda: current_user.id,
        info={"importable": True}
    )
    origin = db.Column(db.String(256), nullable=True)
    entity_type = db.Column(db.String(32), nullable=False, info={"importable": False})

    # One-to-many relationships.
    comments = db.relationship(
        "Comment",
        backref="entity",
        order_by="Comment.timestamp.desc()",
        lazy=True,
        cascade="all, delete-orphan"
    )
    files = db.relationship(
        "File",
        backref="entity",
        order_by="File.timestamp.desc()",
        lazy=True,
        cascade="all, delete-orphan"
    )
    requests = db.relationship(
        "Request",
        backref="entity",
        order_by="Request.timestamp.desc()",
        lazy=True,
        cascade="all, delete-orphan"
    )

    # Proper setup for joined table inheritance.
    __mapper_args__ = {"polymorphic_identity": "base",
                       "polymorphic_on": entity_type}

    __table_args__ = {"extend_existing": True}

    @property
    def deletable(self) -> bool:
        hours = current_app.config["DELETABLE_HOURS"]
        return (datetime.now() - self.timestamp_created) <= timedelta(hours=hours)

    def to_dict(self) -> dict:
        as_dict = super().to_dict()

        return as_dict | {"comments": [c.to_dict() for c in self.comments],
                          "requests": [r.to_dict() for r in self.requests]}


