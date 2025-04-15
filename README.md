# Labbase 2

Labbase2 is a database application written in Python using the Flask 
web-framework. The target of Labbase2 is to organize lab ressources in a 
centralized manner. Labbase2 is a complete re-write of the original Labbase 
that includes a range of improvements in usability, code quality, and 
maintainability.


## Installation

You can install the `labbase2` package to your local Python environment by running the following line of code.

````commandline
pip install pybioimage@git+https://github.com/RSchleutker/labbase2.git
````

Labbase2 is an installable Flask application. After installation, you can create a folder for an instance of the app. That folder contains a python file to run the app, a config file, the SQLite file, a log file, and a sub-folder for files uploaded through the app. So a basic scheme might look like this.

````commandline
project_folder/
├───upload/
├───config.json
├───labbase2.db
├───log.log
└───main.py
````

At the very least, `config.json` should define a secret key for the app.

**config.json**
````json
{"SECRET_KEY": "645588a195c5bbd01943d0addaa3d77c26871ed04c7db3103ed52bb642ce64ee"}
````

In `main.py`, you can then set up the app. A simple example using Flask's integrated development server looks like this.

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
    config_filename = Path(Path.cwd(), "instance", "config.json")
    app = create_app(config=config_filename)

    app.run()
````

Now, you can start the app.

````commandline
python main.py
````

`log.log` and `labbase2.db` will be created automatically once the app is run for the first time.
