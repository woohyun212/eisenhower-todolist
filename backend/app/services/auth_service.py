from uuid import uuid4

import jwt
from fastapi import HTTPException, status

from ..core.security import create_access_token, hash_password, verify_password, verify_token
from ..models.user import User
from ..repositories.user_repository import UserRepository
from ..schemas.user import TokenResponse


INVALID_CREDENTIALS_MESSAGE = "이메일 또는 비밀번호가 잘못되었습니다"


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository: UserRepository = user_repository

    def register(self, email: str, password: str) -> TokenResponse:
        existing = self.user_repository.get_user_by_email(email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 사용 중인 이메일입니다",
            )

        user = User(
            id=str(uuid4()),
            email=email,
            hashed_password=hash_password(password),
        )
        _ = self.user_repository.create_user(user)

        token = create_access_token({"sub": user.id, "email": user.email})
        return TokenResponse(access_token=token)

    def login(self, email: str, password: str) -> TokenResponse:
        user = self.user_repository.get_user_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_CREDENTIALS_MESSAGE,
            )

        token = create_access_token({"sub": user.id, "email": user.email})
        return TokenResponse(access_token=token)

    def get_current_user(self, token: str) -> User:
        try:
            payload = verify_token(token)
        except jwt.InvalidTokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 인증 토큰입니다",
            ) from exc

        user_id = payload.get("sub")
        if not isinstance(user_id, str) or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 인증 토큰입니다",
            )

        user = self.user_repository.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 인증 토큰입니다",
            )

        return user
