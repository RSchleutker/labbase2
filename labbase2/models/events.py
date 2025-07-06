from sqlalchemy import event, func

from labbase2.database import db
from labbase2.models import ColumnMapping, Group, Oligonucleotide, User, file


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

    print("Deleting file.")

    if isinstance(obj, file.BaseFile):
        obj.path.unlink(missing_ok=True)


# TODO: There must be a better option than writing an event for every single child
#  table of BaseEntity.
@event.listens_for(Oligonucleotide, "before_update")
def update_parent(mapper, connection, target) -> None:
    target.timestamp_edited = func.now()


@event.listens_for(ColumnMapping, "before_update")
def update_import_job(mapper, connection, target) -> None:
    target.job.timestamp_edited = func.now()


@event.listens_for(db.session, "before_flush")
def add_default_user_group(session, flush_context, instances):
    """Add the group `user` to every new user automatically

    Every new user is automatically member of the `user` group. This can not be changed.
    In order to avoid errors, the `user` group should not be added to a user
    within views or any other place.

    Parameters
    ----------
    session
    flush_context
    instances

    Returns
    -------
    None
    """

    user_group = db.session.get(Group, "user")

    for obj in session.new:
        if isinstance(obj, User) and user_group not in obj.groups:
            obj.groups.append(user_group)


@event.listens_for(Group, "before_delete")
def protect_standard_groups(mapper, connection, target):
    if target.name in ["admin", "user"]:
        raise ValueError("Groups 'admin' and 'user' cannot be deleted!")


@event.listens_for(User.groups, "remove")
def protect_user_membership(user, group, initiator):
    if group.name == "user":
        raise ValueError("Group 'user' cannot be removed from a user!")
