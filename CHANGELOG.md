# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Updated queries: The project still used the query style from SQLAlchemy 1.4. This was updated to the new style introduced in SQLAlchemy 2. However, `labbase2` makes use of pagination from the `Flask-SQLAlchemy` package and the built-in pagination (as of v3.1) does not support tuples in case of rows with multiple columns. To solution as of now is to implicitly query additional data when the template is rendered. This is significantly slower and will hopefully be changed in the future. 


## [0.1.2] - 2025-04-23


## [0.1.1] - 2025-04-22

### Added

- The `.gitignore` file was added to the repo. For some reason, I forgot this previously.

### Fixed

- Upgraded dependencies: The required Python version was changed from **>3.9** to **>3.12** in `pyproject.toml`. Even before, the package used language features that were not yet present in Python 3.9.

### Changed

- Updated README: With v0.1.0, `labbase2` was added to PyPI and became installable by just running `pip install labbase2`. However, this was not reflected in the README, which still suggested installation directly from Github.


## [0.1.0] - 2025-04-22