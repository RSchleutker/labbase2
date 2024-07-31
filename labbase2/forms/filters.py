from typing import Optional


__all__ = ["remove_whitespaces", "strip_input", "make_lower", "make_upper"]


def remove_whitespaces(x: Optional[str]) -> Optional[str]:
    """Remove whitespaces from a string

    Parameters
    ----------
    x : Optional[str], optional
        A string from which all whitespaces shall be removed or `None`. Defaults to
        `None`.

    Returns
    -------
    Optional[str]
        The original string `x` but with whitespaces removed or `None` if `x` was
        `None`.
    """

    if x is None:
        return None

    if not isinstance(x, str):
        raise ValueError("`x` has to be a string!")

    return "".join(x.split())


def strip_input(x: Optional[str] = None) -> Optional[str]:
    """A simple wrapper for the strip-method of strings applicable for use as a
    filter for form fields.

    Parameters
    ----------
    x : Optional[str], optional
        A string that is to be stripped or `None`. Defaults to `None`.

    Returns
    -------
    Optional[str]
        The original string `x` but stripped at both ends or `None` if `x` was `None`.
    """

    if x is None:
        return

    if not isinstance(x, str):
        raise ValueError("`x` has to be a string!")

    return x.strip()


def make_lower(x: Optional[str] = None) -> Optional[str]:
    """A simple wrapper for the lower-method of strings applicable for use as a
    filter for form fields.

    Parameters
    ----------
    x : Optional[str], optional
        A string that is to be stripped or `None`. Defaults to `None`.

    Returns
    -------
    Optional[str]
        The original string 'x' but with all characters being replaced by their
        lowercase equivalents or `None` if `x` was `None`.
    """

    if x is None:
        return None

    if not isinstance(x, str):
        raise ValueError("`x` has to be a string!")

    return x.lower()


def make_upper(x: Optional[str] = None) -> Optional[str]:
    """A simple wrapper for the upper-method of strings for use as a filter
    for form fields.

    Parameters
    ----------
    x : Optional[str], optional
        A string that is to be converted to uppercase or `None`. Defaults to `None`.

    Returns
    -------
    Optional[str]
        The original string 'x' but with all characters being replaced by their
        uppercase equivalents or `None` if `x` was `None`.
    """

    if x is None:
        return None

    if not isinstance(x, str):
        raise ValueError("`x` has to be a string!")

    return x.upper()
