"""Home and health routes."""
from flask import Blueprint, jsonify, render_template

from app.services.decorators import login_required

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def home():
    return render_template("home.html")


@main_bp.route("/health")
def health():
    """Liveness probe — left public for local ops checks."""
    return jsonify({"status": "ok"})
