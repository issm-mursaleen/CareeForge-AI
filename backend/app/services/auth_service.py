"""Auth business logic — register, login, refresh."""
from __future__ import annotations

from ..core.exceptions import Conflict, Unauthorized
from ..core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from ..models.user import User
from ..schemas.auth import LoginRequest, RegisterRequest, TokenPair


class AuthService:
    @staticmethod
    async def register(data: RegisterRequest) -> User:
        existing = await User.find_one(User.email == data.email)
        if existing:
            raise Conflict("Email already registered")
        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            role=data.role,
        )
        await user.insert()
        return user

    @staticmethod
    async def login(data: LoginRequest) -> tuple[User, TokenPair]:
        user = await User.find_one(User.email == data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise Unauthorized("Invalid credentials")
        if not user.is_active:
            raise Unauthorized("Account disabled")
        return user, AuthService._issue_tokens(user)

    @staticmethod
    async def refresh(refresh_token: str) -> TokenPair:
        try:
            payload = decode_token(refresh_token)
        except ValueError as e:
            raise Unauthorized(str(e)) from e
        if payload.get("type") != "refresh":
            raise Unauthorized("Wrong token type")
        user = await User.get(payload["sub"])
        if not user or not user.is_active:
            raise Unauthorized("User not found")
        return AuthService._issue_tokens(user)

    @staticmethod
    def _issue_tokens(user: User) -> TokenPair:
        return TokenPair(
            access_token=create_access_token(str(user.id), user.role.value),
            refresh_token=create_refresh_token(str(user.id)),
        )
