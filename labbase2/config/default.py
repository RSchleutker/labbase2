__all__ = ["DefaultConfig"]


class DefaultConfig:
    """A default config for logging"""

    SECRET_KEY: str = "verysecretkey"

    # Database.
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///labbase2.db"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Display.
    DELETABLE_HOURS: int = 72
    PER_PAGE: int = 100

    # User.
    USER: tuple = "Admin", "Admin", "admin@admin.de"
    DEFAULT_TIMEZONE: str = "Europe/Berlin"
    UPLOAD_FOLDER: str = "upload"
    RESET_EXPIRES: int = 10
    PERMISSIONS: list[tuple[str, str]] = [
        ("add-comment", "Allows a user to author own comments."),
        ("upload-file", "Allows a user to upload files."),
        ("add-dilution", "Allows a user to add dilutions to antibodies."),
        ("add-preparation", "Allows a user to add plasmid preparations."),
        ("add-glycerol-stock", "Allows a user to create glycerol stocks."),
        ("add-consumable-batch", "Allows a user to add batches of consumables."),
        ("add-antibody", "Allows a user to add antibodies."),
        ("delete-antibody", "Allow a user to delete antibodies."),
        ("add-chemical", "Allows a user to add chemicals."),
        ("add-stock-solution", "Allows a user to add stock solutions of chemicals."),
        ("add-fly-stock", "Allows a user to create fly stocks."),
        ("add-plasmid", "Allows a user to add cloned plasmids."),
        ("add-oligonucleotide", "Allows a user to add primer/oligonucleotides."),
        ("view-user", "Allows a user to see all other users."),
        ("inactivate-user", "Allow a user to inactivate a user account."),
        ("reset-password", "Allow a user to reset passwords for everyone."),
        ("register-user", "Allows a user to register another user."),
        ("change-group", "Allow a user to assign groups to users"),
        ("delete-user", "Allows a user to delete another user."),
        ("export-content", "Allows a user to export content. Suggested level: PhD Student."),
        ("add-request", "Allows a user to add requests for any ressource. Suggested level: PI."),
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
