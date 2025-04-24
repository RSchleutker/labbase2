import io
from datetime import date

from flask import send_file
from pandas import DataFrame
from sqlalchemy import inspect
from labbase2.models import db

__all__ = ["Export"]


class Export:
    """A mixin for exporting instances to CSV, JSON, ...."""

    def to_dict(self) -> dict:
        """Create a dictionary from the object.

        Returns
        -------
        dict
            A dictionary. The keys are exactly labeled like the attributes of
            the instance.
        """

        inst = inspect(self).mapper.column_attrs
        return {c.key: getattr(self, c.key) for c in inst}

    @classmethod
    def to_df(cls, instances) -> DataFrame:
        instances = db.session.scalars(instances)
        return DataFrame(i.to_dict() for i in instances)

    @classmethod
    def _filename(cls) -> str:
        return cls.__name__ + "_" + date.today().isoformat()

    @classmethod
    def export_to_csv(cls, instances):
        with io.StringIO() as proxy:
            cls.to_df(instances).to_csv(proxy)
            mem = io.BytesIO(proxy.getvalue().encode("utf-8"))

        return send_file(
            mem,
            as_attachment=True,
            download_name=cls._filename() + ".csv",
            mimetype="text/csv",
        )

    @classmethod
    def export_to_json(cls, instances):
        with io.StringIO() as proxy:
            cls.to_df(instances).to_json(proxy, orient="records", date_format="iso", indent=2)
            mem = io.BytesIO(proxy.getvalue().encode("utf-8"))

        return send_file(
            mem,
            as_attachment=True,
            download_name=cls._filename() + ".json",
            mimetype="text/json",
        )

    @classmethod
    def to_pdf(cls, instances):
        mem = io.BytesIO()
        mem.seek(0)

        return send_file(
            mem,
            as_attachment=True,
            download_name=cls._filename() + ".pdf",
            mimetype="application/pdf",
        )
