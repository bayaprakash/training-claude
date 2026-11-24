"""Server registry tests."""


def test_add_list_delete_server(auth_client):
    created = auth_client.post(
        "/api/servers",
        json={
            "hostname": "demo-01.local",
            "ssh_port": 22,
            "ssh_username": "monitor",
            "auth_type": "password",
            "credential": "",
            "collection_mode": "mock",
            "display_name": "Demo One",
        },
    )
    assert created.status_code == 201
    body = created.get_json()
    assert body["hostname"] == "demo-01.local"
    assert "credential" not in body
    assert "credential_enc" not in body

    listed = auth_client.get("/api/servers")
    assert listed.status_code == 200
    servers = listed.get_json()
    assert len(servers) == 1
    server_id = servers[0]["id"]

    deleted = auth_client.delete(f"/api/servers/{server_id}")
    assert deleted.status_code == 200
    assert auth_client.get("/api/servers").get_json() == []


def test_reject_invalid_hostname(auth_client):
    response = auth_client.post(
        "/api/servers",
        json={
            "hostname": "bad host!",
            "ssh_username": "monitor",
            "collection_mode": "mock",
        },
    )
    assert response.status_code == 400
    assert "hostname" in response.get_json()["error"].lower()


def test_ssh_mode_requires_credential(auth_client):
    response = auth_client.post(
        "/api/servers",
        json={
            "hostname": "ssh-01.local",
            "ssh_username": "monitor",
            "collection_mode": "ssh",
            "credential": "",
        },
    )
    assert response.status_code == 400
