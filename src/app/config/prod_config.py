import os

from src.app.config.config import Config


class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or f"sqlite:///{os.path.join(os.getcwd(), 'data.sqlite')}"
    )
