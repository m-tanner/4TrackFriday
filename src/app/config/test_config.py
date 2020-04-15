import os

from src.app.config.config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("TEST_DATABASE_URL")
        or f"sqlite:///{os.path.join(os.getcwd(), 'test-data.sqlite')}"
    )
