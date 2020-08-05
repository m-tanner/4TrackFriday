import pytest
from flask import current_app

from src.app import create_app, db


@pytest.fixture
def resource():
    app = create_app("test")
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    yield "resource"
    db.session.remove()
    db.drop_all()
    app_context.pop()


def test_app_exists(resource):
    assert current_app is not None


def test_app_is_testing(resource):
    assert current_app.config["TESTING"]
