import pandas as pd
from sqlalchemy import inspect, select
from sqlalchemy.orm import Mapped
from labbase2.database import db

__all__ = ["Importer"]


class Importer:

    import_attr: tuple = (("id", "ID"),)
    not_updatable: tuple = ("id",)

    def update(self, **kwargs) -> None:
        """Update attributes of an entity.

        Parameters
        ----------
        kwargs
            Attributes to be updated and the new value.

        Returns
        -------
        None

        Notes
        -----
        The changes are not committed automatically to the database, i.e.,
        any changes done via update will not be saved if the calling code
        does not commit these changes on its own.
        """

        for attr, value in kwargs.items():
            if hasattr(self, attr):
                setattr(self, attr, value)

    @classmethod
    def importable_fields(cls) -> list[Mapped]:
        """Get a list of all importable columns

        Returns
        -------
        list[Mapped]
            A list of mapped columns that have been tagged as importable.
        """

        fields = []
        for column in inspect(cls).columns:
            if column.info.get("importable", False):
                fields.append(column.name)
        return fields

    @classmethod
    def from_record(cls, rec: dict, update: bool = False):
        """Create a class instance from a dict

        Parameters
        ----------
        rec: dict
        update: bool

        Returns
        -------
        cls
            An instance of this class
        """

        rec = cls.process_record(rec=rec)

        if update:
            if id_ := rec.pop("id", None):
                entity = db.session.get(cls, id_)
            elif label := rec.pop("label", None):
                entity = db.session.scalar(select(cls).where(cls.label == label))
            else:
                entity = None

            if not entity:
                return None

            for key in rec:
                if key in cls.not_updatable:
                    del rec[key]

            entity.update(**rec)

        else:
            if "id" in rec:
                del rec["id"]

            entity = cls(**rec)

        return entity

    @classmethod
    def process_record(cls, rec: dict) -> dict:
        """Process a row of pd.DataFrame represented as a dict

        Parameters
        ----------
        rec: dict

        Returns
        -------
        dict
            A dict with all entries remove where the value returns `True` for
            `pd.isnull`.
        """

        return {k: v for k, v in rec.items() if not pd.isnull(v)}

    # @classmethod
    # def import_form(cls, columns: list, *args, **kwargs) -> ImportEntity:
    #     data = {'mappings': len(columns) * [[]]}
    #
    #     form = ImportEntity(clss=cls.__name__, data=data, *args, **kwargs)
    #
    #     for column, field in zip(columns, form.mappings):
    #         field.label = column
    #         field.choices += cls.import_attr
    #
    #     return form

    @staticmethod
    def process_formdata(data: dict) -> dict:
        return {k: v for k, v in data.items() if v}
