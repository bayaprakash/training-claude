"""Server registry routes."""
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from app.services.decorators import login_required
from app.services.server_store import (
    add_server,
    delete_server,
    list_servers,
    validate_server_payload,
)

servers_bp = Blueprint("servers", __name__)


@servers_bp.route("/servers", methods=["GET", "POST"])
@login_required
def manage_servers():
    if request.method == "POST":
        payload, error = validate_server_payload(request.form.to_dict())
        if error:
            flash(error, "error")
            return redirect(url_for("servers.manage_servers"))
        _server, add_error = add_server(payload)
        if add_error:
            flash(add_error, "error")
        else:
            flash("Server added.", "success")
        return redirect(url_for("servers.manage_servers"))

    return render_template("servers.html", servers=list_servers())


@servers_bp.route("/servers/<server_id>/delete", methods=["POST"])
@login_required
def remove_server(server_id: str):
    if delete_server(server_id):
        flash("Server removed.", "success")
    else:
        flash("Server not found.", "error")
    return redirect(url_for("servers.manage_servers"))


@servers_bp.route("/api/servers", methods=["GET"])
@login_required
def api_list_servers():
    return jsonify(list_servers())


@servers_bp.route("/api/servers", methods=["POST"])
@login_required
def api_add_server():
    data = request.get_json(silent=True) or {}
    payload, error = validate_server_payload(data)
    if error:
        return jsonify({"error": error}), 400
    server, add_error = add_server(payload)
    if add_error:
        return jsonify({"error": add_error}), 409
    return jsonify(server), 201


@servers_bp.route("/api/servers/<server_id>", methods=["DELETE"])
@login_required
def api_delete_server(server_id: str):
    if not delete_server(server_id):
        return jsonify({"error": "Server not found"}), 404
    return jsonify({"success": True})
