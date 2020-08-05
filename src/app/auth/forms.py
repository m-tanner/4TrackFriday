from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    Regexp,
    EqualTo,
    ValidationError,
)

from src.app.models import User


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Log In")


class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_]*$",
                0,
                "Usernames must have only letters, numbers, or underscores",
            ),
        ],
    )
    name = StringField(
        "Real Name",
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp("^[A-Za-z ]*$", 0, "Real names must have only letters and spaces"),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="Passwords must match."),
        ],
    )
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        # signature required as is
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("Email already registered.")

    def validate_username(self, field):
        # signature required as is
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already in use.")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Old password", validators=[DataRequired()])
    password = PasswordField(
        "New password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="Passwords must match."),
        ],
    )
    password2 = PasswordField("Confirm new password", validators=[DataRequired()])
    submit = SubmitField("Update Password")


class PasswordResetRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField("Reset Password")


class PasswordResetForm(FlaskForm):
    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="Passwords must match"),
        ],
    )
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Reset Password")


class ChangeEmailForm(FlaskForm):
    email = StringField(
        "New Email", validators=[DataRequired(), Length(1, 64), Email()]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Update Email Address")

    def validate_email(self, field):
        # signature required as is
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("Email already registered.")
