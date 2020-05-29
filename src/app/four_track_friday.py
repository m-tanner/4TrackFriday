import os

import click
from flask_migrate import Migrate

from src.app import create_app, db
from src.app.models import User, Role, Permission, Follow

app = create_app(os.getenv("FLASK_CONFIG", "default"))
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Follow=Follow, Role=Role, Permission=Permission)


@app.cli.command()
@click.argument("pytest_arg", nargs=-1)
def test(pytest_arg):
    import pytest

    if not pytest_arg:
        pytest.main(["-x", "-s", "-v", "--disable-pytest-warnings", "tests/"])
    else:
        pytest.main([f"tests/{str(pytest_arg[0])}"])
