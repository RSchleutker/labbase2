from datetime import datetime
from typing import Type

from sqlalchemy import DateTime, ForeignKey, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from labbase2 import models
from labbase2.database import db
from labbase2.models import BaseEntity

__all__ = ["ImportJob", "ColumnMapping"]


class ImportJob(db.Model):
    """A class to hold information for importing a file

    Attributes
    ----------
    id: int
    user_id: int
    timestamp: datetime
    timestamp_edited: datetime
    file_id: int
    is_finished: bool
    entity_type: str
    mappings: list[ColumnMapping]
    file: BaseFile
    """

    __tablename__ = "import_job"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now(),  # pylint: disable=not-callable
    )
    timestamp_edited: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        default=func.now(),  # pylint: disable=not-callable
    )
    file_id: Mapped[int] = mapped_column(ForeignKey("base_file.id"), nullable=False)
    is_finished: Mapped[bool] = mapped_column(default=False, nullable=False)
    entity_type: Mapped[str] = mapped_column(nullable=False)

    # One-to-many relationships.
    mappings: Mapped[list["ColumnMapping"]] = relationship(
        backref="job", cascade="all, delete-orphan", lazy=True
    )
    file: Mapped["BaseFile"] = relationship(
        backref="import_job", lazy=True, cascade="all, delete", single_parent=True
    )

    def get_mapping(self) -> tuple[list[str], list[str]]:
        """Get current mapping between database and uploaded file

        Returns
        -------
        tuple[list[str], list[str]]
            A tuple with two lists. The first list contains the names of the fields in the database.
            The second list containes the names of the corresponding columns in the file, from which
            entries shall be imported.
        """

        mappings = db.session.execute(
            select(ColumnMapping.mapped_field, ColumnMapping.input_column).where(
                ColumnMapping.job_id.is_(self.id), ColumnMapping.input_column.isnot(None)
            )
        ).all()

        fields, columns = zip(*mappings)

        return list(fields), list(columns)

    @property
    def class_(self) -> Type[BaseEntity]:
        """Get the model class for which entities shall be imported

        Returns
        -------
        Type[BaseEntity]
        """

        return self.get_entity_class(self.entity_type)

    @classmethod
    def get_entity_class(cls, type_: str) -> Type[BaseEntity]:
        """Get a model class by name

        Parameters
        ----------
        type_: str
            The name of class as a string. Currently supported are 'antibody', 'chemical',
            'fly_stock', 'oligonucleotide', and 'plasmid'. This is not case-sensitive.

        Returns
        -------
        Type[db.Model]
            The corresponding class.

        Raises
        ------
        ValueError
            If `type_` is none of the supported names.
        """

        match type_.lower():
            case "antibody":
                return models.Antibody
            case "chemical":
                return models.Chemical
            case "fly_stock":
                return models.FlyStock
            case "oligonucleotide":
                return models.Oligonucleotide
            case "plasmid":
                return models.Plasmid
            case _:
                raise ValueError(f"Unknown entity type {type_}!", "danger")


class ColumnMapping(db.Model):
    """A class to represent the mapping between a file and database columns

    Attributes
    job_id: int
    mapped_field: str
        The name of the column in the database.
    input_column: str
        The name of the column in the import file.
    """

    __tablename__ = "column_mapping"

    job_id: Mapped[int] = mapped_column(ForeignKey("import_job.id"), primary_key=True)
    mapped_field: Mapped[str] = mapped_column(primary_key=True)
    input_column: Mapped[str] = mapped_column(nullable=True)
