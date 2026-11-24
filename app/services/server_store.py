"""SQLite persistence for registered Linux servers."""
from __future__ import annotations

import base64
import hashlib
import os
import re
import sqlite3
import uuid
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from flask import current_app

HOSTNAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.\-_]{0,253}$")
VALID_MODES = {"ssh", "mock"}
VALID_AUTH_TYPES = {"password", "key"}


def _fernet() -> Fernet:
    secret = current_app.config.get("SECRET_KEY") or os.getenv("SECRET_KEY")
    if not secret:
        raise RuntimeError("SECRET_KEY must be set to encrypt stored credentials.")
    digest = hashlib.sha256(secret.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def _encrypt(value: str | None) -> str | None:
    if not value:
        return None
    return _fernet().encrypt(value.encode()).decode()


def _decrypt(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return _fernet().decrypt(value.encode()).decode()
    except (InvalidToken, ValueError):
        return None


def _db_path() -> str:
    return current_app.config["DATABASE_PATH"]


def _connect(path: str | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(path or _db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with _connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS servers (
                id TEXT PRIMARY KEY,
                display_name TEXT,
                hostname TEXT NOT NULL UNIQUE,
                ssh_port INTEGER NOT NULL DEFAULT 22,
                ssh_username TEXT NOT NULL,
                auth_type TEXT NOT NULL,
                credential_enc TEXT,
                collection_mode TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()


def validate_server_payload(data: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(data, dict):
        return None, "Invalid payload"

    hostname = (data.get("hostname") or "").strip()
    display_name = (data.get("display_name") or hostname).strip()
    ssh_username = (data.get("ssh_username") or "").strip()
    auth_type = (data.get("auth_type") or "password").strip().lower()
    collection_mode = (data.get("collection_mode") or "mock").strip().lower()
    credential = data.get("credential") or ""

    try:
        ssh_port = int(data.get("ssh_port") or 22)
    except (TypeError, ValueError):
        return None, "SSH port must be an integer"

    if not hostname or not HOSTNAME_RE.match(hostname):
        return None, "Invalid hostname or IP"
    if not ssh_username or len(ssh_username) > 64:
        return None, "SSH username is required"
    if ssh_port < 1 or ssh_port > 65535:
        return None, "SSH port must be between 1 and 65535"
    if auth_type not in VALID_AUTH_TYPES:
        return None, "auth_type must be password or key"
    if collection_mode not in VALID_MODES:
        return None, "collection_mode must be ssh or mock"
    if collection_mode == "ssh" and not credential:
        return None, "SSH credential (password or key path) is required for ssh mode"
    if len(str(credential)) > 4096:
        return None, "Credential is too long"

    return {
        "display_name": display_name[:128],
        "hostname": hostname,
        "ssh_port": ssh_port,
        "ssh_username": ssh_username,
        "auth_type": auth_type,
        "credential": credential if collection_mode == "ssh" else "",
        "collection_mode": collection_mode,
    }, None


def add_server(payload: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    server_id = str(uuid.uuid4())
    try:
        with _connect() as conn:
            conn.execute(
                """
                INSERT INTO servers (
                    id, display_name, hostname, ssh_port, ssh_username,
                    auth_type, credential_enc, collection_mode
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    server_id,
                    payload["display_name"],
                    payload["hostname"],
                    payload["ssh_port"],
                    payload["ssh_username"],
                    payload["auth_type"],
                    _encrypt(payload.get("credential")),
                    payload["collection_mode"],
                ),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        return None, f"Server {payload['hostname']} already exists"

    return get_server(server_id, with_credentials=False), None


def list_servers() -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, display_name, hostname, ssh_port, ssh_username, "
            "auth_type, collection_mode, created_at FROM servers "
            "ORDER BY created_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def get_server(server_id: str, with_credentials: bool = False) -> dict[str, Any] | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM servers WHERE id = ?", (server_id,)).fetchone()
    if not row:
        return None
    server = dict(row)
    if with_credentials:
        server["credential"] = _decrypt(server.pop("credential_enc", None))
    else:
        server.pop("credential_enc", None)
    return server


def delete_server(server_id: str) -> bool:
    with _connect() as conn:
        cur = conn.execute("DELETE FROM servers WHERE id = ?", (server_id,))
        conn.commit()
        return cur.rowcount > 0
