from flask import Blueprint

auth = Blueprint("auth", __name__)

from src.app.auth import views
