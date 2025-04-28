import io
from datetime import date

from Bio import SeqIO
from Bio.Restriction import CommOnly
from Bio.SeqRecord import SeqRecord
from flask import Response, send_file

__all__ = ["Sequence"]


class Sequence:
    """A mixin to export sequence entities (primers/plasmids) to FASTA files"""

    def __len__(self):
        return len(self.seqrecord.seq)

    @property
    def seqrecord(self) -> SeqRecord:
        """Generate a Biopython SeqRecord object

        Returns
        -------
        SeqRecord
            The instance of this class represented as a Biopython SeqRecord object.
        """

        raise NotImplementedError

    def restriction_sites(self, sites: int = 1) -> dict["RestrictionType", int]:
        """Return a list of cutting restriction enzymes

        Parameters
        ----------
        sites: int, optional
            The maximum number of sites a given restriction enzymes cuts. Set to 0 to
            get all cutting enzymes.

        Returns
        -------
        dict[RestrictionType, int]
            A list of all restriction enzymes that cut the sequence at most the
            specified times but at least once.
        """

        if record := self.seqrecord:
            enzymes = CommOnly.search(record.seq, linear=False)
            enzymes = {k: len(v) for k, v in enzymes.items() if len(v) <= sites or sites == 0}

            return enzymes

        return {}

    def formatted_restriction_sites(self) -> str:
        """Return restriction sites with HTML markup.

        Returns
        -------
        str
            A single string that can be inserted into a website as it is. It
            highlights the number of cutting sites.
        """

        sites = list(self.restriction_sites().items())
        sites.sort(key=lambda x: (x[1], x[0]))

        return ", ".join([f"<b>{e}</b> ({n})" for e, n in sites])

    @classmethod
    def to_fasta(cls, instances: list) -> Response:
        """Export instances to a file with multiple FASTA entries

        Parameters
        ----------
        instances: list
            A list of instances to export to a single FASTA file.

        Returns
        -------
        Response
            A file for download.
        """

        with io.StringIO() as proxy:
            SeqIO.write([i.seqrecord for i in instances], proxy, "fasta")
            mem = io.BytesIO(proxy.getvalue().encode("utf-8"))

        filename = cls.__name__ + "_" + date.today().isoformat() + ".fasta"

        return send_file(mem, as_attachment=True, download_name=filename, mimetype="text/fasta")
