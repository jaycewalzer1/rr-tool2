"""WTForms definitions for the authentication and account flows."""

from __future__ import annotations

import re
from typing import Any, Final

from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Regexp,
    ValidationError,
)

# Mirrors the default AWS Cognito password policy so users get immediate,
# specific feedback instead of a generic InvalidPasswordException from Cognito.
MIN_PASSWORD_LENGTH: Final = 8
_COGNITO_SPECIAL_CHARACTERS: Final = r"^$*.[]{}()?\"!@#%&/\\,><':;|_~`+=-"

_PASSWORD_RULES: Final[tuple[tuple[str, str], ...]] = (
    (r"[A-Z]", "Password must contain at least one uppercase letter."),
    (r"[a-z]", "Password must contain at least one lowercase letter."),
    (r"[0-9]", "Password must contain at least one number."),
    (
        f"[{re.escape(_COGNITO_SPECIAL_CHARACTERS)}]",
        "Password must contain at least one special character.",
    ),
)


def validate_cognito_password(_form: FlaskForm, field: Any) -> None:
    """Reject passwords Cognito would refuse, before the API call is made."""
    password: str = field.data or ""

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")

    for pattern, message in _PASSWORD_RULES:
        if not re.search(pattern, password):
            raise ValidationError(message)


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class SignupForm(FlaskForm):
    name = StringField(
        "Full Name",
        validators=[
            DataRequired(),
            Length(min=2, max=100, message="Name must be between 2 and 100 characters."),
        ],
    )
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=25)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    phone_number = StringField(
        "Phone Number",
        validators=[DataRequired(), Regexp(r"^\d{10}$", message="Phone number must be 10 digits.")],
    )
    password = PasswordField("Password", validators=[DataRequired(), validate_cognito_password])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Sign Up")


class ConfirmForm(FlaskForm):
    confirmation_code = StringField(
        "Confirmation Code",
        validators=[
            DataRequired(),
            Length(min=6, max=6, message="Confirmation code must be 6 digits."),
        ],
    )
    submit = SubmitField("Confirm Account")


class ResetPasswordForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Reset Code")


class ConfirmResetForm(FlaskForm):
    confirmation_code = StringField(
        "Confirmation Code",
        validators=[
            DataRequired(),
            Length(min=6, max=6, message="Confirmation code must be 6 digits."),
        ],
    )
    submit = SubmitField("Verify Code")


class NewPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired(), validate_cognito_password])
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Change Password")
