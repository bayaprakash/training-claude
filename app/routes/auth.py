"""Session-based sign-in / sign-out."""
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.services.auth_service import verify_credentials

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("main.home"))

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if verify_credentials(username, password):
            session.clear()
            session["logged_in"] = True
            session["username"] = current_app.config.get("ADMIN_USERNAME")
            flash("Signed in successfully.", "success")
            return redirect(url_for("main.home"))
        flash("Invalid username or password.", "error")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("auth.login"))
