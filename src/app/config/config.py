import abc
import os


class Config(metaclass=abc.ABCMeta):
    SECRET_KEY = os.getenv("FTF_SECRET_KEY", "hard to guess string")
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.mail.me.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() in ["true", "on", "1"]
    MAIL_ADDRESS = os.getenv("FTF_EMAIL_ADDRESS")
    MAIL_USERNAME = MAIL_ADDRESS.split("@")[0]
    MAIL_PASSWORD = os.getenv("FTF_EMAIL_PASSWORD")
    FTF_MAIL_SUBJECT_PREFIX = "[4TrackFriday]"
    FTF_MAIL_SENDER = f"4TrackFriday Admin <{MAIL_ADDRESS}>"
    FTF_ADMIN = os.getenv("ADMIN_EMAIL_ADDRESS")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False
    SSL_REDIRECT = False

    @staticmethod
    def init_app(app):
        pass
