"""Authentication helpers — credential verification only."""
import hmac

from flask import current_app
from werkzeug.security import check_password_hash


def verify_credentials(username: str, password: str) -> bool:
    """Return True when username/password match configured admin credentials."""
    if not isinstance(username, str) or not isinstance(password, str):
        return False
    if not username or not password:
        return False
    if len(username) > 128 or len(password) > 512:
        return False

    expected_username = current_app.config.get("ADMIN_USERNAME")
    password_hash = current_app.config.get("ADMIN_PASSWORD_HASH")
    if not expected_username or not password_hash:
        return False

    if not hmac.compare_digest(username, expected_username):
        return False
    try:
        return check_password_hash(password_hash, password)
    except (ValueError, TypeError, AttributeError):
        return False
