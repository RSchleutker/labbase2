from datetime import date

from sqlalchemy.types import TypeDecorator

from labbase2.models import db


class CustomDate(TypeDecorator):

    impl = db.Date

    def process_bind_param(self, value, dialect):
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except:
                raise ValueError(f"Could not parse date {value}!")

        return value


class SequenceString(TypeDecorator):

    impl = db.String

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        value = value.upper()

        # Remove any whitespace characters from the sequence.
        return "".join(value.split())

    def copy(self, **kw):
        return SequenceString(self.impl.length)
