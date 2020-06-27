from waitress import serve

from src.app.ftf_flask import app


def start_serving():
    serve(app=app, listen="*:8080")


if __name__ == "__main__":
    start_serving()
