import math
import mimetypes
from pathlib import Path
from datetime import datetime

from flask import current_app
from labbase2.models import db
from skimage import io, util
from skimage.transform import resize
from sqlalchemy import func, ForeignKey, String, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship


__all__ = ["BaseFile", "EntityFile"]


class BaseFile(db.Model):
    """Files can be attached to any entity. It is a convenient way to add
    data to entries of the database that do not fit any of the available
    structures. For instance specification sheets for antibodies or
    chemicals, plasmid files, etc...

    Attributes
    ----------
    id : int
        The ID of the filepath for internal identification.
    user_id : int
        The id of the person that has uploaded the filepath.
    filename_internal : str
        The name of the file as it was used to save it to the filesystem.
    filename_exposed : str
        The original filename of the file or the filename provided by the user during
        upload.
    note : str
        A short note about the filepath.
    file_type : str
        The type of the file. This is used for proper mapping and setting up
        inheritance.
    timestamp_uploaded : DateTime
        The time at which the filepath was uploaded. Automatically set by the database.
    timestamp_edited : DateTime
        The time the file entry was last edited.

    Notes
    -----
    There can be different kinds of files (PDFs, images, plasmid files, etc.). Since
    these filepath types sometimes differ in the way they are shown on the website (
    especially images and PDFs) they are modelled through different child classes
    that inherit from this class. Inheritance is implemented as single-table
    inheritance, i.e., all children are represented by a single table/relation in the
    database. They are differentiated by the 'type' attribute.
    """

    __tablename__: str = "base_file"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    filename_internal: Mapped[str] = mapped_column(String(64), nullable=True, unique=True)
    filename_exposed: Mapped[str] = mapped_column(String(512), nullable=False)
    note: Mapped[str] = mapped_column(String(2048), nullable=True)
    file_type: Mapped[str] = mapped_column(String(32), nullable=False)
    timestamp_uploaded: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    timestamp_edited: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, onupdate=func.now())

    __mapper_args__ = {"polymorphic_on": file_type, "polymorphic_identity": "base_file"}

    @property
    def path(self) -> Path:
        return Path(
            current_app.instance_path,
            current_app.config["UPLOAD_FOLDER"],
            self.filename_internal,
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
    def type_(self):
        _, ext = self.filename_internal.rsplit(".", 1)
        match ext.lower():
            case "pdf":
                return "document"
            case "jpg" | "jpeg" | "png" | "tif" | "tiff":
                return "image"
            case "dna" | "gb" | "gbk":
                return "plasmid"
            case _:
                return "misc"

    @property
    def mimetype(self) -> str:
        ext = self.path.suffix.lower()
        return mimetypes.types_map.get(ext, "application/octet-stream")

    def set_filename(self):
        _, ext = self.filename_exposed.split(".", 1)
        self.filename_internal = "{0:07d}.{ext}".format(self.id, ext=ext)

    def resize(self, longest: int):
        if not self.type_ == "image":
            return

        img = io.imread(self.path)
        height, width, _ = img.shape

        if width <= longest and height <= longest:
            return

        if width > height:
            height = math.ceil(height / width * longest)
            width = longest
        else:
            width = math.ceil(width / height * longest)
            height = longest

        resized = resize(img, (height, width), anti_aliasing=True)

        io.imsave(self.path, util.img_as_ubyte(resized))


class EntityFile(BaseFile):
    """A file that is attached to an entity.

    Attributes
    ----------
    id : int
        The internal database ID of this file.
    entity_id : int
        The id of the entity to which this filepath belongs.
    """

    __tablename__ = "entity_file"

    id: Mapped[int] = mapped_column(ForeignKey("base_file.id"), primary_key=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey("base_entity.id"), nullable=False)

    __mapper_args__ = {"polymorphic_identity": "entity_file"}
