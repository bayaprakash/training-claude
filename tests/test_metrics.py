"""Metrics collector and API tests."""
from unittest.mock import patch

from app.services.mock_collector import collect_mock_metrics
from app.services.ssh_collector import (
    collect_ssh_metrics,
    parse_cpu,
    parse_memory,
    parse_network,
    parse_ports,
)


def test_mock_metrics_shape():
    metrics = collect_mock_metrics("host-a")
    assert metrics["status"] == "mock"
    assert "percent" in metrics["cpu"]
    assert "used" in metrics["memory"]
    assert "bytes_recv" in metrics["network"]
    assert isinstance(metrics["ports"], list)


def test_parse_helpers():
    assert parse_cpu("100 50|200 80") == 70.0
    mem = parse_memory("1000 400 600")
    assert mem["percent"] == 40.0
    assert parse_network("123 456") == {"bytes_recv": 123, "bytes_sent": 456}
    ports = parse_ports(
        "LISTEN 0 128 0.0.0.0:22 0.0.0.0:*\nLISTEN 0 128 127.0.0.1:5432 0.0.0.0:*"
    )
    assert {p["port"] for p in ports} >= {22, 5432}


def test_metrics_api_requires_auth(client):
    assert client.get("/api/metrics").status_code == 401


def test_metrics_api_mock(auth_client):
    created = auth_client.post(
        "/api/servers",
        json={
            "hostname": "mock-api.local",
            "ssh_username": "u",
            "collection_mode": "mock",
        },
    )
    server_id = created.get_json()["id"]
    response = auth_client.get(f"/api/metrics/{server_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "mock"
    assert data["server_id"] == server_id


def test_ssh_unreachable_on_connect_failure():
    server = {
        "hostname": "nope.example",
        "ssh_port": 22,
        "ssh_username": "u",
        "auth_type": "password",
        "credential": "x",
    }
    with patch("app.services.ssh_collector._connect", side_effect=OSError("down")):
        metrics = collect_ssh_metrics(server)
    assert metrics["status"] == "unreachable"


def test_ssh_parse_success_with_mocked_client():
    server = {
        "hostname": "ok.example",
        "ssh_port": 22,
        "ssh_username": "u",
        "auth_type": "password",
        "credential": "x",
    }

    class FakeClient:
        def close(self):
            return None

    def fake_exec(_client, command, timeout=12):
        if "proc/stat" in command:
            return "100 90|200 150"
        if "free -b" in command:
            return "8589934592 4294967296 4294967296"
        if "proc/net/dev" in command:
            return "1000 2000"
        return "LISTEN 0 128 0.0.0.0:22 0.0.0.0:*"

    with (
        patch("app.services.ssh_collector._connect", return_value=FakeClient()),
        patch("app.services.ssh_collector._exec", side_effect=fake_exec),
    ):
        metrics = collect_ssh_metrics(server)

    assert metrics["status"] == "online"
    assert metrics["cpu"]["percent"] == 40.0
    assert metrics["network"]["bytes_sent"] == 2000
    assert any(p["port"] == 22 for p in metrics["ports"])


def test_dashboard_requires_auth(client):
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code in (301, 302)
