from fastapi.testclient import TestClient

def test_register_user(client: TestClient):
    payload = {
        "username": "new_agent",
        "email": "new_agent@forensics.local",
        "password": "SecurePassword123!",
        "full_name": "New Agent",
        "role": "Investigator"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "new_agent"
    assert data["email"] == "new_agent@forensics.local"
    assert "password" not in data

def test_login_user(client: TestClient, investigator_user):
    payload = {
        "username": "investigator_test",
        "password": "InvestigatorPass123!"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "investigator_test"

def test_login_invalid_password(client: TestClient, investigator_user):
    payload = {
        "username": "investigator_test",
        "password": "WrongPassword!"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401

def test_get_me(client: TestClient, investigator_token):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "investigator_test"
    assert data["role"] == "Investigator"
