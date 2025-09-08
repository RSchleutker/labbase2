from datetime import date
from typing import Any, Optional, Type

from sqlalchemy import Dialect
from sqlalchemy.sql.type_api import _T
from sqlalchemy.types import TypeDecorator

from labbase2.database import db


class CustomDate(TypeDecorator):
    """A date type that accepts both date objects and str in ISO format"""

    impl = db.Date

    @property
    def python_type(self) -> Type[Any]:
        return date

    def process_bind_param(self, value: Optional[_T], dialect: Dialect) -> Any:
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except Exception as error:
                raise ValueError(f"Could not parse '{value}' as ISO date (YYYY-MM-DD).") from error

        raise TypeError(f"CustomDate expected date or ISO string, got {type(value).__name__}.")

    def process_literal_param(self, value: Optional[_T], dialect: Dialect) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, str):
            try:
                value = date.fromisoformat(value)
            except Exception as error:
                raise ValueError(
                    f"Could not parse date '{value}' as ISO date (YYYY-MM-DD)."
                ) from error
        if not isinstance(value, date):
            raise TypeError(f"CustomDate literal expects date or str, got {type(value).__name__}.")

        match dialect.name.lower():
            case "sqlite":
                return f"'{value.isoformat()}'"
            case _:
                raise NotImplementedError("CustomDate is only implemented for SQLite dialect!")

    def process_result_value(self, value: Optional[Any], dialect: Dialect) -> Optional[_T]:
        if value is None:
            return None

        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except Exception as error:
                raise ValueError(
                    f"Could not parse result '{value}' as ISO date (YYYY-MM-DD)."
                ) from error

        raise TypeError(f"Unexpected DB value type for CustomDate: {type(value).__name__}.")


class SequenceString(TypeDecorator):
    """A str type that processes DNA/RNA sequences properly"""

    impl = db.String

    @property
    def python_type(self) -> Type[Any]:
        return str

    def process_bind_param(self, value: Optional[_T], dialect: Dialect) -> Any:
        if value is None:
            return None
        if not isinstance(value, str):
            raise TypeError(f"SequenceString expected str, got {type(value).__name__}.")

        # Remove whitespaces and convert to uppercase.
        return self._normalize(value)

    def process_literal_param(self, value: Optional[_T], dialect: Dialect) -> str:
        if value is None:
            return "NULL"
        if not isinstance(value, str):
            raise TypeError(f"SequenceString expected str, got {type(value).__name__}.")

        return f"'{self._normalize(value)}'"

    def process_result_value(self, value: Optional[Any], dialect: Dialect) -> Optional[_T]:
        if value is None:
            return None
        if not isinstance(value, str):
            value = str(value)

        return "".join(value.split()).upper()

    def copy(self, **kw):
        return SequenceString(self.impl.length)

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = "".join(value.split()).upper()

        if not normalized.isalpha():
            raise ValueError(f"SequenceString only accepts letters, got: {repr(value)}")

        return normalized
