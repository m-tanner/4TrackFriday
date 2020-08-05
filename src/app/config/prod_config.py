import os

from src.app.config.config import Config


class ProdConfig(Config):
    SSL_REDIRECT = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    PREFERRED_URL_SCHEME = "https"

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # handle reverse proxy server headers
        # from werkzeug.contrib.fixers import ProxyFix
        # app.wsgi_app = ProxyFix(app.wsgi_app)


class DockerConfig(ProdConfig):
    @classmethod
    def init_app(cls, app):
        ProdConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
