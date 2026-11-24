"""Application configuration loaded from environment variables."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
# Always load project .env (cwd-independent; fixes Flask reloader / invalid login)
load_dotenv(BASE_DIR / ".env", override=False)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")
    DATABASE_PATH = os.getenv(
        "DATABASE_PATH",
        str(BASE_DIR / "data" / "servers.db"),
    )
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 1800
    METRICS_REFRESH_SECONDS = int(os.getenv("METRICS_REFRESH_SECONDS", "30"))


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SECRET_KEY = "test-secret-key"
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD_HASH = (
        "scrypt:32768:8:1$cJHo1reDFdv5yrDJ$"
        "5ed23c9f87c3a64ff802f883f677c88e802a68bf4f3184ec7546baf46d0ea4e061b7f22f7a44c2cf5c147e6d744acd78b544850caf423252b82de2c43cd34214"
    )


class ProductionConfig(Config):
    DEBUG = False
