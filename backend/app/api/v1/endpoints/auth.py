from typing import Annotated

from fastapi import APIRouter, Depends, status

from ...deps import get_auth_service, get_current_user
from ....models.user import User
from ....schemas.user import TokenResponse, UserCreate, UserLogin
from ....services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(
    body: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    return auth_service.register(body.email, body.password)


@router.post("/login", response_model=TokenResponse)
def login(
    body: UserLogin,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    return auth_service.login(body.email, body.password)


@router.get("/me")
def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return {"id": current_user.id, "email": current_user.email}
