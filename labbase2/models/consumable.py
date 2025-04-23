from datetime import date

from labbase2.models import db
from labbase2.models.base_entity import BaseEntity
from labbase2.models.mixins.export import Export
from labbase2.models.mixins.filter import Filter
from sqlalchemy import asc, desc, not_, ForeignKey, String, DateTime, Date
from sqlalchemy.orm import column_property, mapped_column, Mapped, relationship

__all__ = ["Batch", "Consumable"]


class Batch(db.Model, Filter, Export):
    """A batch is an order of a consumable.

    Attributes
    ----------
    id : int
        The internal database identifier of this batch.
    consumable_id : int
        The identifier of the consumable to which this batch belongs.
    supplier : str
        The company (or whatever) where this batch was ordered (again, the same
        chemical might be ordered at different companies due to discounts,
        for instance).
    article_number : str
        The article number of the ordered consumable. This serves as a unambiguous
        identifier of the ordered chemical. This is important for different quality
        grades of the same chemical, for instance.
    amount : str
        The amoint that was ordered. For some companies this is already indicated by
        the article number but for some is not. The information is straightforward
        for chemicals. For enzymes this might be the number of reactions or the total
        activity in U. For antibodies the total volume along with the concentration
        would suffice.
    date_ordered : date
        The date at which this batch was ordered.
    date_opened : date
        The date at which this batch was opened.
    date_expiration : date
        The expiration date that was set by the supplier.
    date_emptied : date
        The date at which this batch was emptied.
    price : float
        The price in euros.
    storage_place : str
        The location where this batch can be found. This should be clear and
        unambiguous.
    lot : str
        The lot number of this batch.
    in_use : bool
        A flag indicating if this batch is currently in use. At best, only ever one
        batch for each consumable is in use at a time.
    is_open : bool
        A flag indicating if this batch was opened already.
    is_empty : bool
        A flag indicating if this batch is empty.

    Notes
    -----
    While a consumable is just a description a batch is the actual thing available in
    the lab. For instance, an entry for the chemical 'SDS' only gives general
    informations about the chemical and that it is or was available in the lab at
    some point in time. However, a batch is the actual order of that consumable
    along with additional informations that might be of interest like article number
    and source (the same chemical might be bought from different manufacturers).
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    consumable_id: Mapped[int] = mapped_column(ForeignKey("consumable.id"), nullable=False)
    supplier: Mapped[str] = mapped_column(String(64), nullable=False)
    article_number: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[str] = mapped_column(String(32), nullable=True)
    date_ordered: Mapped[date] = mapped_column(Date, nullable=True)
    date_opened: Mapped[date] = mapped_column(Date, nullable=True)
    date_expiration: Mapped[date] = mapped_column(Date, nullable=True)
    date_emptied: Mapped[date] = mapped_column(Date, nullable=True)
    price: Mapped[float] = mapped_column(nullable=True)
    storage_place: Mapped[str] = mapped_column(String(64), nullable=False)
    lot: Mapped[str] = mapped_column(String(64), nullable=False)
    in_use: Mapped[bool] = mapped_column(nullable=False, default=False)

    is_open: Mapped[bool] = column_property(date_opened.isnot(None).label("is_open"), deferred=True)
    is_empty: Mapped[bool] = column_property(date_emptied.isnot(None).label("is_empty"), deferred=True)

    @classmethod
    def _filters(cls, **fields) -> list:
        filters = []

        if type_ := fields.pop("consumable_type", None):
            filters.append(Consumable.entity_type.is_(type_))
        if label := fields.pop("label", None):
            filters.append(Consumable.label.ilike(f"%{label}%"))

        if (empty := fields.pop("empty", "all")) == "empty":
            filters.append(cls.is_empty)
        elif empty != "all":
            filters.append(not_(cls.is_empty))

        if (in_use := fields.pop("in_use", "all")) == "in_use":
            filters.append(cls.in_use)
        elif in_use != "all":
            filters.append(not_(cls.in_use))

        return super()._filters(**fields) + filters

    @classmethod
    def _order_by(cls, order_by: str, ascending: bool) -> tuple:
        match order_by.strip():
            case "id":
                field = cls.id
            case "label":
                field = Consumable.label
            case "consumable_type":
                field = Consumable.entity_type
            case "supplier":
                field = cls.supplier
            case "date_ordered":
                field = cls.date_ordered
            case _:
                raise ValueError("Unknown order field!")

        fnc = asc if ascending else desc

        return (fnc(field),)

    @classmethod
    def _entities(cls) -> tuple:
        return cls, Consumable.entity_type, Consumable.label

    @classmethod
    def _joins(cls) -> tuple:
        return (Consumable,)


class Consumable(BaseEntity, Export):
    """A consumable is a general class for all kind of stuff in the lab that can be
    used up.

    The thing about consumables is that they can have batches attached to them.
    Please note that a consumable is just a description of the respective enzyme,
    chemical, etc. It does give no information about availability in the lab. For this
    information one has to consult the batches.

    Attributes
    ----------
    id : int
        The internal identifier of the consumable.
    storage_info : str
        A short description how this consumable should be stored.
    batches : list[Batch]
        A list of all batches of this consumable that were ordered.
    """

    id: Mapped[int] = mapped_column(db.ForeignKey("base_entity.id"), primary_key=True, info={"importable": False})
    storage_info: Mapped[str] = mapped_column(String(64), nullable=True, info={"importable": True})

    # One-to-many relationships.
    batches: Mapped[list["Batch"]] = relationship(
        backref="consumable", lazy=True, order_by="Batch.date_emptied, Batch.in_use.desc(), Batch.date_ordered"
    )

    # Proper setup for joined table inheritance.
    __mapper_args__ = {"polymorphic_identity": "consumable"}

    def to_dict(self) -> dict:
        return super().to_dict() | {"batches": [b.to_dict() for b in self.batches]}

    @property
    def location(self):
        if self.batches:
            return self.batches[0].storage_place
        else:
            return None

    @classmethod
    def _subquery(cls):
        return db.session.query(Batch.consumable_id, Batch.storage_place).filter(Batch.in_use).subquery(name="batch")
