import os

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_sslify import SSLify

from src.app.config import config, config_factory
from src.config_manager import ConfigManager
from src.fetcher_factory import FetcherFactory

# logging.basicConfig(
#     format="%(asctime)s %(levelname)-8s %(message)s",
#     level=logging.INFO,
#     datefmt="%Y-%m-%d %H:%M:%S",
# )
# logger = logging.getLogger(__name__)

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
sslify = SSLify()

login_manager = LoginManager()
login_manager.login_view = "auth.login"

config_manager = ConfigManager()
fetcher = FetcherFactory(config=config_manager).get_fetcher()


def create_app(config_type: str) -> Flask:
    app = Flask(__name__.split(".")[0], root_path=os.path.join(os.getcwd(), "src/app"))
    app_config = config_factory.get_config(config_type)
    app.config.from_object(app_config)

    app_config.init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    if app.config['SSL_REDIRECT']:
        sslify.init_app(app)

    from src.app.main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from src.app.auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    return app
