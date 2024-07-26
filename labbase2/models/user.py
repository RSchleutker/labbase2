from labbase2.models import db
from labbase2.models.mixins import Export

from flask_login import UserMixin
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from email_validator import validate_email
from email_validator import EmailNotValidError
from sqlalchemy import func

from typing import Optional


__all__ = ["login_manager", "User", "UserRole", "user_roles", "ResetPassword"]


login_manager = LoginManager()
login_manager.login_view = "auth.login"

# Map users to their roles in a many-to-many relationship.
user_roles = db.Table(
    "user_roles",
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("user.id"),
        primary_key=True
    ),
    db.Column(
        "role_id",
        db.Integer,
        db.ForeignKey("user_role.id"),
        primary_key=True
    )
)


class User(db.Model, UserMixin, Export):
    """A person (user) that should have access to the database.

    Attributes
    ----------
    id : int
        An internal identifier of the person.
    username : str
        The person's username.
    email : str
        The email address.
    password_hash : str
        This is a hash of the password set by the user. This attribute is not set manually. Instead, the clear password
        is passed to the 'set_password' method.
    roles : list[UserRole]
        Roles of this user. The set of roles determines hat a user can see and do in the application.
    comments : list[Comment]
        A list of all comments that were created by this person.
    imported : list[BaseEntity]
        A list of all the entities that were imported by the person.
    plasmids : list[Plasmid]
        A list of all plasmids owned by this user.
    glycerol_stocks : list[GlycerolStock]
        A list of all glycerol stocks owned by this user.
    oligonucleotides : list[Oligonucleotide]
        A list of all oligonucleotides owned by this user. NOTE: This was previously called 'primers' but
        oligonucleotide is more accurate.
    preparations : list[Preparation]
        All plasmid preparations done by this user. This can be different then the owner of the plasmid to which the
        preparation belongs.
    dilutions : list[Dilution]
        A list of antibody dilutions determined by this person.
    files : list[File]
        All files uploaded by this person.
    fly_stocks : list[FlyStock]
        A list of all fly stocks owned by this user.
    modifications : list[Modification]
        All modifications of fly stocks done by this user. This can be different from the owner of the fly stock.
    responsibilities : list[Chemical]
        All chemicals for which this user is responsible.
    stock_solutions : list[StockSolution]
        All stock solutions prepared by this user.
    resets : list[ResetPassword]
        A list of reset requests for the password made by this person. The database scheme theoretically allows to have
        several such resets active for one user but the application should make sure to delete any previous request for
        a new password once another request is started.


    Notes
    -----
    A person is ultimately identified by its id, which is used internally for everything. However, for convenience
    a user can login to the app using his/her email address. Therefore, the email address has to be unique among all
    users. The same applies to the username.

    Users inherit from the UserMixin class of the flask_login module. The roles system is self-implemented in the
    app.utils module via a simple decorator.
    """

    __tablename__: str = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    picture_id = db.Column(db.Integer, db.ForeignKey("file.id"), nullable=True)
    timestamp_created = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    timezone = db.Column(db.String(64), nullable=False, default="UTC")
    status = db.Column(db.String(32), nullable=False, default="active")

    # One-to-many relationships.
    comments = db.relationship("Comment", backref="user", lazy=True)
    plasmids = db.relationship("Plasmid", backref="owner", lazy=True, foreign_keys="Plasmid.owner_id")
    glycerol_stocks = db.relationship("GlycerolStock", backref="owner", lazy=True)
    oligonucleotides = db.relationship(
        "Oligonucleotide",
        backref="owner",
        lazy=True,
        foreign_keys="Oligonucleotide.owner_id"
    )
    preparations = db.relationship("Preparation", backref="owner", lazy=True)
    dilutions = db.relationship("Dilution", backref="user", lazy=True)
    files = db.relationship("File", backref="user", lazy=True)
    modifications = db.relationship("Modification", backref="user", lazy=True)
    fly_stocks = db.relationship("FlyStock", backref="owner", lazy=True, foreign_keys="FlyStock.owner_id")
    responsibilities = db.relationship(
        "Chemical",
        backref="responsible",
        lazy=True,
        foreign_keys="Chemical.responsible_id"
    )
    stock_solutions = db.relationship(
        "StockSolution",
        backref="owner",
        lazy=True
    )
    import_jobs = db.relationship(
        "ImportJob",
        backref="user",
        lazy=True,
        order_by="ImportJob.timestamp.asc()"
    )
    resets = db.relationship(
        "ResetPassword",
        backref="user",
        lazy=True
    )

    # Many-to-many relationships.
    roles = db.relationship(
        "UserRole",
        secondary=user_roles,
        lazy="subquery",
        backref=db.backref("users", lazy=True)
    )

    def set_password(self, password: str) -> None:
        """Creates a hash that is stored in the database to validate the user's password.

        Parameters
        ----------
        password : str
            A string from which the hash shall be created.

        Returns
        -------
        None

        Notes
        -----
        Of course, passwords are not stored as clear text in the database. Instead, a hash is generated from the
        password the user enters and that hash is stored. It is not possible to reconstruct the original password but
        the same hash is generated from the same password. Thus, the hash can be used to verify users.

        Currently, this method accepts all strings. In the future users will maybe be forced to add passwords that
        comply with certain restrictions to ensure a certain level of security.
        """

        self.password_hash = generate_password_hash(password)

    def verify_password(self, password: str) -> bool:
        """Creates the hash from the 'password' parameter and checks this
        hash against the hash deployed in the database.

        Parameters
        ----------
        password : str
            The password to be checked.

        Returns
        -------
        bool
            Returns True if the hash is the same as in the database and False
            otherwise.

        """

        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_by_name_or_email(cls, name_email: str) -> Optional['User']:
        """Load a user from username or email address.

        Parameters
        ----------
        name_email : str
            Either the username or the email address of a user.

        Returns
        -------
        User | None
            A user if either a valid existing email address or an existing
            username is provided or `None` otherwise.

        Notes
        -----
        The email address is always checked first. So in the case the username of
        one user is identical to the email address of another user (which should
        never happen) the user with the email address is returned.
        """

        try:
            email = validate_email(name_email).email
        except EmailNotValidError:
            user = cls.query.filter(cls.username.ilike(name_email)).first()
        else:
            user = User.query.filter(User.email.ilike(email)).first()

        return user


