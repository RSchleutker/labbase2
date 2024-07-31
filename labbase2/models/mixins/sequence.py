import io
from datetime import date

from Bio import SeqIO
from Bio.Restriction import CommOnly
from flask import send_file

__all__ = ["Sequence"]


class Sequence:
    """
    A mixin to export sequence entities (primers/plasmids) to FASTA files.
    """

    def __len__(self):
        return len(self.seqrecord.seq)

    @property
    def seqrecord(self):
        raise NotImplementedError

    def restriction_sites(self) -> dict:
        if record := self.seqrecord:
            sites = CommOnly.search(record.seq, linear=False)
            sites = {k: v for k, v in sites.items() if len(v) == 1}
            sites = [k for k in sites]
            sites.sort(key=lambda x: x.__name__)

            return sites
        else:
            return {}

    def formatted_restriction_sites(self) -> str:
        """Return restriction sites with HTML markup.

        Returns
        -------
        str
            A single string that can be inserted into a website as it is. It
            highlights the number of cutting sites in bold.
        """

        sites = [(e, n) for e, n in self.restriction_sites().items()]
        sites.sort(key=lambda x: (x[1], x[0]))

        return ", ".join(["{} <b>({})</b>".format(e, n) for e, n in sites])

    @classmethod
    def to_fasta(cls, instances):
        with io.StringIO() as proxy:
            SeqIO.write([i.seqrecord for i in instances], proxy, "fasta")
            mem = io.BytesIO(proxy.getvalue().encode("utf-8"))

        filename = cls.__name__ + "_" + date.today().isoformat() + ".fasta"

        return send_file(
            mem, as_attachment=True, download_name=filename, mimetype="text/fasta"
        )
