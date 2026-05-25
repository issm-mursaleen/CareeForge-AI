from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from ..models.user import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=80)
    role: UserRole = UserRole.USER


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class MeResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: UserRole
    profile: dict
    created_at: str