class UserRole(db.Model, Export):
    """Roles a user could possibly have.

    Attributes
    ----------
    id : int
        The database ID of the role.
    name : str
        A descriptive name of the role.

    Notes
    -----
    On the database levels roles don't have any meaning. They are just names. Meaning is conferred by the application.
    """

    __tablename__: str = "user_role"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)


class ResetPassword(db.Model):
    """Requests to reset the password of a user.

    id : int
        The database ID of the request.
    user_id : int
        Database ID of the user for which the password should be reset.
    key : str
        A long random key used to log in a user once.
    timeout : datetime
        The datetime at which this requests becomes invalid. The user then can no longer use the key to log in and has
        to start a new request.
    """

    __tablename__: str = "reset_password"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        unique=True
    )
    key = db.Column(db.String(64), nullable=False)
    timeout = db.Column(db.DateTime, nullable=False)


@login_manager.user_loader
def _load_user(id_: str) -> User | None:
    """Load a user from database by ID.

    Parameters
    ----------
    id_ : str
        The internal database ID of the user. The database ID of a user is an
        integer. However, the user ID for the session is stored in unicode.
        So the value has to be converted to integer before.

    Returns
    -------
    User | None
        Either the user if a valid existing ID was provided or `None` otherwise.
    """

    try:
        id_ = int(id_)
    except ValueError:
        print("Invalid ID provided: {}".format(id))
        return None
    else:
        return User.query.get(id_)
