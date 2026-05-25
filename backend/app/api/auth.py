from __future__ import annotations

from fastapi import APIRouter, Depends

from ..models.user import User
from ..schemas.auth import (
    LoginRequest, MeResponse, RefreshRequest, RegisterRequest, TokenPair,
)
from ..services.auth_service import AuthService
from .dependencies import get_current_user

router = APIRouter()


@router.post("/register", response_model=TokenPair, status_code=201)
async def register(data: RegisterRequest) -> TokenPair:
    user = await AuthService.register(data)
    _, tokens = await AuthService.login(LoginRequest(email=data.email, password=data.password))
    return tokens


@router.post("/login", response_model=TokenPair)
async def login(data: LoginRequest) -> TokenPair:
    _, tokens = await AuthService.login(data)
    return tokens


@router.post("/refresh", response_model=TokenPair)
async def refresh(data: RefreshRequest) -> TokenPair:
    return await AuthService.refresh(data.refresh_token)


@router.get("/me", response_model=MeResponse)
async def me(user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        profile=user.profile.model_dump(),
        created_at=user.created_at.isoformat(),
    )
