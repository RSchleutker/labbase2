from labbase2.models import db

from flask import current_app
from sqlalchemy import func
from pathlib import Path
from datetime import date


__all__ = ["BaseFile", "EntityFile"]


class BaseFile(db.Model):
    """Files can be attached to any entity. It is a convenient way to add
    data to entries of the database that do not fit any of the available
    structures. For instance specification sheets for antibodies or
    chemicals, plasmid files, etc...

    Attributes
    ----------
    id : int
        The id of the filepath for internal identification.
    entity_id : int
        The id of the entity to which this filepath belongs.
    user_id : int
        The id of the person that has uploaded the filepath.
    filename : str
        The token of the filepath. The extension will be used to automatically
        set the type.
    note : str
        A short note about the filepath.
    type : str
        The type of the filepath. Currently supported is 'image', 'document', 'plasmid'. Everything else is
        miscellaneous.
    timestamp : date
        The date at which the filepath was uploaded.

    Notes
    -----
    There can be different kinds of files (PDFs, images, plasmid files, etc.). Since these filepath types sometimes
    differ in the way they are shown on the website (especially images and PDFs) they are modelled through different
    child classes that inherit from this class. Inheritance is implemented as single-table inheritance, i.e.,
    all children are represented by a single table/relation in the database. They are differentiated by the 'type'
    attribute.
    """

    __tablename__: str = "base_file"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    filename_internal = db.Column(db.String(512), nullable=True, unique=True)
    filename_exposed = db.Column(db.String(512), nullable=False)
    note = db.Column(db.String(512))
    file_type = db.Column(db.String(32), nullable=False)
    timestamp_uploaded = db.Column(db.DateTime, nullable=False, server_default=func.now())
    timestamp_edited = db.Column(db.DateTime(timezone=True), nullable=True, onupdate=func.now())

    __mapper_args__ = {
        "polymorphic_on": file_type,
        "polymorphic_identity": "base_file"
    }

    @property
    def path(self) -> Path:
        return Path(
            current_app.instance_path,
            current_app.config["UPLOAD_FOLDER"],
            self.filename_internal
        )

    @property
    def data(self):
        try:
            with open(self.path, mode="r") as file:
                return file.read()
        except UnicodeDecodeError:
            with open(self.path, mode="rb") as file:
                return file.read()

    @property
    def mimetype(self) -> str:
        _, ext = self.filename.split(".", 1)
        return f"application/{ext.lower()}"

    def set_filename(self):
        _, ext = self.original_filename.split(".", 1)
        self.filename = "{0:07d}.{ext}".format(self.id, ext=ext)


class EntityFile(BaseFile):

    __tablename__ = "entity_file"

    id = db.Column(db.Integer, db.ForeignKey("base_file.id"), primary_key=True)
    entity_id = db.Column(
        db.Integer,
        db.ForeignKey("base_entity.id"),
        nullable=False
    )

    __mapper_args__ = {"polymorphic_identity": "entity_file"}
