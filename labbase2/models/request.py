from labbase2.models import db
from labbase2.models.mixins.importer import Importer
from sqlalchemy import func

__all__ = ["Request"]


class Request(db.Model, Importer):
    """A table of requests for a specific entity. This is most useful for fly
    stocks, self-made antibodies, and plasmids.

    Attributes
    ----------
    id : int
        The internal id of the request.
    entity_id : int
        The id of the entity that was requested.
    requested_by : str
        Name of the person that has asked for the entity.
    timestamp : Date
        Date of the request. This defaults to the current date.
    timestamp_sent : date
        The date at which the entity was sent to the requester.

    Notes
    -----
    The whole point about the BaseEntity class is to have a single implementation for
    comments and files that are interesting for all entities. Requests are special in
    this sense as it does not make sense for all kind of child classes. Commercially
    available antibodies or chemicals, for instance, will never be requested.
    However, the BaseEntity class is still the least common denominator to all
    classes, for which requests are of interest.
    """

    id = db.Column(db.Integer, primary_key=True, info={"importable": False})
    entity_id = db.Column(
        db.Integer,
        db.ForeignKey("base_entity.id"),
        nullable=False,
        info={"importable": True},
    )
    requested_by = db.Column(db.String(128), nullable=False, info={"importable": True})
    timestamp = db.Column(
        db.Date, server_default=func.today(), info={"importable": True}
    )
    timestamp_sent = db.Column(db.Date, info={"importable": True})
    note = db.Column(db.String(2048), nullable=True, info={"importable": True})

    __table_args__ = {"extend_existing": True}

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "requested_by": self.requested_by,
            "timestamp": self.timestamp.isoformat(),
            "sent": self.sent.isoformat() if self.sent else None,
        }
