from labbase2.models import db
from sqlalchemy import func

__all__ = ["ImportJob", "ColumnMapping"]


class ImportJob(db.Model):

    __tablename__ = "import_job"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=func.now())
    timestamp_edited = db.Column(db.DateTime, default=func.now())
    file_id = db.Column(db.Text, db.ForeignKey("base_file.id"), nullable=False)
    is_finished = db.Column(db.Boolean, default=False, nullable=False)
    entity_type = db.Column(db.Text, nullable=False)

    # One-to-many relationships.
    mappings = db.relationship(
        "ColumnMapping", backref="job", cascade="all, delete-orphan", lazy=True
    )

    file = db.relationship(
        "BaseFile",
        backref="import_job",
        lazy=True,
        cascade="all, delete",
        single_parent=True,
    )

    def get_file(self):
        pass


class ColumnMapping(db.Model):

    __tablename__ = "column_mapping"

    job_id = db.Column(db.Integer, db.ForeignKey("import_job.id"), primary_key=True)
    mapped_field = db.Column(db.String, primary_key=True)
    input_column = db.Column(db.String)
