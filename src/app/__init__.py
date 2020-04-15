from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from src.app.config import config, config_factory
from src.config_manager import ConfigManager
from src.fetcher_factory import FetcherFactory

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

config_manager = ConfigManager()
fetcher = FetcherFactory(config=config_manager).get_fetcher()


def create_app(config_type: str):
    app = Flask(__name__)
    app_config = config_factory.get_config(config_type)
    app.config.from_object(app_config)

    app_config.init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    from src.app.main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    return app
