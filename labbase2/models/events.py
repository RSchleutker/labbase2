from sqlalchemy import event
from sqlalchemy import func
from labbase2.models import db
from labbase2.models import file
from labbase2.models import Oligonucleotide
from labbase2.models import ColumnMapping


@event.listens_for(db.session, "deleted_to_detached")
def intercept_deleted_to_detached(session, obj) -> None:
    """Removes the physical file when a File row marked as deleted is
    eventually removed from the database.

    Parameters
    ----------
    session
        The current session.
    obj
        The object that is detached. This can be any Database related object
        but so far this function has only implications for 'File'.


    Returns
    -------
    None
    """

    if isinstance(obj, file.File):
        obj.path.unlink(missing_ok=True)


# TODO: There must be a better option than writing an event for every single child table of
#  BaseEntity.
@event.listens_for(Oligonucleotide, "before_update")
def update_parent(mapper, connection, target) -> None:
    target.timestamp_edited = func.now()


@event.listens_for(ColumnMapping, "before_update")
def update_import_job(mapper, connection, target) -> None:
    target.job.timestamp_edited = func.now()
