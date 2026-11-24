"""Flask application factory."""
import os
from pathlib import Path

from flask import Flask

from app.config import DevelopmentConfig, ProductionConfig
from app.services.server_store import init_db


def create_app(config_class=None) -> Flask:
    if config_class is None:
        env = os.getenv("FLASK_ENV", "development").lower()
        config_class = (
            ProductionConfig if env == "production" else DevelopmentConfig
        )

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config.from_object(config_class)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY must be set in the environment (via .env).")
    if not app.config.get("ADMIN_PASSWORD_HASH"):
        raise RuntimeError(
            "ADMIN_PASSWORD_HASH must be set in the environment (via .env)."
        )

    db_path = Path(app.config["DATABASE_PATH"])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    init_db(str(db_path))

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.main import main_bp
    from app.routes.servers import servers_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(servers_bp)
    app.register_blueprint(dashboard_bp)
    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True, port=5000)
