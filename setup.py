from setuptools import setup, find_packages

install_requirements = [
    "flask",
    "click",
    "waitress",
    "wtforms",
    "flask-wtf",
    "flask-bootstrap",
    "flask-mail",
    "flask-moment",
    "flask-sqlalchemy",
    "flask-migrate",
    "alembic",
    "sqlalchemy",
    "boto3",
    "botocore~=1.14",
    "six~=1.12",
    "google-cloud-storage",
    "pytz",
    "psycopg2-binary",
    "flask-login",
    "werkzeug",
    "itsdangerous",
]

test_requirements = [
    "pytest",
    "pytest-cov",
]

lint_requirements = [
    "black",
    "flake8",
    "pylint",
]

setup(
    name="4TrackFriday",
    version="0.1",
    packages=find_packages(),
    url="fourtrackfriday.com",
    license="",
    author="Michael Tanner",
    author_email="tanner.mbt@gmail.com",
    description="Code for the Four Track Friday web app",
    install_requires=install_requirements,
    extras_require={"tests": [test_requirements], "lint": [lint_requirements]},
    python_requires="~=3.7",
    entry_points={"console_scripts": ["ftf_svc=src.app.ftf_waitress:start_serving"]},
)
