import io
from typing import Optional
from zipfile import ZIP_DEFLATED, ZipFile

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from flask import send_file
from flask_login import current_user
from labbase2.models import BaseEntity, db
from labbase2.models.fields import CustomDate
from labbase2.models.mixins import Filter, Sequence
from sqlalchemy import asc, desc

__all__ = ["Plasmid", "Preparation", "GlycerolStock"]


class Plasmid(BaseEntity, Sequence):
    """A class to represent plasmids in the database.

    Attributes
    ----------
    id : int
        The internal ID of this plasmis. The ID is unique among ALL entities
        in the datbase.
    insert : str
        The name of the insert. As explained for 'vector' a plasmid should be fully
        defined by the vector and the insert.
    vector : str
        The vector that was used for cloning. Usually, cloning means transferring an
        insert into a specific vector. By giving both the vector and the insert the
        plasmid should be fully defined.
    cloning_date : Date
        The date the plasmid was first created. This usually corresponds to the day
        of ligation.
    description : str
        A precise definition of the plasmid: What is it and what is it for. You may
        also give further information on how the plasmid was made.
    reference : str
        If the plasmid is published or was used somewhere it is possible to enter the
        DOI here.
    preparations : list[Preparation]
        A list of all preparations that were done of this plasmid.
    glycerol_stocks : list[GlycerolStock]
        A list of bacterial stocks that carry this plasmid.

    Notes
    -----
    As most other classes Plasmid inherits from Entity and therefor has three
    additional attributes: 'comments', 'files', and 'requests'. See 'Entity' for
    further explanations.
    """

    id = db.Column(db.Integer, db.ForeignKey("base_entity.id"), primary_key=True)
    insert = db.Column(db.String(128), nullable=False, info={"importable": True})
    vector = db.Column(db.String(256), info={"importable": True})
    cloning_date = db.Column(CustomDate, info={"importable": True})
    description = db.Column(db.String(2048), info={"importable": True})
    reference = db.Column(db.String(512), info={"importable": True})
    file_plasmid_id = db.Column(
        db.Integer, db.ForeignKey("base_file.id"), nullable=True
    )
    file_map_id = db.Column(db.Integer, db.ForeignKey("base_file.id"), nullable=True)

    file = db.relationship(
        "BaseFile",
        lazy=True,
        foreign_keys=[file_plasmid_id],
        single_parent=True,
        cascade="all, delete-orphan",
    )
    map = db.relationship(
        "BaseFile",
        lazy=True,
        foreign_keys=[file_map_id],
        single_parent=True,
        cascade="all, delete-orphan",
    )

    # One-to-many relationships.
    preparations = db.relationship(
        "Preparation",
        backref="plasmid",
        lazy=True,
        order_by="Preparation.emptied_date, Preparation.preparation_date",
    )
    glycerol_stocks = db.relationship(
        "GlycerolStock",
        backref="plasmid",
        lazy=True,
        order_by="GlycerolStock.disposal_date, GlycerolStock.transformation_date.desc()",
    )

    __mapper_args__ = {"polymorphic_identity": "plasmid"}

    def __len__(self):
        if record := self.seqrecord:
            return len(record)
        else:
            return 0

    @property
    def storage_place(self) -> Optional[str]:
        for preparation in self.preparations:
            if (
                preparation.date_emptied is not None
                and preparation.owner_id == current_user.id
            ):
                return preparation.restricted_storage_place

        return None

    @property
    def seqrecord(self) -> Optional[SeqRecord]:
        """The sequence of this plasmid.

        Returns
        -------
        Seq
            A biopython Seq object.

        Notes
        -----
        The sequence is read out from the plasmid filepath and consequently only
        available if such a filepath was uploaded.
        """

        if self.file_plasmid_id is None:
            return

        match self.file.path.suffix.lower():
            case ".gb" | ".gbk":
                format_ = "genbank"
            case ".dna":
                format_ = "snapgene"
            case ".xdna":
                format_ = "xdna"
            case _:
                return None

        try:
            record = SeqIO.read(self.file.path, format=format_)
        except Exception as error:
            print(error)
            return None
        else:
            return record

    @classmethod
    def to_zip(cls, entities):
        mem = io.BytesIO()

        with ZipFile(mem, "w", ZIP_DEFLATED, False) as archive:
            for plasmid in entities:
                if plasmid.file_plasmid_id:
                    archive.write(plasmid.file.path, plasmid.file.filename_exposed)
                if plasmid.file_map_id:
                    archive.write(plasmid.map.path, plasmid.map.filename_exposed)

        mem.seek(0)

        return send_file(
            mem,
            as_attachment=True,
            download_name="plasmids.zip",
        )


