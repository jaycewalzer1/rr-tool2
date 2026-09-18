"""Stripe checkout, subscription management and webhook handling.

Subscription state is read back from Stripe rather than mirrored locally, so the
webhook only has to keep customer metadata in step.
"""

from __future__ import annotations

import logging
from typing import Any

import stripe
from botocore.exceptions import ClientError
from flask import (
    Blueprint,
    Response,
    current_app,
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
from decorators import login_required, verify_account

logger = logging.getLogger(__name__)

billing_bp = Blueprint("billing", __name__)

PLAN_CREDITS = {"basic": 10, "premium": 50, "enterprise": "unlimited"}


def _config() -> Any:
    return current_app.config["APP_CONFIG"]


@billing_bp.route("/create-checkout-session", methods=["POST"])
def create_checkout_session() -> tuple[Response, int] | Response:
    """Start a Stripe Checkout session for the pending or current signup."""
    pending = session.get("pending_signup") or {}
    user = session.get("user") or {}
    email = pending.get("email") or user.get("email")
    if not email:
        return jsonify(error="No signup in progress."), 400

    price_id = _config().stripe.price_id_basic
    if not price_id:
        logger.error("STRIPE_PRICE_ID_BASIC is not configured")
        return jsonify(error="Billing is not configured."), 503

    try:
        checkout = stripe.checkout.Session.create(
            mode="subscription",
            customer_email=email,
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=url_for("billing.success", _external=True),
            cancel_url=url_for("billing.cancel", _external=True),
            metadata={"email": email, "username": pending.get("username", "")},
        )
    except stripe.StripeError:
        logger.exception("could not create checkout session")
        return jsonify(error="Could not start checkout. Please try again."), 502

    session["stripe_checkout_id"] = checkout.id
    return jsonify(id=checkout.id, url=checkout.url)


@billing_bp.route("/success")
def success() -> WerkzeugResponse:
    """Create the Cognito account once payment has completed.

    The account is deliberately created after checkout so an unpaid signup never
    leaves a half-provisioned user in the pool.
    """
    pending = session.get("pending_signup")
    if not pending:
        # Already provisioned (for example, a refresh of this page).
        return redirect(url_for("auth.confirm_signup"))

    if not session.get("stripe_checkout_id"):
        flash("We could not confirm your payment. Please try again.", "danger")
        return redirect(url_for("auth.subscription"))

    try:
        user_sub = auth.sign_up(
            username=pending["username"],
            password=pending["password"],
            email=pending["email"],
            phone_number=pending["phone_number"],
            name=pending["name"],
        )
    except ClientError as error:
        code = auth.error_code(error)
        logger.warning("cognito signup failed", extra={"code": code})
        flash(_SIGNUP_ERRORS.get(code, "We could not create your account."), "danger")
        return redirect(url_for("auth.signup"))

    # Keep only the username so the confirmation step can address Cognito; the
    # password is dropped as soon as the account exists.
    session["pending_signup"] = {"username": pending["username"]}
    session.pop("stripe_checkout_id", None)
    logger.info("account provisioned", extra={"user_sub": user_sub})

    flash("Payment received. Check your email for a confirmation code.", "success")
    return redirect(url_for("auth.confirm_signup"))


@billing_bp.route("/cancel")
def cancel() -> WerkzeugResponse:
    """Return the user to plan selection after abandoning checkout."""
    flash("Checkout was cancelled.", "info")
    return redirect(url_for("auth.subscription"))


@billing_bp.route("/manage-membership")
@login_required
@verify_account
def manage_membership() -> str:
    """Membership management page; data is loaded from the JSON endpoints."""
    return render_template("dashboard/manage_membership.html")


@billing_bp.route("/subscription/status")
@login_required
@verify_account
def subscription_status() -> Response:
    """Current plan, renewal date and remaining upload credits."""
    customer = _current_customer()
    if customer is None:
        return jsonify(
            status="inactive",
            current_plan=None,
            next_billing_date=None,
            upload_credits=0,
            last_payment_date=None,
            payments=[],
        )

    subscriptions = stripe.Subscription.list(customer=customer.id, limit=1).data
    metadata = customer.metadata

    return jsonify(
        status=metadata.get("subscription_status", "inactive"),
        current_plan=metadata.get("current_plan"),
        next_billing_date=subscriptions[0]["current_period_end"] if subscriptions else None,
        upload_credits=metadata.get("upload_credits", 0),
        last_payment_date=metadata.get("last_payment_date"),
        payments=_payments(customer.id),
    )


@billing_bp.route("/subscription/payment-history")
@login_required
@verify_account
def payment_history() -> Response:
    """Past payments for the logged-in customer."""
    customer = _current_customer()
    return jsonify(payments=[] if customer is None else _payments(customer.id))


@billing_bp.route("/subscription/change-plan", methods=["GET", "POST"])
@login_required
@verify_account
def change_plan() -> tuple[Response, int] | Response:
    """Send an existing customer back through checkout to switch plans."""
    customer = _current_customer()
    if customer is None:
        return jsonify(error="No billing account found."), 404

    try:
        checkout = stripe.checkout.Session.create(
            customer=customer.id,
            mode="subscription",
            line_items=[{"price": _config().stripe.price_id_basic, "quantity": 1}],
            success_url=url_for("billing.manage_membership", _external=True) + "?success=true",
            cancel_url=url_for("billing.manage_membership", _external=True) + "?cancelled=true",
            metadata={"user_id": session["user"]["user_id"]},
        )
    except stripe.StripeError:
        logger.exception("could not create plan change session")
        return jsonify(error="Could not start checkout. Please try again."), 502

    return jsonify(url=checkout.url)


@billing_bp.route("/subscription/cancel", methods=["POST"])
@login_required
@verify_account
def cancel_subscription() -> tuple[Response, int] | Response:
    """Cancel at period end so the user keeps access they have paid for."""
    customer = _current_customer()
    if customer is None:
        return jsonify(error="No billing account found."), 404

    subscriptions = stripe.Subscription.list(customer=customer.id, status="active").data
    if not subscriptions:
        return jsonify(error="No active subscription found."), 404

    stripe.Subscription.modify(subscriptions[0].id, cancel_at_period_end=True)
    stripe.Customer.modify(customer.id, metadata={"subscription_status": "cancelled_at_end"})

    return jsonify(
        status="success",
        message="Your subscription will end when the current billing period closes.",
    )


@billing_bp.route("/webhook", methods=["POST"])
def webhook() -> tuple[Response, int] | Response:
    """Apply Stripe subscription events to customer metadata.

    The signature is verified against ``STRIPE_WEBHOOK_SECRET``; without it
    anyone could POST a forged ``customer.subscription.created`` event and grant
    themselves an active subscription.
    """
    try:
        event = stripe.Webhook.construct_event(
            payload=request.get_data(),
            sig_header=request.headers.get("Stripe-Signature", ""),
            secret=_config().stripe.webhook_secret,
        )
    except ValueError:
        logger.warning("webhook payload was not valid json")
        return jsonify(error="Invalid payload"), 400
    except stripe.SignatureVerificationError:
        logger.warning("webhook signature verification failed")
        return jsonify(error="Invalid signature"), 400

    handler = _WEBHOOK_HANDLERS.get(event["type"])
    if handler is None:
        logger.info("ignoring webhook event", extra={"event_type": event["type"]})
        return jsonify(status="ignored")

    handler(event["data"]["object"])
    logger.info("webhook handled", extra={"event_type": event["type"]})
    return jsonify(status="success")


def _on_checkout_completed(checkout: Any) -> None:
    if checkout.get("customer"):
        stripe.Customer.modify(
            checkout["customer"],
            metadata={
                "subscription_status": "pending",
                "checkout_session_id": checkout["id"],
            },
        )


def _on_subscription_created(subscription: Any) -> None:
    price = subscription["items"]["data"][0]["price"]
    plan = str(price.get("nickname") or price.get("product") or "basic").lower()
    stripe.Customer.modify(
        subscription["customer"],
        metadata={
            "subscription_status": "active",
            "current_plan": plan,
            "subscription_id": subscription["id"],
            # Stripe stores metadata as strings; sending an int silently coerces
            # and comes back as a string anyway, so convert here.
            "subscription_end_date": str(subscription["current_period_end"]),
            "upload_credits": str(PLAN_CREDITS.get(plan, 0)),
        },
    )


def _on_payment_succeeded(invoice: Any) -> None:
    stripe.Customer.modify(
        invoice["customer"],
        metadata={
            "subscription_status": "active",
            "last_payment_date": invoice["created"],
        },
    )


def _on_payment_failed(invoice: Any) -> None:
    stripe.Customer.modify(invoice["customer"], metadata={"subscription_status": "failed"})


def _on_subscription_deleted(subscription: Any) -> None:
    stripe.Customer.modify(
        subscription["customer"],
        metadata={"subscription_status": "cancelled", "current_plan": ""},
    )


_WEBHOOK_HANDLERS = {
    "checkout.session.completed": _on_checkout_completed,
    "customer.subscription.created": _on_subscription_created,
    "customer.subscription.deleted": _on_subscription_deleted,
    "invoice.payment_succeeded": _on_payment_succeeded,
    "invoice.payment_failed": _on_payment_failed,
}

_SIGNUP_ERRORS = {
    "UsernameExistsException": "That username is already taken.",
    "InvalidPasswordException": "That password does not meet the requirements.",
    "InvalidParameterException": "Please check your details and try again.",
}


def _current_customer() -> Any | None:
    """Stripe customer for the logged-in user, or ``None`` if they have none."""
    email = (session.get("user") or {}).get("email")
    if not email:
        return None
    customers = stripe.Customer.list(email=email, limit=1).data
    return customers[0] if customers else None


def _payments(customer_id: str) -> list[dict[str, Any]]:
    return [
        {
            "id": payment.id,
            "amount": payment.amount,
            "created": payment.created,
            "status": payment.status,
            "invoice_url": payment["invoice"],
        }
        for payment in stripe.PaymentIntent.list(customer=customer_id).data
    ]
