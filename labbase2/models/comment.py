from labbase2.models.mixins.export import Export
from labbase2.models.mixins.importer import Importer

from labbase2.models import db

from sqlalchemy import func


__all__ = ["Comment"]


class Comment(db.Model, Importer, Export):
    """A comment to an entity.

    Attributes
    ----------
    id : int
        The identifier of this comment.
    entity_id : int
        The identifier of the entity about which this comment is.
    user_id : str
        The id of the person that has written the comment.
    timestamp : date
        The date of the comment. This defaults to the current date.
    text : str
        The message of the comment.
    """

    __tablename__: str = "comment"

    id = db.Column(
        db.Integer,
        primary_key=True,
        info={"importable": False}
    )
    entity_id = db.Column(
        db.Integer,
        db.ForeignKey("base_entity.id"),
        nullable=False,
        info={"importable": True}
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        info={"importable": True}
    )
    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(timezone=True),
        info={"importable": True}
    )
    timestamp_edited = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
        onupdate=func.now(timezone=True),
        info={"importable": True}
    )
    subject = db.Column(
        db.String(128),
        nullable=True,
        info={"importable": True}
    )
    text = db.Column(
        db.String(2048),
        nullable=False,
        info={"importable": True}
    )

    __table_args__ = {"extend_existing": True}
