__all__ = ["strip_input", "make_lower", "make_upper", "upper_seq_input"]


def strip_input(x: str) -> str:
    """A simple wrapper for the strip-method of strings apllicable for use as a filter for form fields.

    Parameters
    ----------
    x : str
    A string that is to be stripped.

    Returns
    -------
    str
        The original string 'x' but stripped at both ends.
    """

    if not isinstance(x, str):
        raise ValueError('x has to be a string!')

    return x.strip()


def make_lower(x: str) -> str:
    """A simple wrapper for the lower-method of strings apllicable for use as a
    filter for form fields.

    Parameters
    ----------
    x : str
        A string that is to be converted to lowercase.

    Returns
    -------
    str
        The original string 'x' but with all characters being replaced by
        their lowercase equivalents.
    """

    if not isinstance(x, str):
        raise ValueError('x has to be a string!')

    return x.lower()


def make_upper(x: str) -> str:
    """A simple wrapper for the upper-method of strings for use as a filter
    for form fields.

    Parameters
    ----------
    x : str
        A string that is to be converted to uppercase.

    Returns
    -------
    str
        The original string 'x' but with all characters being replace by
        their uppercase equivalents.
    """

    if not isinstance(x, str):
        raise ValueError("Must be a string: x")

    return x.upper()


def upper_seq_input(x: str) -> str:
    """A simple wrapper for the lower-method of strings apllicable for use as a
    filter for form fields.

    Parameters
    ----------
    x : str
    A string that is to be converted to lowercase.

    Returns
    -------
    str
        The original string 'x' but with all characters beeing replaced by
        their uppercase equivalents but only when ALL characters were
        lowercase.
    """

    if not isinstance(x, str):
        raise ValueError("Must be a string: x")

    return x.upper() if x.islower() else x
