from labbase2.models import db
from labbase2.models.mixins.export import Export
from labbase2.models.mixins.importer import Importer
from sqlalchemy import func, String, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from datetime import datetime

__all__ = ["Comment"]

from sqlalchemy.orm import Mapped


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
    timestamp_created : DateTime
        The time of the comment. This is automatically set by the database.
    timestamp_edited : DateTime
        The time this comment was last edited. Might be `None` if the comment was
        never modified.
    subject : str
        A short string describing the subject of the comment.
    text : str
        The message of the comment.
    """

    __tablename__: str = "comment"

    id: Mapped[int] = mapped_column(primary_key=True, info={"importable": False})
    entity_id: Mapped[int] = mapped_column(ForeignKey("base_entity.id"), nullable=False, info={"importable": True})
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, info={"importable": True})
    timestamp_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), info={"importable": True}
    )
    timestamp_edited: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=func.now(), info={"importable": True}
    )
    subject: Mapped[str] = mapped_column(String(128), nullable=False, info={"importable": True})
    text: Mapped[str] = mapped_column(String(2048), nullable=False, info={"importable": True})

    __table_args__ = {"extend_existing": True}
