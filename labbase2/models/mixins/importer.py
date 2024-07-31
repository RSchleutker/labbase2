import pandas as pd
from sqlalchemy import inspect

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
    def importable_fields(cls) -> list:
        fields = []
        for column in inspect(cls).columns:
            if column.info.get("importable", False):
                fields.append(column.name)
        return fields

    @classmethod
    def from_record(cls, rec: dict, update: bool = False):

        rec = cls.process_record(rec=rec)

        if update:
            if id_ := rec.pop("id", None):
                entity = cls.query.get(id_)
            elif label := rec.pop("label", None):
                entity = cls.query.filter(cls.label == label).first()
            else:
                entity = None

            if not entity:
                return

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
