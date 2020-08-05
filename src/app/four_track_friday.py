import os

import click
from flask_migrate import Migrate, upgrade

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


@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # migrate database to latest revision
    upgrade()

    # create or update user roles
    Role.insert_roles()

    # ensure all users are following themselves
    User.add_self_follows()
