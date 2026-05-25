from __future__ import annotations

from datetime import datetime
from enum import Enum

from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    USER = "user"
    RECRUITER = "recruiter"
    ADMIN = "admin"


class UserProfile(BaseModel):
    title: str | None = None
    bio: str | None = None
    target_role: str | None = None
    location: str | None = None
    avatar_url: str | None = None


class User(Document):
    email: Indexed(EmailStr, unique=True)
    password_hash: str
    full_name: str
    role: UserRole = UserRole.USER
    profile: UserProfile = Field(default_factory=UserProfile)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        indexes = ["role"]
