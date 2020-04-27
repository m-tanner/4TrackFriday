import time

import pytest

from src.app import create_app, db
from src.app.models import User, Role, Permission, AnonymousUser


@pytest.fixture
def resource():
    app = create_app("testing")
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    Role.insert_roles()
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


def test_valid_reset_token(resource):
    u = User(password='cat')
    db.session.add(u)
    db.session.commit()
    token = u.generate_reset_token()
    assert User.reset_password(token, 'dog')
    assert u.verify_password('dog')


def test_invalid_reset_token(resource):
    u = User(password='cat')
    db.session.add(u)
    db.session.commit()
    token = u.generate_reset_token()
    assert not User.reset_password(token + 'a', 'horse')
    assert u.verify_password('cat')


def test_valid_email_change_token(resource):
    u = User(email='john@example.com', password='cat')
    db.session.add(u)
    db.session.commit()
    token = u.generate_email_change_token('susan@example.org')
    assert u.change_email(token)
    assert u.email == 'susan@example.org'


def test_invalid_email_change_token(resource):
    u1 = User(email='john@example.com', password='cat')
    u2 = User(email='susan@example.org', password='dog')
    db.session.add(u1)
    db.session.add(u2)
    db.session.commit()
    token = u1.generate_email_change_token('david@example.net')
    assert not u2.change_email(token)
    assert u2.email == 'susan@example.org'


def test_duplicate_email_change_token(resource):
    u1 = User(email='john@example.com', password='cat')
    u2 = User(email='susan@example.org', password='dog')
    db.session.add(u1)
    db.session.add(u2)
    db.session.commit()
    token = u2.generate_email_change_token('john@example.com')
    assert not u2.change_email(token)
    assert u2.email == 'susan@example.org'


def test_user_role(resource):
    u = User(email='john@example.com', password='cat')
    assert u.can(Permission.FOLLOW)
    assert u.can(Permission.COMMENT)
    assert u.can(Permission.WRITE)
    assert not u.can(Permission.MODERATE)
    assert not u.can(Permission.ADMIN)


def test_moderator_role(resource):
    r = Role.query.filter_by(name='Moderator').first()
    u = User(email='john@example.com', password='cat', role=r)
    assert u.can(Permission.FOLLOW)
    assert u.can(Permission.COMMENT)
    assert u.can(Permission.WRITE)
    assert u.can(Permission.MODERATE)
    assert not u.can(Permission.ADMIN)


def test_administrator_role(resource):
    r = Role.query.filter_by(name='Administrator').first()
    u = User(email='john@example.com', password='cat', role=r)
    assert u.can(Permission.FOLLOW)
    assert u.can(Permission.COMMENT)
    assert u.can(Permission.WRITE)
    assert u.can(Permission.MODERATE)
    assert u.can(Permission.ADMIN)


def test_anonymous_user(resource):
    u = AnonymousUser()
    assert not u.can(Permission.FOLLOW)
    assert not u.can(Permission.COMMENT)
    assert not u.can(Permission.WRITE)
    assert not u.can(Permission.MODERATE)
    assert not u.can(Permission.ADMIN)