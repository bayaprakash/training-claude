"""Dashboard UX and metrics refresh endpoint tests."""


def test_dashboard_shows_refresh_interval(auth_client):
    response = auth_client.get("/dashboard")
    assert response.status_code == 200
    assert b"Auto-refreshes every 30s" in response.data
    assert b"Refresh now" in response.data


def test_dashboard_with_server_includes_refresh_data_attr(auth_client):
    created = auth_client.post(
        "/api/servers",
        json={
            "hostname": "dash-01.local",
            "ssh_username": "monitor",
            "collection_mode": "mock",
            "display_name": "Dash One",
        },
    )
    assert created.status_code == 201
    server_id = created.get_json()["id"]

    dashboard = auth_client.get("/dashboard")
    assert dashboard.status_code == 200
    assert b'data-refresh="30"' in dashboard.data
    assert b"Dash One" in dashboard.data

    detail = auth_client.get(f"/servers/{server_id}")
    assert detail.status_code == 200
    assert b"Read-only view" in detail.data
    assert b'data-refresh="30"' in detail.data


def test_metrics_refresh_endpoint(auth_client):
    auth_client.post(
        "/api/servers",
        json={
            "hostname": "refresh.local",
            "ssh_username": "u",
            "collection_mode": "mock",
        },
    )
    response = auth_client.get("/api/metrics")
    assert response.status_code == 200
    payload = response.get_json()
    assert "servers" in payload
    assert len(payload["servers"]) >= 1
    assert payload["servers"][0]["status"] == "mock"


def test_end_to_end_mock_flow(auth_client):
    """Login already done via fixture: add mock server → metrics → delete → logout."""
    created = auth_client.post(
        "/api/servers",
        json={
            "hostname": "e2e.local",
            "ssh_username": "ops",
            "collection_mode": "mock",
            "display_name": "E2E",
        },
    )
    assert created.status_code == 201
    server_id = created.get_json()["id"]

    metrics = auth_client.get(f"/api/metrics/{server_id}")
    assert metrics.status_code == 200
    body = metrics.get_json()
    assert body["status"] == "mock"
    assert "cpu" in body and "memory" in body and "network" in body and "ports" in body

    assert auth_client.delete(f"/api/servers/{server_id}").status_code == 200
    logout = auth_client.post("/logout", follow_redirects=True)
    assert logout.status_code == 200
    assert auth_client.get("/dashboard", follow_redirects=False).status_code in (301, 302)
