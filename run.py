"""Local entry point for the monitoring demo."""
import os

from app.app import create_app

app = create_app()

if __name__ == "__main__":
    # Default 5095 — port 5000 is often taken on shared lab hosts
    port = int(os.getenv("PORT", "5095"))
    # use_reloader=False avoids bind races on busy lab VMs
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=port)
