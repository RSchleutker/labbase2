from labbase2.models import db
from sqlalchemy import asc, desc, select

__all__ = ["Filter"]


class Filter:
    """A mixin to add basic filter functionality to a model.

    Notes
    -----
    The mixin is inspired by the template design pattern. The basics method to be
    used is `filter_`. `filter_` uses additional methods to customize the filtering
    process like `_filters` to add filters or `_order_by` to sort the results. The
    mixin provides basic implementations for this. Each model class inheriting from
    this mixin can override one or several of these methods to customize the filter
    process.
    """

    @classmethod
    def filter_(cls, order_by: str, ascending: bool = True, **fields):
        """Create a query object to retrieve matching rows from the database.

        Parameters
        ----------
        order_by : str
            The column name, by which the result shall be ordered.
        ascending : bool
            Order results either ascending or descending. Defaults to `True` (
            ascending).
        fields : **dict
            A list of key-value pairs. The key is a field in the database and the
            value is some constraint which should be applied to this field. See
            `_filters` for details.

        Returns
        -------
        query
            An SQLAlchemy query object. Can be either further customized by adding
            additional query parameters or be used to retrieve matching instances
            from the database.
        """

        # query = db.session.query(*cls._entities())
        query = select(*cls._entities())

        for join in cls._joins():
            if isinstance(join, tuple):
                query = query.join(*join, isouter=True)
            else:
                query = query.join(join, isouter=True)

        return (
            query.options(*cls._options()).where(*cls._filters(**fields)).order_by(*cls._order_by(order_by, ascending))
        )

    @classmethod
    def _filters(cls, **fields) -> list:
        filters = []

        poly_on = cls.__mapper__.polymorphic_on
        if poly_on is not None:
            filters.append(poly_on.is_(cls.__mapper__.polymorphic_identity))

        for field, value in fields.items():
            attr = getattr(cls, field, None)
            if not attr or not value:
                continue

            if value == "none":
                filters.append(attr.is_(None))
            elif value == "any":
                filters.append(attr.isnot(None))
            elif value == "all" or value == 0:
                continue
            # TODO: Improve full-text search (FTS5?)
            elif field == "description":
                value = [f"%{v.strip()}%" for v in value.split()]
                filters += [attr.ilike(v) for v in value]
            elif isinstance(value, int) or field == "entity_type":
                filters.append(attr.is_(value))
            elif isinstance(value, str):
                filters.append(attr.ilike(f"%{value}%"))

        return filters

    @classmethod
    def _order_by(cls, order_by: str, ascending: bool) -> tuple:
        fnc = asc if ascending else desc
        field = getattr(cls, order_by.strip(), cls.id)

        return (fnc(field),)

    @classmethod
    def _options(cls) -> tuple:
        return ()

    @classmethod
    def _entities(cls) -> tuple:
        return (cls,)

    @classmethod
    def _joins(cls) -> tuple:
        return ()

    @classmethod
    def _subquery(cls):
        return None
