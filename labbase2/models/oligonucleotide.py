import re
from datetime import date
from itertools import chain, zip_longest

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqUtils import gc_fraction
from labbase2.models import BaseEntity, db
from labbase2.models.fields import SequenceString
from labbase2.models.mixins import Sequence
from sqlalchemy import asc, desc, func, ForeignKey, String, Date
from sqlalchemy.orm import mapped_column, Mapped, relationship

__all__ = ["Oligonucleotide"]


class Oligonucleotide(BaseEntity, Sequence):
    """A class to represent a primer.

    Attributes
    ----------
    id : int
        The internal ID of this primer. This ID is unique among ALL entities in the
        database.
    date_ordered : date
        The date this oligo was ordered.
    sequence : str
        The sequence of the primer. Will be automatically converted to uppercase
        letters. Whitespaces are removed. Max length is 256.
    storage_place : str
        The storage location of the primer. Max length is 64.
    description : str
        A description of the purpose of the primer. Max length is 512.
    """

    __tablename__: str = "oligonucleotide"

    id: Mapped[int] = mapped_column(ForeignKey("base_entity.id"), primary_key=True, info={"importable": False})
    date_ordered: Mapped[date] = mapped_column(Date, nullable=False, info={"importable": True})
    sequence: Mapped[str] = mapped_column(SequenceString(256), nullable=False, info={"importable": True})
    storage_place: Mapped[str] = mapped_column(String(64), nullable=True, info={"importable": True})
    description: Mapped[str] = mapped_column(String(512), nullable=True, info={"importable": True})

    __mapper_args__ = {"polymorphic_identity": "oligonucleotide"}

    def __len__(self):
        return len(self.sequence)

    @property
    def gc_content(self) -> float:
        return gc_fraction(self.sequence)

    def formatted_seq(self, max_len: int = None) -> str:
        """Creates a formatted string for the sequence attribute by placing HTML
        <span> blocks around lowercase letters.

        Parameters
        ----------
        max_len : int
            The maximum number of bases that shall be returned. Default is 'None'
            which means all bases.

        Returns
        -------
        str
            The sequence of this primer with '<span class="lower-seq">'
            elements around blocks of lowercase letters.

        """

        seq = self.sequence[:max_len]
        if max_len and max_len < len(self):
            seq += "..."

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
            description=f"id={self.id};len={len(self)}",
        )

    @classmethod
    def _order_by(cls, order_by: str, ascending: bool) -> tuple:
        match order_by:
            case "length":
                field = func.length(cls.sequence)
            case _:
                field = getattr(cls, order_by)

        fnc = asc if ascending else desc

        return (fnc(field),)
