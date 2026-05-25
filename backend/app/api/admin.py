from __future__ import annotations

from fastapi import APIRouter, Depends

from ..models.ai_log import AILog
from ..models.resume import Resume
from ..models.user import User, UserRole
from .dependencies import require_role

router = APIRouter()


@router.get("/overview", dependencies=[Depends(require_role(UserRole.ADMIN))])
async def overview() -> dict:
    total_users = await User.count()
    total_resumes = await Resume.count()
    total_ai_calls = await AILog.count()
    total_cost = sum(
        log.cost_usd for log in await AILog.find().to_list()
    )
    by_role: dict[str, int] = {}
    for role in UserRole:
        by_role[role.value] = await User.find(User.role == role).count()
    return {
        "total_users": total_users,
        "total_resumes": total_resumes,
        "total_ai_calls": total_ai_calls,
        "estimated_cost_usd": round(total_cost, 4),
        "users_by_role": by_role,
    }


@router.get("/users", dependencies=[Depends(require_role(UserRole.ADMIN))])
async def list_users(limit: int = 50) -> list[dict]:
    users = await User.find().limit(limit).to_list()
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role.value,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]
