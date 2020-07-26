import os

from src.app.config.config import Config


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL")
