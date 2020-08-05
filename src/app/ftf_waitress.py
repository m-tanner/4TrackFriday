import os

from flask_migrate import Migrate, upgrade
from waitress import serve

from src.app.models import Role, User
from src.app import create_app, db


def start_serving():
    app = create_app(os.getenv("FLASK_CONFIG"))
    migrate = Migrate(app, db)

    with app.app_context():
        upgrade()
        Role.insert_roles()
        User.add_self_follows()

    serve(app, listen="*:8080")


if __name__ == "__main__":
    start_serving()
