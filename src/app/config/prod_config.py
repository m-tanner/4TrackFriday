import os

from src.app.config.config import Config


class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    PREFERRED_URL_SCHEME = "https"
