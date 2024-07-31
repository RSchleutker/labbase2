import json
from typing import Iterable

import numpy as np
from numpy.typing import NDArray

__all__ = ["LCSFinder", "LCSResult"]


class LCSFinder:
    """A class to find matching primers for a target sequence.

    The class is initialized with the target sequence, which can be of any
    length. The instance can then be queried with any other sequence that
    consists only of "ATCG" and is not longer than 255 elements.

    Attributes
    ----------
    seq: NDArray
        The target sequence for which primers shall be found. The sequence is
        stored as a numpy array of dtype 'U1'.
    idx2len: NDArray
        A 2-dimensional array of unsigned 8-bit integers indicating the
        longest substring at each position. Rows correspond to positions in
        the queried sequence and columns correspond to positions in the
        sequence the Seeker class was initialized with. The number of rows is
        always 255, which therefor is the max length for the queried
        sequence. This allows it to use dtype uint8 to reduce the footprint.
    profile: NDArray
        A 1-dimensional array of dtype uint8 the same length as 'seq'. The
        profile indicates the longest substring at each position in 'seq'.
    """

    _bases: NDArray = np.array(["A", "T", "C", "G"], dtype=np.dtype("U1"))

    def __init__(self, seq: str):
        self.seq = np.array(list(seq.upper()), dtype=np.dtype("U1"))
        self.idx2len = np.zeros((255, len(self)), dtype=np.uint8)
        self.profile = np.zeros_like(self.seq, dtype=np.ubyte)
        self._base2idx = self._build_base2idx(self.seq)

    def __len__(self) -> int:
        return len(self.seq)

    def __call__(self, query: str) -> "LCSResult":
        """

        Parameters
        ----------
        query: Iterable
            The query sequence. Should be an iterable that yields single
            characters, e.g. a str or array of characters.

        Returns
        -------
        None
            This method doesn't return anything. It only sets attributes of
            the Seeker class, which allows it to extract relevant information
            afterwards.
        """

        if len(query) > 255:
            raise ValueError(f"Max supported query length is 255!")

        # Clear table from any previous searches.
        self.idx2len[...] = 0

        for i, base in enumerate(query.upper()):
            j = self._base2idx[base]
            self.idx2len[i, j] = self.idx2len[i - 1, j - 1] + 1

        return LCSResult(self.seq, self.idx2len)

    @classmethod
    def _build_base2idx(cls, seq) -> dict:
        """Build a dict of positions for each base in 'seq'.

        The dict is a helper for finding the longest common substring. For
        each of the four bases 'ACTG' the dict contains an NDArray with the
        positions of the base in 'seq'.

        Returns
        -------
        None
        """

        base2idx = {}

        for base in cls._bases:
            (idx,) = (seq == base).nonzero()  # 'nonzero' returns tuples.
            base2idx |= {base: idx}

        return base2idx


class LCSResult:

    def __init__(self, seq: NDArray, idx2len: NDArray):
        self.seq = seq
        self.profile = idx2len.max(axis=0)

        lcs_pos = self.profile.argmax()

        self.length = self.profile[lcs_pos]
        self.start = lcs_pos - self.length + 1
        self.lcs = seq[self.start : (self.start + self.length)]
        self.lcs = "".join(self.lcs)

    def to_jsarray(self) -> str:
        """Convert profile into a javascript array string.

        Returns
        -------
        str
            A string of the form '[1, 2, 3, ...]'.
        """

        return json.dumps(self.profile.tolist())
