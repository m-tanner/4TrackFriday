import os

from src.app.config.config import Config


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DEV_DATABASE_URL")
        or f"sqlite:///{os.path.join(os.getcwd(), 'dev-data.sqlite')}"
    )
