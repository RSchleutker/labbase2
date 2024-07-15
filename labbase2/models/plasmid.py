import io

from labbase2.models.mixins import Sequence
from labbase2.models.mixins import Filter
from labbase2.models import BaseEntity
from labbase2.models import db
from labbase2.models.fields import CustomDate

from flask import send_file
from flask_login import current_user
from sqlalchemy import asc
from sqlalchemy import desc
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from datetime import date
from Bio import SeqIO

from zipfile import ZipFile
from zipfile import ZIP_DEFLATED


__all__ = ["Plasmid", "Preparation", "GlycerolStock"]


class Plasmid(BaseEntity, Sequence):
    """A class to represent plasmids in the database.

    Attributes
    ----------
    id : int
        The internal ID of this plasmis. The ID is unique among ALL entities
        in the datbase.
    vector : str
        The vector that was used for cloning. Usually, cloning means
        transferring an insert into a specific vector. By giving both the
        vector and the insert the plasmid should be fully defined.
    constructed_by : str
        The token of the person(s) that constructed and created the plasmid.
    created : date
        The date the plasmid was first created. This usually corresponds to
        the day of ligation.
    description : str
        A precise definition of the plasmid: What is it and what is it for.
        You may also give further information on how the plasmid was made.
    reference : str
        If the plasmid is published or was used somewhere it is possible to
        enter the DOI here.
    insert : str
        The token of the insert. As explained for 'vector' a plasmid should be
        fully defined by the vector and the insert.
    preps : list of Preparation
        A list of all preps that were done of this plasmid.
    bacteria : list of Bacteria
        A list of bacterial stocks that carry this plasmid.
    features : list of Feature
        A list of all features that this plasmid has like ampicillin
        resistance etc.
    sequence : Seq
        The sequence of the plasmid. The sequence is only available if a
        plasmid filepath was uploaded for the plasmid. This plasmid filepath
        is then read out and the sequence returned as a biopython Seq object.
        This attribute is generated with the @property decorator and accordingly
        can not be set manually.
    risk : int
        The risk potential of this plasmid. It is determined as the highest
        risk of any feature. This attribute is generated with the @property
        decorator and accordingly can not be set manually.

    Notes
    -----
    As most other classes Plasmid inherits from Entity and therefor has three
    additional attributes: 'comments', 'files', and 'requests'. See 'Entity'
    for further explanations.
    """

    id = db.Column(db.Integer, db.ForeignKey("base_entity.id"), primary_key=True)
    insert = db.Column(db.String(128), nullable=False, info={"importable": True})
    vector = db.Column(db.String(256), info={"importable": True})
    cloning_date = db.Column(CustomDate, info={"importable": True})
    description = db.Column(db.String(1024), info={"importable": True})
    reference = db.Column(db.String(512), info={"importable": True})

    # One-to-many relationships.
    preparations = db.relationship(
        "Preparation",
        backref="plasmid",
        lazy=True,
        order_by="Preparation.emptied_date, Preparation.preparation_date"
    )
    glycerol_stocks = db.relationship(
        "GlycerolStock",
        backref="plasmid",
        lazy=True,
        order_by="GlycerolStock.disposal_date, GlycerolStock.transformation_date.desc()"
    )

    __mapper_args__ = {"polymorphic_identity": "plasmid"}

    def __len__(self):
        if record := self.seqrecord:
            return len(record)
        else:
            return 0

    @property
    def storage_place(self) -> str:
        for preparation in self.preparations:
            if (preparation.emptied_date is not None
                    and preparation.owner_id == current_user.id):
                return preparation.restricted_storage_place

        return None

    @property
    def file(self):
        for file in self.files:
            if file.type == "plasmid":
                return file

    @property
    def seqrecord(self) -> SeqRecord | None:
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

        if not (file := self.file):
            return None

        match file.path.suffix.lower():
            case ".gb" | ".gbk":
                format = "genbank"
                reader = io.StringIO
            case ".dna":
                format = "snapgene"
                reader = io.BytesIO
            case ".xdna":
                format = "xdna"
                reader = io.BytesIO
            case _:
                return None

        with reader(file.data) as handle:
            try:
                record = SeqIO.read(handle, format=format)
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
                if not (file := plasmid.file):
                    continue
                else:
                    archive.write(file.path, file.filename)

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
        The internal identifier of this preparation. This identifier is an
        integer that is not continuous with the identifiers of entities (
        antibodies, flies, plasmids, ...).
    plasmid_id : int
        The identifier of the plasmid that was prepared.
    by : str
        The person who did this preparation.
    timestamp : date
        The date at which the preparation was done.
    method : str
        A short description of the method that was used for preparation. Most
        likely, this will be the token of the kit used.
    eluent : str
        The eluent. This will probably be either ddH2O or the elution buffer
        of the kit.
    concentration : float
        The concentration of this preparation. This should be in ng/ul or an
        appropriate concentration (ug/ml, ...).
    location : str
        The location of this preparation.
    empty_timestamp : date
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
        integer that is not continuous with the identifiers of entities (
        antibodies, flies, plasmids, ...).
    plasmid_id : int
        The internal identifier of the plasmid that was transformed into the
        bacteria.
    strain : str
        The token of the bacterial strain that was used for transformation,
        for instance 'DH10B'. Maximum number of chars is 64.
    risk_group : str
        The risk group of thr bacterial strain. Is must not be set manually
        but should be automatically determined by the application in order to
        the strain and the features of the transformed plasmid. Maximum
        number of chars is 8.
    created : date
        The date the stock was created. This is the date of transformation.
    created_by : str
        The token of the person that transformed the plasmid into the
        bacteria. Maximum number of chars is 64. This might be changed in the
        future to an integer that refers to a person that is represented in
        the database.
    location : str
        The storage place of the stock. This should include the -80°C freezer
        and the exact shelf in that freezer. Maximum number of chars is 128.
    disposed : date
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
    def filter_(cls, order_by: str = 'label', ascending: bool = True, **fields):
        return super().filter_(order_by, ascending, **fields)

    @classmethod
    def _order_by(cls, order_by: str, ascending: bool) -> tuple:
        fnc = asc if ascending else desc
        if order_by == 'label':
            field = Plasmid.label
        else:
            field = getattr(cls, order_by.strip())

        return fnc(field),

    @classmethod
    def _entities(cls) -> tuple:
        return cls, Plasmid.label

    @classmethod
    def _joins(cls) -> tuple:
        return Plasmid,
