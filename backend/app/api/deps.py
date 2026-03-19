from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from ..models.user import User
from ..repositories.user_repository import UserRepository
from ..services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_auth_service() -> AuthService:
    return AuthService(UserRepository())


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    return auth_service.get_current_user(token)
