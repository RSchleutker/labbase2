# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


## [0.3.0] - 2025-07-06

### Added

- Added views to add and edit groups, group permissions, and group memberships.
- Added additional tests for group-related views.
- Added event function to ensure integrity of system groups `users` and `admins`.

### Change

- It is now ensured at app startup that every user is member of the `users` group.

### Fixed

- Checking if a user is an admin or not is now correctly done by checking if the user belongs to the Admin group. Previously, this was done through a boolean column in the database scheme for users.


## [0.2.3] - 2025-06-15

### Changed

- Admins can ~~not~~ now edit plasmids, oligos, and some other entities even if they are not the owner of that resource.

### Fixed

- The button to write a new comment was not shown because the respective permission name was changed in the database but not in the template.

## [0.2.2] - 2025-05-19

### Changed

- Add `openpyxl` package to dependencies. This package is required to parse excel files for importing entities.

### Fixed

- Fixed an error that ocurred when changing the password.


## [0.2.1] - 2025-05-12

### Changed

- Move `db = SQLAlchemy()` to its own module. Previously, `db` was defined in the `__init__.py` of the `models` package. To avoid the risk of circular imports it was now moved to `labbase2/database.py`.
- Permissions are no longer assigned to users directly but to groups. Those groups are then assigned to users. This also includes a group for *admins*. The `.is_admin` attribute of class `User` will be dropped.
- Moved `config` from its own package to a module.

### Code quality

- Applied consistent importing using `isort`.
- Applied consistent formatting using `black` with a line length of 100.
- Approved code quality by `pylint`. The quality was drastically improved.


## [0.2.0] - 2025-04-24

### Changed

- Updated queries: The project still used the query style from SQLAlchemy 1.4. This was updated to the new style introduced in SQLAlchemy 2. However, `labbase2` makes use of pagination from the `Flask-SQLAlchemy` package and the built-in pagination (as of v3.1) does not support tuples in case of rows with multiple columns. To solution as of now is to implicitly query additional data when the template is rendered. This is significantly slower and will hopefully be changed in the future. 


## [0.1.2] - 2025-04-23

### Changed

- Dropped Font Awesome: Replaced all icons from Font Awesome with icons from Bootstrap Icons.


## [0.1.1] - 2025-04-22

### Added

- The `.gitignore` file was added to the repo. For some reason, I forgot this previously.

### Fixed

- Upgraded dependencies: The required Python version was changed from **>3.9** to **>3.12** in `pyproject.toml`. Even before, the package used language features that were not yet present in Python 3.9.

### Changed

- Updated README: With v0.1.0, `labbase2` was added to PyPI and became installable by just running `pip install labbase2`. However, this was not reflected in the README, which still suggested installation directly from Github.


## [0.1.0] - 2025-04-22