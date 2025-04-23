from datetime import datetime

from labbase2.models import db
from sqlalchemy import func, ForeignKey, DateTime, String
from sqlalchemy.orm import mapped_column, Mapped, relationship

__all__ = ["ImportJob", "ColumnMapping"]


class ImportJob(db.Model):

    __tablename__ = "import_job"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    timestamp_edited: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=func.now())
    file_id: Mapped[int] = mapped_column(ForeignKey("base_file.id"), nullable=False)
    is_finished: Mapped[bool] = mapped_column(default=False, nullable=False)
    entity_type: Mapped[str] = mapped_column(nullable=False)

    # One-to-many relationships.
    mappings: Mapped[list["ColumnMapping"]] = relationship(backref="job", cascade="all, delete-orphan", lazy=True)
    file: Mapped[list["BaseFile"]] = relationship(
        backref="import_job", lazy=True, cascade="all, delete", single_parent=True
    )

    def get_file(self):
        pass


class ColumnMapping(db.Model):

    __tablename__ = "column_mapping"

    job_id: Mapped[int] = mapped_column(ForeignKey("import_job.id"), primary_key=True)
    mapped_field: Mapped[str] = mapped_column(primary_key=True)
    input_column: Mapped[str] = mapped_column(nullable=True)
