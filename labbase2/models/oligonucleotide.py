import string

from labbase2.models.mixins import Sequence
from labbase2.models import BaseEntity
from labbase2.models import db
from labbase2.models.fields import SequenceString

from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy.orm import column_property
from flask_login import current_user
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqUtils import GC
from itertools import chain
from itertools import zip_longest
from datetime import date
import re


__all__ = ["Oligonucleotide"]


# Map finding jobs to the oligonucleotide in a many-to-many relationship.
find_oligonucleotides_result = db.Table(
    "find_oligonucleotides_result",
    db.Column(
        "job_id",
        db.String(36),
        db.ForeignKey("find_oligonucleotides_job.id"),
        primary_key=True
    ),
    db.Column(
        "oligonucleotide_id",
        db.Integer,
        db.ForeignKey("oligonucleotide.id"),
        primary_key=True
    ),
    db.Column("profile", db.String)
)


class Oligonucleotide(BaseEntity, Sequence):
    """A class to represent a primer.

    Attributes
    ----------
    id : int
        The internal ID of this primer. This ID is unique among ALL entities
        in the database.
    owner_id : int
        Foreign key to the user owning this oligonucleotide.
    date_ordered : date
        The date this oligo was ordered.
    sequence : str
        The sequence of the primer. This should be all uppercase. Lowercase letters can be used to highlight special
        parts of the sequence like non-matching bases or overhangs. Lowercase letters will be emphasized in the app.
        A sequence consisting only of lowercase letters will be converted to uppercase. Max length is 256.
    storage_place : str
        The storage location of the primer. Max length is 64.
    description : str
        A description of the purpose of the primer. Max length is 512.
    """

    __tablename__: str = "oligonucleotide"

    id = db.Column(
        db.Integer,
        db.ForeignKey("base_entity.id"),
        primary_key=True,
        info={"importable": False}
    )
    date_ordered = db.Column(
        db.Date,
        nullable=False,
        info={"importable": True}
    )
    sequence = db.Column(
        SequenceString(256),
        nullable=False,
        info={"importable": True}
    )
    storage_place = db.Column(
        db.String(64),
        info={"importable": True}
    )
    description = db.Column(
        db.String(512),
        info={"importable": True}
    )

    __mapper_args__ = {"polymorphic_identity": "oligonucleotide"}

    def __len__(self):
        return len(self.sequence)

    @property
    def gc_content(self) -> float:
        return GC(self.sequence)

    def formatted_seq(self, max_len: int = None) -> str:
        """Creates a formatted string for the sequence attribute by placing HTML <span> blocks around lowercase letters.

        Parameters
        ----------
        max_len : int
            The maximum number of bases that shall be returned. Default is 'None' which means all bases.

        Returns
        -------
        str
            The sequence of this primer with '<span class="lower-seq">'
            elements around blocks of lowercase letters.

        """

        seq = self.sequence[:max_len]
        if max_len and max_len < len(self):
            seq += '...'

        # Extract blocks of lowercase and uppercase letters from sequence.
        low = re.compile("[a-z]+").findall(seq)
        upp = re.compile("[A-Z.]+").findall(seq)

        low = [f'<span class="lower-seq">{s}</span>' for s in low]

        # Merge the sequences in correct order.
        ordered = (low, upp) if seq[0].islower() else (upp, low)

        return "".join(chain(*zip_longest(*ordered, fillvalue="")))

    @property
    def seqrecord(self) -> SeqRecord:
        seq = [L if L in "ATCG" else "." for L in self.sequence.upper()]

        return SeqRecord(
            Seq("".join(seq)),
            id=self.label,
            description=f"id={self.id};len={len(self)}"
        )

    @classmethod
    def _order_by(cls, order_by: str, ascending: bool) -> tuple:
        match order_by:
            case "length":
                field = func.length(cls.sequence)
            case _:
                field = getattr(cls, order_by)

        fnc = asc if ascending else desc

        return fnc(field),


class FindOligoJob(db.Model):

    __tablename__ = "find_oligonucleotides_job"

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        default=lambda: current_user.id,
        nullable=False,
        info={"importable": False}
    )
    submission_time = db.Column(db.DateTime, default=func.now(), nullable=False)
    finished_time = db.Column(db.DateTime, nullable=True)
    query_sequence = db.Column(db.String(256), nullable=False)
    reverse_complement = db.Column(db.Boolean, nullable=False)
    minimum_match_length = db.Column(db.Integer, nullable=False)
    maximum_oligo_length = db.Column(db.Integer, nullable=False)

    has_finished = column_property(finished_time.isnot(None).label("has_finished"), deferred=True)

    # Many-to-many relationships.
    oligonucleotides = db.relationship(
        "Oligonucleotide",
        secondary=find_oligonucleotides_result,
        lazy="subquery",
        backref=db.backref("find_jobs", lazy=True)
    )
