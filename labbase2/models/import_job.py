from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from labbase2.database import db

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

    def get_file(self):
        pass


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
