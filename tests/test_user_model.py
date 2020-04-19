import time

import pytest

from src.app import create_app, db
from src.app.models import User


@pytest.fixture
def resource():
    app = create_app("testing")
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    yield "resource"
    db.session.remove()
    db.drop_all()
    app_context.pop()


def test_password_setter(resource):
    user = User(password="badPassword")
    assert user.password_hash is not None


def test_no_password_getter(resource):
    user = User(password="badPassword")
    with pytest.raises(expected_exception=AttributeError):
        user.password


def test_password_verification(resource):
    user = User(password="badPassword")
    assert user.verify_password("badPassword")
    assert not user.verify_password("goodPassword")


def test_password_salts_are_random(resource):
    user_one = User(password="badPassword")
    user_two = User(password="goodPassword")
    assert user_one.password_hash != user_two.password_hash


def test_valid_confirmation_token(resource):
    user = User(password="badPassword")
    db.session.add(user)
    db.session.commit()
    token = user.generate_confirmation_token()
    assert user.confirm(token)


def test_invalid_confirmation_token(resource):
    user_one = User(password="badPassword")
    user_two = User(password="goodPassword")
    db.session.add(user_one)
    db.session.add(user_two)
    db.session.commit()
    token_one = user_one.generate_confirmation_token()
    assert not user_two.confirm(token_one)


def test_expired_confirmation_token(resource):
    user = User(password="badPassword")
    db.session.add(user)
    db.session.commit()
    token = user.generate_confirmation_token(expiration=1)  # in seconds
    time.sleep(2)  # in seconds
    assert not user.confirm(token)
