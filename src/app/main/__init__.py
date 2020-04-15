from flask import Blueprint

main = Blueprint("main", __name__)

from src.app.main import views, errors
