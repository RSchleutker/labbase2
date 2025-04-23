from labbase2.models import db
from labbase2.models.consumable import Consumable
from labbase2.models.mixins.filter import Filter
from sqlalchemy import asc, desc, func, ForeignKey, Date, String
from sqlalchemy.orm import subqueryload, mapped_column, Mapped, relationship

from datetime import date


__all__ = ["Chemical", "StockSolution"]


class Chemical(Consumable):
    """A class to represent a chemical compound.

    Currently, a Chemical has only very few attributes, i.e., two: The CAS
    number and the PubChem CID. The CID is used to retrieve further
    informations from the web. The CAS number is sued for 'official' reference.

    Attributes
    ----------
    id : int
        The internal ID of this chemical. This is unique among all entities
        in the database.
    responsible_id : int
        ID of the user who is responsible for this chemical.
    cas_number : str
        The CAS registry number, a mandatory number for all chemical compounds.
    pubchem_cid : int
        The PubChem reference number. This will be used to retrieve
        additional informations about this compound from PubChem.

    Notes
    -----
    Currently, the Chemical class uses the PubChem CID to retrieve
    information like the molecular weight from the PubChem REST API. This
    causes problems at the moment. These problems might be caused of people
    requesting too much information in too little time followed by banning the IP
    by PubChem. Therefor, it is likely that the implementation will change in
    the future such that people have to add specific information about the
    chemical themselves.
    """

    __tablename__: str = "chemical"

    id: Mapped[int] = mapped_column(db.ForeignKey("consumable.id"), primary_key=True, info={"importable": False})
    molecular_weight: Mapped[float] = mapped_column(nullable=True, info={"importable": True})

    # One-to-many relationships.
    stocks: Mapped[list["StockSolution"]] = relationship(
        backref="chemical", lazy=True, order_by="StockSolution.date_emptied, StockSolution.date_created.desc()"
    )

    __mapper_args__ = {"polymorphic_identity": "chemical"}

    @classmethod
    def _options(cls) -> tuple:
        return subqueryload(cls.stocks), subqueryload(cls.batches)


class StockSolution(db.Model, Filter):
    """

    Attributes
    ----------
    id : int
        An id that identifies the stock solution.
    label : str
        The label, that is the token, of the stock solution. Can be something
        like 'Tris/HCl pH 9.5'.
    details : str
        A mored detailed description of the stock solution.

    Notes
    -----
    Stocks are used to model stock solutions. Each stock solution can contain
    several chemicals. Therefor, this is modeled as a many-to-many
    relationship.
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    chemical_id: Mapped[int] = mapped_column(ForeignKey("chemical.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    solvent: Mapped[str] = mapped_column(String(64), nullable=False)
    date_created: Mapped[date] = mapped_column(Date, nullable=False, default=func.today())
    date_emptied: Mapped[date] = mapped_column(Date, nullable=True)
    concentration: Mapped[str] = mapped_column(String(32), nullable=False)
    storage_place: Mapped[str] = mapped_column(String(64), nullable=False)
    details: Mapped[str] = mapped_column(String(2048), nullable=True)

    @classmethod
    def _filters(cls, **fields) -> list:
        if lbl := fields.pop("label", None):
            f = super()._filters(**fields) + [Chemical.label.ilike(f"%{lbl}%")]
        else:
            f = super()._filters(**fields)

        return f

    @classmethod
    def _order_by(cls, order_by: str, ascending: bool) -> tuple:
        fnc = asc if ascending else desc
        if order_by == "label":
            field = Chemical.label
        else:
            field = getattr(cls, order_by.strip())

        return (fnc(field),)

    @classmethod
    def _entities(cls) -> tuple:
        return cls, Chemical

    @classmethod
    def _joins(cls) -> tuple:
        return ((Chemical, cls.chemical_id == Chemical.id),)
