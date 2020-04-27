import os

from flask_migrate import Migrate

from src.app import create_app, db
from src.app.models import User, Role, Permission

app = create_app(os.getenv("FLASK_CONFIG", "default"))
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Permission=Permission)


@app.cli.command()
def test():
    import pytest

    pytest.main(["-x", "tests/"])
