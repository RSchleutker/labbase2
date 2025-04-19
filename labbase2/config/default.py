__all__ = ["DefaultConfig"]


class DefaultConfig(object):
    SECRET_KEY: str ="verysecretkey"

    # Database.
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///labbase2.db"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Display.
    DELETABLE_HOURS: int = 72
    PER_PAGE: int = 100

    # User.
    USER: tuple = "Max", "Mustermann", "test@test.de"
    DEFAULT_TIMEZONE: str = "Europe/Berlin"
    UPLOAD_FOLDER: str = "upload"
    RESET_EXPIRES: int = 1
    PERMISSIONS: list[tuple[str, str]] = [
        (
            "Write comment",
            """Allows a user to author own comments. Applies to all entity types that 
            support comments. Suggested level: Intern.""",
        ),
        (
            "Upload files",
            """"Allows a user to upload files. Applies to all entity types that support 
            files. Suggested level: Master student.""",
        ),
        (
            "Add dilutions",
            """Allows a user to add dilutions to antibodies. Suggested level: Bachelor 
            student.""",
        ),
        (
            "Add preparations",
            """Allows a user to add plasmid preparations. Suggested level: Intern.""",
        ),
        (
            "Add glycerol stocks",
            """Allows a user to create glycerol stocks. Suggested level: PhD 
            student.""",
        ),
        (
            "Add consumable batches",
            """Allows a user to add batches of consumables. Suggested level: 
            Technician.""",
        ),
        (
            "Add antibodies",
            """Allows a user to add antibodies. Suggested level: Master/PhD student.""",
        ),
        (
            "Add chemicals",
            """Allows a user to add chemicals. Suggested level: PhD student.""",
        ),
        (
            "Add stock solutions",
            """Allows a user to create glycerol stocks. Suggested level: PhD 
            student.""",
        ),
        (
            "Add Fly Stock",
            """Allows a user to create fly stocks. Suggested level: PhD""",
        ),
        (
            "Add plasmid",
            """Allows a user to add cloned plasmids. Suggested level: Bachelor 
            student.""",
        ),
        (
            "Add oligonucleotide",
            """Allows a user to add primer/oligonucleotides. Suggested level: Bachelor 
            student.""",
        ),
        (
            "Manage users",
            """Allows a user to manage other users. This includes registering new users 
            as well as changing a users status and permissions.""",
        ),
        (
            "Export content",
            """Allows a user to export content. Suggested level: PhD Student.""",
        ),
        (
            "Add requests",
            """Allows a user to add requests for any ressource. Suggested level: PI.""",
        ),
    ]

    # Data.
    RESISTANCES: list[str] = [
        "Ampicillin",
        "Ampicillin and Kanamycin",
        "Apramycin",
        "Chloramphenicol",
        "Chloramphenicol and Ampicillin",
        "Gentamicin",
        "Kanamycin",
        "Spectinomycin",
        "Streptomycin",
        "Tetracyclin",
    ]
    STRAINS: list[str] = [
        "ccdB Survival 2 T1",
        "DB3.1",
        "DH10B",
        "DH5alpha",
        "HB101",
        "JM109",
        "JM110",
        "MC1061",
        "MG1655",
        "NEB Stable",
        "Pir1",
        "Stbl2",
        "Stbl3",
        "Stbl4",
        "TOP10",
        "XL1 Blue",
        "XL10 Gold",
    ]
