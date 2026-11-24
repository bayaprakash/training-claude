"""Auth route tests."""


def test_login_page_renders(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"InfraWatch" in response.data


def test_login_success(client):
    response = client.post(
        "/login",
        data={"username": "admin", "password": "admin123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Signed in as" in response.data


def test_login_failure(client):
    response = client.post(
        "/login",
        data={"username": "admin", "password": "wrong"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_home_requires_auth(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (301, 302)
    assert "/login" in response.headers.get("Location", "")


def test_logout(auth_client):
    response = auth_client.post("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Sign in" in response.data
    blocked = auth_client.get("/", follow_redirects=False)
    assert blocked.status_code in (301, 302)
