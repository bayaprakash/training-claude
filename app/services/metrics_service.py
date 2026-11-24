"""Route metrics collection by server mode."""
from __future__ import annotations

from typing import Any

from app.services.mock_collector import collect_mock_metrics
from app.services.server_store import get_server
from app.services.ssh_collector import collect_ssh_metrics


def collect_metrics_for_server(server_id: str) -> dict[str, Any] | None:
    server = get_server(server_id, with_credentials=True)
    if not server:
        return None

    mode = server.get("collection_mode")
    if mode == "mock":
        metrics = collect_mock_metrics(server["hostname"])
    else:
        metrics = collect_ssh_metrics(server)

    metrics["server_id"] = server_id
    metrics["display_name"] = server.get("display_name") or server["hostname"]
    metrics["collection_mode"] = mode
    return metrics