class Preparation(db.Model):
    """A specific preparation of a plasmid.

    Attributes
    ----------
    id : int
        The internal identifier of this preparation. This identifier is an integer
        that is not continuous with the identifiers of entities (antibodies, flies,
        plasmids, ...).
    plasmid_id : int
        The identifier of the plasmid that was prepared.
    owner_id : int
        The ID of the user who made this preparation.
    preparation_date : Date
        The date at which the preparation was done.
    method : str
        A short description of the method that was used for preparation. Most likely,
        this will be the name of the kit used.
    eluent : str
        The eluent. This will probably be either ddH2O or the elution buffer of the kit.
    concentration : float
        The concentration of this preparation. This should be in ng/ul or an
        appropriate concentration (ug/ml, ...).
    storage_place : str
        The location of this preparation.
    emptied_date : Date
        The date at which this preparation was used up.

    """

    id = db.Column(db.Integer, primary_key=True)
    plasmid_id = db.Column(db.Integer, db.ForeignKey("plasmid.id"), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    preparation_date = db.Column(db.Date)
    method = db.Column(db.String(64))
    eluent = db.Column(db.String(32))
    concentration = db.Column(db.Integer())
    storage_place = db.Column(db.String(64))
    emptied_date = db.Column(db.Date)
    stock_id = db.Column(db.Integer, db.ForeignKey("glycerol_stock.id"), nullable=False)

    stock = db.relationship("GlycerolStock", backref="preparation", lazy=True)

    @property
    def restricted_storage_place(self) -> str:
        if current_user.id == self.owner_id:
            return self.storage_place
        else:
            return "Only accessible by owner of preparation!"


class GlycerolStock(db.Model, Filter):
    """A bacterial stock (glycerol stock) of a plasmid.

    Attributes
    ----------
    id : int
        The internal identifier of this bacterial stock. This identifier is an
        integer that is not continuous with the identifiers of entities (antibodies,
        flies, plasmids, ...).
    plasmid_id : int
        The internal identifier of the plasmid that was transformed into the
        bacteria.
    owner_id : int
        The ID of the person that transformed the plasmid into the bacteria. Maximum
        number of chars is 64. This might be changed in the future to an integer that
        refers to a person that is represented in the database.
    strain : str
        The token of the bacterial strain that was used for transformation,
        for instance 'DH10B'. Maximum number of chars is 64.
    transformation_date : Date
        The date the stock was created. This is the date of transformation.
    storage_place : str
        The storage place of the stock. This should include the -80°C freezer
        and the exact shelf in that freezer. Maximum number of chars is 128.
    disposal_date : Date
        The date the stock was disposed.
    """

    __tablename__: str = "glycerol_stock"

    id = db.Column(db.Integer, primary_key=True)
    plasmid_id = db.Column(db.Integer, db.ForeignKey("plasmid.id"), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    strain = db.Column(db.String(64), nullable=False)
    transformation_date = db.Column(db.Date, nullable=False)
    storage_place = db.Column(db.String(128), nullable=False)
    disposal_date = db.Column(db.Date)

    @classmethod
    def filter_(cls, order_by: str = "label", ascending: bool = True, **fields):
        return super().filter_(order_by, ascending, **fields)

    @classmethod
    def _order_by(cls, order_by: str, ascending: bool) -> tuple:
        fnc = asc if ascending else desc
        if order_by == "label":
            field = Plasmid.label
        else:
            field = getattr(cls, order_by.strip())

        return (fnc(field),)

    @classmethod
    def _entities(cls) -> tuple:
        return cls, Plasmid.label

    @classmethod
    def _joins(cls) -> tuple:
        return (Plasmid,)
