from datetime import datetime, timedelta

from flask import current_app
from flask_login import current_user
from labbase2.models import db, mixins
from sqlalchemy import func, Table, Column, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

__all__ = ["BaseEntity"]


base_to_base = db.Table(
    "base_to_base",
    Column("left_base_id", db.ForeignKey("base_entity.id"), primary_key=True),
    Column("right_base_id", db.ForeignKey("base_entity.id"), primary_key=True),
)


class BaseEntity(db.Model, mixins.Filter, mixins.Export, mixins.Importer):
    """The basic class from which every entry in the database inherits.

    Attributes
    ----------
    id : int
        The identifier of this entity. This ID is unique among all fly stocks,
        primer, antibodies, etc.
    label : str
        A string naming the entity. This must be unique among all entities and is
        supposed to be more human accessible than the ID.
    timestamp_created : DatetTime
        The time this entity was added to the database. This is not to be set by the
        user but will be set by the database.
    timestamp_edited : DatetTime
        The time this entity was last edited. Can be `None` if the entity was never
        modified. Update will automatically be triggered by the application and set
        by the database.
    owner_id : int
        The user ID of the person who imported this entity.
    origin : str
        A short string describing how the entity was added to the database.
    entity_type : str
        The type of the instance. This is needed for proper mapping in the database
        and setting up inheritance.
    comments : list[Comment]
        A list of all comments that were created for this entity.
    files : list[File]
        A list of all files that are attached to this entity. Note that some models
        feature additional files like plasmid maps for `Plasmid`. These file swill
        not be included in this list.
    requests : list[Request]
        A list of all requests that were made for this entity.

    Notes
    -----
    This base class allows that every child has a comments and files as well as a
    requests attribute that is stored in a single table in the final database. The
    inheritance is implemented as joined inheritance. That means that there is one
    table in the database for all entities with file_columns common to all children
    (those defined in this class) and one table for each child with file_columns
    specific to the respective class. Therefore, instances of child classes can only
    be constructed from the database by joining several tables.
    """

    __tablename__: str = "base_entity"

    id: Mapped[int] = mapped_column(primary_key=True, info={"importable": False})
    label: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True, info={"importable": True})
    timestamp_created: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), info={"importable": False}
    )
    timestamp_edited: Mapped[datetime] = mapped_column(
        DateTime(), nullable=True, onupdate=func.now(), info={"importable": True}
    )
    owner_id: Mapped[int] = mapped_column(
        db.ForeignKey("user.id"), nullable=False, default=lambda: current_user.id, info={"importable": True}
    )
    origin: Mapped[str] = mapped_column(String(256), nullable=True, info={"importable": False})
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False, info={"importable": False})

    # One-to-many relationships.
    comments: Mapped[list["Comment"]] = relationship(
        backref="entity", order_by="Comment.timestamp_created.desc()", lazy=True, cascade="all, delete-orphan"
    )
    files: Mapped[list["EntityFile"]] = relationship(
        backref="entity", order_by="EntityFile.timestamp_uploaded.desc()", lazy=True, cascade="all, delete-orphan"
    )
    requests: Mapped[list["Request"]] = relationship(
        backref="entity", order_by="Request.timestamp.desc()", lazy=True, cascade="all, delete-orphan"
    )

    # Self-referencing
    self_references: Mapped[list["BaseEntity"]] = relationship(
        secondary=base_to_base,
        primaryjoin=id == base_to_base.c.left_base_id,
        secondaryjoin=id == base_to_base.c.right_base_id,
        backref="self_referenced_by",
    )

    # Proper setup for joined table inheritance.
    __mapper_args__ = {"polymorphic_identity": "base", "polymorphic_on": entity_type}

    __table_args__ = {"extend_existing": True}

    @property
    def deletable(self) -> bool:
        hours = current_app.config["DELETABLE_HOURS"]
        return (datetime.now() - self.timestamp_created) <= timedelta(hours=hours)

    def to_dict(self) -> dict:
        as_dict = super().to_dict()

        return as_dict | {
            "comments": [c.to_dict() for c in self.comments],
            "requests": [r.to_dict() for r in self.requests],
        }

    @classmethod
    def _filters(cls, **fields) -> list:
        filters = []

        owner_id = fields.pop("owner_id", 0)
        if owner_id != 0:
            filters.append(cls.owner_id == owner_id)

        return super()._filters(**fields) + filters
