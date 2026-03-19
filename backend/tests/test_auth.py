from datetime import timedelta
from importlib import import_module

import pytest
from fastapi import HTTPException

security_module = import_module("app.core.security")
model_module = import_module("app.models.user")
repository_module = import_module("app.repositories.user_repository")
service_module = import_module("app.services.auth_service")

create_access_token = security_module.create_access_token
hash_password = security_module.hash_password
verify_password = security_module.verify_password
verify_token = security_module.verify_token
User = model_module.User
UserRepository = repository_module.UserRepository
AuthService = service_module.AuthService


def test_hash_and_verify_password():
    password = "secure-password-123"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_create_and_verify_token():
    payload = {"sub": "u1", "email": "u1@example.com"}

    token = create_access_token(payload)
    decoded = verify_token(token)

    assert decoded["sub"] == payload["sub"]
    assert decoded["email"] == payload["email"]


def test_register_new_user(dynamodb_table):
    repository = UserRepository(dynamodb_table)
    service = AuthService(repository)

    response = service.register("new@example.com", "password-123")
    saved_user = repository.get_user_by_email("new@example.com")

    assert response.token_type == "bearer"
    assert response.access_token
    assert saved_user is not None
    assert saved_user.email == "new@example.com"
    assert saved_user.hashed_password != "password-123"
    assert verify_password("password-123", saved_user.hashed_password) is True


def test_register_duplicate_email(dynamodb_table):
    service = AuthService(UserRepository(dynamodb_table))
    email = "duplicate@example.com"

    service.register(email, "password-123")

    with pytest.raises(HTTPException) as exc_info:
        service.register(email, "password-123")

    assert exc_info.value.status_code == 409


def test_login_success(dynamodb_table):
    repository = UserRepository(dynamodb_table)
    service = AuthService(repository)
    email = "login-success@example.com"
    password = "password-123"

    repository.create_user(
        User(id="user-1", email=email, hashed_password=hash_password(password))
    )

    response = service.login(email, password)
    decoded = verify_token(response.access_token)

    assert response.token_type == "bearer"
    assert decoded["sub"] == "user-1"
    assert decoded["email"] == email


def test_login_wrong_password(dynamodb_table):
    repository = UserRepository(dynamodb_table)
    service = AuthService(repository)
    email = "login-wrong@example.com"

    repository.create_user(
        User(id="user-2", email=email, hashed_password=hash_password("right-password"))
    )

    with pytest.raises(HTTPException) as exc_info:
        service.login(email, "wrong-password")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "이메일 또는 비밀번호가 잘못되었습니다"


def test_get_current_user_valid_token(dynamodb_table):
    repository = UserRepository(dynamodb_table)
    service = AuthService(repository)
    user = User(
        id="user-3",
        email="current@example.com",
        hashed_password=hash_password("password-123"),
    )
    repository.create_user(user)

    token = create_access_token({"sub": user.id, "email": user.email})
    current_user = service.get_current_user(token)

    assert current_user.id == user.id
    assert current_user.email == user.email


def test_get_current_user_expired_token(dynamodb_table):
    repository = UserRepository(dynamodb_table)
    service = AuthService(repository)
    user = User(
        id="user-4",
        email="expired@example.com",
        hashed_password=hash_password("password-123"),
    )
    repository.create_user(user)

    expired_token = create_access_token(
        {"sub": user.id, "email": user.email},
        expires_delta=timedelta(minutes=-1),
    )

    with pytest.raises(HTTPException) as exc_info:
        service.get_current_user(expired_token)

    assert exc_info.value.status_code == 401
