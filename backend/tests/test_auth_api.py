from datetime import timedelta

import pytest

from app.api.deps import get_auth_service
from app.core.security import create_access_token
from app.main import app
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService


@pytest.fixture(autouse=True)
def _override_auth_service(dynamodb_table):
    """Override get_auth_service to use the moto-backed DynamoDB table.

    Without this, UserRepository calls get_dynamodb_table() which creates a
    boto3 resource with endpoint_url — moto does not intercept those calls,
    causing the test to hang on a real connection attempt.
    """

    def override():
        return AuthService(UserRepository(table=dynamodb_table))

    app.dependency_overrides[get_auth_service] = override
    yield
    app.dependency_overrides.clear()


def test_register_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@test.com", "password": "Test1234!"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "dup@test.com", "password": "Test1234!"},
    )
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "dup@test.com", "password": "Test1234!"},
    )
    assert response.status_code == 409


def test_login_success(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "login@test.com", "password": "Test1234!"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "login@test.com", "password": "Test1234!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "wrong@test.com", "password": "Test1234!"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@test.com", "password": "WrongPass1!"},
    )
    assert response.status_code == 401


def test_me_with_token(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": "me@test.com", "password": "Test1234!"},
    )
    token = reg.json()["access_token"]
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@test.com"


def test_me_without_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_with_expired_token(client):
    token = create_access_token(
        data={"sub": "fake-id", "email": "exp@test.com"},
        expires_delta=timedelta(seconds=-1),
    )
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
