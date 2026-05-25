"""Reusable FastAPI dependencies — auth extraction, role gating."""
from __future__ import annotations

from typing import Callable

from fastapi import Depends, Header

from ..core.exceptions import Forbidden, Unauthorized
from ..core.security import decode_token
from ..models.user import User, UserRole


async def get_current_user(authorization: str | None = Header(default=None)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise Unauthorized("Missing or malformed Authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except ValueError as e:
        raise Unauthorized(str(e)) from e
    if payload.get("type") != "access":
        raise Unauthorized("Wrong token type")
    user = await User.get(payload["sub"])
    if not user or not user.is_active:
        raise Unauthorized("User not found or inactive")
    return user


def require_role(*roles: UserRole) -> Callable:
    async def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise Forbidden(f"Requires role: {', '.join(r.value for r in roles)}")
        return user
    return _checker
