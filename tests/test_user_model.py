import time
from datetime import datetime

import pytest

from src.app import create_app, db
from src.app.models import User, Role, Permission, AnonymousUser


@pytest.fixture(autouse=True)
def app():
    app = create_app("testing")
    app_context = app.app_context()
    app_context.push()
    yield app
    app_context.pop()


@pytest.fixture(autouse=False)
def context(app):
    with app.test_request_context("/") as context:
        yield context


@pytest.fixture(autouse=True)
def resource(app):
    db.create_all()
    Role.insert_roles()
    yield resource
    db.session.remove()
    db.drop_all()


def test_password_setter():
    user = User(password="badPassword")
    assert user.password_hash is not None


def test_no_password_getter():
    user = User(password="badPassword")
    with pytest.raises(expected_exception=AttributeError):
        user.password


def test_password_verification():
    user = User(password="badPassword")
    assert user.verify_password("badPassword")
    assert not user.verify_password("goodPassword")


def test_password_salts_are_random():
    user_one = User(password="badPassword")
    user_two = User(password="goodPassword")
    assert user_one.password_hash != user_two.password_hash


def test_valid_confirmation_token():
    user = User(password="badPassword")
    db.session.add(user)
    db.session.commit()
    token = user.generate_confirmation_token()
    assert user.confirm(token)


def test_invalid_confirmation_token():
    user_one = User(password="badPassword")
    user_two = User(password="goodPassword")
    db.session.add(user_one)
    db.session.add(user_two)
    db.session.commit()
    token_one = user_one.generate_confirmation_token()
    assert not user_two.confirm(token_one)


def test_expired_confirmation_token():
    user = User(password="badPassword")
    db.session.add(user)
    db.session.commit()
    token = user.generate_confirmation_token(expiration=1)  # in seconds
    time.sleep(2)  # in seconds
    assert not user.confirm(token)


def test_valid_reset_token():
    u = User(password="cat")
    db.session.add(u)
    db.session.commit()
    token = u.generate_reset_token()
    assert User.reset_password(token, "dog")
    assert u.verify_password("dog")


def test_invalid_reset_token():
    u = User(password="cat")
    db.session.add(u)
    db.session.commit()
    token = u.generate_reset_token()
    assert not User.reset_password(token + "a", "horse")
    assert u.verify_password("cat")


def test_valid_email_change_token():
    u = User(email="john@example.com", password="cat")
    db.session.add(u)
    db.session.commit()
    token = u.generate_email_change_token("susan@example.org")
    assert u.change_email(token)
    assert u.email == "susan@example.org"


def test_invalid_email_change_token():
    u1 = User(email="john@example.com", password="cat")
    u2 = User(email="susan@example.org", password="dog")
    db.session.add(u1)
    db.session.add(u2)
    db.session.commit()
    token = u1.generate_email_change_token("david@example.net")
    assert not u2.change_email(token)
    assert u2.email == "susan@example.org"


def test_duplicate_email_change_token():
    u1 = User(email="john@example.com", password="cat")
    u2 = User(email="susan@example.org", password="dog")
    db.session.add(u1)
    db.session.add(u2)
    db.session.commit()
    token = u2.generate_email_change_token("john@example.com")
    assert not u2.change_email(token)
    assert u2.email == "susan@example.org"


def test_user_role():
    u = User(email="john@example.com", password="cat")
    assert u.can(Permission.FOLLOW)
    assert u.can(Permission.COMMENT)
    assert u.can(Permission.WRITE)
    assert not u.can(Permission.MODERATE)
    assert not u.can(Permission.ADMIN)


def test_moderator_role():
    r = Role.query.filter_by(name="Moderator").first()
    u = User(email="john@example.com", password="cat", role=r)
    assert u.can(Permission.FOLLOW)
    assert u.can(Permission.COMMENT)
    assert u.can(Permission.WRITE)
    assert u.can(Permission.MODERATE)
    assert not u.can(Permission.ADMIN)


def test_administrator_role():
    r = Role.query.filter_by(name="Administrator").first()
    u = User(email="john@example.com", password="cat", role=r)
    assert u.can(Permission.FOLLOW)
    assert u.can(Permission.COMMENT)
    assert u.can(Permission.WRITE)
    assert u.can(Permission.MODERATE)
    assert u.can(Permission.ADMIN)


def test_anonymous_user():
    u = AnonymousUser()
    assert not u.can(Permission.FOLLOW)
    assert not u.can(Permission.COMMENT)
    assert not u.can(Permission.WRITE)
    assert not u.can(Permission.MODERATE)
    assert not u.can(Permission.ADMIN)


def test_timestamps():
    u = User(password="cat")
    db.session.add(u)
    db.session.commit()
    assert (datetime.utcnow() - u.member_since).total_seconds() < 3
    assert (datetime.utcnow() - u.last_seen).total_seconds() < 3


def test_ping():
    u = User(password="cat")
    db.session.add(u)
    db.session.commit()
    time.sleep(2)
    last_seen_before = u.last_seen
    u.ping()
    assert u.last_seen > last_seen_before


def test_gravatar(context):
    u = User(email="john@example.com", password="cat")
    with context:
        gravatar = u.gravatar()
        gravatar_256 = u.gravatar(size=256)
        gravatar_pg = u.gravatar(rating="pg")
        gravatar_retro = u.gravatar(default="retro")
    assert (
        "https://secure.gravatar.com/avatar/" + "d4c74594d841139328695756648b6bd6"
        in gravatar
    )
    assert "s=256" in gravatar_256
    assert "r=pg" in gravatar_pg
    assert "d=retro" in gravatar_retro
