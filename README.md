![Python](https://img.shields.io/badge/python-3.12-blue)
![Pytest](https://img.shields.io/badge/tests-pytest%20passed-brightgreen)

# Labbase2

**Labbase2** is a database application written in Python using the Flask web framework. It is designed to help manage lab resources in a centralized and efficient way.

This project is a complete rewrite of the original Labbase and includes major improvements in usability, code quality, and maintainability.

---

## 🚀 Installation

Install the `labbase2` package directly from PyPI:

````commandline
pip install labbase2
````

Labbase2 is an installable Flask application. After installation, you can create a dedicated folder for your app instance. The folder typically contains:

````commandline
project_folder/
├── upload/           # Folder for uploaded files
├── labbase2.db       # SQLite database (created on first run)
├── log.log           # Log file (created on first run)
└── main.py           # Script to start the app
````

## ⚙️ Configuration

At the very least, a secret ky should be configured, either through a config file or via the `config_dict` argument of `create_app`.

## 🧪 Example main.py
Here's a minimal setup to launch the app with Flask's built-in development server:

**main.py**
````python
import logging

from labbase2 import create_app
from pathlib import Path
from logging.config import dictConfig


if __name__ == "__main__":

    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "()": "labbase2.logging.RequestFormatter",
                    "format": "[%(asctime)s] %(levelname)-7s in %(module)-10s: [%(user)s] %(message)s",
                }
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://flask.logging.wsgi_errors_stream",
                    "formatter": "default",
                },
                "file": {
                    "class": "logging.FileHandler",
                    "level": "DEBUG",
                    "filename": Path("instance", "log.log"),
                    "mode": "w",
                    "formatter": "default",
                },
            },
            "root": {"level": "DEBUG", "handlers": ["wsgi", "file"]},
        }
    )

    # Prevent 'werkzeug' from logging every single request.
    logger_werkz = logging.getLogger("werkzeug")
    logger_werkz.level = logging.ERROR

    # Configure the app.
    app = create_app(config_dict={"SECRET_KEY": "645588a195c5bbd"})

    app.run()
````

Start the app by running:

````commandline
python main.py
````

The database (`labbase2.db`) and log file (`log.log`) will be created automatically on first run.


## 📄 License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

### Third-Party Libraries

This project uses the following third-party libraries:

- [Bootstrap 5.2.3-dist](https://getbootstrap.com/) – MIT License
- [jQuery 3.7.1](https://jquery.com/) – MIT License
- [Popper.js](https://popper.js.org/) – MIT License

The above libraries are included locally in this repository or via CDNs. If included locally, their original license files are included in the respective folders.

