"""Dashboard and metrics API (read-only)."""
from flask import Blueprint, abort, current_app, jsonify, render_template

from app.services.decorators import login_required
from app.services.metrics_service import collect_metrics_for_server
from app.services.server_store import get_server, list_servers

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def index():
    return render_template(
        "dashboard.html",
        servers=list_servers(),
        refresh_seconds=current_app.config.get("METRICS_REFRESH_SECONDS", 30),
    )


@dashboard_bp.route("/servers/<server_id>")
@login_required
def server_detail(server_id: str):
    server = get_server(server_id)
    if not server:
        abort(404)
    return render_template(
        "server_detail.html",
        server=server,
        refresh_seconds=current_app.config.get("METRICS_REFRESH_SECONDS", 30),
    )


@dashboard_bp.route("/api/metrics")
@login_required
def metrics_all():
    results = []
    for server in list_servers():
        metrics = collect_metrics_for_server(server["id"])
        if metrics:
            results.append(metrics)
    return jsonify({"servers": results})


@dashboard_bp.route("/api/metrics/<server_id>")
@login_required
def metrics_one(server_id: str):
    metrics = collect_metrics_for_server(server_id)
    if not metrics:
        abort(404)
    return jsonify(metrics)
