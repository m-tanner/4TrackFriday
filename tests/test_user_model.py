import time
from datetime import datetime

import pytest

from src.app import create_app, db
from src.app.models import User, Role, Permission, AnonymousUser, Follow


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
    user = User(email="forTests@example.com", password="badPassword")
    assert user.password_hash is not None


def test_no_password_getter():
    user = User(email="forTests@example.com", password="badPassword")
    with pytest.raises(expected_exception=AttributeError):
        user.password


def test_password_verification():
    user = User(email="forTests@example.com", password="badPassword")
    assert user.verify_password("badPassword")
    assert not user.verify_password("goodPassword")


def test_password_salts_are_random():
    user_one = User(email="forTests@example.com", password="badPassword")
    user_two = User(email="forTests@example.com", password="goodPassword")
    assert user_one.password_hash != user_two.password_hash


def test_valid_confirmation_token():
    user = User(email="forTests@example.com", password="badPassword")
    db.session.add(user)
    db.session.commit()
    token = user.generate_confirmation_token()
    assert user.confirm(token)
    db.session.delete(user)
    db.session.commit()


def test_invalid_confirmation_token():
    user_one = User(email="forTests@example.com", password="badPassword")
    user_two = User(email="forTests@example.com", password="goodPassword")
    db.session.add(user_one)
    db.session.add(user_two)
    db.session.commit()
    token_one = user_one.generate_confirmation_token()
    assert not user_two.confirm(token_one)
    db.session.delete(user_one)
    db.session.delete(user_two)
    db.session.commit()


def test_expired_confirmation_token():
    user = User(email="forTests@example.com", password="badPassword")
    db.session.add(user)
    db.session.commit()
    token = user.generate_confirmation_token(expiration=1)  # in seconds
    time.sleep(2)  # in seconds
    assert not user.confirm(token)
    db.session.delete(user)
    db.session.commit()


def test_valid_reset_token():
    user = User(email="forTests@example.com", password="cat")
    db.session.add(user)
    db.session.commit()
    token = user.generate_reset_token()
    assert User.reset_password(token, "dog")
    assert user.verify_password("dog")
    db.session.delete(user)
    db.session.commit()


def test_invalid_reset_token():
    user = User(email="forTests@example.com", password="cat")
    db.session.add(user)
    db.session.commit()
    token = user.generate_reset_token()
    assert not User.reset_password(token + "a", "horse")
    assert user.verify_password("cat")
    db.session.delete(user)
    db.session.commit()


def test_valid_email_change_token():
    user = User(email="john@example.com", password="cat")
    db.session.add(user)
    db.session.commit()
    token = user.generate_email_change_token("susan@example.org")
    assert user.change_email(token)
    assert user.email == "susan@example.org"
    db.session.delete(user)
    db.session.commit()


def test_invalid_email_change_token():
    user_one = User(email="john@example.com", password="cat")
    user_two = User(email="susan@example.org", password="dog")
    db.session.add(user_one)
    db.session.add(user_two)
    db.session.commit()
    token = user_one.generate_email_change_token("david@example.net")
    assert not user_two.change_email(token)
    assert user_two.email == "susan@example.org"
    db.session.delete(user_one)
    db.session.delete(user_two)
    db.session.commit()


def test_duplicate_email_change_token():
    user_one = User(email="john@example.com", password="cat")
    user_two = User(email="susan@example.org", password="dog")
    db.session.add(user_one)
    db.session.add(user_two)
    db.session.commit()
    token = user_two.generate_email_change_token("john@example.com")
    assert not user_two.change_email(token)
    assert user_two.email == "susan@example.org"
    db.session.delete(user_one)
    db.session.delete(user_two)
    db.session.commit()


def test_user_role():
    user = User(email="john@example.com", password="cat")
    assert user.can(Permission.FOLLOW)
    assert user.can(Permission.COMMENT)
    assert user.can(Permission.WRITE)
    assert not user.can(Permission.MODERATE)
    assert not user.can(Permission.ADMIN)


def test_moderator_role():
    role = Role.query.filter_by(name="Moderator").first()
    user = User(email="john@example.com", password="cat", role=role)
    assert user.can(Permission.FOLLOW)
    assert user.can(Permission.COMMENT)
    assert user.can(Permission.WRITE)
    assert user.can(Permission.MODERATE)
    assert not user.can(Permission.ADMIN)


def test_administrator_role():
    role = Role.query.filter_by(name="Administrator").first()
    user = User(email="john@example.com", password="cat", role=role)
    assert user.can(Permission.FOLLOW)
    assert user.can(Permission.COMMENT)
    assert user.can(Permission.WRITE)
    assert user.can(Permission.MODERATE)
    assert user.can(Permission.ADMIN)


def test_anonymous_user():
    user = AnonymousUser()
    assert not user.can(Permission.FOLLOW)
    assert not user.can(Permission.COMMENT)
    assert not user.can(Permission.WRITE)
    assert not user.can(Permission.MODERATE)
    assert not user.can(Permission.ADMIN)


def test_timestamps():
    user = User(password="cat")
    db.session.add(user)
    db.session.commit()
    assert (datetime.utcnow() - user.member_since).total_seconds() < 3
    assert (datetime.utcnow() - user.last_seen).total_seconds() < 3
    db.session.delete(user)
    db.session.commit()


def test_ping():
    user = User(password="cat")
    db.session.add(user)
    db.session.commit()
    time.sleep(2)
    last_seen_before = user.last_seen
    user.ping()
    assert user.last_seen > last_seen_before
    db.session.delete(user)
    db.session.commit()


def test_gravatar(context):
    user = User(email="john@example.com", password="cat")
    with context:
        gravatar = user.gravatar()
        gravatar_256 = user.gravatar(size=256)
        gravatar_pg = user.gravatar(rating="pg")
        gravatar_retro = user.gravatar(default="retro")
    assert (
        "https://secure.gravatar.com/avatar/" + "d4c74594d841139328695756648b6bd6"
        in gravatar
    )
    assert "s=256" in gravatar_256
    assert "r=pg" in gravatar_pg
    assert "d=retro" in gravatar_retro


def test_follows():
    user_one = User(email="john@example.com", username="john", password="cat")
    user_two = User(email="susan@example.org", username="susan", password="dog")
    db.session.add(user_one)
    db.session.add(user_two)
    db.session.commit()
    assert not user_one.is_following(user_two)
    assert not user_one.is_followed_by(user_two)

    timestamp_before = datetime.utcnow()
    user_one.follow(user_two)
    db.session.add(user_one)
    db.session.commit()
    timestamp_after = datetime.utcnow()

    assert user_one.is_following(user_two)
    assert not user_one.is_followed_by(user_two)
    assert user_two.is_followed_by(user_one)
    assert user_one.followed.count() == 2
    assert user_two.followers.count() == 2
    assert user_one.followed.all()[-1].followed == user_two
    assert timestamp_before <= user_one.followed.all()[-1].timestamp <= timestamp_after
    assert user_two.followers.all()[0].follower == user_one

    user_one.unfollow(user_two)
    db.session.add(user_one)
    db.session.commit()
    assert user_one.followed.count() == 1
    assert user_two.followers.count() == 1
    assert Follow.query.count() == 2

    user_two.follow(user_one)
    db.session.add(user_one)
    db.session.add(user_two)
    db.session.commit()
    db.session.delete(user_two)
    db.session.commit()
    assert Follow.query.count() == 1
