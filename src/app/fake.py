from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from src.app.models import User


def users(count=100):
    """
    To be used as a script:
        (venv) % flask shell
        >>> from src.app import fake
        >>> fake.users(100)

    This takes a while to run.
    """
    fake = Faker()
    i = 0
    while i < count:
        user = User(
            email=fake.email(),
            username=fake.user_name(),
            password="password",
            confirmed=True,
            name=fake.name(),
            location=fake.city(),
            about_me=fake.text(),
            favorite_genres=fake.text(),
            first_artist_forever=fake.name(),
            second_artist_forever=fake.name(),
            member_since=fake.past_date(),
        )
        db.session.add(user)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            # we somehow got a random duplicate
            db.session.rollback()
