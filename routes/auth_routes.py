"""Signup, login, email confirmation and password reset flows."""

from __future__ import annotations

import logging
from typing import Any

from botocore.exceptions import ClientError
from flask import (
    Blueprint,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.wrappers.response import Response as WerkzeugResponse

import auth
from forms import (
    ConfirmForm,
    ConfirmResetForm,
    LoginForm,
    NewPasswordForm,
    ResetPasswordForm,
    SignupForm,
)
from utils import start_session

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)

# Signup collects details, then payment, then creates the Cognito account. The
# pending details therefore live in the server-side (filesystem) session and are
# discarded the moment the account exists - they are never sent to the browser.
PENDING_SIGNUP_KEY = "pending_signup"

ViewResponse = str | Response | WerkzeugResponse


@auth_bp.route("/subscription")
def subscription() -> str:
    """Plan selection page shown between signup and account creation."""
    return render_template("account/subscription.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login() -> ViewResponse:
    """Authenticate against Cognito and establish a session."""
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data or ""
        try:
            tokens = auth.authenticate(email, form.password.data or "")
        except ClientError as error:
            return _login_error(auth.error_code(error))

        if tokens is None:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        attributes = auth.user_attributes(tokens["access_token"])
        start_session(
            email=email,
            username=email,
            user_id=attributes.get("sub", ""),
            tokens=tokens,
        )

        if attributes.get("email_verified") != "true":
            flash("Please verify your email address before proceeding.", "warning")
            return redirect(url_for("auth.confirm_signup"))

        # Redirect rather than render, so a refresh does not re-post credentials.
        return redirect(url_for("dashboard.files"))

    return render_template("account/login.html", form=form)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup() -> ViewResponse:
    """Collect account details and hand off to plan selection."""
    form = SignupForm()
    if form.validate_on_submit():
        session[PENDING_SIGNUP_KEY] = {
            "name": form.name.data,
            "username": form.username.data,
            "email": form.email.data,
            "phone_number": f"+1{form.phone_number.data}",
            "password": form.password.data,
        }
        session.permanent = True
        logger.info("signup started", extra={"username": form.username.data})
        return redirect(url_for("auth.subscription"))

    return render_template("account/signup.html", form=form)


@auth_bp.route("/confirm-signup", methods=["GET", "POST"])
def confirm_signup() -> ViewResponse:
    """Verify the emailed confirmation code for a newly created account."""
    username = _pending_username()
    if username is None:
        flash("Please sign up first.", "warning")
        return redirect(url_for("auth.signup"))

    form = ConfirmForm()
    if form.validate_on_submit():
        try:
            auth.confirm_sign_up(username, form.confirmation_code.data or "")
        except ClientError as error:
            flash(_CONFIRM_ERRORS.get(auth.error_code(error), _GENERIC_ERROR), "danger")
        else:
            session.pop(PENDING_SIGNUP_KEY, None)
            flash("Account confirmed successfully. Please log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("account/confirm_signup.html", form=form)


@auth_bp.route("/resend-confirmation-code", methods=["POST"])
def resend_confirmation_code() -> tuple[Response, int] | Response:
    """Ask Cognito to email a fresh confirmation code."""
    username = _pending_username()
    if username is None:
        return jsonify(error="No signup in progress."), 400

    try:
        auth.resend_confirmation_code(username)
    except ClientError as error:
        logger.info("resend code failed", extra={"code": auth.error_code(error)})
        return jsonify(error="Could not resend the confirmation code."), 502

    return jsonify(success=True)


@auth_bp.route("/reset", methods=["GET", "POST"])
def reset() -> ViewResponse:
    """Start a password reset by emailing a verification code."""
    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data or ""
        try:
            auth.forgot_password(email)
        except ClientError as error:
            code = auth.error_code(error)
            if code == "LimitExceededException":
                flash("Too many reset attempts. Please try again later.", "danger")
                return render_template("account/reset_password.html", form=form)
            # Any other failure is swallowed so the response does not reveal
            # whether the address is registered.
            logger.info("password reset request failed", extra={"code": code})

        session["reset_email"] = email
        flash("If that address has an account, a reset code is on its way.", "info")
        return redirect(url_for("auth.confirm_reset"))

    return render_template("account/reset_password.html", form=form)


@auth_bp.route("/confirm-reset", methods=["GET", "POST"])
def confirm_reset() -> ViewResponse:
    """Collect the reset code before asking for a new password."""
    if "reset_email" not in session:
        flash("Start a reset request first.", "info")
        return redirect(url_for("auth.reset"))

    form = ConfirmResetForm()
    if form.validate_on_submit():
        session["reset_code"] = form.confirmation_code.data
        return redirect(url_for("auth.new_password"))

    return render_template("account/confirm_reset.html", form=form)


@auth_bp.route("/new-password", methods=["GET", "POST"])
def new_password() -> ViewResponse:
    """Set a new password using the previously supplied reset code."""
    email = session.get("reset_email")
    code = session.get("reset_code")
    if not email or not code:
        flash("Your reset session expired. Please start again.", "info")
        return redirect(url_for("auth.reset"))

    form = NewPasswordForm()
    if form.validate_on_submit():
        try:
            auth.confirm_forgot_password(email, code, form.password.data or "")
        except ClientError as error:
            flash(_RESET_ERRORS.get(auth.error_code(error), _GENERIC_ERROR), "danger")
        else:
            session.pop("reset_email", None)
            session.pop("reset_code", None)
            flash("Password reset successfully. You can log in now.", "success")
            return redirect(url_for("auth.login"))

    return render_template("account/new_password.html", form=form)


@auth_bp.route("/logout", methods=["GET", "POST"])
def logout() -> ViewResponse:
    """Confirm and then clear the session."""
    if request.method == "POST":
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("misc.home"))
    return render_template("account/confirm_logout.html")


_GENERIC_ERROR = "Something went wrong. Please try again."

_CONFIRM_ERRORS = {
    "ExpiredCodeException": "That code has expired. Please request a new one.",
    "CodeMismatchException": "That code is not correct. Please try again.",
    "UserNotFoundException": "We could not find that account.",
    "NotAuthorizedException": "This account is already confirmed. Please log in.",
    "LimitExceededException": "Too many attempts. Please try again later.",
}

_RESET_ERRORS = {
    "CodeMismatchException": "That code is not correct. Please request a new one.",
    "ExpiredCodeException": "That code has expired. Please start the reset again.",
    "NotAuthorizedException": "That code has expired. Please start the reset again.",
    "InvalidPasswordException": "That password does not meet the requirements.",
}

_LOGIN_ERRORS = {
    "UserNotConfirmedException": (
        "Your account is not confirmed. Please check your email for the code.",
        "auth.confirm_signup",
    ),
    "UserNotFoundException": ("Email not found. Please sign up first.", "auth.signup"),
}


def _login_error(code: str) -> WerkzeugResponse:
    message, endpoint = _LOGIN_ERRORS.get(code, (_GENERIC_ERROR, "auth.login"))
    logger.info("login failed", extra={"code": code})
    flash(message, "danger")
    return redirect(url_for(endpoint))


def _pending_username() -> str | None:
    """Username of the signup in progress, or of the logged-in user."""
    pending: dict[str, Any] = session.get(PENDING_SIGNUP_KEY) or {}
    return pending.get("username") or (session.get("user") or {}).get("username")
